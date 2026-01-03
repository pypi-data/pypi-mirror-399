"""State management for Enhanced Input Plugin."""

import time
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .config import InputConfig


class PluginState:
    """Manages runtime state for Enhanced Input Plugin."""

    def __init__(self, config: 'InputConfig'):
        """Initialize plugin state.

        Args:
            config: Plugin configuration instance.
        """
        self.config = config

        # Randomization state
        self.last_randomize_time = 0
        self.current_random_style = config.style

        # Cursor blinking state
        self.cursor_visible = True
        self.last_blink_time = 0

        # Curated list of sophisticated styles matching user preferences
        self.random_styles = [
            # User's confirmed favorites
            "dots_only", "brackets", "dotted", "dashed", "square",
            # Clean classics
            "rounded", "double", "thick", "underline", "minimal",
            # New sophisticated mixed-weight styles
            "mixed_weight", "typography", "sophisticated", "editorial",
            "clean_corners", "refined", "gradient_line",
            # Clean minimal lines
            "lines_only", "thick_lines", "double_lines"
        ]

    def get_current_style(self) -> str:
        """Get the current style, handling randomization.

        Returns:
            Current active style name.
        """
        current_time = time.time()

        # Handle randomization
        if self.config.randomize_style or self.config.style == "random":
            if (current_time - self.last_randomize_time) >= self.config.randomize_interval:
                self.current_random_style = self._get_random_style()
                self.last_randomize_time = current_time
            return self.current_random_style

        return self.config.style

    def _get_random_style(self) -> str:
        """Get a random style from curated good styles.

        Returns:
            Random style name.
        """
        return random.choice(self.random_styles)

    def update_cursor_blink(self, input_is_active: bool) -> None:
        """Update cursor blinking state.

        Args:
            input_is_active: Whether input is currently active.
        """
        if not input_is_active:
            self.cursor_visible = True
            return

        current_time = time.time()
        if current_time - self.last_blink_time >= self.config.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.last_blink_time = current_time

    def get_cursor_char(self, input_is_active: bool) -> str:
        """Get the current cursor character.

        Args:
            input_is_active: Whether input is currently active.

        Returns:
            Cursor character to display.
        """
        if input_is_active:
            return "█" if self.cursor_visible else " "
        else:
            return "█"

    def is_input_active(self, renderer) -> bool:
        """Determine if input is currently active.

        Args:
            renderer: Terminal renderer instance.

        Returns:
            True if input should be considered active.
        """
        writing_messages = getattr(renderer, 'writing_messages', False)
        thinking_active = getattr(renderer, 'thinking_active', False)
        conversation_active = getattr(renderer, 'conversation_active', True)

        return not writing_messages and not thinking_active and conversation_active

    def get_status_display(self) -> str:
        """Get status display string for current style.

        Returns:
            Status string showing current style.
        """
        current_style = self.get_current_style()
        if self.config.randomize_style or self.config.style == "random":
            return f"{current_style} (random)"
        return current_style

    def reset_randomization(self) -> None:
        """Reset randomization timer."""
        self.last_randomize_time = 0

    def reset_cursor_blink(self) -> None:
        """Reset cursor blink state."""
        self.cursor_visible = True
        self.last_blink_time = 0