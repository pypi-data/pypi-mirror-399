"""Box rendering components for enhanced input plugin."""

from typing import List
from .box_styles import BoxStyleRegistry, BoxStyle
from .color_engine import ColorEngine
from .geometry import GeometryCalculator
from .text_processor import TextProcessor


class BoxRenderer:
    """Renders complete input boxes with borders and content."""

    def __init__(self, style_registry: BoxStyleRegistry, color_engine: ColorEngine,
                 geometry_calculator: GeometryCalculator, text_processor: TextProcessor):
        """Initialize box renderer.

        Args:
            style_registry: Registry for box styles.
            color_engine: Engine for color operations.
            geometry_calculator: Calculator for layout.
            text_processor: Processor for text operations.
        """
        self.style_registry = style_registry
        self.color_engine = color_engine
        self.geometry = geometry_calculator
        self.text_processor = text_processor

    def render_box(self, content_lines: List[str], box_width: int, style_name: str) -> List[str]:
        """Render a complete input box.

        Args:
            content_lines: Lines of content to display.
            box_width: Total width of the box.
            style_name: Name of the box style to use.

        Returns:
            List of rendered box lines.
        """
        style = self.style_registry.get_style(style_name)
        box_height = self.geometry.calculate_box_height(content_lines)
        content_width = self.geometry.calculate_content_width(box_width)

        lines = []

        # Top border
        lines.append(self._create_top_border(box_width, style))

        # Content lines
        for line in content_lines:
            fitted_content = self.text_processor.fit_text_to_width(line, content_width)
            lines.append(self._create_content_line(fitted_content, box_width, style))

        # Fill empty content lines if needed (for minimum height)
        while len(lines) < box_height - 1:  # -1 for bottom border
            lines.append(self._create_content_line("", box_width, style))

        # Bottom border
        lines.append(self._create_bottom_border(box_width, style))

        return lines

    def _create_top_border(self, width: int, style: BoxStyle) -> str:
        """Create the top border of the box.

        Args:
            width: Total width of the box.
            style: Box style to use.

        Returns:
            Top border line.
        """
        horizontal_line = style.horizontal * (width - 2)
        border_line = f"{style.top_left}{horizontal_line}{style.top_right}"
        return self.color_engine.apply_color(border_line, 'border')

    def _create_bottom_border(self, width: int, style: BoxStyle) -> str:
        """Create the bottom border of the box.

        Args:
            width: Total width of the box.
            style: Box style to use.

        Returns:
            Bottom border line.
        """
        horizontal_line = style.horizontal * (width - 2)
        border_line = f"{style.bottom_left}{horizontal_line}{style.bottom_right}"
        return self.color_engine.apply_color(border_line, 'border')

    def _create_content_line(self, content: str, width: int, style: BoxStyle) -> str:
        """Create a single content line of the input box.

        Args:
            content: Content to display in the box.
            width: Total width of the box.
            style: Box style to use.

        Returns:
            Formatted box line.
        """
        left_border = self.color_engine.apply_color(style.vertical, 'border')
        right_border = self.color_engine.apply_color(style.vertical, 'border')
        return f"{left_border} {content} {right_border}"