"""Enhanced Input Plugin for Kollabor CLI - Refactored Version.

Provides enhanced input rendering with bordered boxes using Unicode box-drawing characters.
Now built with modular components following DRY principles.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, TYPE_CHECKING

from core.io.visual_effects import AgnosterSegment

logger = logging.getLogger(__name__)

# Add parent directory to path so we can import from chat_app
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.events import Event, EventType, Hook, HookPriority

# Import our modular components
from plugins.enhanced_input.config import InputConfig
from plugins.enhanced_input.state import PluginState
from plugins.enhanced_input.box_styles import BoxStyleRegistry
from plugins.enhanced_input.color_engine import ColorEngine
from plugins.enhanced_input.geometry import GeometryCalculator
from plugins.enhanced_input.text_processor import TextProcessor
from plugins.enhanced_input.cursor_manager import CursorManager
from plugins.enhanced_input.box_renderer import BoxRenderer

# Type hints (only needed for type checking)
if TYPE_CHECKING:
    from core.config import ConfigManager
    from core.storage import StateManager
    from core.events import EventBus
    from core.io.terminal_renderer import TerminalRenderer


class EnhancedInputPlugin:
    """Plugin that renders enhanced bordered input boxes using modular components."""

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get the default configuration for the enhanced input plugin.

        Returns:
            Default configuration dictionary for the enhanced input plugin.
        """
        # Use the default config from InputConfig
        default_config = InputConfig()
        return default_config.get_default_config_dict()

    @staticmethod
    def get_startup_info(config: 'ConfigManager') -> List[str]:
        """Get startup information to display for this plugin.

        Args:
            config: Configuration manager instance.

        Returns:
            List of strings to display during startup.
        """
        enabled = config.get('plugins.enhanced_input.enabled', True)
        style = config.get('plugins.enhanced_input.style', 'rounded')
        return [
            f"Enabled: {enabled}",
            f"Style: {style}",
            f"Unicode box drawing support"
        ]

    @staticmethod
    def get_config_widgets() -> Dict[str, Any]:
        """Get configuration widgets for this plugin.

        Returns:
            Widget section definition for the config modal.
        """
        return {
            "title": "Enhanced Input Plugin",
            "widgets": [
                {
                    "type": "dropdown",
                    "label": "Box Style",
                    "config_path": "plugins.enhanced_input.style",
                    "options": [
                        "rounded", "square", "double", "thick", "thin",
                        "dotted", "dashed", "minimal", "brackets", "underline",
                        "lines_only", "dots_only", "mixed_weight", "sophisticated"
                    ],
                    "help": "Visual style of the input box border"
                },
                {
                    "type": "text_input",
                    "label": "Width",
                    "config_path": "plugins.enhanced_input.width",
                    "placeholder": "auto",
                    "help": "Box width (auto, pixels, or percentage)"
                },
                {
                    "type": "text_input",
                    "label": "Placeholder Text",
                    "config_path": "plugins.enhanced_input.placeholder",
                    "placeholder": "Type your message here...",
                    "help": "Text shown when input is empty"
                },
                {
                    "type": "checkbox",
                    "label": "Show Placeholder",
                    "config_path": "plugins.enhanced_input.show_placeholder",
                    "help": "Display placeholder text when input is empty"
                },
                {
                    "type": "slider",
                    "label": "Min Width",
                    "config_path": "plugins.enhanced_input.min_width",
                    "min_value": 20,
                    "max_value": 200,
                    "step": 10,
                    "help": "Minimum box width in characters"
                },
                {
                    "type": "slider",
                    "label": "Max Width",
                    "config_path": "plugins.enhanced_input.max_width",
                    "min_value": 40,
                    "max_value": 300,
                    "step": 10,
                    "help": "Maximum box width in characters"
                },
                {
                    "type": "checkbox",
                    "label": "Randomize Style",
                    "config_path": "plugins.enhanced_input.randomize_style",
                    "help": "Randomly change box style periodically"
                },
                {
                    "type": "slider",
                    "label": "Randomize Interval",
                    "config_path": "plugins.enhanced_input.randomize_interval",
                    "min_value": 1.0,
                    "max_value": 60.0,
                    "step": 1.0,
                    "help": "Seconds between style randomizations"
                },
                {
                    "type": "checkbox",
                    "label": "Dynamic Sizing",
                    "config_path": "plugins.enhanced_input.dynamic_sizing",
                    "help": "Automatically resize box based on content"
                },
                {
                    "type": "slider",
                    "label": "Min Height",
                    "config_path": "plugins.enhanced_input.min_height",
                    "min_value": 1,
                    "max_value": 20,
                    "step": 1,
                    "help": "Minimum box height in lines"
                },
                {
                    "type": "slider",
                    "label": "Max Height",
                    "config_path": "plugins.enhanced_input.max_height",
                    "min_value": 3,
                    "max_value": 50,
                    "step": 1,
                    "help": "Maximum box height in lines"
                },
                {
                    "type": "checkbox",
                    "label": "Wrap Text",
                    "config_path": "plugins.enhanced_input.wrap_text",
                    "help": "Enable text wrapping in input box"
                },
                {
                    "type": "slider",
                    "label": "Cursor Blink Rate",
                    "config_path": "plugins.enhanced_input.cursor_blink_rate",
                    "min_value": 0.1,
                    "max_value": 2.0,
                    "step": 0.1,
                    "help": "Cursor blink speed in seconds"
                },
                {
                    "type": "checkbox",
                    "label": "Show Status",
                    "config_path": "plugins.enhanced_input.show_status",
                    "help": "Display status information below input box"
                },
                # Color settings
                {
                    "type": "dropdown",
                    "label": "Border Color",
                    "config_path": "plugins.enhanced_input.colors.border",
                    "options": ["dim", "white", "cyan", "green", "yellow", "magenta", "blue", "red"],
                    "help": "Color of the input box border"
                },
                {
                    "type": "dropdown",
                    "label": "Text Color",
                    "config_path": "plugins.enhanced_input.colors.text",
                    "options": ["dim", "white", "cyan", "green", "yellow", "magenta", "blue", "red"],
                    "help": "Color of the input text"
                },
                {
                    "type": "dropdown",
                    "label": "Placeholder Color",
                    "config_path": "plugins.enhanced_input.colors.placeholder",
                    "options": ["dim", "white", "cyan", "green", "yellow", "magenta", "blue"],
                    "help": "Color of the placeholder text"
                },
                {
                    "type": "checkbox",
                    "label": "Gradient Mode",
                    "config_path": "plugins.enhanced_input.colors.gradient_mode",
                    "help": "Enable gradient coloring effects"
                },
                {
                    "type": "checkbox",
                    "label": "Border Gradient",
                    "config_path": "plugins.enhanced_input.colors.border_gradient",
                    "help": "Apply gradient to border"
                },
                {
                    "type": "checkbox",
                    "label": "Text Gradient",
                    "config_path": "plugins.enhanced_input.colors.text_gradient",
                    "help": "Apply gradient to input text"
                }
            ]
        }

    def __init__(self, name: str, state_manager: 'StateManager', event_bus: 'EventBus',
                 renderer: 'TerminalRenderer', config: 'ConfigManager') -> None:
        """Initialize the enhanced input plugin.

        Args:
            name: Plugin name.
            state_manager: State management system.
            event_bus: Event bus for hook registration.
            renderer: Terminal renderer.
            config: Configuration manager.
        """
        self.name = name
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer

        # Initialize configuration
        self.config = InputConfig.from_config_manager(config)

        # Initialize state management
        self.state = PluginState(self.config)

        # Initialize modular components
        self.box_styles = BoxStyleRegistry()
        self.color_engine = ColorEngine(self.config)
        self.geometry = GeometryCalculator(self.config)
        self.text_processor = TextProcessor(self.config)
        self.cursor_manager = CursorManager(self.config)
        self.box_renderer = BoxRenderer(self.box_styles, self.color_engine, self.geometry, self.text_processor)

        # Register hooks for input rendering
        self.hooks = [
            Hook(
                name="render_fancy_input",
                plugin_name=self.name,
                event_type=EventType.INPUT_RENDER,
                priority=HookPriority.DISPLAY.value,
                callback=self._render_fancy_input
            )
        ]

    def get_status_lines(self) -> Dict[str, List[str]]:
        """Get status lines for the enhanced input plugin organized by area.

        Returns:
            Dictionary with status lines organized by area A, B, C.
        """
        # Check if status display is enabled for this plugin
        if not self.config.show_status:
            return {"A": [], "B": [], "C": []}

        # UI-related status goes in area C
        if not self.config.enabled:
            return {"A": [], "B": [], "C": ["Enhanced Input: Off"]}

        style_display = self.state.get_status_display()

        return {
            "A": [],
            "B": [],
            "C": [
                f"Input: {style_display}",
                f"Width: {self.config.width_mode}"
            ]
        }

    async def _render_fancy_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Render the fancy input box using modular components.

        Args:
            data: Event data containing input information.
            event: The event object.

        Returns:
            Modified event data.
        """
        if not self.config.enabled:
            return {"status": "disabled"}

        # Get input buffer and cursor position from renderer
        input_text = getattr(self.renderer, 'input_buffer', '')
        cursor_position = getattr(self.renderer, 'cursor_position', len(input_text))

        # Determine if input is active and update cursor state
        input_is_active = self.state.is_input_active(self.renderer)
        self.state.update_cursor_blink(input_is_active)

        # Get cursor character
        cursor_char = self.state.get_cursor_char(input_is_active)

        # Insert cursor at correct position
        text_with_cursor = self.cursor_manager.insert_cursor(
            input_text, cursor_position, cursor_char
        )

        # Prepare content with prompt
        if input_text:
            content_with_cursor = f"> {text_with_cursor}"
        elif self.config.show_placeholder:
            colored_placeholder = self.color_engine.apply_color(
                self.config.placeholder, 'placeholder'
            )
            content_with_cursor = f"> {cursor_char}{colored_placeholder}"
        else:
            content_with_cursor = f"> {cursor_char}"

        # Calculate box dimensions
        box_width = self.geometry.calculate_box_width()
        content_width = self.geometry.calculate_content_width(box_width)

        # Process text (wrapping if enabled)
        content_lines = self.text_processor.wrap_text(content_with_cursor, content_width)

        # Calculate dynamic height
        box_height = self.geometry.calculate_box_height(content_lines)

        # Get current style
        current_style = self.state.get_current_style()

        # Render the complete box
        fancy_lines = self.box_renderer.render_box(
            content_lines=content_lines,
            box_width=box_width,
            style_name=current_style
        )

        # Store the fancy input lines for the renderer to use
        data["fancy_input_lines"] = fancy_lines

        return {"status": "rendered", "lines": len(fancy_lines), "fancy_input_lines": fancy_lines}

    async def initialize(self) -> None:
        """Initialize the plugin."""
        pass

    async def register_hooks(self) -> None:
        """Register all plugin hooks with the event bus."""
        for hook in self.hooks:
            await self.event_bus.register_hook(hook)

        # Register status view
        await self._register_status_view()

    async def _register_status_view(self) -> None:
        """Register enhanced input status view."""
        try:
            # Check if renderer has status registry
            if (hasattr(self.renderer, 'status_renderer') and
                self.renderer.status_renderer and
                hasattr(self.renderer.status_renderer, 'status_registry') and
                self.renderer.status_renderer.status_registry):

                from core.io.status_renderer import StatusViewConfig, BlockConfig

                # Create input UI view
                input_view = StatusViewConfig(
                    name="Input UI",
                    plugin_source="enhanced_input",
                    priority=200,  # Lower than core views
                    blocks=[
                        BlockConfig(
                            width_fraction=1.0,
                            content_provider=self._get_input_ui_content,
                            title="Input UI",
                            priority=100
                        )
                    ]
                )

                registry = self.renderer.status_renderer.status_registry
                registry.register_status_view("enhanced_input", input_view)
                logger.info(" Enhanced Input registered 'Input UI' status view")

            else:
                logger.debug("Status registry not available - cannot register status view")

        except Exception as e:
            logger.error(f"Failed to register enhanced input status view: {e}")

    def _get_input_ui_content(self) -> List[str]:
        """Get input UI content (agnoster style)."""
        try:
            seg = AgnosterSegment()

            if not self.config.enabled:
                seg.add_neutral("Input: Off", "dark")
                return [seg.render()]

            style_display = self.state.get_status_display()

            seg.add_lime("Input", "dark")
            seg.add_cyan(style_display, "dark")
            seg.add_neutral(f"Width: {self.config.width_mode}", "mid")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Error getting input UI content: {e}")
            seg = AgnosterSegment()
            seg.add_neutral("Input: Error", "dark")
            return [seg.render()]


    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        pass