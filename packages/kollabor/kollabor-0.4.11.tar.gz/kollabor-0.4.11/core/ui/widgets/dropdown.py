"""Dropdown widget for modal UI components."""

from typing import List, Any
from .base_widget import BaseWidget
from ...io.key_parser import KeyPress
from ...io.visual_effects import ColorPalette


class DropdownWidget(BaseWidget):
    """Interactive dropdown widget with ▼ indicator.

    Displays as [value ▼] format and cycles through options on Enter.
    Uses ColorPalette.BRIGHT for focus highlighting.
    """

    def __init__(self, config: dict, config_path: str, config_service=None):
        """Initialize dropdown widget.

        Args:
            config: Widget configuration containing 'options' list.
            config_path: Dot-notation path to config value.
            config_service: ConfigService instance for reading/writing config values.
        """
        super().__init__(config, config_path, config_service)
        self.options = config.get("options", [])
        self._expanded = False

    def render(self) -> List[str]:
        """Render dropdown with current selection.

        Returns:
            List containing dropdown display line(s).
        """
        current_value = self.get_pending_value()
        label = self.get_label()

        # Display current selection with dropdown indicator
        display_value = str(current_value) if current_value is not None else "None"

        if self.focused:
            main_line = f"{ColorPalette.BRIGHT_WHITE}  {label}: [{display_value} ▼]{ColorPalette.RESET}"
        else:
            main_line = f"  {label}: [{display_value} ▼]"

        lines = [main_line]

        # If expanded, show options (Phase 2B feature)
        if self._expanded and self.focused:
            for i, option in enumerate(self.options):
                prefix = "    > " if option == current_value else "      "
                option_line = f"{ColorPalette.DIM}{prefix}{option}{ColorPalette.RESET}"
                lines.append(option_line)

        return lines

    def handle_input(self, key_press: KeyPress) -> bool:
        """Handle dropdown input - cycle options or toggle expansion.

        Args:
            key_press: Key press event to handle.

        Returns:
            True if key was handled.
        """
        if key_press.name == "Enter":
            if not self._expanded:
                # Expand dropdown to show options
                self._expanded = True
                return True
            else:
                # Collapse dropdown
                self._expanded = False
                return True

        elif key_press.name == "ArrowUp" and self._expanded:
            # Navigate to previous option
            self._cycle_option(-1)
            return True

        elif key_press.name == "ArrowDown" and self._expanded:
            # Navigate to next option
            self._cycle_option(1)
            return True

        elif key_press.name == "Escape" and self._expanded:
            # Collapse dropdown without changing value
            self._expanded = False
            return True

        # Quick cycling without expansion (for compact interaction)
        elif key_press.name == "ArrowRight":
            self._cycle_option(1)
            return True

        elif key_press.name == "ArrowLeft":
            self._cycle_option(-1)
            return True

        return False

    def _cycle_option(self, direction: int):
        """Cycle through available options.

        Args:
            direction: 1 for next, -1 for previous.
        """
        if not self.options:
            return

        current_value = self.get_pending_value()

        try:
            current_index = self.options.index(current_value)
        except ValueError:
            # Current value not in options, start from beginning
            current_index = -1 if direction == 1 else 0

        new_index = (current_index + direction) % len(self.options)
        self.set_value(self.options[new_index])

    def set_focus(self, focused: bool):
        """Set focus and collapse dropdown when losing focus.

        Args:
            focused: Whether widget should be focused.
        """
        super().set_focus(focused)
        if not focused:
            self._expanded = False

    def is_valid_value(self, value: Any) -> bool:
        """Validate dropdown value - must be in options list.

        Args:
            value: Value to validate.

        Returns:
            True if value is in the options list.
        """
        return value in self.options or not self.options