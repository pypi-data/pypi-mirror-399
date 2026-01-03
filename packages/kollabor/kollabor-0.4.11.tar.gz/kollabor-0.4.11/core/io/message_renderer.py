"""Message rendering system for conversation display.

This module provides comprehensive message rendering for conversation display,
including message formatting, conversation buffer management, and streaming
response support.
"""

import logging
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any, Callable


logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"
    INFO = "info"
    DEBUG = "debug"


class MessageFormat(Enum):
    """Message formatting styles."""

    PLAIN = "plain"
    GRADIENT = "gradient"
    HIGHLIGHTED = "highlighted"
    DIMMED = "dimmed"


@dataclass
class ConversationMessage:
    """Represents a message in the conversation."""

    content: str
    message_type: MessageType
    format_style: MessageFormat = MessageFormat.PLAIN
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            import time

            self.timestamp = time.time()


class MessageFormatter:
    """Handles formatting of individual messages."""

    def __init__(self, visual_effects=None):
        """Initialize message formatter.

        Args:
            visual_effects: VisualEffects instance for applying effects.
        """
        self.visual_effects = visual_effects
        self._format_functions: Dict[MessageFormat, Callable] = {
            MessageFormat.PLAIN: self._format_plain,
            MessageFormat.GRADIENT: self._format_gradient,
            MessageFormat.HIGHLIGHTED: self._format_highlighted,
            MessageFormat.DIMMED: self._format_dimmed,
        }

    def format_message(self, message: ConversationMessage) -> str:
        """Format a conversation message for display.

        Args:
            message: ConversationMessage to format.

        Returns:
            Formatted message string.
        """
        formatter = self._format_functions.get(
            message.format_style, self._format_plain
        )
        return formatter(message)

    def _format_plain(self, message: ConversationMessage) -> str:
        """Format message with no special effects.

        Args:
            message: Message to format.

        Returns:
            Plain formatted message.
        """
        return message.content

    def _format_gradient(self, message: ConversationMessage) -> str:
        """Format message with gradient effects.

        Args:
            message: Message to format.

        Returns:
            Gradient formatted message.
        """
        if not self.visual_effects:
            return message.content

        # Apply appropriate gradient based on message type
        if message.message_type == MessageType.USER:
            return self.visual_effects.apply_message_gradient(
                message.content, "white_to_grey"
            )
        elif message.message_type == MessageType.ASSISTANT:
            return self.visual_effects.apply_message_gradient(
                message.content, "white_to_grey"
            )
        else:
            return self.visual_effects.apply_message_gradient(
                message.content, "dim_white"
            )

    def _format_highlighted(self, message: ConversationMessage) -> str:
        """Format message with highlighting effects.

        Args:
            message: Message to format.

        Returns:
            Highlighted formatted message.
        """
        # Apply highlighting based on message type
        if message.message_type == MessageType.ERROR:
            return f"\033[1;31m{message.content}\033[0m"  # Bright red
        elif message.message_type == MessageType.SYSTEM:
            return f"\033[1;33m{message.content}\033[0m"  # Bright yellow
        elif message.message_type == MessageType.INFO:
            return f"\033[1;36m{message.content}\033[0m"  # Bright cyan
        elif message.message_type == MessageType.DEBUG:
            return f"\033[2;37m{message.content}\033[0m"  # Dim white
        else:
            return f"\033[1m{message.content}\033[0m"  # Bright

    def _format_dimmed(self, message: ConversationMessage) -> str:
        """Format message with dimmed appearance.

        Args:
            message: Message to format.

        Returns:
            Dimmed formatted message.
        """
        return f"\033[2m{message.content}\033[0m"


