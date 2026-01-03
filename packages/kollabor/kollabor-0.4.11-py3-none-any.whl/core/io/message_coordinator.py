"""Message coordination system for preventing race conditions.

This coordinator solves the fundamental race condition where multiple
message writing systems interfere with each other, causing messages
to be overwritten or cleared unexpectedly.

IMPORTANT: All terminal state changes (input rendering, clearing, buffer
transitions) should go through this coordinator to prevent state bugs.

This module provides atomic message display coordination and unified
state management to prevent interference between different message
writing systems.
"""

import logging
from typing import List, Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MessageDisplayCoordinator:
    """Coordinates message display AND render state to prevent interference.

    Key Features:
    - Atomic message sequences (all messages display together)
    - Unified state management (prevents clearing conflicts)
    - Proper ordering (system messages before responses)
    - Protection from interference (no race conditions)
    - Buffer transition management (modal open/close state preservation)
    """

    def __init__(self, terminal_renderer):
        """Initialize message display coordinator.

        Args:
            terminal_renderer: TerminalRenderer instance for display
        """
        self.terminal_renderer = terminal_renderer
        self.message_queue: List[Tuple[str, str, Dict[str, Any]]] = []
        self.is_displaying = False

        # Saved state for buffer transitions (modal, fullscreen, etc.)
        self._saved_main_buffer_state: Optional[Dict[str, Any]] = None
        self._in_alternate_buffer = False

        logger.debug("MessageDisplayCoordinator initialized")

    def _capture_render_state(self) -> Dict[str, Any]:
        """Capture current render state for later restoration.

        Returns:
            Dictionary containing render state snapshot.
        """
        return {
            "writing_messages": self.terminal_renderer.writing_messages,
            "input_line_written": self.terminal_renderer.input_line_written,
            "last_line_count": self.terminal_renderer.last_line_count,
            "conversation_active": self.terminal_renderer.conversation_active,
            "thinking_active": self.terminal_renderer.thinking_active,
        }

    def queue_message(self, message_type: str, content: str, **kwargs) -> None:
        """Queue a message for coordinated display.

        Args:
            message_type: Type of message ("system", "assistant", "user", "error")
            content: Message content to display
            **kwargs: Additional arguments for message formatting
        """
        self.message_queue.append((message_type, content, kwargs))
        logger.debug(f"Queued {message_type} message: {content[:50]}...")

    def display_single_message(
        self, message_type: str, content: str, **kwargs
    ) -> None:
        """Display a single message immediately through coordination.

        This method provides a coordinated way for plugins and other systems
        to display individual messages without bypassing the coordination system.

        Args:
            message_type: Type of message ("system", "assistant", "user", "error")
            content: Message content to display
            **kwargs: Additional arguments for message formatting
        """
        self.display_message_sequence([(message_type, content, kwargs)])

    def display_queued_messages(self) -> None:
        """Display all queued messages in proper atomic sequence.

        This method ensures all queued messages display together
        without interference from other systems.
        """
        if self.is_displaying or not self.message_queue:
            return

        logger.debug(f"Displaying {len(self.message_queue)} queued messages")

        # Enter atomic display mode
        self.is_displaying = True
        self.terminal_renderer.writing_messages = True

        # Clear active area once before all messages
        self.terminal_renderer.clear_active_area()

        try:
            # Display all messages in sequence
            for message_type, content, kwargs in self.message_queue:
                self._display_single_message(message_type, content, kwargs)

            # Add blank line for visual separation
            self.terminal_renderer.message_renderer.write_message(
                "", apply_gradient=False
            )

        finally:
            # Exit atomic display mode
            self.terminal_renderer.writing_messages = False
            self.message_queue.clear()
            self.is_displaying = False
            # Reset render state for clean input box rendering
            # This prevents duplicate input boxes when render loop resumes
            self.terminal_renderer.input_line_written = False
            self.terminal_renderer.last_line_count = 0
            self.terminal_renderer.invalidate_render_cache()
            logger.debug("Completed atomic message display")

    def display_message_sequence(
        self, messages: List[Tuple[str, str, Dict[str, Any]]]
    ) -> None:
        """Display a sequence of messages atomically.

        This is the primary method for coordinated message display.
        All messages in the sequence will display together without
        interference from other systems.

        Args:
            messages: List of (message_type, content, kwargs) tuples

        Example:
            coordinator.display_message_sequence([
                ("system", "Thought for 2.1 seconds", {}),
                ("assistant", "Hello! How can I help you?", {})
            ])
        """
        # Queue all messages
        for message_type, content, kwargs in messages:
            self.queue_message(message_type, content, **kwargs)

        # Display them atomically
        self.display_queued_messages()

    def _display_single_message(
        self, message_type: str, content: str, kwargs: Dict[str, Any]
    ) -> None:
        """Display a single message using the appropriate method.

        Args:
            message_type: Type of message to display
            content: Message content
            kwargs: Additional formatting arguments
        """
        try:
            if message_type == "system":
                # System messages use DIMMED format as per CLAUDE.md spec
                from .message_renderer import MessageType, MessageFormat

                self.terminal_renderer.message_renderer.conversation_renderer.write_message(
                    content,
                    message_type=MessageType.SYSTEM,  # No ∴ prefix for system messages
                    format_style=MessageFormat.DIMMED,  # Professional dimmed formatting
                    **kwargs,
                )
            elif message_type == "assistant":
                # Use MessageFormat.GRADIENT for assistant messages
                from .message_renderer import MessageType, MessageFormat

                format_style = (
                    MessageFormat.GRADIENT
                    if kwargs.get("apply_gradient", True)
                    else MessageFormat.PLAIN
                )
                self.terminal_renderer.message_renderer.conversation_renderer.write_message(
                    content,
                    message_type=MessageType.ASSISTANT,
                    format_style=format_style,
                    **kwargs,
                )
            elif message_type == "user":
                self.terminal_renderer.message_renderer.write_user_message(
                    content, **kwargs
                )
            elif message_type == "error":
                # For error messages, use MessageType.ERROR for proper red color, no ∴ prefix
                from .message_renderer import MessageType, MessageFormat

                self.terminal_renderer.message_renderer.conversation_renderer.write_message(
                    content,
                    message_type=MessageType.ERROR,
                    format_style=MessageFormat.HIGHLIGHTED,  # Uses red color from _format_highlighted
                    **kwargs,
                )
            else:
                logger.warning(f"Unknown message type: {message_type}")
                # Fallback to regular message
                self.terminal_renderer.message_renderer.write_message(
                    content, apply_gradient=False
                )

        except Exception as e:
            logger.error(f"Error displaying {message_type} message: {e}")
            # Fallback display to prevent total failure
            try:
                print(f"[{message_type.upper()}] {content}")
            except Exception:
                logger.error(
                    "Critical: Failed to display message even with fallback"
                )

    def clear_queue(self) -> None:
        """Clear all queued messages without displaying them."""
        self.message_queue.clear()
        logger.debug("Cleared message queue")

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status for debugging.

        Returns:
            Dictionary with queue information
        """
        return {
            "queue_length": len(self.message_queue),
            "is_displaying": self.is_displaying,
            "queued_types": [msg[0] for msg in self.message_queue],
        }

    # === Buffer Transition Management ===
    # These methods handle state preservation during modal/fullscreen transitions

    def enter_alternate_buffer(self) -> None:
        """Mark entering alternate buffer and pause render loop.

        Call this BEFORE opening a modal or entering fullscreen mode.
        Captures current render state for potential restoration.
        """
        if self._in_alternate_buffer:
            logger.warning("Already in alternate buffer")
            return

        # Capture state BEFORE modifying anything
        self._saved_main_buffer_state = self._capture_render_state()
        logger.debug(f"Captured render state: {self._saved_main_buffer_state}")

        self._in_alternate_buffer = True
        # Prevent render loop interference during modal
        self.terminal_renderer.writing_messages = True
        logger.debug("Entered alternate buffer mode")

    def exit_alternate_buffer(self, restore_state: bool = False) -> None:
        """Exit alternate buffer mode and reset render state.

        Call this AFTER closing a modal or exiting fullscreen mode.

        Args:
            restore_state: If True, restore captured state. If False (default),
                          reset to clean state for fresh input rendering.
        """
        if not self._in_alternate_buffer:
            logger.warning("Not in alternate buffer")
            return

        self._in_alternate_buffer = False

        if restore_state and self._saved_main_buffer_state:
            # Restore previously captured state
            self.terminal_renderer.writing_messages = self._saved_main_buffer_state[
                "writing_messages"
            ]
            self.terminal_renderer.input_line_written = self._saved_main_buffer_state[
                "input_line_written"
            ]
            self.terminal_renderer.last_line_count = self._saved_main_buffer_state[
                "last_line_count"
            ]
            logger.debug(f"Restored render state: {self._saved_main_buffer_state}")
        else:
            # Reset to clean state (default - prevents duplicate input boxes)
            self.terminal_renderer.writing_messages = False
            self.terminal_renderer.input_line_written = False
            self.terminal_renderer.last_line_count = 0
            logger.debug("Reset to clean render state")

        # Always invalidate cache after buffer transition
        self.terminal_renderer.invalidate_render_cache()
        self._saved_main_buffer_state = None

    def get_saved_state(self) -> Optional[Dict[str, Any]]:
        """Get the saved render state (for debugging).

        Returns:
            Saved state dict if in alternate buffer, None otherwise.
        """
        return self._saved_main_buffer_state
