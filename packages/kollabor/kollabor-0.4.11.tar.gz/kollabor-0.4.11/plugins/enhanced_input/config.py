"""Configuration management for Enhanced Input Plugin."""

from dataclasses import dataclass
from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.config import ConfigManager


@dataclass
class InputConfig:
    """Type-safe configuration for Enhanced Input Plugin."""

    # Core settings
    enabled: bool = True
    style: str = "rounded"
    width_mode: str = "auto"
    placeholder: str = "Type your message here..."
    show_placeholder: bool = True

    # Dimensions
    min_width: int = 60
    max_width: int = 80
    min_height: int = 3
    max_height: int = 10

    # Dynamic behavior
    dynamic_sizing: bool = True
    wrap_text: bool = True
    randomize_style: bool = False
    randomize_interval: float = 5.0

    # Cursor settings
    cursor_blink_rate: float = 0.5

    # Status display
    show_status: bool = True

    # Color settings
    border_color: str = "dim"
    text_color: str = "dim"
    placeholder_color: str = "dim"
    gradient_mode: bool = True
    gradient_colors: List[str] = None
    border_gradient: bool = True
    text_gradient: bool = True


    def __post_init__(self):
        """Initialize default gradient colors if not provided."""
        if self.gradient_colors is None:
            self.gradient_colors = ["#333333", "#999999", "#222222"]

    @classmethod
    def from_config_manager(cls, config: 'ConfigManager') -> 'InputConfig':
        """Create InputConfig from ConfigManager.

        Args:
            config: Configuration manager instance.

        Returns:
            InputConfig instance with values from config.
        """
        colors_config = config.get("plugins.enhanced_input.colors", {})

        # Ensure colors_config is a dictionary
        if not isinstance(colors_config, dict):
            colors_config = {}  # Fallback to empty dict

        return cls(
            enabled=config.get("plugins.enhanced_input.enabled", True),
            style=config.get("plugins.enhanced_input.style", "rounded"),
            width_mode=config.get("plugins.enhanced_input.width", "auto"),
            placeholder=config.get("plugins.enhanced_input.placeholder", "Type your message here..."),
            show_placeholder=config.get("plugins.enhanced_input.show_placeholder", True),

            min_width=config.get("plugins.enhanced_input.min_width", 60),
            max_width=config.get("plugins.enhanced_input.max_width", 100),
            min_height=config.get("plugins.enhanced_input.min_height", 3),
            max_height=config.get("plugins.enhanced_input.max_height", 10),

            dynamic_sizing=config.get("plugins.enhanced_input.dynamic_sizing", True),
            wrap_text=config.get("plugins.enhanced_input.wrap_text", True),
            randomize_style=config.get("plugins.enhanced_input.randomize_style", False),
            randomize_interval=config.get("plugins.enhanced_input.randomize_interval", 5.0),

            cursor_blink_rate=config.get("plugins.enhanced_input.cursor_blink_rate", 0.5),
            show_status=config.get("plugins.enhanced_input.show_status", True),

            border_color=colors_config.get("border", "dim"),
            text_color=colors_config.get("text", "dim"),
            placeholder_color=colors_config.get("placeholder", "dim"),
            gradient_mode=colors_config.get("gradient_mode", True),
            gradient_colors=colors_config.get("gradient_colors", ["#333333", "#999999", "#222222"]),
            border_gradient=colors_config.get("border_gradient", True),
            text_gradient=colors_config.get("text_gradient", True)
        )

    def get_color_config(self) -> Dict[str, Any]:
        """Get color configuration as dictionary for ColorEngine.

        Returns:
            Dictionary with color configuration.
        """
        return {
            "border": self.border_color,
            "text": self.text_color,
            "placeholder": self.placeholder_color,
            "gradient_mode": self.gradient_mode,
            "gradient_colors": self.gradient_colors,
            "border_gradient": self.border_gradient,
            "text_gradient": self.text_gradient
        }

    def get_default_config_dict(self) -> Dict[str, Any]:
        """Get default configuration as dictionary for plugin registration.

        Returns:
            Default configuration dictionary.
        """
        return {
            "plugins": {
                "enhanced_input": {
                    "enabled": self.enabled,
                    "style": self.style,
                    "width": self.width_mode,
                    "placeholder": self.placeholder,
                    "show_placeholder": self.show_placeholder,
                    "min_width": self.min_width,
                    "max_width": self.max_width,
                    "randomize_style": self.randomize_style,
                    "randomize_interval": self.randomize_interval,
                    "dynamic_sizing": self.dynamic_sizing,
                    "min_height": self.min_height,
                    "max_height": self.max_height,
                    "wrap_text": self.wrap_text,
                    "colors": {
                        "border": self.border_color,
                        "text": self.text_color,
                        "placeholder": self.placeholder_color,
                        "gradient_mode": self.gradient_mode,
                        "gradient_colors": self.gradient_colors,
                        "border_gradient": self.border_gradient,
                        "text_gradient": self.text_gradient
                    },
                    "cursor_blink_rate": self.cursor_blink_rate,
                    "show_status": self.show_status
                }
            }
        }