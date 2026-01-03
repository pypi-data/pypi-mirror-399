"""Modal renderer using existing visual effects infrastructure."""

import asyncio
import logging
import re
from typing import List, Dict, Any, Optional

from ..events.models import UIConfig
from ..io.visual_effects import ColorPalette, GradientRenderer
from ..io.key_parser import KeyPress
from .widgets import BaseWidget, CheckboxWidget, DropdownWidget, TextInputWidget, SliderWidget, LabelWidget
from .config_merger import ConfigMerger
from .modal_actions import ModalActionHandler
from .modal_overlay_renderer import ModalOverlayRenderer
from .modal_state_manager import ModalStateManager, ModalLayout, ModalDisplayMode

logger = logging.getLogger(__name__)

# Maximum modal width to prevent overly wide modals
MAX_MODAL_WIDTH = 80


class ModalRenderer:
    """Modal overlay renderer using existing visual effects system."""

    def __init__(self, terminal_renderer, visual_effects, config_service=None):
        """Initialize modal renderer with existing infrastructure.

        Args:
            terminal_renderer: Terminal renderer for output.
            visual_effects: Visual effects system for styling.
            config_service: ConfigService for config persistence.
        """
        self.terminal_renderer = terminal_renderer
        self.visual_effects = visual_effects
        self.gradient_renderer = GradientRenderer()
        self.config_service = config_service

        # NEW: Initialize overlay rendering system for proper modal display
        if terminal_renderer and hasattr(terminal_renderer, 'terminal_state'):
            self.overlay_renderer = ModalOverlayRenderer(terminal_renderer.terminal_state)
            self.state_manager = ModalStateManager(terminal_renderer.terminal_state)
        else:
            # Fallback for testing or when terminal_renderer is not available
            self.overlay_renderer = None
            self.state_manager = None

        # Widget management
        self.widgets: List[BaseWidget] = []
        self.focused_widget_index = 0
        self.scroll_offset = 0
        self.visible_height = 20  # Number of widget lines visible at once
        self._save_confirm_active = False  # For save confirmation prompt

        # Command list selection (for modals with "commands" sections)
        self.command_items: List[Dict] = []  # Flat list of all command items
        self.selected_command_index = 0
        self.has_command_sections = False

        # Action handling
        self.action_handler = ModalActionHandler(config_service) if config_service else None

    async def show_modal(self, ui_config: UIConfig) -> Dict[str, Any]:
        """Show modal overlay using TRUE overlay system.

        Args:
            ui_config: Modal configuration.

        Returns:
            Modal interaction result.
        """
        try:
            # Reset command selection state for fresh modal
            self._command_selected = False

            # FIXED: Use overlay system instead of chat pipeline clearing
            # No more clear_active_area() - that only clears display, not buffers

            # Render modal using existing visual effects (content generation)
            modal_lines = self._render_modal_box(ui_config)

            # Use overlay rendering instead of animation that routes through chat
            await self._render_modal_lines(modal_lines)

            return await self._handle_modal_input(ui_config)
        except Exception as e:
            logger.error(f"Error showing modal: {e}")
            # Ensure proper cleanup on error
            if self.state_manager:
                self.state_manager.restore_terminal_state()
            return {"success": False, "error": str(e)}

    def refresh_modal_display(self) -> bool:
        """Refresh modal display without accumulation using overlay system.

        This method refreshes the current modal content without any
        interaction with conversation buffers or message systems.

        Returns:
            True if refresh was successful.
        """
        try:
            # Use state manager to refresh display without chat pipeline
            if self.state_manager:
                return self.state_manager.refresh_modal_display()
            else:
                logger.warning("State manager not available - fallback refresh")
                return True
        except Exception as e:
            logger.error(f"Error refreshing modal display: {e}")
            return False

    def close_modal(self) -> bool:
        """Close modal and restore terminal state.

        Returns:
            True if modal was closed successfully.
        """
        try:
            # Use state manager to properly restore terminal state
            if self.state_manager:
                return self.state_manager.restore_terminal_state()
            else:
                logger.warning("State manager not available - fallback close")
                return True
        except Exception as e:
            logger.error(f"Error closing modal: {e}")
            return False

    def _render_modal_box(self, ui_config: UIConfig, preserve_widgets: bool = False) -> List[str]:
        """Render modal box using existing ColorPalette.

        Args:
            ui_config: Modal configuration.
            preserve_widgets: If True, preserve existing widget states instead of recreating.

        Returns:
            List of rendered modal lines.
        """
        # Use existing ColorPalette for styling
        border_color = ColorPalette.GREY
        title_color = ColorPalette.BRIGHT_WHITE
        footer_color = ColorPalette.GREY
        # Use dynamic terminal width, capped at MAX_MODAL_WIDTH (80 cols)
        terminal_width = getattr(self.terminal_renderer.terminal_state, 'width', 80) if self.terminal_renderer else 80
        requested_width = int(ui_config.width or MAX_MODAL_WIDTH)
        width = min(requested_width, terminal_width, MAX_MODAL_WIDTH)
        title = ui_config.title or "Modal"

        lines = []

        # Top border with colored title embedded
        title_separators = "─"
        remaining_width = max(0, width - 2 - len(title) - 2)  # -2 for separators
        left_padding = remaining_width // 2
        right_padding = remaining_width - left_padding
        title_border = f"{border_color}╭{'─' * left_padding}{title_separators}{title_color}{title}{ColorPalette.RESET}{border_color}{title_separators}{'─' * right_padding}╮{ColorPalette.RESET}"
        lines.append(title_border)

        # Content area
        # Use actual width for content rendering
        actual_content_width = width - 2  # Remove padding from width for content
        content_lines = self._render_modal_content(ui_config.modal_config or {}, actual_content_width + 2, preserve_widgets)
        lines.extend(content_lines)

        # Bottom border with footer embedded
        if self._save_confirm_active:
            footer = "Save changes? (Y)es / (N)o / (Esc) cancel"
            footer_color = ColorPalette.BRIGHT_YELLOW
        else:
            footer = (ui_config.modal_config or {}).get("footer", "enter to select • esc to close")
        footer_remaining = max(0, width - 2 - len(footer))
        footer_left = footer_remaining // 2
        footer_right = footer_remaining - footer_left
        footer_border = f"{border_color}╰{'─' * footer_left}{footer_color}{footer}{ColorPalette.RESET}{border_color}{'─' * footer_right}╯{ColorPalette.RESET}"
        lines.append(footer_border)

        return lines

    def _render_modal_content(self, modal_config: dict, width: int, preserve_widgets: bool = False) -> List[str]:
        """Render modal content with interactive widgets and scrolling.

        Args:
            modal_config: Modal configuration dict.
            width: Modal width.
            preserve_widgets: If True, preserve existing widget states instead of recreating.

        Returns:
            List of content lines with rendered widgets.
        """
        all_lines = []  # All content lines before pagination
        border_color = ColorPalette.GREY  # Modal border color

        # Create or preserve widgets based on mode
        if not preserve_widgets:
            self.widgets = []
            self.focused_widget_index = 0
            self.scroll_offset = 0
            self.widgets = self._create_widgets(modal_config)
            if self.widgets:
                self.widgets[0].set_focus(True)
            # Reset command selection for command-style modals
            self.selected_command_index = 0

        # Always rebuild command_items list (but preserve selected_command_index)
        self.command_items = []
        self.has_command_sections = False

        # Build all content lines with widget indices
        widget_index = 0
        widget_line_map = []  # Maps line index to widget index
        sections = modal_config.get("sections", [])

        for section_idx, section in enumerate(sections):
            section_title = section.get("title", "Section")
            # Use lime green for section headers
            title_text = f"  {ColorPalette.LIME_LIGHT}{section_title}{ColorPalette.RESET}"
            # Build line with proper color separation: border | content | border
            title_line = f"{border_color}│{ColorPalette.RESET}{self._pad_line_with_ansi(title_text, width-2)}{border_color}│{ColorPalette.RESET}"
            all_lines.append(title_line)
            widget_line_map.append(-1)  # Section header, no widget

            section_widgets = section.get("widgets", [])
            if section_widgets:
                for widget_config in section_widgets:
                    if widget_index < len(self.widgets):
                        widget = self.widgets[widget_index]
                        widget_lines = widget.render()

                        for widget_line in widget_lines:
                            clean_line = widget_line.strip()
                            if clean_line.startswith("  "):
                                clean_line = clean_line[2:]
                            padded_line = f"  {clean_line}"
                            modal_line = f"│{self._pad_line_with_ansi(padded_line, width-2)}│"
                            all_lines.append(f"{border_color}{modal_line}{ColorPalette.RESET}")
                            widget_line_map.append(widget_index)

                        widget_index += 1

            # Handle "commands" format (used by help modal, etc.)
            section_commands = section.get("commands", [])
            if section_commands and not section_widgets:
                self.has_command_sections = True
                for cmd_idx, cmd in enumerate(section_commands):
                    # Track command item with its global index
                    global_cmd_idx = len(self.command_items)
                    self.command_items.append(cmd)

                    name = cmd.get("name", "")
                    description = cmd.get("description", "")

                    # Check if this item is selected
                    is_selected = (global_cmd_idx == self.selected_command_index)

                    # Truncate description BEFORE adding ANSI codes
                    # Layout: "  > name                    description" = ~34 chars prefix + description
                    max_desc_len = width - 38  # Account for prefix, name padding, and borders
                    if len(description) > max_desc_len:
                        description = description[:max_desc_len - 3] + "..."

                    # Format command line with selection indicator
                    if is_selected:
                        # Highlight selected item with lime color
                        cmd_text = f"  {ColorPalette.LIME_LIGHT}> {name:<26}{ColorPalette.RESET} {description}"
                    else:
                        cmd_text = f"    {name:<26} {description}"

                    modal_line = f"│{self._pad_line_with_ansi(cmd_text, width-2)}│"
                    all_lines.append(f"{border_color}{modal_line}{ColorPalette.RESET}")
                    widget_line_map.append(-2)  # Command entry (use -2 to distinguish from headers)

            # Also handle "sessions" format (used by resume modal, etc.)
            section_sessions = section.get("sessions", [])
            if section_sessions and not section_widgets and not section_commands:
                self.has_command_sections = True
                for sess_idx, sess in enumerate(section_sessions):
                    # Track session item with its global index
                    global_sess_idx = len(self.command_items)
                    # Convert session format to command format for selection handling
                    cmd_item = {
                        "name": sess.get("title", sess.get("id", "Unknown")),
                        "description": sess.get("subtitle", ""),
                        "session_id": sess.get("id") or sess.get("metadata", {}).get("session_id", ""),
                        "action": sess.get("action", "resume_session"),  # Use session's action or default
                        "exit_mode": sess.get("exit_mode", "normal"),  # How to exit modal before handling
                        "metadata": sess.get("metadata", {})
                    }
                    self.command_items.append(cmd_item)

                    title = sess.get("title", sess.get("id", "Unknown"))
                    subtitle = sess.get("subtitle", "")

                    # Check if this item is selected
                    is_selected = (global_sess_idx == self.selected_command_index)

                    # Format session line with selection indicator
                    # Truncate title BEFORE adding ANSI codes to avoid mid-code truncation
                    max_title_len = width - 8  # Account for "  > " prefix and borders
                    if len(title) > max_title_len:
                        title = title[:max_title_len - 3] + "..."

                    if is_selected:
                        # Highlight selected item with lime color
                        sess_text = f"  {ColorPalette.LIME_LIGHT}> {title}{ColorPalette.RESET}"
                    else:
                        sess_text = f"    {title}"

                    modal_line = f"│{self._pad_line_with_ansi(sess_text, width-2)}│"
                    all_lines.append(f"{border_color}{modal_line}{ColorPalette.RESET}")
                    widget_line_map.append(-2)  # Session entry

                    # Add subtitle on a second line if present
                    if subtitle:
                        # Truncate subtitle BEFORE adding ANSI codes
                        max_sub_len = width - 10  # Account for "      " prefix and borders
                        if len(subtitle) > max_sub_len:
                            subtitle = subtitle[:max_sub_len - 3] + "..."

                        if is_selected:
                            sub_text = f"      {ColorPalette.GREY}{subtitle}{ColorPalette.RESET}"
                        else:
                            sub_text = f"      {ColorPalette.DIM}{subtitle}{ColorPalette.RESET}"
                        sub_line = f"│{self._pad_line_with_ansi(sub_text, width-2)}│"
                        all_lines.append(f"{border_color}{sub_line}{ColorPalette.RESET}")
                        widget_line_map.append(-3)  # Subtitle line (non-selectable)

            # Add blank line after each section (except the last one)
            if section_idx < len(sections) - 1:
                blank_line = f"│{' ' * (width-2)}│"
                all_lines.append(f"{border_color}{blank_line}{ColorPalette.RESET}")
                widget_line_map.append(-1)  # Blank line, no widget

        # Auto-scroll to keep focused widget visible
        if self.widgets:
            focused_lines = [i for i, w in enumerate(widget_line_map) if w == self.focused_widget_index]
            if focused_lines:
                first_line = focused_lines[0]

                # When scrolling up, include section header
                if first_line < self.scroll_offset:
                    # If focusing first widget (wrap-around), scroll to top to show header
                    if self.focused_widget_index == 0:
                        self.scroll_offset = 0
                    else:
                        # Look for section header above the focused widget
                        section_header_line = first_line
                        for i in range(first_line - 1, -1, -1):
                            if widget_line_map[i] == -1:  # Header or blank line
                                section_header_line = i
                            else:
                                break  # Found another widget, stop
                        self.scroll_offset = section_header_line
                elif first_line >= self.scroll_offset + self.visible_height:
                    self.scroll_offset = first_line - self.visible_height + 1

        # Apply scroll offset and return visible lines
        total_lines = len(all_lines)

        # Clamp scroll offset to valid range (fixes wrap-around from first to last item)
        max_scroll = max(0, total_lines - self.visible_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        end_offset = min(self.scroll_offset + self.visible_height, total_lines)
        visible_lines = all_lines[self.scroll_offset:end_offset]

        # Pad to fixed height (visible_height) to prevent height changes when scrolling
        while len(visible_lines) < self.visible_height:
            empty_line = f"│{' ' * (width-2)}│"
            visible_lines.append(f"{border_color}{empty_line}{ColorPalette.RESET}")

        # Add scroll indicator if needed (always at the same position)
        if total_lines > self.visible_height:
            scroll_info = f" [{self.scroll_offset + 1}-{end_offset}/{total_lines}] "
            if self.scroll_offset > 0:
                scroll_info = f"↑{scroll_info}"
            if end_offset < total_lines:
                scroll_info = f"{scroll_info}↓"
            indicator_line = f"│{scroll_info.center(width-2)}│"
            visible_lines.append(f"{ColorPalette.DIM}{indicator_line}{ColorPalette.RESET}")
        else:
            # Add empty indicator line to maintain fixed height
            empty_indicator = f"│{' ' * (width-2)}│"
            visible_lines.append(f"{border_color}{empty_indicator}{ColorPalette.RESET}")

        return visible_lines

    async def _animate_entrance(self, lines: List[str]):
        """Render modal cleanly without stacking animation.

        Args:
            lines: Modal lines to render.
        """
        try:
            # Single clean render without animation to prevent stacking
            await self._render_modal_lines(lines)
        except Exception as e:
            logger.error(f"Error rendering modal: {e}")
            # Single fallback render only
            await self._render_modal_lines(lines)

    async def _render_modal_lines(self, lines: List[str]):
        """Render modal lines using TRUE overlay system (no chat pipeline).

        Args:
            lines: Lines to render.
        """
        try:
            # FIXED: Use overlay rendering system instead of chat pipeline
            # This completely bypasses write_message() and conversation buffers

            # Create modal layout configuration
            # Use visible width (strip ANSI) for accurate layout calculation
            visible_widths = [len(self._strip_ansi(line)) for line in lines] if lines else [MAX_MODAL_WIDTH]
            content_width = max(visible_widths)
            # Constrain to terminal width and MAX_MODAL_WIDTH (80 cols)
            terminal_width = getattr(self.terminal_renderer.terminal_state, 'width', 80) if self.terminal_renderer else 80
            width = min(content_width, terminal_width - 2, MAX_MODAL_WIDTH)  # Cap at 80 cols
            height = len(lines)
            layout = ModalLayout(
                width=width,
                height=height + 2,         # Add border space
                center_horizontal=True,
                center_vertical=True,
                padding=2,
                border_style="box"
            )

            # Prepare modal display with state isolation
            if self.state_manager:
                prepare_result = self.state_manager.prepare_modal_display(layout, ModalDisplayMode.OVERLAY)
                if not prepare_result:
                    logger.error("Failed to prepare modal display")
                    return

                # Render modal content using direct terminal output (bypassing chat)
                render_result = self.state_manager.render_modal_content(lines)
                if not render_result:
                    logger.error("Failed to render modal content")
                    return

                logger.info(f"Modal rendered via overlay system: {len(lines)} lines")
            else:
                # Fallback to basic display for testing
                logger.warning("Modal overlay system not available - using fallback display")
                for line in lines:
                    print(line)

        except Exception as e:
            logger.error(f"Error rendering modal via overlay system: {e}")
            # Ensure state is cleaned up on error
            if self.state_manager:
                self.state_manager.restore_terminal_state()

    def _create_widgets(self, modal_config: dict) -> List[BaseWidget]:
        """Create widgets from modal configuration.

        Args:
            modal_config: Modal configuration dictionary.

        Returns:
            List of instantiated widgets.
        """

        widgets = []
        sections = modal_config.get("sections", [])


        for section_idx, section in enumerate(sections):
            section_widgets = section.get("widgets", [])

            for widget_idx, widget_config in enumerate(section_widgets):
                try:
                    widget = self._create_widget(widget_config)
                    widgets.append(widget)
                except Exception as e:
                    logger.error(f"FAILED to create widget {widget_idx} in section {section_idx}: {e}")
                    logger.error(f"Widget config that failed: {widget_config}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")

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

        try:
            widget_type = config["type"]
        except KeyError as e:
            logger.error(f"Widget config missing 'type' field: {e}")
            raise ValueError(f"Widget config missing required 'type' field: {config}")

        # Support both "config_path" (for config-bound widgets) and "field" (for form modals)
        config_path = config.get("config_path") or config.get("field", "core.ui.unknown")

        # Get current value from config service if available
        current_value = None
        if self.config_service:
            current_value = self.config_service.get(config_path)
        else:
            pass

        # Create widget config with current value
        widget_config = config.copy()
        if current_value is not None:
            widget_config["current_value"] = current_value


        try:
            if widget_type == "checkbox":
                widget = CheckboxWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "dropdown":
                widget = DropdownWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "text_input":
                widget = TextInputWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "slider":
                widget = SliderWidget(widget_config, config_path, self.config_service)
                return widget
            elif widget_type == "label":
                # Label widgets use "value" directly, not config_path
                label_text = config.get("label", "")
                value_text = config.get("value", "")
                help_text = config.get("help", "")
                widget = LabelWidget(
                    label=label_text,
                    value=value_text,
                    help_text=help_text,
                    config_path=config_path,
                    current_value=value_text
                )
                return widget
            else:
                error_msg = f"Unknown widget type: {widget_type}"
                logger.error(f"{error_msg}")
                raise ValueError(error_msg)
        except Exception as e:
            logger.error(f"FATAL: Widget constructor failed for type '{widget_type}': {e}")
            logger.error(f"Widget config that caused failure: {widget_config}")
            import traceback
            logger.error(f"Full constructor traceback: {traceback.format_exc()}")
            raise

    def _handle_widget_navigation(self, key_press: KeyPress) -> bool:
        """Handle widget focus navigation.

        Args:
            key_press: Key press event.

        Returns:
            True if navigation was handled.
        """
        # Handle command-style modal navigation (no widgets, just command items)
        if self.has_command_sections and self.command_items and not self.widgets:
            old_index = self.selected_command_index
            if key_press.name == "ArrowDown" or key_press.name == "Tab":
                self.selected_command_index = (self.selected_command_index + 1) % len(self.command_items)
            elif key_press.name == "ArrowUp":
                self.selected_command_index = (self.selected_command_index - 1) % len(self.command_items)
            elif key_press.name == "PageDown":
                self.selected_command_index = min(self.selected_command_index + 10, len(self.command_items) - 1)
            elif key_press.name == "PageUp":
                self.selected_command_index = max(self.selected_command_index - 10, 0)
            else:
                return False

            # Update scroll offset to keep selection visible
            # Each command item takes ~2 lines (title + subtitle), adjust accordingly
            lines_per_item = 2  # Approximate lines per session item
            selected_line = self.selected_command_index * lines_per_item

            # Scroll down if selection is below visible area
            if selected_line >= self.scroll_offset + self.visible_height - 2:
                self.scroll_offset = max(0, selected_line - self.visible_height + 4)

            # Scroll up if selection is above visible area
            if selected_line < self.scroll_offset:
                self.scroll_offset = max(0, selected_line - 2)

            # Handle wrap-around: if we went from last to first, scroll to top
            if old_index == len(self.command_items) - 1 and self.selected_command_index == 0:
                self.scroll_offset = 0

            # Handle wrap-around: if we went from first to last, scroll to bottom
            if old_index == 0 and self.selected_command_index == len(self.command_items) - 1:
                max_scroll = max(0, len(self.command_items) * lines_per_item - self.visible_height + 4)
                self.scroll_offset = max_scroll

            return True

        if not self.widgets:
            return False

        # CRITICAL FIX: Check if focused widget is expanded before handling navigation
        # If a dropdown is expanded, let it handle its own ArrowDown/ArrowUp
        focused_widget = self.widgets[self.focused_widget_index]
        if hasattr(focused_widget, '_expanded') and focused_widget._expanded:
            # Widget is expanded - don't intercept arrow keys
            if key_press.name in ["ArrowDown", "ArrowUp"]:
                return False  # Let widget handle its own navigation

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

        elif key_press.name == "PageDown":
            # Jump forward by visible_height widgets
            self.widgets[self.focused_widget_index].set_focus(False)
            self.focused_widget_index = min(self.focused_widget_index + self.visible_height, len(self.widgets) - 1)
            self.widgets[self.focused_widget_index].set_focus(True)
            return True

        elif key_press.name == "PageUp":
            # Jump backward by visible_height widgets
            self.widgets[self.focused_widget_index].set_focus(False)
            self.focused_widget_index = max(self.focused_widget_index - self.visible_height, 0)
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
        # Handle Enter key for command-style modals
        logger.info(f"🔧 _handle_widget_input: has_command_sections={self.has_command_sections}, "
                    f"command_items={len(self.command_items) if self.command_items else 0}, "
                    f"widgets={len(self.widgets) if self.widgets else 0}")
        if self.has_command_sections and self.command_items and not self.widgets:
            if key_press.name == "Enter" or key_press.char == "\r":
                # Mark that a command was selected
                self._command_selected = True
                logger.info(f"🎯 Command selected! _command_selected={self._command_selected}")
                return True
            return False

        if not self.widgets or self.focused_widget_index >= len(self.widgets):
            return False

        focused_widget = self.widgets[self.focused_widget_index]

        result = focused_widget.handle_input(key_press)
        return result

    def get_selected_command(self) -> Optional[Dict]:
        """Get the currently selected command item.

        Returns:
            Selected command dict or None.
        """
        if self.has_command_sections and self.command_items:
            if 0 <= self.selected_command_index < len(self.command_items):
                return self.command_items[self.selected_command_index]
        return None

    def was_command_selected(self) -> bool:
        """Check if a command was selected via Enter.

        Returns:
            True if a command was selected.
        """
        return getattr(self, '_command_selected', False)

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

    def _create_gradient_header(self, title: str) -> str:
        """Create a gradient header text with bold white and cyan-blue gradient.

        Args:
            title: Section title text.

        Returns:
            Formatted title with gradient effect.
        """
        if not title:
            return ""

        # Make section headers slightly brighter than normal text
        return f"{ColorPalette.BRIGHT}{title}{ColorPalette.RESET}"

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text.

        Args:
            text: Text with potential ANSI codes.

        Returns:
            Text with ANSI codes removed.
        """
        return re.sub(r'\033\[[0-9;]*m', '', text)

    def _pad_line_with_ansi(self, line: str, target_width: int) -> str:
        """Pad line to target width, accounting for ANSI escape codes.

        Args:
            line: Line that may contain ANSI codes.
            target_width: Target visible width.

        Returns:
            Line padded to target visible width.
        """
        visible_length = len(self._strip_ansi(line))
        padding_needed = max(0, target_width - visible_length)
        return line + ' ' * padding_needed

    async def _handle_modal_input(self, ui_config: UIConfig) -> Dict[str, Any]:
        """Handle modal input with persistent event loop for widget interaction.

        Args:
            ui_config: Modal configuration.

        Returns:
            Modal completion result when user exits.
        """
        # Store ui_config for refresh operations
        self.current_ui_config = ui_config

        # Modal is now active and waiting for input
        # Input handling happens through input_handler._handle_modal_keypress()
        # which calls our widget methods and refreshes display


        # The modal stays open until input_handler calls one of:
        # - _exit_modal_mode() (Escape key)
        # - _save_and_exit_modal() (Enter key or save action)

        # This method completes when the modal is closed externally
        # Return success with widget information
        return {
            "success": True,
            "action": "modal_interactive",
            "widgets_enabled": True,
            "widget_count": len(self.widgets),
            "widgets_created": [w.__class__.__name__ for w in self.widgets]
        }