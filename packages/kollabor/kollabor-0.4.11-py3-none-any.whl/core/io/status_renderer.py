"""Status rendering system for terminal applications.

This module provides block-based status rendering for terminal applications
with plugin-configurable views and navigation.
"""

import re
import logging
import sys
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable

from .visual_effects import ColorPalette

logger = logging.getLogger(__name__)

# Platform check for keyboard shortcut display
IS_WINDOWS = sys.platform == "win32"


@dataclass
class BlockConfig:
    """Configuration for a single status block."""

    width_fraction: float  # 0.25, 0.33, 0.5, 0.67, 1.0
    content_provider: Callable[[], List[str]]  # Function that returns status content
    title: str  # Block title/label
    priority: int = 0  # Block priority within view


@dataclass
class StatusViewConfig:
    """Configuration for a complete status view."""

    name: str  # "Session Stats", "Performance", "My Plugin View"
    plugin_source: str  # Plugin that registered this view
    priority: int  # Display order priority
    blocks: List[BlockConfig]  # Block layout configuration


class StatusViewRegistry:
    """Registry for plugin-configurable status views with navigation."""

    def __init__(self, event_bus=None):
        """Initialize status view registry.

        Args:
            event_bus: Event bus for firing status change events.
        """
        self.views: List[StatusViewConfig] = []
        self.current_index = 0
        self.event_bus = event_bus
        logger.info("StatusViewRegistry initialized")

    def register_status_view(
        self, plugin_name: str, config: StatusViewConfig
    ) -> None:
        """Register a new status view from a plugin.

        Args:
            plugin_name: Name of the plugin registering the view.
            config: StatusViewConfig for the new view.
        """
        self.views.append(config)
        self.views.sort(key=lambda v: v.priority, reverse=True)

        logger.info(
            f"Registered status view '{config.name}' from plugin '{plugin_name}' "
            f"with priority {config.priority}"
        )

    def _view_has_content(self, view: StatusViewConfig) -> bool:
        """Check if a view has any content to display."""
        for block in view.blocks:
            try:
                content = block.content_provider()
                if content:
                    return True
            except Exception:
                pass
        return False

    def cycle_next(self) -> Optional[StatusViewConfig]:
        """Navigate to next status view (skips empty views)."""
        if not self.views:
            return None

        start_index = self.current_index
        for _ in range(len(self.views)):
            self.current_index = (self.current_index + 1) % len(self.views)
            current_view = self.views[self.current_index]

            if self._view_has_content(current_view):
                if self.event_bus:
                    try:
                        from ..events.models import EventType, Event

                        event = Event(
                            type=EventType.STATUS_VIEW_CHANGED,
                            data={"view_name": current_view.name, "direction": "next"},
                            source="status_view_registry",
                        )
                        self.event_bus.fire_event(event)
                    except Exception as e:
                        logger.warning(f"Failed to fire STATUS_VIEW_CHANGED event: {e}")

                logger.debug(f"Cycled to next status view: '{current_view.name}'")
                return current_view

        self.current_index = start_index
        return self.views[self.current_index] if self.views else None

    def cycle_previous(self) -> Optional[StatusViewConfig]:
        """Navigate to previous status view (skips empty views)."""
        if not self.views:
            return None

        start_index = self.current_index
        for _ in range(len(self.views)):
            self.current_index = (self.current_index - 1) % len(self.views)
            current_view = self.views[self.current_index]

            if self._view_has_content(current_view):
                if self.event_bus:
                    try:
                        from ..events.models import EventType, Event

                        event = Event(
                            type=EventType.STATUS_VIEW_CHANGED,
                            data={
                                "view_name": current_view.name,
                                "direction": "previous",
                            },
                            source="status_view_registry",
                        )
                        self.event_bus.fire_event(event)
                    except Exception as e:
                        logger.warning(f"Failed to fire STATUS_VIEW_CHANGED event: {e}")

                logger.debug(f"Cycled to previous status view: '{current_view.name}'")
                return current_view

        self.current_index = start_index
        return self.views[self.current_index] if self.views else None

    def get_current_view(self) -> Optional[StatusViewConfig]:
        """Get the currently active status view."""
        if not self.views:
            return None
        return self.views[self.current_index]

    def get_view_count(self) -> int:
        """Get total number of views with content."""
        return sum(1 for view in self.views if self._view_has_content(view))

    def get_current_view_index(self) -> int:
        """Get 1-indexed position of current view among views with content."""
        if not self.views:
            return 0
        current_view = self.views[self.current_index]
        index = 0
        for view in self.views:
            if self._view_has_content(view):
                index += 1
                if view is current_view:
                    return index
        return index

    def get_view_names(self) -> List[str]:
        """Get names of all registered views."""
        return [view.name for view in self.views]

    def get_active_view_names(self) -> List[str]:
        """Get names of views with content."""
        return [view.name for view in self.views if self._view_has_content(view)]


