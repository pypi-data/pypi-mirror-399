"""Response parsing for LLM outputs with comprehensive tag support.

Handles parsing of special tags including thinking, terminal commands,
MCP tool calls, and file operations from LLM responses with clean architecture.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)


class FileOperationParser:
    """Parse file operations from LLM response without XML parser.

    Uses regex-based parsing to extract file operation blocks, treating
    tag content as raw text (no CDATA escaping needed).

    Supports 14 file operations:
    - edit: Replace content in existing file
    - create: Create new file
    - create_overwrite: Create/overwrite file
    - delete: Delete file
    - move: Move/rename file
    - copy: Copy file
    - copy_overwrite: Copy file with overwrite
    - append: Append to file
    - insert_after: Insert content after pattern
    - insert_before: Insert content before pattern
    - mkdir: Create directory
    - rmdir: Remove directory
    - read: Read file content
    - grep: Search file for pattern
    """

    def __init__(self):
        """Initialize file operation parser with compiled regex patterns."""
        # Operation-level patterns (outer tags only)
        self.edit_pattern = re.compile(
            r'<edit>(.*?)</edit>',
            re.DOTALL | re.IGNORECASE
        )
        self.create_pattern = re.compile(
            r'<create>(.*?)</create>',
            re.DOTALL | re.IGNORECASE
        )
        self.create_overwrite_pattern = re.compile(
            r'<create_overwrite>(.*?)</create_overwrite>',
            re.DOTALL | re.IGNORECASE
        )
        self.delete_pattern = re.compile(
            r'<delete>(.*?)</delete>',
            re.DOTALL | re.IGNORECASE
        )
        self.move_pattern = re.compile(
            r'<move>(.*?)</move>',
            re.DOTALL | re.IGNORECASE
        )
        self.copy_pattern = re.compile(
            r'<copy>(.*?)</copy>',
            re.DOTALL | re.IGNORECASE
        )
        self.copy_overwrite_pattern = re.compile(
            r'<copy_overwrite>(.*?)</copy_overwrite>',
            re.DOTALL | re.IGNORECASE
        )
        self.append_pattern = re.compile(
            r'<append>(.*?)</append>',
            re.DOTALL | re.IGNORECASE
        )
        self.insert_after_pattern = re.compile(
            r'<insert_after>(.*?)</insert_after>',
            re.DOTALL | re.IGNORECASE
        )
        self.insert_before_pattern = re.compile(
            r'<insert_before>(.*?)</insert_before>',
            re.DOTALL | re.IGNORECASE
        )
        self.mkdir_pattern = re.compile(
            r'<mkdir>(.*?)</mkdir>',
            re.DOTALL | re.IGNORECASE
        )
        self.rmdir_pattern = re.compile(
            r'<rmdir>(.*?)</rmdir>',
            re.DOTALL | re.IGNORECASE
        )
        self.read_pattern = re.compile(
            r'<read>(.*?)</read>',
            re.DOTALL | re.IGNORECASE
        )
        self.grep_pattern = re.compile(
            r'<grep>(.*?)</grep>',
            re.DOTALL | re.IGNORECASE
        )

        logger.debug("File operation parser initialized with 14 operation patterns")

    def parse_response(self, llm_response: str) -> List[Dict[str, Any]]:
        """Extract all file operations from LLM response.

        Args:
            llm_response: Raw LLM response text

        Returns:
            List of operation dictionaries with type and parameters
        """
        operations = []

        # Parse each operation type in order of appearance
        operations.extend(self._parse_operations(
            self.edit_pattern, self._parse_edit_block, llm_response, "edit"
        ))
        operations.extend(self._parse_operations(
            self.create_pattern, self._parse_create_block, llm_response, "create"
        ))
        operations.extend(self._parse_operations(
            self.create_overwrite_pattern, self._parse_create_overwrite_block,
            llm_response, "create_overwrite"
        ))
        operations.extend(self._parse_operations(
            self.delete_pattern, self._parse_delete_block, llm_response, "delete"
        ))
        operations.extend(self._parse_operations(
            self.move_pattern, self._parse_move_block, llm_response, "move"
        ))
        operations.extend(self._parse_operations(
            self.copy_pattern, self._parse_copy_block, llm_response, "copy"
        ))
        operations.extend(self._parse_operations(
            self.copy_overwrite_pattern, self._parse_copy_overwrite_block,
            llm_response, "copy_overwrite"
        ))
        operations.extend(self._parse_operations(
            self.append_pattern, self._parse_append_block, llm_response, "append"
        ))
        operations.extend(self._parse_operations(
            self.insert_after_pattern, self._parse_insert_after_block,
            llm_response, "insert_after"
        ))
        operations.extend(self._parse_operations(
            self.insert_before_pattern, self._parse_insert_before_block,
            llm_response, "insert_before"
        ))
        operations.extend(self._parse_operations(
            self.mkdir_pattern, self._parse_mkdir_block, llm_response, "mkdir"
        ))
        operations.extend(self._parse_operations(
            self.rmdir_pattern, self._parse_rmdir_block, llm_response, "rmdir"
        ))
        operations.extend(self._parse_operations(
            self.read_pattern, self._parse_read_block, llm_response, "read"
        ))
        operations.extend(self._parse_operations(
            self.grep_pattern, self._parse_grep_block, llm_response, "grep"
        ))

        if operations:
            logger.info(f"Parsed {len(operations)} file operations from response")

        return operations

    def _parse_operations(
        self,
        pattern: re.Pattern,
        parser_func: callable,
        text: str,
        op_name: str
    ) -> List[Dict[str, Any]]:
        """Generic operation parser.

        Args:
            pattern: Compiled regex pattern for operation
            parser_func: Function to parse inner content
            text: Text to search in
            op_name: Operation name for error reporting

        Returns:
            List of parsed operations
        """
        operations = []

        for i, match in enumerate(pattern.finditer(text)):
            inner_content = match.group(1)
            try:
                op = parser_func(inner_content)
                op["id"] = f"file_{op_name}_{i}"
                operations.append(op)
                logger.debug(f"Parsed {op_name} operation: {op.get('file', 'N/A')}")
            except ValueError as e:
                logger.error(f"Invalid <{op_name}> block: {e}")
                # Build helpful error with expected format
                expected_format = self._get_expected_format(op_name)
                # Add malformed operation for error reporting
                operations.append({
                    "type": "malformed_file_op",
                    "id": f"malformed_{op_name}_{i}",
                    "operation": op_name,
                    "error": str(e),
                    "expected_format": expected_format,
                    "content_preview": inner_content[:300] if len(inner_content) > 300 else inner_content
                })

        return operations

    def _get_expected_format(self, op_name: str) -> str:
        """Get expected format string for a file operation."""
        formats = {
            "edit": "<edit>\n  <file>path/to/file</file>\n  <find>text to find</find>\n  <replace>replacement text</replace>\n</edit>",
            "create": "<create>\n  <file>path/to/file</file>\n  <content>file content</content>\n</create>",
            "create_overwrite": "<create_overwrite>\n  <file>path/to/file</file>\n  <content>file content</content>\n</create_overwrite>",
            "delete": "<delete>\n  <file>path/to/file</file>\n</delete>",
            "move": "<move>\n  <from>source/path</from>\n  <to>dest/path</to>\n</move>",
            "copy": "<copy>\n  <from>source/path</from>\n  <to>dest/path</to>\n</copy>",
            "append": "<append>\n  <file>path/to/file</file>\n  <content>content to append</content>\n</append>",
            "read": "<read>\n  <file>path/to/file</file>\n</read>",
            "mkdir": "<mkdir>\n  <path>directory/path</path>\n</mkdir>",
            "rmdir": "<rmdir>\n  <path>directory/path</path>\n</rmdir>",
            "insert_after": "<insert_after>\n  <file>path</file>\n  <pattern>match</pattern>\n  <content>new content</content>\n</insert_after>",
            "insert_before": "<insert_before>\n  <file>path</file>\n  <pattern>match</pattern>\n  <content>new content</content>\n</insert_before>",
        }
        return formats.get(op_name, f"<{op_name}>...</{op_name}>")

    def _extract_tag(
        self,
        tag_name: str,
        content: str,
        required: bool = True
    ) -> Optional[str]:
        """Extract content between tags.

        Args:
            tag_name: Tag name (without < >)
            content: Content to search in
            required: If True, raises ValueError if tag not found

        Returns:
            Content between tags, or None if not found and not required

        Raises:
            ValueError: If tag not found and required=True
        """
        pattern = re.compile(
            f'<{tag_name}>(.*?)</{tag_name}>',
            re.DOTALL | re.IGNORECASE
        )
        match = pattern.search(content)

        if not match:
            if required:
                raise ValueError(f"Missing required tag: <{tag_name}>")
            return None

        return match.group(1)

    def _parse_edit_block(self, content: str) -> Dict[str, Any]:
        """Parse <edit> block.

        Args:
            content: Inner content of <edit> tag

        Returns:
            Parsed operation dictionary
        """
        return {
            "type": "file_edit",
            "file": self._extract_tag("file", content).strip(),
            "find": self._extract_tag("find", content),       # Preserve whitespace
            "replace": self._extract_tag("replace", content)  # Preserve whitespace
        }

    def _parse_create_block(self, content: str) -> Dict[str, Any]:
        """Parse <create> block."""
        return {
            "type": "file_create",
            "file": self._extract_tag("file", content).strip(),
            "content": self._extract_tag("content", content)
        }

    def _parse_create_overwrite_block(self, content: str) -> Dict[str, Any]:
        """Parse <create_overwrite> block."""
        return {
            "type": "file_create_overwrite",
            "file": self._extract_tag("file", content).strip(),
            "content": self._extract_tag("content", content)
        }

    def _parse_delete_block(self, content: str) -> Dict[str, Any]:
        """Parse <delete> block."""
        return {
            "type": "file_delete",
            "file": self._extract_tag("file", content).strip()
        }

    def _parse_move_block(self, content: str) -> Dict[str, Any]:
        """Parse <move> block."""
        return {
            "type": "file_move",
            "from": self._extract_tag("from", content).strip(),
            "to": self._extract_tag("to", content).strip()
        }

    def _parse_copy_block(self, content: str) -> Dict[str, Any]:
        """Parse <copy> block."""
        return {
            "type": "file_copy",
            "from": self._extract_tag("from", content).strip(),
            "to": self._extract_tag("to", content).strip()
        }

    def _parse_copy_overwrite_block(self, content: str) -> Dict[str, Any]:
        """Parse <copy_overwrite> block."""
        return {
            "type": "file_copy_overwrite",
            "from": self._extract_tag("from", content).strip(),
            "to": self._extract_tag("to", content).strip()
        }

    def _parse_append_block(self, content: str) -> Dict[str, Any]:
        """Parse <append> block."""
        return {
            "type": "file_append",
            "file": self._extract_tag("file", content).strip(),
            "content": self._extract_tag("content", content)
        }

    def _parse_insert_after_block(self, content: str) -> Dict[str, Any]:
        """Parse <insert_after> block."""
        return {
            "type": "file_insert_after",
            "file": self._extract_tag("file", content).strip(),
            "pattern": self._extract_tag("pattern", content),
            "content": self._extract_tag("content", content)
        }

    def _parse_insert_before_block(self, content: str) -> Dict[str, Any]:
        """Parse <insert_before> block."""
        return {
            "type": "file_insert_before",
            "file": self._extract_tag("file", content).strip(),
            "pattern": self._extract_tag("pattern", content),
            "content": self._extract_tag("content", content)
        }

    def _parse_mkdir_block(self, content: str) -> Dict[str, Any]:
        """Parse <mkdir> block."""
        return {
            "type": "file_mkdir",
            "path": self._extract_tag("path", content).strip()
        }

    def _parse_rmdir_block(self, content: str) -> Dict[str, Any]:
        """Parse <rmdir> block."""
        return {
            "type": "file_rmdir",
            "path": self._extract_tag("path", content).strip()
        }

    def _parse_read_block(self, content: str) -> Dict[str, Any]:
        """Parse <read> block."""
        file_path = self._extract_tag("file", content).strip()
        lines_spec = self._extract_tag("lines", content, required=False)

        result = {
            "type": "file_read",
            "file": file_path
        }

        if lines_spec:
            result["lines"] = lines_spec.strip()

        return result

    def _parse_grep_block(self, content: str) -> Dict[str, Any]:
        """Parse <grep> block."""
        file_path = self._extract_tag("file", content).strip()
        pattern = self._extract_tag("pattern", content).strip()

        result = {
            "type": "file_grep",
            "file": file_path,
            "pattern": pattern
        }

        # Optional: case_insensitive flag
        case_insensitive = self._extract_tag("case_insensitive", content, required=False)
        if case_insensitive:
            result["case_insensitive"] = case_insensitive.strip().lower() in ("true", "1", "yes")

        return result


class ResponseParser:
    """Parse and extract structured content from LLM responses.

    Supports multiple tag formats:
    - <think>content</think> - Thinking/reasoning content (removed from output)
    - <terminal>command</terminal> - Bash terminal commands
    - <tool name="tool_name" arg1="value" arg2="value">content</tool> - MCP tool calls
    - File operations: <edit>, <create>, <delete>, <move>, <copy>, <append>, etc.
    """

    def __init__(self):
        """Initialize response parser with compiled regex patterns."""
        # Thinking tags - removed from final output
        self.thinking_pattern = re.compile(
            r'<think>(.*?)</think>',
            re.DOTALL | re.IGNORECASE
        )

        # Terminal command tags
        self.terminal_pattern = re.compile(
            r'<terminal>(.*?)</terminal>',
            re.DOTALL | re.IGNORECASE
        )

        # MCP tool call tags with attributes
        self.tool_pattern = re.compile(
            r'<tool\s+([^>]*?)>(.*?)</tool>',
            re.DOTALL | re.IGNORECASE
        )

        # File operations parser
        self.file_ops_parser = FileOperationParser()

        logger.info("Response parser initialized with comprehensive tag support + file operations")
    
    async def initialize(self) -> bool:
        """Initialize the response parser."""
        self.is_initialized = True
        logger.debug("Response parser async initialization complete")
        return True
    
    def parse_response(self, raw_response: str) -> Dict[str, Any]:
        """Parse LLM response and extract all components.

        Args:
            raw_response: Raw response text from LLM

        Returns:
            Parsed response with all extracted components
        """
        # DIAGNOSTIC: McKinsey Phase 2 - Root cause analysis
        opening_count = raw_response.count('<think>')
        closing_count = raw_response.count('</think>')
        orphaned_closes = closing_count - opening_count

        if orphaned_closes > 0:
            logger.critical(f"🔍 BUG-011 DIAGNOSTIC: Found {orphaned_closes} orphaned </think> tags in RAW response")
            logger.critical(f"Opening tags: {opening_count}, Closing tags: {closing_count}")
            logger.critical(f"First 500 chars: {raw_response[:500]}")
        elif orphaned_closes < 0:
            logger.warning(f"🔍 BUG-011 DIAGNOSTIC: Found {abs(orphaned_closes)} orphaned <think> tags (unclosed)")

        # Extract all components
        thinking_blocks = self._extract_thinking(raw_response)
        terminal_commands = self._extract_terminal_commands(raw_response)
        tool_calls = self._extract_tool_calls(raw_response)
        file_operations = self.file_ops_parser.parse_response(raw_response)

        # Clean content (remove all tags)
        clean_content = self._clean_content(raw_response)

        # DIAGNOSTIC: Verify defensive fix effectiveness
        if '</think>' in clean_content or '<think>' in clean_content:
            remaining_closes = clean_content.count('</think>')
            remaining_opens = clean_content.count('<think>')
            logger.error(f"⚠️ BUG-011 ALERT: Defensive fix FAILED - {remaining_closes} </think> and {remaining_opens} <think> remain!")
            logger.error(f"Cleaned content sample: {clean_content[:500]}")
        elif orphaned_closes > 0:
            logger.info(f"✅ BUG-011 SUCCESS: Defensive fix removed {orphaned_closes} orphaned tags")

        # Determine if turn is completed (no tools pending execution)
        turn_completed = (
            len(terminal_commands) == 0 and
            len(tool_calls) == 0 and
            len(file_operations) == 0
        )

        parsed = {
            "raw": raw_response,
            "content": clean_content,
            "turn_completed": turn_completed,
            "components": {
                "thinking": thinking_blocks,
                "terminal_commands": terminal_commands,
                "tool_calls": tool_calls,
                "file_operations": file_operations
            },
            "metadata": {
                "has_thinking": bool(thinking_blocks),
                "has_terminal_commands": bool(terminal_commands),
                "has_tool_calls": bool(tool_calls),
                "has_file_operations": bool(file_operations),
                "total_tools": len(terminal_commands) + len(tool_calls) + len(file_operations),
                "content_length": len(clean_content)
            }
        }

        logger.debug(f"Parsed response: {len(thinking_blocks)} thinking, "
                    f"{len(terminal_commands)} terminal, {len(tool_calls)} tools, "
                    f"{len(file_operations)} file ops")

        return parsed
    
    def _extract_thinking(self, content: str) -> List[str]:
        """Extract thinking content blocks.
        
        Args:
            content: Raw response content
            
        Returns:
            List of thinking content strings
        """
        matches = self.thinking_pattern.findall(content)
        return [match.strip() for match in matches if match.strip()]
    
    def _extract_terminal_commands(self, content: str) -> List[Dict[str, Any]]:
        """Extract terminal command blocks.
        
        Args:
            content: Raw response content
            
        Returns:
            List of terminal command dictionaries
        """
        commands = []
        matches = self.terminal_pattern.findall(content)
        
        for i, match in enumerate(matches):
            command = match.strip()
            if command:
                commands.append({
                    "type": "terminal",
                    "id": f"terminal_{i}",
                    "command": command,
                    "raw": match
                })
        
        return commands
    
    def _extract_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Extract MCP tool call blocks.
        
        Args:
            content: Raw response content
            
        Returns:
            List of tool call dictionaries
        """
        tool_calls = []
        matches = self.tool_pattern.findall(content)
        
        for i, (attributes_str, tool_content) in enumerate(matches):
            try:
                # Parse tool attributes
                tool_info = self._parse_tool_attributes(attributes_str)
                
                # Build tool call
                tool_call = {
                    "type": "mcp_tool",
                    "id": f"mcp_tool_{i}",
                    "name": tool_info.get("name", "unknown"),
                    "arguments": tool_info.get("arguments", {}),
                    "content": tool_content.strip(),
                    "raw": f"<tool {attributes_str}>{tool_content}</tool>"
                }
                
                tool_calls.append(tool_call)
                
            except Exception as e:
                logger.warning(f"Failed to parse tool call: {e}")
                # Add as malformed tool call for debugging
                tool_calls.append({
                    "type": "malformed_tool",
                    "id": f"malformed_{i}",
                    "error": str(e),
                    "raw": f"<tool {attributes_str}>{tool_content}</tool>"
                })
        
        return tool_calls
    
    def _parse_tool_attributes(self, attributes_str: str) -> Dict[str, Any]:
        """Parse tool tag attributes.
        
        Supports formats like:
        - name="file_reader" path="/etc/hosts"
        - name="search" query="python" limit="10"
        
        Args:
            attributes_str: Raw attributes string
            
        Returns:
            Parsed attributes with name and arguments
        """
        tool_info = {"name": None, "arguments": {}}
        
        # Parse attributes using regex to handle quoted values
        attr_pattern = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))'
        matches = re.findall(attr_pattern, attributes_str)
        
        for attr_name, quoted_val1, quoted_val2, unquoted_val in matches:
            value = quoted_val1 or quoted_val2 or unquoted_val
            
            if attr_name == "name":
                tool_info["name"] = value
            else:
                # Convert value to appropriate type
                tool_info["arguments"][attr_name] = self._convert_value(value)
        
        return tool_info
    
    def _convert_value(self, value: str) -> Any:
        """Convert string value to appropriate Python type.
        
        Args:
            value: String value to convert
            
        Returns:
            Converted value (str, int, float, bool, or original)
        """
        if not value:
            return value
        
        # Try boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Try integer
        try:
            if "." not in value:
                return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _clean_content(self, content: str) -> str:
        """Remove all special tags from content.

        Args:
            content: Raw content with tags

        Returns:
            Cleaned content without any special tags
        """
        # Remove thinking tags (paired)
        cleaned = self.thinking_pattern.sub('', content)

        # DEFENSIVE: Remove any orphaned thinking tags
        # McKinsey Root Cause Analysis tracked to BUG-011
        cleaned = re.sub(r'</think>', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'<think>', '', cleaned, flags=re.IGNORECASE)

        # Remove terminal tags but preserve content structure
        cleaned = self.terminal_pattern.sub('', cleaned)

        # Remove tool tags but preserve content structure
        cleaned = self.tool_pattern.sub('', cleaned)

        # Remove file operation tags (all 14 types)
        # Only successfully parsed tags are removed; malformed tags remain visible
        cleaned = self.file_ops_parser.edit_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.create_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.create_overwrite_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.delete_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.move_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.copy_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.copy_overwrite_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.append_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.insert_after_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.insert_before_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.mkdir_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.rmdir_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.read_pattern.sub('', cleaned)
        cleaned = self.file_ops_parser.grep_pattern.sub('', cleaned)

        # Clean up excessive whitespace
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = cleaned.strip()

        return cleaned
    
    def get_all_tools(self, parsed_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all tools (terminal + MCP + file ops) in execution order.

        Args:
            parsed_response: Parsed response from parse_response()

        Returns:
            List of all tools to execute in order
        """
        components = parsed_response.get("components", {})

        all_tools = []
        all_tools.extend(components.get("terminal_commands", []))
        all_tools.extend(components.get("tool_calls", []))
        all_tools.extend(components.get("file_operations", []))

        # Sort by original position in text (based on ID)
        def sort_key(tool):
            tool_id = tool.get("id", "")
            if "terminal_" in tool_id:
                return (0, int(tool_id.split("_")[1]))
            elif "mcp_tool_" in tool_id:
                return (1, int(tool_id.split("_")[2]))
            elif "file_" in tool_id:
                # Extract index from file operation IDs like "file_edit_0"
                parts = tool_id.split("_")
                if len(parts) >= 3:
                    return (2, int(parts[-1]))
                return (2, 0)
            else:
                return (3, 0)

        all_tools.sort(key=sort_key)
        return all_tools
    
    def format_for_display(self, parsed_response: Dict[str, Any],
                          show_thinking: bool = True) -> str:
        """Format parsed response for terminal display.

        Args:
            parsed_response: Parsed response data
            show_thinking: Whether to include thinking content

        Returns:
            Formatted string for display
        """
        parts = []

        # Add thinking content if enabled
        if show_thinking:
            thinking = parsed_response.get("components", {}).get("thinking", [])
            for thought in thinking:
                parts.append(f"[dim]{thought}[/dim]")
                parts.append("")

        # Add main content
        content = parsed_response.get("content", "").strip()
        if content:
            parts.append(content)

        # Add tool execution indicators
        metadata = parsed_response.get("metadata", {})
        if (metadata.get("has_terminal_commands") or
            metadata.get("has_tool_calls") or
            metadata.get("has_file_operations")):
            tools_count = metadata.get("total_tools", 0)
            parts.append("")
            parts.append(f"[cyan]Executing {tools_count} tool(s)...[/cyan]")

        return "\n".join(parts)
    
    def validate_response(self, response: str) -> Tuple[bool, List[str]]:
        """Validate response format and syntax.
        
        Args:
            response: Raw response to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for unclosed tags
        open_tags = ["<think>", "<terminal>", "<tool"]
        close_tags = ["</think>", "</terminal>", "</tool>"]
        
        for open_tag, close_tag in zip(open_tags, close_tags):
            if open_tag in response and close_tag not in response:
                issues.append(f"Unclosed tag: {open_tag}")
        
        # Check for malformed tool tags
        tool_matches = self.tool_pattern.findall(response)
        for attributes_str, content in tool_matches:
            if 'name=' not in attributes_str:
                issues.append("Tool tag missing 'name' attribute")
        
        # Check for empty response
        if not response.strip():
            issues.append("Empty response")
        
        return len(issues) == 0, issues
    
    def extract_execution_stats(self, parsed_response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract execution statistics from parsed response.
        
        Args:
            parsed_response: Parsed response data
            
        Returns:
            Execution statistics
        """
        metadata = parsed_response.get("metadata", {})
        components = parsed_response.get("components", {})
        
        return {
            "content_words": len(parsed_response.get("content", "").split()),
            "thinking_blocks": len(components.get("thinking", [])),
            "terminal_commands": len(components.get("terminal_commands", [])),
            "mcp_tool_calls": len(components.get("tool_calls", [])),
            "total_tools": metadata.get("total_tools", 0),
            "turn_completed": parsed_response.get("turn_completed", True),
            "complexity": self._assess_complexity(parsed_response)
        }
    
    def _assess_complexity(self, parsed_response: Dict[str, Any]) -> str:
        """Assess response complexity level.
        
        Args:
            parsed_response: Parsed response data
            
        Returns:
            Complexity level: simple, moderate, complex
        """
        score = 0
        metadata = parsed_response.get("metadata", {})
        
        # Content length scoring
        content_length = metadata.get("content_length", 0)
        if content_length > 500:
            score += 2
        elif content_length > 200:
            score += 1
        
        # Tool usage scoring
        if metadata.get("has_thinking"):
            score += 1
        if metadata.get("has_terminal_commands"):
            score += 1
        if metadata.get("has_tool_calls"):
            score += 2
        
        # Multiple tools indicate complexity
        if metadata.get("total_tools", 0) > 1:
            score += 1
        
        # Map score to complexity
        if score >= 4:
            return "complex"
        elif score >= 2:
            return "moderate"
        else:
            return "simple"