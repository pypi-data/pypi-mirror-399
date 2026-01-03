"""Geometry calculations for enhanced input plugin."""

import shutil
from typing import List


class GeometryCalculator:
    """Handles all layout and dimension calculations for enhanced input boxes."""

    def __init__(self, config):
        """Initialize geometry calculator.

        Args:
            config: InputConfig object with plugin configuration.
        """
        self.config = config

    def calculate_box_width(self) -> int:
        """Calculate the optimal box width.

        Returns:
            Box width in characters.
        """
        width_mode = self.config.width_mode

        if width_mode == "auto":
            terminal_width = self._get_terminal_width()
            # Leave some margin on both sides
            proposed_width = terminal_width - 4
            # Apply min/max constraints
            min_width = self.config.min_width
            max_width = self.config.max_width
            return max(min_width, min(max_width, proposed_width))
        else:
            # Fixed width mode - use configured width or sensible default
            return getattr(self.config, 'fixed_width', 80)

    def calculate_box_height(self, content_lines: List[str]) -> int:
        """Calculate the box height based on content.

        Args:
            content_lines: List of content lines.

        Returns:
            Total box height including borders.
        """
        dynamic_sizing = self.config.dynamic_sizing

        if not dynamic_sizing:
            return 3  # Fixed: top border + content + bottom border

        content_height = len(content_lines)
        total_height = content_height + 2  # Add top and bottom borders

        # Apply min/max constraints
        min_height = self.config.min_height
        max_height = self.config.max_height
        return max(min_height, min(max_height, total_height))

    def calculate_content_width(self, box_width: int) -> int:
        """Calculate content area width.

        Args:
            box_width: Total box width.

        Returns:
            Content width (excluding borders and spaces).
        """
        # Width breakdown: │ + space + content + space + │ = box_width
        return box_width - 4  # 2 border chars + 2 spaces

    def _get_terminal_width(self) -> int:
        """Get the current terminal width.

        Returns:
            Terminal width in columns.
        """
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80  # Default fallback