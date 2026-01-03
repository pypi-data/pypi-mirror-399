"""Checkbox widget for modal UI components."""

import logging
from typing import List
from .base_widget import BaseWidget
from ...io.key_parser import KeyPress
from ...io.visual_effects import ColorPalette

logger = logging.getLogger(__name__)


class CheckboxWidget(BaseWidget):
    """Interactive checkbox widget with ✓ symbol.

    Displays as [ ] or [✓] and toggles state on Enter or Space key press.
    Uses ColorPalette.BRIGHT for focus highlighting.
    """

    def __init__(self, config: dict, config_path: str, config_service=None):
        """Initialize checkbox widget.

        Args:
            config: Widget configuration dictionary.
            config_path: Dot-notation path to config value.
            config_service: ConfigService instance for reading/writing config values.
        """
        super().__init__(config, config_path, config_service)

    def render(self) -> List[str]:
        """Render checkbox with current state.

        Returns:
            List containing single checkbox display line.
        """
        # Get current value (prefer pending value if available)
        current_value = self.get_pending_value()
        check = "✓" if current_value else " "
        label = self.get_label()

        logger.info(f"Checkbox render: value={current_value}, check='{check}', focused={self.focused}")

        # Apply focus highlighting using existing ColorPalette
        if self.focused:
            rendered = f"{ColorPalette.BRIGHT_WHITE}  [{check}] {label}{ColorPalette.RESET}"
        else:
            rendered = f"  [{check}] {label}"

        logger.info(f"Checkbox rendered as: '{rendered}'")
        return [rendered]

    def handle_input(self, key_press: KeyPress) -> bool:
        """Handle checkbox input - toggle on Enter or Space.

        Args:
            key_press: Key press event to handle.

        Returns:
            True if key was handled (Enter or Space).
        """
        # Check for Enter key (name="Enter" or char="\r" or char="\n")
        is_enter = key_press.name == "Enter" or key_press.char in ("\r", "\n")
        # Check for Space key (name="Space" or char=" ")
        is_space = key_press.name == "Space" or key_press.char == " "

        logger.info(f"🔘 Checkbox handle_input: name={key_press.name}, char={repr(key_press.char)}, is_enter={is_enter}, is_space={is_space}")

        if is_enter or is_space:
            current_value = self.get_pending_value()
            new_value = not current_value
            logger.info(f"🔘 Checkbox TOGGLING: {current_value} → {new_value}")
            self.set_value(new_value)
            logger.info(f"🔘 Checkbox value after set: {self.get_pending_value()}, _pending={self._pending_value}")
            return True
        return False

    def is_valid_value(self, value) -> bool:
        """Validate checkbox value - must be boolean.

        Args:
            value: Value to validate.

        Returns:
            True if value is boolean.
        """
        return isinstance(value, bool)