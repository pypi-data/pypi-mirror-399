"""Cursor management for enhanced input plugin."""

import time


class CursorManager:
    """Manages cursor positioning, blinking, and rendering."""

    def __init__(self, config):
        """Initialize cursor manager.

        Args:
            config: InputConfig object with plugin configuration.
        """
        self.config = config
        self.cursor_visible = True
        self.last_blink_time = 0
        self.blink_interval = config.cursor_blink_rate

    def insert_cursor(self, text: str, cursor_position: int, cursor_char: str = None) -> str:
        """Insert cursor character at the specified position.

        Args:
            text: Text to insert cursor into.
            cursor_position: Position to insert cursor (0-based).
            cursor_char: Optional cursor character to use. If None, uses get_cursor_char().

        Returns:
            Text with cursor inserted.
        """
        if cursor_char is None:
            cursor_char = self.get_cursor_char()
        cursor_pos = max(0, min(cursor_position, len(text)))
        return text[:cursor_pos] + cursor_char + text[cursor_pos:]

    def get_cursor_char(self) -> str:
        """Get the current cursor character.

        Returns:
            Cursor character ("▌" or " " based on blink state).
        """
        return "▌" if self.cursor_visible else " "

    def update_blink_state(self, input_is_active: bool) -> None:
        """Update cursor blinking state.

        Args:
            input_is_active: Whether input is currently active.
        """
        if not input_is_active:
            self.cursor_visible = True
            return

        current_time = time.time()
        if current_time - self.last_blink_time >= self.blink_interval:
            self.cursor_visible = not self.cursor_visible
            self.last_blink_time = current_time

    def is_input_active(self, renderer) -> bool:
        """Determine if input is currently active.

        Args:
            renderer: Terminal renderer object.

        Returns:
            True if input is active (not writing messages or thinking).
        """
        writing_messages = getattr(renderer, 'writing_messages', False)
        thinking_active = getattr(renderer, 'thinking_active', False)
        conversation_active = getattr(renderer, 'conversation_active', True)

        return not writing_messages and not thinking_active and conversation_active