class ConversationBuffer:
    """Manages conversation message history with formatting."""

    def __init__(self, max_messages: int = 1000):
        """Initialize conversation buffer.

        Args:
            max_messages: Maximum messages to keep in buffer.
        """
        self.max_messages = max_messages
        self.messages = deque(maxlen=max_messages)
        self._message_counter = 0

    def add_message(
        self,
        content: str,
        message_type: MessageType,
        format_style: MessageFormat = MessageFormat.PLAIN,
        **metadata,
    ) -> None:
        """Add a message to the conversation buffer.

        Args:
            content: Message content.
            message_type: Type of message.
            format_style: Formatting style to apply.
            **metadata: Additional metadata for the message.
        """
        message = ConversationMessage(
            content=content,
            message_type=message_type,
            format_style=format_style,
            metadata=metadata,
        )

        self.messages.append(message)
        self._message_counter += 1
        logger.debug(f"Added {message_type.value} message to conversation buffer")

    def get_recent_messages(self, count: int) -> List[ConversationMessage]:
        """Get the most recent messages from buffer.

        Args:
            count: Number of recent messages to retrieve.

        Returns:
            List of recent ConversationMessage objects.
        """
        if count <= 0:
            return []

        return list(self.messages)[-count:]

    def get_messages_by_type(
        self, message_type: MessageType
    ) -> List[ConversationMessage]:
        """Get all messages of a specific type.

        Args:
            message_type: Type of messages to retrieve.

        Returns:
            List of ConversationMessage objects of specified type.
        """
        return [msg for msg in self.messages if msg.message_type == message_type]

    def clear(self) -> None:
        """Clear all messages from buffer."""
        self.messages.clear()
        self._message_counter = 0
        logger.debug("Conversation buffer cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation buffer statistics.

        Returns:
            Dictionary with buffer statistics.
        """
        type_counts = {}
        for msg in self.messages:
            type_counts[msg.message_type.value] = (
                type_counts.get(msg.message_type.value, 0) + 1
            )

        return {
            "total_messages": len(self.messages),
            "max_messages": self.max_messages,
            "messages_added": self._message_counter,
            "type_counts": type_counts,
        }


class ConversationRenderer:
    """Handles rendering of conversation messages to terminal."""

    def __init__(self, terminal_state, visual_effects=None):
        """Initialize conversation renderer.

        Args:
            terminal_state: TerminalState instance for output operations.
            visual_effects: VisualEffects instance for formatting.
        """
        self.terminal_state = terminal_state
        self.visual_effects = visual_effects
        self.formatter = MessageFormatter(visual_effects)
        self.buffer = ConversationBuffer()

        # Rendering configuration
        self.auto_format = True
        self.flush_immediately = True

        # State tracking
        self._last_render_count = 0

    def write_message(
        self,
        content: str,
        message_type: MessageType = MessageType.ASSISTANT,
        format_style: MessageFormat = MessageFormat.GRADIENT,
        immediate_display: bool = True,
        **metadata,
    ) -> None:
        """Write a message to the conversation.

        Args:
            content: Message content to write.
            message_type: Type of message.
            format_style: How to format the message.
            immediate_display: Whether to display immediately.
            **metadata: Additional message metadata.
        """
        # Add to buffer
        self.buffer.add_message(content, message_type, format_style, **metadata)

        # Display immediately if requested
        if immediate_display:
            self._display_message_immediately(content, message_type, format_style)

    def start_streaming_response(self) -> None:
        """Start a streaming response by setting up the display area."""
        # Use the existing message display infrastructure
        # Write to conversation area using proper positioning
        self._display_message_immediately(
            "\n∴ ", MessageType.ASSISTANT, MessageFormat.PLAIN
        )

    def write_streaming_chunk(self, chunk: str) -> None:
        """Write a streaming chunk directly to the conversation area."""
        # Use the display infrastructure to write in the conversation area
        self._display_chunk_immediately(chunk)

    def write_user_message(self, content: str, **metadata) -> None:
        """Write a user message (convenience method).

        Args:
            content: User message content.
            **metadata: Additional metadata.
        """
        self.write_message(
            content, MessageType.USER, MessageFormat.GRADIENT, **metadata
        )

    def write_system_message(self, content: str, **metadata) -> None:
        """Write a system message (convenience method).

        Args:
            content: System message content.
            **metadata: Additional metadata.
        """
        self.write_message(
            content, MessageType.SYSTEM, MessageFormat.HIGHLIGHTED, **metadata
        )

    def write_error_message(self, content: str, **metadata) -> None:
        """Write an error message (convenience method).

        Args:
            content: Error message content.
            **metadata: Additional metadata.
        """
        self.write_message(
            content, MessageType.ERROR, MessageFormat.HIGHLIGHTED, **metadata
        )

    def _display_message_immediately(
        self,
        content: str,
        message_type: MessageType,
        format_style: MessageFormat,
    ) -> None:
        """Display a message immediately to the terminal.

        Args:
            content: Message content.
            message_type: Type of message.
            format_style: Formatting style.
        """
        # Skip display if content is empty (fix for duplicate display issue)
        if not content or not content.strip():
            return

        # Check if we're in pipe mode (no formatting/symbols)
        pipe_mode = getattr(self, 'pipe_mode', False)

        # Store symbol info for later application (after gradient)
        add_symbol = None
        if not pipe_mode:
            if message_type == MessageType.ASSISTANT and content.strip():
                if not content.startswith("∴") and not content.startswith("\033[36m∴"):
                    add_symbol = "llm"
            elif message_type == MessageType.USER:
                add_symbol = "user"

        # Create temporary message for formatting
        temp_message = ConversationMessage(content, message_type, format_style)

        # Format the message (apply gradient first) - skip in pipe mode
        if self.auto_format and format_style != MessageFormat.PLAIN and not pipe_mode:
            formatted_content = self.formatter.format_message(temp_message)
        else:
            formatted_content = content

        # Add symbols AFTER gradient processing - skip in pipe mode
        if add_symbol == "user":
            formatted_content = f"\033[2;33m>\033[0m {formatted_content}"
        elif add_symbol == "llm":
            formatted_content = f"\033[36m∴\033[0m {formatted_content}"

        # Exit raw mode temporarily for writing
        # Handle both enum and string cases for current_mode
        current_mode = getattr(
            self.terminal_state.current_mode,
            "value",
            self.terminal_state.current_mode,
        )
        was_raw = current_mode == "raw"
        if was_raw:
            self.terminal_state.exit_raw_mode()

        try:
            # Write to terminal
            print(formatted_content, flush=self.flush_immediately)
            # Add blank line for visual separation between messages
            print("", flush=self.flush_immediately)
            logger.debug(
                f"Displayed {message_type.value} message: {content[:50]}..."
            )
        finally:
            # Restore raw mode if it was active
            if was_raw:
                self.terminal_state.enter_raw_mode()

    def _display_chunk_immediately(self, chunk: str) -> None:
        """Display a streaming chunk immediately without line breaks.

        Args:
            chunk: Text chunk to display.
        """
        # Exit raw mode temporarily for writing
        current_mode = getattr(
            self.terminal_state.current_mode,
            "value",
            self.terminal_state.current_mode,
        )
        was_raw = current_mode == "raw"
        if was_raw:
            self.terminal_state.exit_raw_mode()

        try:
            # Write chunk without newline and flush immediately
            print(chunk, end="", flush=True)
        finally:
            # Restore raw mode if it was active
            if was_raw:
                self.terminal_state.enter_raw_mode()

    def render_conversation_history(self, count: Optional[int] = None) -> List[str]:
        """Render conversation history as formatted lines.

        Args:
            count: Number of recent messages to render (None for all).

        Returns:
            List of formatted message lines.
        """
        if count is None:
            messages = list(self.buffer.messages)
        else:
            messages = self.buffer.get_recent_messages(count)

        formatted_lines = []
        for message in messages:
            if self.auto_format:
                formatted_content = self.formatter.format_message(message)
            else:
                formatted_content = message.content

            # Split multi-line messages
            lines = formatted_content.split("\n")
            formatted_lines.extend(lines)

        return formatted_lines

    def clear_conversation_area(self) -> None:
        """Clear the conversation display area."""
        # This would typically involve clearing the terminal screen
        # or specific regions, depending on layout management
        if self.terminal_state.is_terminal:
            self.terminal_state.write_raw(
                "\033[2J\033[H"
            )  # Clear screen, move to home
            logger.debug("Cleared conversation area")

    def set_auto_formatting(self, enabled: bool) -> None:
        """Enable or disable automatic message formatting.

        Args:
            enabled: Whether to apply automatic formatting.
        """
        self.auto_format = enabled
        logger.debug(f"Auto formatting {'enabled' if enabled else 'disabled'}")

    def set_visual_effects(self, visual_effects) -> None:
        """Update the visual effects instance.

        Args:
            visual_effects: New VisualEffects instance.
        """
        self.visual_effects = visual_effects
        self.formatter = MessageFormatter(visual_effects)
        logger.debug("Visual effects updated")

    def get_render_stats(self) -> Dict[str, Any]:
        """Get conversation rendering statistics.

        Returns:
            Dictionary with rendering statistics.
        """
        buffer_stats = self.buffer.get_stats()

        return {
            "buffer": buffer_stats,
            "auto_format": self.auto_format,
            "flush_immediately": self.flush_immediately,
            "last_render_count": self._last_render_count,
            "terminal_mode": (
                getattr(
                    self.terminal_state.current_mode,
                    "value",
                    self.terminal_state.current_mode,
                )
                if self.terminal_state
                else "unknown"
            ),
        }


class MessageRenderer:
    """Main message rendering coordinator."""

    def __init__(self, terminal_state, visual_effects=None):
        """Initialize message renderer.

        Args:
            terminal_state: TerminalState instance.
            visual_effects: VisualEffects instance.
        """
        self.conversation_renderer = ConversationRenderer(
            terminal_state, visual_effects
        )
        self.terminal_state = terminal_state
        self.visual_effects = visual_effects

    def write_message(self, content: str, apply_gradient: bool = True) -> None:
        """Write a message with optional gradient (backward compatibility).

        Args:
            content: Message content.
            apply_gradient: Whether to apply gradient effect.
        """
        format_style = (
            MessageFormat.GRADIENT if apply_gradient else MessageFormat.PLAIN
        )
        self.conversation_renderer.write_message(content, format_style=format_style)

    def write_streaming_chunk(self, chunk: str) -> None:
        """Write a streaming chunk without buffering for real-time display.

        Args:
            chunk: Text chunk to write immediately.
        """
        # Initialize streaming state if needed
        if not hasattr(self, "_streaming_buffer"):
            self._streaming_buffer = ""
            # Use the conversation renderer to start streaming properly
            self.conversation_renderer.start_streaming_response()

        # Add chunk to buffer and display it through conversation renderer
        self._streaming_buffer += chunk
        self.conversation_renderer.write_streaming_chunk(chunk)

    def finish_streaming_message(self) -> None:
        """Finish streaming and properly format the complete message."""
        if hasattr(self, "_streaming_buffer"):
            # End the streaming line
            self.terminal_state.write_raw("\n\n")
            # Reset streaming state
            del self._streaming_buffer

    def write_user_message(self, content: str) -> None:
        """Write a user message (backward compatibility).

        Args:
            content: User message content.
        """
        self.conversation_renderer.write_user_message(content)

    def write_system_message(self, content: str, **metadata) -> None:
        """Write a system message (delegated to conversation renderer).

        Args:
            content: System message content.
            **metadata: Additional metadata.
        """
        self.conversation_renderer.write_system_message(content, **metadata)

    def get_conversation_buffer(self) -> ConversationBuffer:
        """Get the conversation buffer for direct access.

        Returns:
            ConversationBuffer instance.
        """
        return self.conversation_renderer.buffer

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive message rendering statistics.

        Returns:
            Dictionary with all rendering statistics.
        """
        return {
            "conversation": self.conversation_renderer.get_render_stats(),
            "terminal_state": (
                self.terminal_state.get_status() if self.terminal_state else {}
            ),
            "visual_effects": (
                self.visual_effects.get_effect_stats() if self.visual_effects else {}
            ),
        }
