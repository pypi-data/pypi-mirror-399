"""Widget integration methods for modal_renderer.py.

This module contains the complete widget integration logic ready to be
merged into modal_renderer.py when Phase 1 signals completion.
"""

from typing import List, Dict, Any, Optional
from .widgets import BaseWidget, CheckboxWidget, DropdownWidget, TextInputWidget, SliderWidget
from ..io.key_parser import KeyPress
from ..io.visual_effects import ColorPalette


class WidgetIntegrationMixin:
    """Mixin class containing widget integration methods for ModalRenderer."""

    def __init__(self):
        """Initialize widget management."""
        self.widgets: List[BaseWidget] = []
        self.focused_widget_index = 0

    def _create_widgets(self, modal_config: dict) -> List[BaseWidget]:
        """Create widgets from modal configuration.

        Args:
            modal_config: Modal configuration dictionary.

        Returns:
            List of instantiated widgets.
        """
        widgets = []
        for section in modal_config.get("sections", []):
            for widget_config in section.get("widgets", []):
                widget = self._create_widget(widget_config)
                widgets.append(widget)
        return widgets

    def _create_widget(self, config: dict) -> BaseWidget:
        """Create a single widget from configuration.

        Args:
            config: Widget configuration dictionary.

        Returns:
            Instantiated widget.

        Raises:
            ValueError: If widget type is unknown.
        """
        widget_type = config["type"]

        # Use config_path directly if provided, otherwise construct from config_path + key
        if "config_path" in config:
            config_path = config["config_path"]
        else:
            config_path = f"{config.get('config_path', 'core.ui')}.{config['key']}"

        if widget_type == "checkbox":
            return CheckboxWidget(config, config_path, self.config_service)
        elif widget_type == "dropdown":
            return DropdownWidget(config, config_path, self.config_service)
        elif widget_type == "text_input":
            return TextInputWidget(config, config_path, self.config_service)
        elif widget_type == "slider":
            return SliderWidget(config, config_path, self.config_service)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")

    def _render_modal_content_with_widgets(self, modal_config: dict, width: int) -> List[str]:
        """Render modal content with interactive widgets.

        Args:
            modal_config: Modal configuration dict.
            width: Modal width.

        Returns:
            List of content lines with rendered widgets.
        """
        lines = []
        border_color = ColorPalette.DIM_CYAN

        # Create widgets if not already created
        if not self.widgets:
            self.widgets = self._create_widgets(modal_config)
            if self.widgets:
                self.widgets[0].set_focus(True)

        # Add empty line
        lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

        # Render sections with widgets
        widget_index = 0
        sections = modal_config.get("sections", [])

        for section in sections:
            section_title = section.get("title", "Section")

            # Section title
            title_text = f"  {section_title}"
            title_line = f"│{title_text.ljust(width-2)}│"
            lines.append(f"{border_color}{title_line}{ColorPalette.RESET}")

            # Empty line after title
            lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

            # Render widgets in this section
            section_widgets = section.get("widgets", [])
            for widget_config in section_widgets:
                if widget_index < len(self.widgets):
                    widget = self.widgets[widget_index]
                    widget_lines = widget.render()

                    # Add each widget line with proper padding
                    for widget_line in widget_lines:
                        # Remove any existing padding and reformat for modal
                        clean_line = widget_line.strip()
                        if clean_line.startswith("  "):  # Remove widget's default padding
                            clean_line = clean_line[2:]

                        # Add modal padding and border
                        padded_line = f"  {clean_line}"
                        modal_line = f"│{padded_line.ljust(width-2)}│"
                        lines.append(f"{border_color}{modal_line}{ColorPalette.RESET}")

                    widget_index += 1

            # Empty line after section
            lines.append(f"{border_color}│{' ' * (width-2)}│{ColorPalette.RESET}")

        return lines

    def _handle_widget_navigation(self, key_press: KeyPress) -> bool:
        """Handle widget focus navigation.

        Args:
            key_press: Key press event.

        Returns:
            True if navigation was handled.
        """
        if not self.widgets:
            return False

        if key_press.name == "Tab" or key_press.name == "ArrowDown":
            # Move to next widget
            self.widgets[self.focused_widget_index].set_focus(False)
            self.focused_widget_index = (self.focused_widget_index + 1) % len(self.widgets)
            self.widgets[self.focused_widget_index].set_focus(True)
            return True

        elif key_press.name == "ArrowUp":
            # Move to previous widget
            self.widgets[self.focused_widget_index].set_focus(False)
            self.focused_widget_index = (self.focused_widget_index - 1) % len(self.widgets)
            self.widgets[self.focused_widget_index].set_focus(True)
            return True

        return False

    def _handle_widget_input(self, key_press: KeyPress) -> bool:
        """Route input to focused widget.

        Args:
            key_press: Key press event.

        Returns:
            True if input was handled by a widget.
        """
        if not self.widgets or self.focused_widget_index >= len(self.widgets):
            return False

        focused_widget = self.widgets[self.focused_widget_index]
        return focused_widget.handle_input(key_press)

    def _get_widget_values(self) -> Dict[str, Any]:
        """Get all widget values for saving.

        Returns:
            Dictionary mapping config paths to values.
        """
        values = {}
        for widget in self.widgets:
            if widget.has_pending_changes():
                values[widget.config_path] = widget.get_pending_value()
        return values

    def _reset_widget_focus(self):
        """Reset widget focus to first widget."""
        if self.widgets:
            for widget in self.widgets:
                widget.set_focus(False)
            self.focused_widget_index = 0
            self.widgets[0].set_focus(True)


# INTEGRATION INSTRUCTIONS FOR PHASE 1 COMPLETION:
"""
TO INTEGRATE WIDGETS INTO modal_renderer.py:

1. Add import at top:
   from .widget_integration import WidgetIntegrationMixin

2. Make ModalRenderer inherit from mixin:
   class ModalRenderer(WidgetIntegrationMixin):

3. Update __init__ method:
   def __init__(self, terminal_renderer, visual_effects):
       super().__init__()  # Initialize widget management
       self.terminal_renderer = terminal_renderer
       self.visual_effects = visual_effects
       self.gradient_renderer = GradientRenderer()

4. Replace _render_modal_content with:
   def _render_modal_content(self, modal_config: dict, width: int) -> List[str]:
       return self._render_modal_content_with_widgets(modal_config, width)

5. Update _handle_modal_input to include widget handling:
   async def _handle_modal_input(self, ui_config: UIConfig) -> Dict[str, Any]:
       # Add widget input handling here
       # Navigation: self._handle_widget_navigation(key_press)
       # Widget input: self._handle_widget_input(key_press)
       # Save values: self._get_widget_values()
"""