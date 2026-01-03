"""Label widget for read-only value display."""

from typing import Any, Dict, List, Optional
from .base_widget import BaseWidget
from ...io.visual_effects import ColorPalette


class LabelWidget(BaseWidget):
    """Read-only label widget for displaying status values.

    Unlike other widgets, this doesn't allow user interaction -
    it simply displays a label and value pair.
    """

    def __init__(self, label: str, value: str = "", help_text: str = "",
                 config_path: str = "", current_value: Any = None, **kwargs):
        """Initialize label widget.

        Args:
            label: Display label text.
            value: Value to display (can also be set via current_value).
            help_text: Optional help text.
            config_path: Config path (usually empty for labels).
            current_value: Alternative way to set value.
            **kwargs: Additional configuration.
        """
        config = {
            "label": label,
            "value": value or str(current_value or ""),
            "help": help_text,
            **kwargs
        }
        super().__init__(config, config_path, None)
        self._value = value or str(current_value or "")

    def render(self) -> List[str]:
        """Render the label widget.

        Returns:
            List containing single label display line.
        """
        label = self.config.get("label", "")
        value = self._value

        # Format: "  Label: Value" (matching other widgets' indentation)
        if self.focused:
            rendered = f"{ColorPalette.BRIGHT_WHITE}  {label}: {value}{ColorPalette.RESET}"
        else:
            rendered = f"  {label}: {value}"

        return [rendered]

    def handle_input(self, key_press) -> bool:
        """Handle input (no-op for labels).

        Args:
            key_press: Key press event.

        Returns:
            False - labels don't consume input.
        """
        return False

    def get_value(self) -> str:
        """Get the label value.

        Returns:
            Current value string.
        """
        return self._value

    def set_value(self, value: Any) -> None:
        """Set the label value.

        Args:
            value: New value to display.
        """
        self._value = str(value)
