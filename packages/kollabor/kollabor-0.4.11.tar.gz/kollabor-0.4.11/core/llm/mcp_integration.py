"""MCP (Model Context Protocol) integration for LLM core service.

Provides integration with MCP servers for tool discovery and execution,
enabling the LLM to interact with external tools and services.
"""

import asyncio
import json
import logging
import re
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MCPIntegration:
    """MCP server and tool integration.
    
    Manages discovery, registration, and execution of MCP tools,
    bridging external services with the LLM core service.
    """
    
    def __init__(self):
        """Initialize MCP integration."""
        self.mcp_servers = {}
        self.tool_registry = {}
        self.active_connections = {}
        
        # MCP configuration directories (local project first, then global)
        self.local_mcp_dir = Path.cwd() / ".kollabor-cli" / "mcp"
        self.global_mcp_dir = Path.home() / ".kollabor-cli" / "mcp"
        
        # Load from both local and global configs
        self._load_mcp_config()
        
        logger.info("MCP Integration initialized")
    
    def _load_mcp_config(self):
        """Load MCP configuration from Kollabor config directories."""
        # Load from global config first (lower priority)
        self._load_config_from_dir(self.global_mcp_dir, "global")
        
        # Load from local config second (higher priority, can override)
        self._load_config_from_dir(self.local_mcp_dir, "local")
        
        logger.info(f"Loaded {len(self.mcp_servers)} total MCP server configurations")
    
    def _load_config_from_dir(self, config_dir: Path, config_type: str):
        """Load MCP config from a specific directory.
        
        Args:
            config_dir: Directory to load config from
            config_type: Type of config (local/global) for logging
        """
        try:
            mcp_settings = config_dir / "mcp_settings.json"
            if mcp_settings.exists():
                with open(mcp_settings, 'r') as f:
                    config = json.load(f)
                    servers = config.get("servers", {})
                    self.mcp_servers.update(servers)
                    logger.info(f"Loaded {len(servers)} MCP servers from {config_type} config")
        except Exception as e:
            logger.warning(f"Failed to load {config_type} MCP config: {e}")
    
    async def discover_mcp_servers(self) -> Dict[str, Any]:
        """Auto-discover available MCP servers.
        
        Returns:
            Dictionary of discovered MCP servers and their capabilities
        """
        discovered = {}
        
        # Check for local MCP servers
        await self._discover_local_servers(discovered)
        
        # Check for configured servers
        for server_name, server_config in self.mcp_servers.items():
            if await self._validate_server(server_config):
                discovered[server_name] = {
                    "name": server_name,
                    "type": server_config.get("type", "unknown"),
                    "capabilities": await self._get_server_capabilities(server_config),
                    "status": "available"
                }
                logger.info(f"Discovered MCP server: {server_name}")
        
        return discovered
    
    async def _discover_local_servers(self, discovered: Dict):
        """Discover locally running MCP servers."""
        # Check common MCP server locations
        common_paths = [
            Path.home() / ".mcp" / "servers",
            Path("/usr/local/mcp/servers"),
            Path.cwd() / ".mcp" / "servers"
        ]
        
        for path in common_paths:
            if path.exists():
                for server_dir in path.iterdir():
                    if server_dir.is_dir():
                        manifest = server_dir / "manifest.json"
                        if manifest.exists():
                            try:
                                with open(manifest, 'r') as f:
                                    server_info = json.load(f)
                                    server_name = server_info.get("name", server_dir.name)
                                    discovered[server_name] = {
                                        "name": server_name,
                                        "path": str(server_dir),
                                        "manifest": server_info,
                                        "status": "local"
                                    }
                                    logger.info(f"Discovered local MCP server: {server_name}")
                            except Exception as e:
                                logger.warning(f"Failed to load manifest from {server_dir}: {e}")
    
    async def _validate_server(self, server_config: Dict) -> bool:
        """Validate that an MCP server is accessible.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            True if server is accessible, False otherwise
        """
        # Basic validation - can be extended with actual connection test
        required_fields = ["command"] if server_config.get("type") == "stdio" else ["url"]
        return all(field in server_config for field in required_fields)
    
    async def _get_server_capabilities(self, server_config: Dict) -> List[str]:
        """Get capabilities of an MCP server.
        
        Args:
            server_config: Server configuration dictionary
            
        Returns:
            List of server capabilities
        """
        capabilities = []
        
        # For stdio servers, we can query capabilities
        if server_config.get("type") == "stdio":
            try:
                result = await self._execute_server_command(
                    server_config.get("command", ""),
                    "--list-tools"
                )
                if result:
                    # Parse tool list from output
                    tools = result.split("\n")
                    capabilities.extend([t.strip() for t in tools if t.strip()])
            except Exception as e:
                logger.warning(f"Failed to get server capabilities: {e}")
        
        return capabilities or ["unknown"]
    
    async def register_mcp_tool(self, tool_name: str, server: str, 
                               tool_definition: Optional[Dict] = None) -> bool:
        """Register an MCP tool for LLM use.
        
        Args:
            tool_name: Name of the tool
            server: Server providing the tool
            tool_definition: Optional tool definition/schema
            
        Returns:
            True if registration successful
        """
        try:
            self.tool_registry[tool_name] = {
                "server": server,
                "definition": tool_definition or {},
                "enabled": True
            }
            logger.info(f"Registered MCP tool: {tool_name} from {server}")
            return True
        except Exception as e:
            logger.error(f"Failed to register MCP tool {tool_name}: {e}")
            return False
    
    async def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool call.
        
        Args:
            tool_name: Name of the tool to execute
            params: Parameters for the tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in self.tool_registry:
            return {
                "error": f"Tool '{tool_name}' not found",
                "available_tools": list(self.tool_registry.keys())
            }
        
        tool_info = self.tool_registry[tool_name]
        server_name = tool_info["server"]
        
        if not tool_info["enabled"]:
            return {"error": f"Tool '{tool_name}' is disabled"}
        
        try:
            # Get server configuration
            server_config = self.mcp_servers.get(server_name, {})
            
            # Execute tool based on server type
            if server_config.get("type") == "stdio":
                result = await self._execute_stdio_tool(server_config, tool_name, params)
            elif server_config.get("type") == "http":
                result = await self._execute_http_tool(server_config, tool_name, params)
            else:
                result = {"error": f"Unknown server type for {server_name}"}
            
            logger.info(f"Executed MCP tool: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute MCP tool {tool_name}: {e}")
            return {"error": str(e)}
    
    async def _execute_stdio_tool(self, server_config: Dict, tool_name: str,
                                 params: Dict) -> Dict[str, Any]:
        """Execute a tool via stdio MCP server.

        Args:
            server_config: Server configuration
            tool_name: Tool to execute
            params: Tool parameters

        Returns:
            Tool execution result
        """
        command = server_config.get("command", "")
        if not command:
            return {"error": "No command specified for stdio server"}

        # Validate tool_name to prevent command injection
        # Only allow alphanumeric, underscore, hyphen, and dot
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', tool_name):
            return {"error": f"Invalid tool name: {tool_name}"}

        # Build command as list (safer than shell=True)
        # Parse the command string and add tool arguments
        try:
            command_parts = shlex.split(command)
        except ValueError as e:
            return {"error": f"Invalid command format: {e}"}

        command_parts.extend(["--tool", tool_name])

        # Add parameters as JSON input
        input_json = json.dumps(params)

        try:
            result = subprocess.run(
                command_parts,
                shell=False,
                input=input_json,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Try to parse JSON output
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"output": result.stdout}
            else:
                return {"error": result.stderr or f"Tool exited with code {result.returncode}"}
                
        except subprocess.TimeoutExpired:
            return {"error": "Tool execution timed out"}
        except Exception as e:
            return {"error": f"Failed to execute tool: {e}"}
    
    async def _execute_http_tool(self, server_config: Dict, tool_name: str, 
                                params: Dict) -> Dict[str, Any]:
        """Execute a tool via HTTP MCP server.
        
        Args:
            server_config: Server configuration
            tool_name: Tool to execute
            params: Tool parameters
            
        Returns:
            Tool execution result
        """
        # This would implement HTTP-based MCP tool calls
        # For now, return a placeholder
        return {
            "status": "not_implemented",
            "message": "HTTP MCP servers not yet implemented"
        }
    
    async def _execute_server_command(self, command: str, *args) -> Optional[str]:
        """Execute a server command and return output.
        
        Args:
            command: Base command to execute
            *args: Additional arguments
            
        Returns:
            Command output or None if failed
        """
        try:
            full_command = [command] + list(args)
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout
            return None
        except Exception as e:
            logger.warning(f"Failed to execute server command: {e}")
            return None
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available MCP tools.
        
        Returns:
            List of available tools with their information
        """
        tools = []
        for tool_name, tool_info in self.tool_registry.items():
            tools.append({
                "name": tool_name,
                "server": tool_info["server"],
                "enabled": tool_info["enabled"],
                "definition": tool_info.get("definition", {})
            })
        return tools
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable an MCP tool.
        
        Args:
            tool_name: Name of the tool to enable
            
        Returns:
            True if tool was enabled
        """
        if tool_name in self.tool_registry:
            self.tool_registry[tool_name]["enabled"] = True
            logger.info(f"Enabled MCP tool: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable an MCP tool.
        
        Args:
            tool_name: Name of the tool to disable
            
        Returns:
            True if tool was disabled
        """
        if tool_name in self.tool_registry:
            self.tool_registry[tool_name]["enabled"] = False
            logger.info(f"Disabled MCP tool: {tool_name}")
            return True
        return False
    
    async def shutdown(self):
        """Shutdown MCP integration and close connections."""
        # Close any active connections
        for connection_id, connection in self.active_connections.items():
            try:
                if hasattr(connection, 'close'):
                    await connection.close()
                logger.debug(f"Closed MCP connection: {connection_id}")
            except Exception as e:
                logger.warning(f"Error closing MCP connection {connection_id}: {e}")
        
        self.active_connections.clear()
        logger.info("MCP Integration shutdown complete")