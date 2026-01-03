"""Tool execution engine for terminal commands, MCP tools, and file operations.

Provides unified execution interface for terminal commands, MCP tool calls, and
file operations with proper error handling, logging, and result processing.
"""

import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .mcp_integration import MCPIntegration
from .file_operations_executor import FileOperationsExecutor
from ..events.models import EventType

logger = logging.getLogger(__name__)


class ToolExecutionResult:
    """Result of tool execution."""

    def __init__(self, tool_id: str, tool_type: str, success: bool,
                 output: str = "", error: str = "", execution_time: float = 0.0,
                 metadata: Dict[str, Any] = None):
        """Initialize tool execution result.

        Args:
            tool_id: Unique identifier for the tool
            tool_type: Type of tool (terminal, mcp_tool, file_edit, etc.)
            success: Whether execution was successful
            output: Tool output/result
            error: Error message if failed
            execution_time: Execution time in seconds
            metadata: Additional metadata (e.g., diff_info for file edits)
        """
        self.tool_id = tool_id
        self.tool_type = tool_type
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "tool_id": self.tool_id,
            "tool_type": self.tool_type,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp
        }
    
    def __str__(self) -> str:
        """String representation of result."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"[{status}] {self.tool_type}:{self.tool_id} ({self.execution_time:.2f}s)"


class ToolExecutor:
    """Execute tools with unified interface for terminal, MCP, and file operations.

    Handles execution of terminal commands, MCP tool calls, and file operations
    with proper error handling, timeouts, and result logging.
    """

    def __init__(self, mcp_integration: MCPIntegration, event_bus,
                 terminal_timeout: int = 90, mcp_timeout: int = 180, config=None):
        """Initialize tool executor.

        Args:
            mcp_integration: MCP integration instance
            event_bus: Event bus for hook emissions
            terminal_timeout: Timeout for terminal commands in seconds
            mcp_timeout: Timeout for MCP tool calls in seconds
            config: Configuration manager (optional)
        """
        self.mcp_integration = mcp_integration
        self.event_bus = event_bus
        self.terminal_timeout = terminal_timeout
        self.mcp_timeout = mcp_timeout

        # File operations executor
        self.file_ops_executor = FileOperationsExecutor(config=config)

        # Execution statistics
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "terminal_executions": 0,
            "mcp_executions": 0,
            "file_op_executions": 0,
            "total_execution_time": 0.0
        }

        logger.info("Tool executor initialized with terminal, MCP, and file operations support")
    
    async def execute_tool(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a single tool (terminal, MCP, or file operation).

        Args:
            tool_data: Tool information from ResponseParser

        Returns:
            Tool execution result
        """
        tool_type = tool_data.get("type", "unknown")
        tool_id = tool_data.get("id", "unknown")

        start_time = time.time()

        try:
            # Emit pre-execution hook
            await self.event_bus.emit_with_hooks(
                EventType.TOOL_CALL_PRE,
                {"tool_data": tool_data},
                "tool_executor"
            )

            # Execute based on tool type
            try:
                logger.debug(f"Executing tool {tool_id} of type {tool_type}")
                try:
                    if tool_type == "terminal":
                        logger.debug(f"About to call _execute_terminal_command for {tool_id}")
                        result = await self._execute_terminal_command(tool_data)
                        logger.debug(f"_execute_terminal_command completed for {tool_id}")
                    elif tool_type == "mcp_tool":
                        logger.debug(f"About to call _execute_mcp_tool for {tool_id}")
                        result = await self._execute_mcp_tool(tool_data)
                        logger.debug(f"_execute_mcp_tool completed for {tool_id}")
                    elif tool_type.startswith("file_"):
                        # File operation
                        logger.debug(f"About to call _execute_file_operation for {tool_id}")
                        result = await self._execute_file_operation(tool_data)
                        logger.debug(f"_execute_file_operation completed for {tool_id}")
                    else:
                        result = ToolExecutionResult(
                            tool_id=tool_id,
                            tool_type=tool_type,
                            success=False,
                            error=f"Unknown tool type: {tool_type}"
                        )
                    logger.debug(f"Tool {tool_id} execution result: success={result.success}")
                except Exception as inner_e:
                    import traceback
                    inner_trace = traceback.format_exc()
                    logger.error(f"Inner execution error for {tool_id}: {str(inner_e)}")
                    logger.error(f"Inner execution traceback for {tool_id}: {inner_trace}")
                    raise  # Re-raise for outer handler
            except Exception as e:
                import traceback
                error_details = f"Tool execution exception: {str(e)}\nTraceback: {traceback.format_exc()}"
                logger.error(f"Critical error during tool {tool_id} execution: {error_details}")
                result = ToolExecutionResult(
                    tool_id=tool_id,
                    tool_type=tool_type,
                    success=False,
                    error=f"Tool execution error: {str(e)}"
                )

            # Update execution time
            result.execution_time = time.time() - start_time

            # Emit post-execution hook
            await self.event_bus.emit_with_hooks(
                EventType.TOOL_CALL_POST,
                {
                    "tool_data": tool_data,
                    "result": result.to_dict()
                },
                "tool_executor"
            )

            # Update statistics
            self._update_stats(result)

            logger.info(f"Tool execution completed: {result}")
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_result = ToolExecutionResult(
                tool_id=tool_id,
                tool_type=tool_type,
                success=False,
                error=f"Execution error: {str(e)}",
                execution_time=execution_time
            )

            self._update_stats(error_result)
            logger.error(f"Tool execution failed: {e}")
            return error_result
    
    async def execute_all_tools(self, tools: List[Dict[str, Any]]) -> List[ToolExecutionResult]:
        """Execute multiple tools in sequence.
        
        Args:
            tools: List of tool data from ResponseParser
            
        Returns:
            List of execution results in order
        """
        if not tools:
            return []
        
        logger.info(f"Executing {len(tools)} tools in sequence")
        results = []
        
        for i, tool_data in enumerate(tools):
            logger.debug(f"Executing tool {i+1}/{len(tools)}: {tool_data.get('id', 'unknown')}")
            
            result = await self.execute_tool(tool_data)
            results.append(result)
            
            # Log intermediate result
            if result.success:
                logger.debug(f"Tool {i+1} succeeded: {len(result.output)} chars output")
            else:
                logger.warning(f"Tool {i+1} failed: {result.error}")
                # Continue executing remaining tools even if one fails
        
        logger.info(f"Tool execution batch completed: "
                   f"{sum(1 for r in results if r.success)}/{len(results)} successful")
        
        return results
    
    async def _execute_terminal_command(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a terminal command.
        
        Args:
            tool_data: Terminal tool data with command
            
        Returns:
            Execution result
        """
        command = tool_data.get("command", "").strip()
        tool_id = tool_data.get("id", "unknown")
        
        if not command:
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type="terminal",
                success=False,
                error="Empty command"
            )
        
        logger.debug(f"Executing terminal command: {command[:100]}...")
        
        try:
            # Execute command with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.terminal_timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolExecutionResult(
                    tool_id=tool_id,
                    tool_type="terminal",
                    success=False,
                    error=f"Command timed out after {self.terminal_timeout} seconds"
                )
            
            # Process results
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            success = process.returncode == 0
            output = stdout_text if success else stderr_text
            error = "" if success else f"Exit code {process.returncode}: {stderr_text}"
            
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type="terminal",
                success=success,
                output=output,
                error=error
            )
            
        except Exception as e:
            import traceback
            error_details = f"Execution exception: {str(e)}\nTraceback: {traceback.format_exc()}"
            logger.error(f"Terminal execution failed for command '{command}': {error_details}")
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type="terminal",
                success=False,
                error=f"Execution error: {str(e)}"
            )
    
    async def _execute_mcp_tool(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
        """Execute an MCP tool call.
        
        Args:
            tool_data: MCP tool data with name and arguments
            
        Returns:
            Execution result
        """
        tool_name = tool_data.get("name", "")
        tool_arguments = tool_data.get("arguments", {})
        tool_id = tool_data.get("id", "unknown")
        
        if not tool_name:
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type="mcp_tool",
                success=False,
                error="Missing tool name"
            )
        
        logger.debug(f"Executing MCP tool: {tool_name} with args {tool_arguments}")
        
        try:
            # Call MCP tool with timeout
            mcp_result = await asyncio.wait_for(
                self.mcp_integration.call_mcp_tool(tool_name, tool_arguments),
                timeout=self.mcp_timeout
            )
            
            # Process MCP result
            if "error" in mcp_result:
                return ToolExecutionResult(
                    tool_id=tool_id,
                    tool_type="mcp_tool",
                    success=False,
                    error=mcp_result["error"]
                )
            else:
                # Format MCP output for display
                output = self._format_mcp_output(mcp_result)
                
                return ToolExecutionResult(
                    tool_id=tool_id,
                    tool_type="mcp_tool",
                    success=True,
                    output=output
                )
                
        except asyncio.TimeoutError:
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type="mcp_tool",
                success=False,
                error=f"MCP tool timed out after {self.mcp_timeout} seconds"
            )
        except Exception as e:
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type="mcp_tool",
                success=False,
                error=f"MCP execution error: {str(e)}"
            )
    
    def _format_mcp_output(self, mcp_result: Dict[str, Any]) -> str:
        """Format MCP tool result for display.

        Args:
            mcp_result: Raw MCP result dictionary

        Returns:
            Formatted output string
        """
        # Handle different MCP result formats
        if "content" in mcp_result:
            # Standard MCP content format
            content = mcp_result["content"]
            if isinstance(content, list) and content:
                # Multiple content blocks
                parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            parts.append(block.get("text", ""))
                        else:
                            parts.append(str(block))
                    else:
                        parts.append(str(block))
                return "\n".join(parts)
            else:
                return str(content)

        elif "output" in mcp_result:
            # Simple output format
            return str(mcp_result["output"])

        elif "result" in mcp_result:
            # JSON-RPC result format
            return str(mcp_result["result"])

        else:
            # Fallback: stringify entire result
            return str(mcp_result)

    async def _execute_file_operation(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a file operation.

        Args:
            tool_data: File operation data from parser

        Returns:
            Tool execution result
        """
        tool_id = tool_data.get("id", "unknown")
        tool_type = tool_data.get("type", "unknown")

        logger.debug(f"Executing file operation: {tool_type}")

        # Run file operation synchronously (file I/O is blocking anyway)
        # Use asyncio.to_thread to avoid blocking the event loop
        try:
            result_dict = await asyncio.to_thread(
                self.file_ops_executor.execute_operation,
                tool_data
            )

            # Convert to ToolExecutionResult, preserving metadata (e.g., diff_info)
            metadata = {}
            if "diff_info" in result_dict:
                metadata["diff_info"] = result_dict["diff_info"]

            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type=tool_type,
                success=result_dict.get("success", False),
                output=result_dict.get("output", ""),
                error=result_dict.get("error", ""),
                metadata=metadata
            )

        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"File operation execution failed: {error_trace}")
            return ToolExecutionResult(
                tool_id=tool_id,
                tool_type=tool_type,
                success=False,
                error=f"File operation error: {str(e)}"
            )
    
    def _update_stats(self, result: ToolExecutionResult):
        """Update execution statistics.

        Args:
            result: Tool execution result
        """
        self.stats["total_executions"] += 1
        self.stats["total_execution_time"] += result.execution_time

        if result.success:
            self.stats["successful_executions"] += 1
        else:
            self.stats["failed_executions"] += 1

        if result.tool_type == "terminal":
            self.stats["terminal_executions"] += 1
        elif result.tool_type == "mcp_tool":
            self.stats["mcp_executions"] += 1
        elif result.tool_type.startswith("file_"):
            self.stats["file_op_executions"] += 1
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics.
        
        Returns:
            Dictionary of execution statistics
        """
        total = self.stats["total_executions"]
        if total == 0:
            return {**self.stats, "success_rate": 0.0, "average_time": 0.0}
        
        return {
            **self.stats,
            "success_rate": self.stats["successful_executions"] / total,
            "average_time": self.stats["total_execution_time"] / total
        }
    
    def format_result_for_conversation(self, result: ToolExecutionResult) -> str:
        """Format tool result for conversation history.
        
        Args:
            result: Tool execution result
            
        Returns:
            Formatted string for conversation logging
        """
        if result.success:
            return f"[{result.tool_type}] {result.output}"
        else:
            return f"[{result.tool_type}] ERROR: {result.error}"
    
    def reset_stats(self):
        """Reset execution statistics."""
        self.stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "terminal_executions": 0,
            "mcp_executions": 0,
            "file_op_executions": 0,
            "total_execution_time": 0.0
        }
        logger.info("Tool execution statistics reset")