class StatusRenderer:
    """Block-based status rendering system."""

    def __init__(
        self,
        terminal_width: int = 80,
        status_registry: Optional[StatusViewRegistry] = None,
    ):
        """Initialize status renderer.

        Args:
            terminal_width: Terminal width for layout calculations.
            status_registry: Status view registry for block-based rendering.
        """
        self.terminal_width = terminal_width
        self.status_registry = status_registry
        self.spacing = 4  # Spacing between columns

    def set_terminal_width(self, width: int) -> None:
        """Update terminal width for layout calculations."""
        self.terminal_width = width

    def render_horizontal_layout(self, colorizer_func=None) -> List[str]:
        """Render status views in horizontal layout.

        Args:
            colorizer_func: Optional function to apply colors to text.

        Returns:
            List of formatted status lines.
        """
        if not self.status_registry:
            return []
        return self._render_block_layout(colorizer_func)

    def _render_block_layout(self, colorizer_func=None) -> List[str]:
        """Render flexible block-based layout using StatusViewRegistry."""
        if not self.status_registry:
            return []

        current_view = self.status_registry.get_current_view()
        if not current_view:
            return []

        # Get content from all blocks in the current view
        block_contents = []
        for block in current_view.blocks:
            try:
                content = block.content_provider()
                if content:
                    block_contents.append(
                        {
                            "width_fraction": block.width_fraction,
                            "title": block.title,
                            "content": content,
                            "priority": block.priority,
                        }
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to get content from block '{block.title}': {e}"
                )

        if not block_contents:
            return []

        # Sort blocks by priority
        block_contents.sort(key=lambda b: b["priority"], reverse=True)

        # Calculate block layout
        total_width = sum(block["width_fraction"] for block in block_contents)
        if total_width <= 1.0:
            lines = self._render_single_row_blocks(block_contents, colorizer_func)
        else:
            lines = self._render_multi_row_blocks(block_contents, colorizer_func)

        # Add cycling hint if multiple views with content are available
        view_count = self.status_registry.get_view_count()
        if view_count > 1:
            current_index = self.status_registry.get_current_view_index()
            mod_key = "Alt" if IS_WINDOWS else "Opt"
            hint = (
                f"{ColorPalette.INFO_CYAN}({mod_key}+Left/Right to cycle • "
                f"View {current_index}/{view_count}: {current_view.name})"
                f"{ColorPalette.RESET}"
            )
            lines.append(hint)

        return lines

    def _render_single_row_blocks(
        self, block_contents: List[Dict], colorizer_func=None
    ) -> List[str]:
        """Render blocks in a single horizontal row."""
        lines = []

        # Calculate column widths
        total_spacing = (
            (len(block_contents) - 1) * self.spacing
            if len(block_contents) > 1
            else 0
        )
        available_width = self.terminal_width - total_spacing

        column_widths = []
        for block in block_contents:
            width = int(available_width * block["width_fraction"])
            column_widths.append(max(10, width))

        # Find maximum lines across all blocks
        max_lines = (
            max(len(block["content"]) for block in block_contents)
            if block_contents
            else 0
        )

        # Create each row
        for line_idx in range(max_lines):
            columns = []

            for i, block in enumerate(block_contents):
                if line_idx < len(block["content"]):
                    text = block["content"][line_idx]

                    # Skip colorizer for pre-colored content
                    if colorizer_func and "\033[" not in text:
                        text = colorizer_func(text)

                    # Truncate if too long
                    visible_text = self._strip_ansi(text)
                    max_width = column_widths[i]

                    if len(visible_text) > max_width:
                        if max_width > 3:
                            text = self._truncate_with_ansi(text, max_width - 3) + "..."
                        else:
                            text = "..."

                    columns.append(text)
                else:
                    columns.append("")

            # Join columns with spacing
            formatted_line = ""
            for i, col in enumerate(columns):
                formatted_line += col

                if i < len(columns) - 1 and any(columns[i + 1:]):
                    visible_length = len(self._strip_ansi(col))
                    padding = max(0, column_widths[i] - visible_length)
                    formatted_line += " " * padding
                    formatted_line += " " * self.spacing

            if formatted_line.strip():
                lines.append(formatted_line.rstrip())

        return lines

    def _render_multi_row_blocks(
        self, block_contents: List[Dict], colorizer_func=None
    ) -> List[str]:
        """Render blocks that don't fit in a single row."""
        lines = []

        for block in block_contents:
            for content_line in block["content"]:
                # Skip colorizer for pre-colored content
                if colorizer_func and "\033[" not in content_line:
                    content_line = colorizer_func(content_line)

                # Truncate if too long
                visible_text = self._strip_ansi(content_line)
                if len(visible_text) > self.terminal_width - 3:
                    content_line = (
                        self._truncate_with_ansi(content_line, self.terminal_width - 6)
                        + "..."
                    )

                lines.append(content_line)

        return lines

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text."""
        return re.sub(r"\033\[[0-9;]*m", "", text)

    def _truncate_with_ansi(self, text: str, max_length: int) -> str:
        """Truncate text while preserving ANSI codes."""
        result = ""
        visible_count = 0
        i = 0

        while i < len(text) and visible_count < max_length:
            if text[i:i + 1] == "\033" and i + 1 < len(text) and text[i + 1] == "[":
                # Find end of ANSI sequence
                end = i + 2
                while end < len(text) and text[end] not in "mhlABCDEFGHJKSTfimpsuI":
                    end += 1
                if end < len(text):
                    end += 1
                result += text[i:end]
                i = end
            else:
                result += text[i]
                visible_count += 1
                i += 1

        return result
