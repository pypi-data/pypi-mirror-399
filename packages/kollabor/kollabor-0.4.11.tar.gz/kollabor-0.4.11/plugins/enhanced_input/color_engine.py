"""Color and gradient engine for enhanced input plugin."""

from typing import List, Tuple

from core.io.visual_effects import get_color_support, ColorSupport, rgb_to_256


class ColorEngine:
    """Handles all color and gradient operations for enhanced input rendering."""

    def __init__(self, config):
        """Initialize color engine.

        Args:
            config: InputConfig object with plugin configuration.
        """
        self.config = config

    def apply_color(self, text: str, color_type: str) -> str:
        """Apply color formatting to text.

        Args:
            text: Text to color.
            color_type: Color type ('border', 'text', 'placeholder').

        Returns:
            Colored text with ANSI codes.
        """
        # Check if gradient mode is enabled
        gradient_mode = self.config.gradient_mode

        if gradient_mode:
            return self._apply_gradient_color(text, color_type)
        else:
            return self._apply_standard_color(text, color_type)

    def _apply_gradient_color(self, text: str, color_type: str) -> str:
        """Apply gradient coloring to text.

        Args:
            text: Text to color.
            color_type: Color type.

        Returns:
            Text with gradient colors.
        """
        gradient_colors = self.config.gradient_colors

        # Apply gradient based on color type
        if color_type == 'border' and self.config.border_gradient:
            return self.apply_gradient(text, gradient_colors)
        elif color_type == 'text' and self.config.text_gradient:
            return self.apply_gradient(text, gradient_colors)
        elif color_type == 'placeholder':
            # Always apply dim to placeholder regardless of gradient
            return f"\033[2m{text}\033[0m"

        return text

    def _apply_standard_color(self, text: str, color_type: str) -> str:
        """Apply standard color formatting.

        Args:
            text: Text to color.
            color_type: Color type.

        Returns:
            Colored text with ANSI codes.
        """
        color_config = getattr(self.config, f'{color_type}_color', 'default')

        if color_config == 'dim':
            return f"\033[2m{text}\033[0m"
        elif color_config == 'bright':
            return f"\033[1m{text}\033[0m"
        elif color_config == 'default':
            return text
        else:
            return text

    def apply_gradient(self, text: str, gradient_colors: List[str], is_background: bool = False) -> str:
        """Apply gradient colors to text.

        Args:
            text: Text to apply gradient to.
            gradient_colors: List of hex color strings.
            is_background: Whether to apply as background colors.

        Returns:
            Text with gradient ANSI codes.
        """
        if len(gradient_colors) < 2 or len(text) == 0:
            return text

        # Convert hex colors to RGB
        rgb_colors = [self._hex_to_rgb(color) for color in gradient_colors]

        # Apply gradient character by character
        result = ""
        text_length = len(text)

        for i, char in enumerate(text):
            # Calculate position in gradient (0.0 to 1.0)
            position = i / max(1, text_length - 1)

            # Find which color segment we're in
            segment_size = 1.0 / (len(rgb_colors) - 1)
            segment_index = min(int(position / segment_size), len(rgb_colors) - 2)
            local_position = (position - segment_index * segment_size) / segment_size

            # Interpolate between colors
            color1 = rgb_colors[segment_index]
            color2 = rgb_colors[segment_index + 1]
            interpolated = self._interpolate_color(color1, color2, local_position)

            # Apply color to character
            ansi_code = self._rgb_to_ansi(*interpolated, is_background)
            result += f"{ansi_code}{char}"

        # Reset color at the end
        result += "\033[0m"
        return result

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple.

        Args:
            hex_color: Hex color string (e.g., '#1e3a8a').

        Returns:
            RGB tuple (r, g, b).
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_ansi(self, r: int, g: int, b: int, is_background: bool = False) -> str:
        """Convert RGB to ANSI escape code with automatic fallback.

        Uses true color (24-bit) when supported, otherwise falls back
        to 256-color palette.

        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
            is_background: Whether this is a background color.

        Returns:
            ANSI escape sequence.
        """
        support = get_color_support()

        if support == ColorSupport.TRUE_COLOR:
            if is_background:
                return f"\033[48;2;{r};{g};{b}m"
            else:
                return f"\033[38;2;{r};{g};{b}m"
        else:
            # Use 256-color fallback
            idx = rgb_to_256(r, g, b)
            if is_background:
                return f"\033[48;5;{idx}m"
            else:
                return f"\033[38;5;{idx}m"

    def _interpolate_color(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
        """Interpolate between two RGB colors.

        Args:
            color1: First RGB color tuple.
            color2: Second RGB color tuple.
            factor: Interpolation factor (0.0 to 1.0).

        Returns:
            Interpolated RGB tuple.
        """
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        return (r, g, b)