"""Base widget class for modal UI components."""

from abc import ABC, abstractmethod
from typing import Any, List
from ...io.key_parser import KeyPress


class BaseWidget(ABC):
    """Base class for all modal widgets.

    Provides common functionality for rendering, input handling, and value management
    across all widget types including checkboxes, dropdowns, text inputs, and sliders.
    """

    def __init__(self, config: dict, config_path: str, config_service=None):
        """Initialize base widget.

        Args:
            config: Widget configuration dictionary containing display options.
            config_path: Dot-notation path to config value (e.g., "core.llm.temperature").
            config_service: ConfigService instance for reading/writing config values.
        """
        self.config = config
        self.config_path = config_path
        self.config_service = config_service
        self.focused = False
        self._pending_value = None

    @abstractmethod
    def render(self) -> List[str]:
        """Render widget using existing ColorPalette.

        Returns:
            List of strings representing widget display lines.
        """
        pass

    @abstractmethod
    def handle_input(self, key_press: KeyPress) -> bool:
        """Handle input, return True if consumed.

        Args:
            key_press: Key press event to handle.

        Returns:
            True if the key press was handled by this widget.
        """
        pass

    def get_value(self) -> Any:
        """Get current value from config system.

        Returns:
            Current configuration value for this widget's config path.
        """
        # First check if widget config has an explicit 'value' or 'current_value' field
        # This is used for form modals with pre-populated data
        if "value" in self.config:
            return self.config["value"]
        if "current_value" in self.config:
            return self.config["current_value"]

        # Try to get real value from config service
        if self.config_service:
            try:
                value = self.config_service.get(self.config_path)
                # If we got a value, return it
                if value is not None:
                    return value
            except Exception:
                # Fall through to defaults if config access fails
                pass

        # Fallback to defaults for testing or when config service is unavailable
        # Use reasonable defaults based on widget type
        widget_type = self.__class__.__name__.lower()

        if "checkbox" in widget_type:
            return True
        elif "slider" in widget_type:
            # For sliders, check config for min/max and return middle value
            min_val = self.config.get("min_value", 0)
            max_val = self.config.get("max_value", 1)
            return (min_val + max_val) / 2
        elif "dropdown" in widget_type:
            options = self.config.get("options", [])
            return options[0] if options else "Unknown"
        elif "text_input" in widget_type:
            placeholder = self.config.get("placeholder", "")
            return placeholder
        else:
            return ""

    def set_value(self, value: Any):
        """Set value (will be saved in Phase 3).

        Args:
            value: New value to set for this widget.
        """
        self._pending_value = value

    def get_pending_value(self) -> Any:
        """Get pending value if set, otherwise current value.

        Returns:
            Pending value if available, otherwise current config value.
        """
        return self._pending_value if self._pending_value is not None else self.get_value()

    def has_pending_changes(self) -> bool:
        """Check if widget has unsaved changes.

        Returns:
            True if there are pending changes to save.
        """
        return self._pending_value is not None

    def set_focus(self, focused: bool):
        """Set widget focus state.

        Args:
            focused: Whether widget should be focused.
        """
        self.focused = focused

    def get_label(self) -> str:
        """Get widget label from config.

        Returns:
            Label text for display.
        """
        return self.config.get("label", "Widget")

    def is_valid_value(self, value: Any) -> bool:
        """Validate if a value is acceptable for this widget.

        Args:
            value: Value to validate.

        Returns:
            True if value is valid for this widget type.
        """
        return True  # Base implementation accepts any value