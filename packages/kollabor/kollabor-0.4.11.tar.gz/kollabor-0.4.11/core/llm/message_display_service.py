"""Message Display Service for LLM responses.

Handles unified message display coordination, eliminating duplicated
display logic throughout the LLM service. Follows KISS principle with
single responsibility for message display orchestration.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from core.io.visual_effects import ColorPalette

logger = logging.getLogger(__name__)


class MessageDisplayService:
    """Unified service for coordinating LLM message display.
    
    Eliminates code duplication by providing a single point of control
    for all message display operations including thinking duration,
    assistant responses, and tool execution results.
    
    Follows KISS principle: Single responsibility for message display coordination.
    Implements DRY principle: Eliminates ~90 lines of duplicated display code.
    """
    
    def __init__(self, renderer):
        """Initialize message display service.

        Args:
            renderer: Terminal renderer with message_coordinator
        """
        self.renderer = renderer
        self.message_coordinator = renderer.message_coordinator
        self._streaming_active = False

        logger.info("Message display service initialized")
    
    
    def display_thinking_and_response(self,
                                    thinking_duration: float,
                                    response: str,
                                    show_thinking_threshold: float = 0.1) -> None:
        """Display thinking duration and assistant response atomically.

        Args:
            thinking_duration: Time spent thinking in seconds
            response: Assistant response content
            show_thinking_threshold: Minimum duration to show thinking message
        """
        # Use the unified display method for consistency
        self.display_complete_response(
            thinking_duration=thinking_duration,
            response=response,
            tool_results=None,
            original_tools=None,
            show_thinking_threshold=show_thinking_threshold
        )
    
    def display_tool_results(self, tool_results: List[Any], original_tools: List[Dict] = None) -> None:
        """Display tool execution results with consistent formatting.
        
        Args:
            tool_results: List of tool execution result objects
            original_tools: List of original tool data for command extraction
        """
        for i, result in enumerate(tool_results):
            # Get original tool data for display
            tool_data = original_tools[i] if original_tools and i < len(original_tools) else {}
            
            # Format tool execution display with consistent styling
            tool_display = self._format_tool_header(result, tool_data)
            result_display = self._format_tool_result(result)
            
            # Build combined tool display message
            combined_output = [tool_display, result_display]
            
            # Add actual output if appropriate
            if self._should_show_output(result):
                output_lines = self._format_tool_output(result)
                combined_output.extend(output_lines)
            
            # Create message sequence for this tool
            tool_messages = [
                ("error" if not result.success else "system", 
                 "\n".join(combined_output), {})
            ]
            
            # Add spacing between tools if multiple
            if len(tool_results) > 1 and i < len(tool_results) - 1:
                tool_messages.append(("system", "", {}))
            
            # Display tool messages using coordinator
            self.message_coordinator.display_message_sequence(tool_messages)
        
        logger.debug(f"Displayed {len(tool_results)} tool results")
    
    def display_user_message(self, message: str) -> None:
        """Display user message through coordinator.

        Args:
            message: User's input message
        """
        # Don't display user messages in pipe mode
        if getattr(self.renderer, 'pipe_mode', False):
            logger.debug(f"Suppressing user message in pipe mode: {len(message)} chars")
            return

        message_sequence = [("user", message, {})]
        self.message_coordinator.display_message_sequence(message_sequence)
        logger.debug(f"Displayed user message: {len(message)} chars")
    
    def display_system_message(self, message: str) -> None:
        """Display system message through coordinator.
        
        Args:
            message: System message to display
        """
        message_sequence = [("system", message, {})]
        self.message_coordinator.display_message_sequence(message_sequence)
        logger.debug(f"Displayed system message: {message[:50]}...")
    
    def display_error_message(self, error: str) -> None:
        """Display error message through coordinator.
        
        Args:
            error: Error message to display
        """
        message_sequence = [("error", f"Error: {error}", {})]
        self.message_coordinator.display_message_sequence(message_sequence)
        logger.debug(f"Displayed error message: {error[:50]}...")
    
    def display_cancellation_message(self) -> None:
        """Display request cancellation message."""
        # Don't display cancellation message in pipe mode (it's expected during cleanup)
        pipe_mode = getattr(self.renderer, 'pipe_mode', False)

        if hasattr(self.renderer, 'pipe_mode') and pipe_mode:
            logger.debug("Suppressing cancellation message in pipe mode")
            return

        message_sequence = [
            ("system", "Request cancelled", {}),
            ("system", "", {})  # Empty line for spacing
        ]
        self.message_coordinator.display_message_sequence(message_sequence)
        logger.debug("Displayed cancellation message")
    
    def _format_tool_header(self, result, tool_data: Dict = None) -> str:
        """Format tool execution header with consistent styling.

        Args:
            result: Tool execution result
            tool_data: Original tool data for command/name extraction

        Returns:
            Formatted tool header string
        """
        # Tool indicator with dynamic color support
        indicator = f"{ColorPalette.BRIGHT_LIME}⏺{ColorPalette.RESET}"

        if result.tool_type == "terminal":
            # Extract actual command from original tool data
            command = tool_data.get("command", "unknown") if tool_data else result.tool_id
            return f"{indicator} terminal({command})"
        elif result.tool_type == "mcp_tool":
            # Extract tool name and arguments from original tool data
            tool_name = tool_data.get("name", "unknown") if tool_data else result.tool_id
            arguments = tool_data.get("arguments", {}) if tool_data else {}
            return f"{indicator} {tool_name}({arguments})"
        elif result.tool_type.startswith("file_"):
            # Extract filename/path from file operation data
            display_info = self._extract_file_display_info(tool_data, result.tool_type)
            return f"{indicator} {result.tool_type}({display_info})"
        else:
            return f"{indicator} {result.tool_type}({result.tool_id})"

    def _extract_file_display_info(self, tool_data: Dict, tool_type: str) -> str:
        """Extract display information from file operation data.

        Args:
            tool_data: Original tool data
            tool_type: Type of file operation

        Returns:
            Filename or path to display
        """
        if not tool_data:
            return "unknown"

        # Most file operations use 'file' key
        if "file" in tool_data:
            return tool_data["file"]

        # Move/copy operations use 'from' and 'to'
        if "from" in tool_data and "to" in tool_data:
            return f"{tool_data['from']} → {tool_data['to']}"

        # mkdir/rmdir use 'path'
        if "path" in tool_data:
            return tool_data["path"]

        return "unknown"
    
    def _format_tool_result(self, result) -> str:
        """Format tool execution result summary.

        Args:
            result: Tool execution result

        Returns:
            Formatted result summary string
        """
        if result.success:
            # Count output characteristics for summary
            output_lines = result.output.count('\n') + 1 if result.output else 0
            output_chars = len(result.output) if result.output else 0

            if result.tool_type == "terminal" and result.output:
                return f"\033[32m ▮ Read {output_lines} lines ({output_chars} chars)\033[0m"
            elif result.tool_type == "file_read" and result.output:
                # Extract line count from output message "✓ Read X lines from..."
                import re
                match = re.search(r'Read (\d+) lines', result.output)
                if match:
                    line_count = match.group(1)
                    return f"\033[32m ▮ Read {line_count} lines\033[0m"
                return f"\033[32m ▮ Success\033[0m"
            elif result.tool_type == "mcp_tool" and result.output:
                preview = result.output[:50] + "..." if len(result.output) > 50 else result.output
                return f"\033[32m ▮ {preview}\033[0m"
            else:
                return f"\033[32m ▮ Success\033[0m"
        else:
            return f"\033[31m ▮ Error: {result.error}\033[0m"
    
    def _should_show_output(self, result) -> bool:
        """Determine if tool output should be displayed inline.
        
        Args:
            result: Tool execution result
            
        Returns:
            True if output should be shown
        """
        return (result.success and 
                result.output and 
                len(result.output) < 500)
    
    def _format_tool_output(self, result) -> List[str]:
        """Format tool output for inline display.

        Args:
            result: Tool execution result

        Returns:
            List of formatted output lines
        """
        # Special formatting for file_edit with diff info
        if (result.tool_type == "file_edit" and
            hasattr(result, 'metadata') and
            result.metadata and
            'diff_info' in result.metadata):
            return self._format_edit_diff(result)

        # Default formatting for other outputs
        output_lines = result.output.strip().split('\n')
        formatted_lines = []

        # Show first 20 lines with indentation
        for line in output_lines[:20]:
            formatted_lines.append(f"    {line}")

        # Add truncation message if needed
        if len(output_lines) > 20:
            remaining = len(output_lines) - 20
            formatted_lines.append(f"    ... ({remaining} more lines)")

        return formatted_lines

    def _format_edit_diff(self, result) -> List[str]:
        """Format file edit as a pretty condensed diff.

        Args:
            result: Tool execution result with diff_info

        Returns:
            List of formatted diff lines
        """
        diff_info = result.metadata.get('diff_info', {})
        find_text = diff_info.get('find', '')
        replace_text = diff_info.get('replace', '')
        count = diff_info.get('count', 0)

        formatted_lines = []

        # Show the first line of output (✅ Replaced...)
        first_line = result.output.split('\n')[0]
        formatted_lines.append(f"    {first_line}")

        # Add pretty diff visualization
        formatted_lines.append("")

        # Removed lines (red with -)
        removed_lines = find_text.split('\n')
        for line in removed_lines[:3]:  # Show max 3 lines
            formatted_lines.append(f"    \033[31m│- {line}\033[0m")

        if len(removed_lines) > 3:
            formatted_lines.append(f"    \033[31m│  ... ({len(removed_lines) - 3} more lines)\033[0m")

        # Separator
        formatted_lines.append("    \033[90m│\033[0m")

        # Added lines (green with +)
        added_lines = replace_text.split('\n')
        for line in added_lines[:3]:  # Show max 3 lines
            formatted_lines.append(f"    \033[32m│+ {line}\033[0m")

        if len(added_lines) > 3:
            formatted_lines.append(f"    \033[32m│  ... ({len(added_lines) - 3} more lines)\033[0m")

        formatted_lines.append("")

        # Add backup info if present
        output_lines = result.output.split('\n')
        for line in output_lines[1:]:  # Skip first line (already shown)
            if line.strip():
                formatted_lines.append(f"    {line}")

        return formatted_lines

    def display_generating_progress(self, estimated_tokens: int) -> None:
        """Display generating progress with token estimate.
        
        Args:
            estimated_tokens: Estimated number of tokens being generated
        """
        if estimated_tokens > 0:
            self.renderer.update_thinking(True, f"Generating... ({estimated_tokens} tokens)")
        else:
            self.renderer.update_thinking(True, "Generating...")
        logger.debug(f"Displaying generating progress: {estimated_tokens} tokens")
    
    def clear_thinking_display(self) -> None:
        """Clear thinking/generating display."""
        self.renderer.update_thinking(False)
        logger.debug("Cleared thinking display")

    def show_loading(self, message: str = "Loading...") -> None:
        """Show loading indicator with custom message.

        Args:
            message: Loading message to display (default: "Loading...")
        """
        self.renderer.update_thinking(True, message)
        logger.debug(f"Showing loading: {message}")

    def hide_loading(self) -> None:
        """Hide loading indicator.""" 
        self.renderer.update_thinking(False)
        logger.debug("Hiding loading indicator")

    def start_streaming_response(self) -> None:
        """Start a streaming response session.

        This method initializes streaming mode, disabling atomic batching
        for the duration of the response to allow real-time display.
        """
        self._streaming_active = True
        logger.debug("Started streaming response session")

    def end_streaming_response(self) -> None:
        """End a streaming response session.

        This method disables streaming mode and returns to normal
        atomic batching behavior.
        """
        self._streaming_active = False
        logger.debug("Ended streaming response session")

    def is_streaming_active(self) -> bool:
        """Check if streaming mode is currently active.

        Returns:
            True if streaming is active, False otherwise
        """
        return self._streaming_active

    def display_complete_response(self,
                                 thinking_duration: float,
                                 response: str,
                                 tool_results: List[Any] = None,
                                 original_tools: List[Dict] = None,
                                 show_thinking_threshold: float = 0.1,
                                 skip_response_content: bool = False) -> None:
        """Display complete response with thinking, content, and tools atomically.

        This unified method ensures that thinking duration, assistant response,
        and tool execution results all display together in a single atomic
        operation, preventing commands from appearing after the response.

        Args:
            thinking_duration: Time spent thinking in seconds
            response: Assistant response content
            tool_results: List of tool execution result objects (optional)
            original_tools: List of original tool data for command extraction (optional)
            show_thinking_threshold: Minimum duration to show thinking message
            skip_response_content: Skip displaying response content (for streaming mode)
        """
        message_sequence = []
        pipe_mode = getattr(self.renderer, 'pipe_mode', False)

        # Add thinking duration if meaningful (suppress in pipe mode)
        if thinking_duration > show_thinking_threshold and not pipe_mode:
            thought_message = f"Thought for {thinking_duration:.1f} seconds"
            message_sequence.append(("system", thought_message, {}))

        # Add assistant response if present and not skipped (for streaming mode)
        if response.strip() and not skip_response_content:
            message_sequence.append(("assistant", response, {}))

        # Add tool results if present (suppress in pipe mode)
        if tool_results and not pipe_mode:
            for i, result in enumerate(tool_results):
                # Get original tool data for display
                tool_data = original_tools[i] if original_tools and i < len(original_tools) else {}

                # Format tool execution display with consistent styling
                tool_display = self._format_tool_header(result, tool_data)
                result_display = self._format_tool_result(result)

                # Build combined tool display message
                combined_output = [tool_display, result_display]

                # Add actual output if appropriate
                if self._should_show_output(result):
                    output_lines = self._format_tool_output(result)
                    combined_output.extend(output_lines)

                # Add tool message to sequence
                message_sequence.append((
                    "error" if not result.success else "system",
                    "\n".join(combined_output),
                    {}
                ))

                # Add spacing between tools if multiple
                if len(tool_results) > 1 and i < len(tool_results) - 1:
                    message_sequence.append(("system", "", {}))

        # Display everything atomically to prevent race conditions
        if message_sequence:
            self.message_coordinator.display_message_sequence(message_sequence)
            logger.debug(f"Displayed complete response with {len(message_sequence)} messages atomically")

    def get_display_stats(self) -> Dict[str, int]:
        """Get display operation statistics.

        Returns:
            Dictionary with display operation counts
        """
        # This could be enhanced with actual counters if needed
        return {
            "messages_displayed": 0,  # Placeholder - could track actual counts
            "tool_results_displayed": 0,
            "thinking_displays": 0,
            "streaming_sessions": 1 if self._streaming_active else 0
        }