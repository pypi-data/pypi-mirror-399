"""Tests for MessageDisplayService component.

Tests the unified message display functionality that eliminates
code duplication from the LLM service.
"""

import unittest
from unittest.mock import MagicMock, call
from dataclasses import dataclass
from typing import Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm.message_display_service import MessageDisplayService


@dataclass
class MockToolResult:
    """Mock tool execution result for testing."""
    tool_type: str
    tool_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    command: Optional[str] = None
    tool_name: Optional[str] = None
    arguments: Optional[dict] = None


class TestMessageDisplayService(unittest.TestCase):
    """Test message display service functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.renderer = MagicMock()
        self.message_coordinator = MagicMock()
        self.renderer.message_coordinator = self.message_coordinator
        
        self.service = MessageDisplayService(self.renderer)
    
    def test_service_initialization(self):
        """Test service initializes correctly."""
        self.assertEqual(self.service.renderer, self.renderer)
        self.assertEqual(self.service.message_coordinator, self.message_coordinator)
    
    def test_display_thinking_and_response_with_thinking(self):
        """Test displaying response with thinking duration."""
        thinking_duration = 1.5
        response = "This is the assistant response."
        
        self.service.display_thinking_and_response(thinking_duration, response)
        
        # Should call message coordinator once
        self.message_coordinator.display_message_sequence.assert_called_once()
        
        # Check message sequence
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 2)  # Thinking + response
        
        # Check thinking message
        self.assertEqual(call_args[0][0], "system")
        self.assertIn("Thought for 1.5 seconds", call_args[0][1])
        
        # Check response message
        self.assertEqual(call_args[1][0], "assistant")
        self.assertEqual(call_args[1][1], response)
    
    def test_display_thinking_and_response_without_thinking(self):
        """Test displaying response without significant thinking duration."""
        thinking_duration = 0.05  # Below threshold
        response = "Quick response."
        
        self.service.display_thinking_and_response(thinking_duration, response)
        
        # Should only show response, not thinking
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 1)  # Only response
        
        self.assertEqual(call_args[0][0], "assistant")
        self.assertEqual(call_args[0][1], response)
    
    def test_display_thinking_and_response_empty_response(self):
        """Test handling empty response."""
        thinking_duration = 1.0
        response = ""  # Empty response
        
        self.service.display_thinking_and_response(thinking_duration, response)
        
        # Should only show thinking, not empty response
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 1)  # Only thinking
        
        self.assertEqual(call_args[0][0], "system")
        self.assertIn("Thought for 1.0 seconds", call_args[0][1])
    
    def test_display_user_message(self):
        """Test displaying user message."""
        message = "User input message"
        
        self.service.display_user_message(message)
        
        # Should call coordinator with user message
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0], ("user", message, {}))
    
    def test_display_system_message(self):
        """Test displaying system message."""
        message = "System notification"
        
        self.service.display_system_message(message)
        
        # Should call coordinator with system message
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0], ("system", message, {}))
    
    def test_display_error_message(self):
        """Test displaying error message."""
        error = "Something went wrong"
        
        self.service.display_error_message(error)
        
        # Should call coordinator with error message
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        self.assertEqual(call_args[0], ("error", "Error: Something went wrong", {}))
    
    def test_display_cancellation_message(self):
        """Test displaying cancellation message."""
        self.service.display_cancellation_message()
        
        # Should call coordinator with cancellation message and spacing
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 2)
        self.assertEqual(call_args[0], ("system", "Request cancelled", {}))
        self.assertEqual(call_args[1], ("system", "", {}))  # Spacing
    
    def test_display_tool_results_terminal_success(self):
        """Test displaying successful terminal tool result."""
        result = MockToolResult(
            tool_type="terminal",
            tool_id="terminal_0", 
            success=True,
            output="file1.txt\nfile2.txt\n",
            command="ls"
        )
        
        # Original tool data for command extraction
        original_tools = [{"command": "ls"}]
        
        self.service.display_tool_results([result], original_tools)
        
        # Should call coordinator for tool display
        self.message_coordinator.display_message_sequence.assert_called_once()
        
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        self.assertEqual(len(call_args), 1)
        
        # Check tool message format
        message_type, message_content, _ = call_args[0]
        self.assertEqual(message_type, "system")
        self.assertIn("⏺", message_content)  # Tool symbol
        self.assertIn("terminal(ls)", message_content)
        self.assertIn("▮", message_content)  # Result symbol
        self.assertIn("Read 3 lines", message_content)  # Output summary
    
    def test_display_tool_results_mcp_success(self):
        """Test displaying successful MCP tool result."""
        result = MockToolResult(
            tool_type="mcp_tool",
            tool_id="mcp_tool_0",
            success=True,
            output="Search found 3 results",
            tool_name="search",
            arguments={"query": "test"}
        )
        
        # Original tool data for name/args extraction
        original_tools = [{"name": "search", "arguments": {"query": "test"}}]
        
        self.service.display_tool_results([result], original_tools)
        
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        message_type, message_content, _ = call_args[0]
        
        self.assertEqual(message_type, "system")
        self.assertIn("search({'query': 'test'})", message_content)
        self.assertIn("Search found 3 results", message_content)
    
    def test_display_tool_results_terminal_failure(self):
        """Test displaying failed terminal tool result."""
        result = MockToolResult(
            tool_type="terminal",
            tool_id="terminal_0",
            success=False,
            error="Command not found",
            command="badcommand"
        )
        
        # Original tool data for command extraction
        original_tools = [{"command": "badcommand"}]
        
        self.service.display_tool_results([result], original_tools)
        
        call_args = self.message_coordinator.display_message_sequence.call_args[0][0]
        message_type, message_content, _ = call_args[0]
        
        # Failed tools should display as error type
        self.assertEqual(message_type, "error")
        self.assertIn("terminal(badcommand)", message_content)
        self.assertIn("Error: Command not found", message_content)
    
    def test_display_tool_results_multiple_tools(self):
        """Test displaying multiple tool results with spacing."""
        results = [
            MockToolResult("terminal", "term1", True, "output1", command="ls"),
            MockToolResult("mcp_tool", "mcp1", True, "output2", tool_name="search")
        ]
        
        # Original tool data for command/name extraction
        original_tools = [
            {"command": "ls"},
            {"name": "search", "arguments": {}}
        ]
        
        self.service.display_tool_results(results, original_tools)
        
        # Should be called twice (once per tool)
        self.assertEqual(self.message_coordinator.display_message_sequence.call_count, 2)
        
        # Check that spacing was added between tools
        calls = self.message_coordinator.display_message_sequence.call_args_list
        
        # First tool
        first_call = calls[0][0][0]
        self.assertIn("terminal(ls)", first_call[0][1])
        
        # Second tool should have spacing in its message sequence
        second_call = calls[1][0][0]  
        # The second call should contain the tool display (may have spacing)
        self.assertTrue(any("search" in str(msg) for msg in second_call))
    
    def test_format_tool_header_terminal(self):
        """Test terminal tool header formatting."""
        result = MockToolResult(
            tool_type="terminal",
            tool_id="terminal_0",
            success=True,
            command="pwd"
        )
        
        tool_data = {"command": "pwd"}
        header = self.service._format_tool_header(result, tool_data)
        
        self.assertIn("⏺", header)
        self.assertIn("terminal(pwd)", header)
        self.assertIn("\033[1;33m", header)  # Yellow color code
    
    def test_format_tool_header_mcp(self):
        """Test MCP tool header formatting."""
        result = MockToolResult(
            tool_type="mcp_tool",
            tool_id="mcp_0",
            success=True,
            tool_name="file_reader",
            arguments={"path": "/test.txt"}
        )
        
        tool_data = {"name": "file_reader", "arguments": {"path": "/test.txt"}}
        header = self.service._format_tool_header(result, tool_data)
        
        self.assertIn("⏺", header)
        self.assertIn("file_reader", header)
        self.assertIn("{'path': '/test.txt'}", header)
    
    def test_format_tool_result_success(self):
        """Test successful tool result formatting."""
        result = MockToolResult(
            tool_type="terminal",
            tool_id="term1",
            success=True,
            output="line1\nline2\nline3"
        )
        
        result_text = self.service._format_tool_result(result)
        
        self.assertIn("▮", result_text)
        self.assertIn("Read 3 lines", result_text)
        self.assertIn("chars)", result_text)
    
    def test_format_tool_result_failure(self):
        """Test failed tool result formatting."""
        result = MockToolResult(
            tool_type="terminal",
            tool_id="term1", 
            success=False,
            error="Permission denied"
        )
        
        result_text = self.service._format_tool_result(result)
        
        self.assertIn("▮ Error: Permission denied", result_text)
    
    def test_should_show_output_conditions(self):
        """Test conditions for showing inline output."""
        # Should show: success, has output, under 500 chars
        result1 = MockToolResult("terminal", "t1", True, "short output")
        self.assertTrue(self.service._should_show_output(result1))
        
        # Should not show: failure
        result2 = MockToolResult("terminal", "t2", False, "output", error="failed")
        self.assertFalse(self.service._should_show_output(result2))
        
        # Should not show: no output
        result3 = MockToolResult("terminal", "t3", True, None)
        self.assertFalse(self.service._should_show_output(result3))
        
        # Should not show: too long
        result4 = MockToolResult("terminal", "t4", True, "x" * 600)  # Over 500 chars
        self.assertFalse(self.service._should_show_output(result4))
    
    def test_format_tool_output_truncation(self):
        """Test tool output formatting with truncation."""
        # Create output with more than 20 lines
        lines = [f"line{i}" for i in range(25)]
        output = "\n".join(lines)
        
        result = MockToolResult("terminal", "t1", True, output)
        formatted = self.service._format_tool_output(result)
        
        # Should have 20 lines plus truncation message
        self.assertEqual(len(formatted), 21)
        
        # Check first few lines are indented
        self.assertTrue(formatted[0].startswith("    line0"))
        self.assertTrue(formatted[19].startswith("    line19"))
        
        # Check truncation message
        self.assertIn("... (5 more lines)", formatted[20])
    
    def test_generating_progress_display(self):
        """Test generating progress display."""
        self.service.display_generating_progress(150)
        
        self.renderer.update_thinking.assert_called_once_with(True, "Generating... (150 tokens)")
    
    def test_clear_thinking_display(self):
        """Test clearing thinking display."""
        self.service.clear_thinking_display()
        
        self.renderer.update_thinking.assert_called_once_with(False)


if __name__ == '__main__':
    unittest.main(verbosity=2)