"""Visual effects system for terminal rendering.

This module provides comprehensive visual effects for terminal rendering,
including gradient effects, shimmer animations, color palettes,
and banner generation.
"""

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict, Any


class ColorSupport(Enum):
    """Terminal color support levels."""

    NONE = 0  # No color support
    BASIC = 1  # 16 colors (4-bit)
    EXTENDED = 2  # 256 colors (8-bit)
    TRUE_COLOR = 3  # 16 million colors (24-bit RGB)


def detect_color_support() -> ColorSupport:
    """Detect terminal color support level.

    Checks environment variables and terminal type to determine
    the maximum color depth supported.

    Returns:
        ColorSupport level for current terminal.
    """
    # Check for explicit no-color request
    if os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return ColorSupport.NONE

    # Check for explicit true color support
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        return ColorSupport.TRUE_COLOR

    # Check terminal type for known true color support
    term = os.environ.get("TERM", "").lower()
    term_program = os.environ.get("TERM_PROGRAM", "").lower()

    # Terminals known to support true color
    true_color_terms = (
        "iterm.app",
        "iterm2",
        "vscode",
        "hyper",
        "alacritty",
        "kitty",
        "wezterm",
        "rio",
    )
    if term_program in true_color_terms:
        return ColorSupport.TRUE_COLOR

    # Check TERM for true color indicators
    if "truecolor" in term or "24bit" in term or "direct" in term:
        return ColorSupport.TRUE_COLOR

    # Modern terminal emulators with 256+ color support in TERM
    if "256color" in term or "256" in term:
        return ColorSupport.EXTENDED

    # xterm and similar usually support 256 colors
    if term.startswith(("xterm", "screen", "tmux", "rxvt")):
        return ColorSupport.EXTENDED

    # Apple Terminal.app - only 256 color, NOT true color
    if term_program == "apple_terminal":
        return ColorSupport.EXTENDED

    # Basic color support for other terminals
    if term:
        return ColorSupport.BASIC

    return ColorSupport.NONE


# Global color support level - detected once at import
_COLOR_SUPPORT: ColorSupport | None = None


def get_color_support() -> ColorSupport:
    """Get cached color support level.

    Checks KOLLABOR_COLOR_MODE env var first for manual override:
      - "truecolor" or "24bit" -> TRUE_COLOR
      - "256" or "256color"    -> EXTENDED
      - "16" or "basic"        -> BASIC
      - "none" or "off"        -> NONE

    Returns:
        ColorSupport level for current terminal.
    """
    global _COLOR_SUPPORT
    if _COLOR_SUPPORT is None:
        # Check for manual override
        override = os.environ.get("KOLLABOR_COLOR_MODE", "").lower()
        if override in ("truecolor", "24bit", "true"):
            _COLOR_SUPPORT = ColorSupport.TRUE_COLOR
        elif override in ("256", "256color", "extended"):
            _COLOR_SUPPORT = ColorSupport.EXTENDED
        elif override in ("16", "basic"):
            _COLOR_SUPPORT = ColorSupport.BASIC
        elif override in ("none", "off", "no"):
            _COLOR_SUPPORT = ColorSupport.NONE
        else:
            _COLOR_SUPPORT = detect_color_support()
    return _COLOR_SUPPORT


def set_color_support(level: ColorSupport) -> None:
    """Manually set color support level.

    Args:
        level: ColorSupport level to use.
    """
    global _COLOR_SUPPORT
    _COLOR_SUPPORT = level


def reset_color_support() -> None:
    """Reset color support to re-detect on next call."""
    global _COLOR_SUPPORT
    _COLOR_SUPPORT = None


def rgb_to_256(r: int, g: int, b: int) -> int:
    """Convert RGB color to nearest 256-color palette index.

    Uses the 6x6x6 color cube (indices 16-231) for colored values,
    or grayscale ramp (indices 232-255) for near-gray colors.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        256-color palette index (0-255)
    """
    # Check if color is near grayscale
    if abs(r - g) < 10 and abs(g - b) < 10 and abs(r - b) < 10:
        # Use grayscale ramp (232-255, 24 shades)
        gray = (r + g + b) // 3
        if gray < 8:
            return 16  # black
        if gray > 248:
            return 231  # white
        return 232 + ((gray - 8) * 24) // 240

    # Use 6x6x6 color cube (indices 16-231)
    # Each component maps to 0-5
    r_idx = (r * 6) // 256
    g_idx = (g * 6) // 256
    b_idx = (b * 6) // 256
    return 16 + (36 * r_idx) + (6 * g_idx) + b_idx


def color_code(r: int, g: int, b: int, bold: bool = False, dim: bool = False) -> str:
    """Generate a foreground color escape code with automatic fallback.

    Uses true color (24-bit) when supported, otherwise falls back
    to 256-color palette.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)
        bold: Add bold attribute
        dim: Add dim attribute

    Returns:
        ANSI escape sequence for the color.
    """
    prefix = ""
    if bold:
        prefix = "\033[1m"
    elif dim:
        prefix = "\033[2m"

    if get_color_support() == ColorSupport.TRUE_COLOR:
        return f"{prefix}\033[38;2;{r};{g};{b}m"
    else:
        idx = rgb_to_256(r, g, b)
        return f"{prefix}\033[38;5;{idx}m"


class EffectType(Enum):
    """Types of visual effects."""

    GRADIENT = "gradient"
    SHIMMER = "shimmer"
    DIM = "dim"
    ANIMATION = "animation"
    COLOR = "color"


@dataclass
class EffectConfig:
    """Configuration for visual effects."""

    effect_type: EffectType
    enabled: bool = True
    intensity: float = 1.0
    speed: int = 3
    width: int = 4
    colors: List[str] = field(default_factory=list)


# Color definitions as (r, g, b, modifier) tuples
# modifier: None=normal, 'bold'=bright, 'dim'=dim
_COLOR_DEFINITIONS = {
    # Basic colors
    "WHITE": (220, 220, 220, None),
    "BRIGHT_WHITE": (255, 255, 255, "bold"),
    "BLACK": (0, 0, 0, None),
    # Red variants
    "DIM_RED": (205, 49, 49, "dim"),
    "RED": (205, 49, 49, None),
    "BRIGHT_RED": (241, 76, 76, "bold"),
    # Green variants
    "DIM_GREEN": (13, 188, 121, "dim"),
    "GREEN": (13, 188, 121, None),
    "BRIGHT_GREEN": (35, 209, 139, "bold"),
    # Yellow variants
    "DIM_YELLOW": (229, 192, 123, "dim"),
    "YELLOW": (229, 192, 123, None),
    "BRIGHT_YELLOW": (245, 223, 77, "bold"),
    # Blue variants
    "DIM_BLUE": (36, 114, 200, "dim"),
    "BLUE": (36, 114, 200, None),
    "BRIGHT_BLUE": (59, 142, 234, "bold"),
    "NORMAL_BLUE": (100, 149, 237, None),
    # Magenta variants
    "DIM_MAGENTA": (188, 63, 188, "dim"),
    "MAGENTA": (188, 63, 188, None),
    "BRIGHT_MAGENTA": (214, 112, 214, "bold"),
    # Cyan variants
    "DIM_CYAN": (17, 168, 205, "dim"),
    "CYAN": (17, 168, 205, None),
    "BRIGHT_CYAN": (41, 184, 219, "bold"),
    # Grey variants
    "DIM_GREY": (128, 128, 128, "dim"),
    "GREY": (128, 128, 128, None),
    "BRIGHT_GREY": (169, 169, 169, "bold"),
    # Extended bright colors
    "BRIGHT_CYAN_256": (0, 255, 255, "bold"),
    "BRIGHT_BLUE_256": (94, 156, 255, "bold"),
    "BRIGHT_GREEN_256": (90, 247, 142, "bold"),
    "BRIGHT_YELLOW_256": (255, 231, 76, "bold"),
    "BRIGHT_MAGENTA_256": (255, 92, 205, "bold"),
    "BRIGHT_RED_256": (255, 85, 85, "bold"),
    # Neon Minimal Palette - Lime
    "LIME": (163, 230, 53, None),
    "BRIGHT_LIME": (163, 230, 53, "bold"),
    "LIME_LIGHT": (190, 242, 100, None),
    "LIME_DARK": (132, 204, 22, None),
    # Info: Cyan
    "INFO_CYAN": (6, 182, 212, None),
    "INFO_CYAN_LIGHT": (34, 211, 238, None),
    "INFO_CYAN_DARK": (8, 145, 178, None),
    # Warning: Gold
    "WARNING_GOLD": (234, 179, 8, None),
    "WARNING_GOLD_LIGHT": (253, 224, 71, None),
    "WARNING_GOLD_DARK": (202, 138, 4, None),
    # Error: Red
    "ERROR_RED": (239, 68, 68, None),
    "ERROR_RED_LIGHT": (248, 113, 113, None),
    "ERROR_RED_DARK": (220, 38, 38, None),
    # Muted: Steel
    "MUTED_STEEL": (113, 113, 122, None),
    "DIM_STEEL": (113, 113, 122, "dim"),
}


def _make_color_code(r: int, g: int, b: int, modifier: str | None = None) -> str:
    """Generate escape code for a color with automatic fallback.

    Args:
        r, g, b: RGB components (0-255)
        modifier: 'bold', 'dim', or None

    Returns:
        ANSI escape sequence appropriate for terminal capability.
    """
    prefix = ""
    if modifier == "bold":
        prefix = "\033[1m"
    elif modifier == "dim":
        prefix = "\033[2m"

    support = get_color_support()

    if support == ColorSupport.NONE:
        return prefix if prefix else ""

    if support == ColorSupport.TRUE_COLOR:
        return f"{prefix}\033[38;2;{r};{g};{b}m"
    else:
        # Use 256-color fallback
        idx = rgb_to_256(r, g, b)
        return f"{prefix}\033[38;5;{idx}m"


class _ColorPaletteMeta(type):
    """Metaclass that generates color codes dynamically based on terminal support."""

    def __getattr__(cls, name: str) -> str:
        if name in _COLOR_DEFINITIONS:
            r, g, b, modifier = _COLOR_DEFINITIONS[name]
            return _make_color_code(r, g, b, modifier)
        raise AttributeError(f"ColorPalette has no color '{name}'")


class ColorPalette(metaclass=_ColorPaletteMeta):
    """Color palette with automatic terminal capability detection.

    Colors are generated dynamically based on terminal support:
    - TRUE_COLOR: Uses 24-bit RGB escape codes
    - EXTENDED: Falls back to 256-color palette
    - BASIC: Uses 16-color approximations
    - NONE: Returns empty strings or just modifiers
    """

    # Standard modifiers (not affected by color support)
    RESET = "\033[0m"
    DIM = "\033[2m"
    BRIGHT = "\033[1m"

    # Grey gradient levels (256-color palette indices)
    GREY_LEVELS = [255, 254, 253, 252, 251, 250]

    # Dim white gradient levels (bright white to subtle dim white)
    DIM_WHITE_LEVELS = [255, 254, 253, 252, 251, 250]

    # Lime green gradient scheme RGB values for ultra-smooth gradients
    DIM_SCHEME_COLORS = [
        (190, 242, 100),  # Bright lime (#bef264)
        (175, 235, 80),   # Light lime
        (163, 230, 53),   # Primary lime (#a3e635) - hero color!
        (145, 210, 45),   # Medium lime
        (132, 204, 22),   # Darker lime (#84cc16)
        (115, 180, 18),   # Deep lime
        (100, 160, 15),   # Strong lime
        (115, 180, 18),   # Deep lime (return)
        (132, 204, 22),   # Darker lime (return)
        (163, 230, 53),   # Primary lime (return)
        (190, 242, 100),  # Bright lime
    ]


# Powerline separator characters
class Powerline:
    """Powerline/Agnoster style separator characters."""

    # Solid arrows
    RIGHT = "\ue0b0"  #
    LEFT = "\ue0b2"   #

    # Thin arrows (for sub-segments)
    RIGHT_THIN = "\ue0b1"  #
    LEFT_THIN = "\ue0b3"   #

    # Rounded
    RIGHT_ROUND = "\ue0b4"  #
    LEFT_ROUND = "\ue0b6"   #

    # Flame/fire style
    RIGHT_FLAME = "\ue0c0"  #
    LEFT_FLAME = "\ue0c2"   #

    # Pixelated
    RIGHT_PIXEL = "\ue0c4"  #
    LEFT_PIXEL = "\ue0c6"   #

    # Ice/diagonal
    RIGHT_ICE = "\ue0c8"    #
    LEFT_ICE = "\ue0ca"     #


def make_bg_color(r: int, g: int, b: int) -> str:
    """Create background color escape code.

    Args:
        r, g, b: RGB values (0-255).

    Returns:
        ANSI escape code for background color.
    """
    support = get_color_support()

    if support == ColorSupport.NONE:
        return ""

    if support == ColorSupport.TRUE_COLOR:
        return f"\033[48;2;{r};{g};{b}m"
    else:
        # Use 256-color fallback
        idx = rgb_to_256(r, g, b)
        return f"\033[48;5;{idx}m"


def make_fg_color(r: int, g: int, b: int) -> str:
    """Create foreground color escape code.

    Args:
        r, g, b: RGB values (0-255).

    Returns:
        ANSI escape code for foreground color.
    """
    support = get_color_support()

    if support == ColorSupport.NONE:
        return ""

    if support == ColorSupport.TRUE_COLOR:
        return f"\033[38;2;{r};{g};{b}m"
    else:
        idx = rgb_to_256(r, g, b)
        return f"\033[38;5;{idx}m"


class AgnosterColors:
    """Signature color scheme for agnoster segments - lime and cyan."""

    # Lime palette (RGB tuples)
    LIME = (163, 230, 53)
    LIME_DARK = (132, 204, 22)
    LIME_DARKER = (100, 160, 15)

    # Cyan palette
    CYAN = (6, 182, 212)
    CYAN_DARK = (8, 145, 178)
    CYAN_LIGHT = (34, 211, 238)

    # Neutral backgrounds
    BG_DARK = (30, 30, 30)
    BG_MID = (50, 50, 50)
    BG_LIGHT = (70, 70, 70)

    # Text colors
    TEXT_DARK = (20, 20, 20)
    TEXT_LIGHT = (240, 240, 240)


class AgnosterSegment:
    """Builder for powerline/agnoster style segments."""

    def __init__(self):
        """Initialize empty segment list."""
        self.segments: List[Tuple[Tuple[int, int, int], Tuple[int, int, int], str]] = []

    def add(
        self,
        text: str,
        bg: Tuple[int, int, int],
        fg: Tuple[int, int, int] = AgnosterColors.TEXT_DARK
    ) -> "AgnosterSegment":
        """Add a segment.

        Args:
            text: Segment text content.
            bg: Background color RGB tuple.
            fg: Foreground (text) color RGB tuple.

        Returns:
            Self for chaining.
        """
        self.segments.append((bg, fg, text))
        return self

    def add_lime(self, text: str, variant: str = "normal") -> "AgnosterSegment":
        """Add a lime-colored segment.

        Args:
            text: Segment text.
            variant: "normal", "dark", or "darker".

        Returns:
            Self for chaining.
        """
        bg_map = {
            "normal": AgnosterColors.LIME,
            "dark": AgnosterColors.LIME_DARK,
            "darker": AgnosterColors.LIME_DARKER,
        }
        return self.add(text, bg_map.get(variant, AgnosterColors.LIME))

    def add_cyan(self, text: str, variant: str = "normal") -> "AgnosterSegment":
        """Add a cyan-colored segment.

        Args:
            text: Segment text.
            variant: "normal", "dark", or "light".

        Returns:
            Self for chaining.
        """
        bg_map = {
            "normal": AgnosterColors.CYAN,
            "dark": AgnosterColors.CYAN_DARK,
            "light": AgnosterColors.CYAN_LIGHT,
        }
        return self.add(text, bg_map.get(variant, AgnosterColors.CYAN))

    def add_neutral(self, text: str, variant: str = "mid") -> "AgnosterSegment":
        """Add a neutral gray segment.

        Args:
            text: Segment text.
            variant: "dark", "mid", or "light".

        Returns:
            Self for chaining.
        """
        bg_map = {
            "dark": AgnosterColors.BG_DARK,
            "mid": AgnosterColors.BG_MID,
            "light": AgnosterColors.BG_LIGHT,
        }
        fg = AgnosterColors.TEXT_LIGHT
        return self.add(text, bg_map.get(variant, AgnosterColors.BG_MID), fg)

    def render(self, separator: str = Powerline.RIGHT) -> str:
        """Render all segments with powerline separators.

        Args:
            separator: Powerline separator character to use.

        Returns:
            Fully formatted powerline string.
        """
        if not self.segments:
            return ""

        result = []
        reset = ColorPalette.RESET

        for i, (bg, fg, text) in enumerate(self.segments):
            bg_code = make_bg_color(*bg)
            fg_code = make_fg_color(*fg)

            # Segment content with padding
            result.append(f"{bg_code}{fg_code} {text} ")

            # Add separator (arrow colored: fg=current_bg, bg=next_bg or transparent)
            if i < len(self.segments) - 1:
                next_bg = self.segments[i + 1][0]
                sep_fg = make_fg_color(*bg)  # Arrow color = current segment bg
                sep_bg = make_bg_color(*next_bg)  # Arrow bg = next segment bg
                result.append(f"{sep_bg}{sep_fg}{separator}")
            else:
                # Last segment - arrow fades to transparent
                sep_fg = make_fg_color(*bg)
                result.append(f"{reset}{sep_fg}{separator}{reset}")

        return "".join(result)

    def render_minimal(self) -> str:
        """Render segments with thin separators (less prominent).

        Returns:
            Formatted string with thin separators.
        """
        return self.render(Powerline.RIGHT_THIN)


class GradientRenderer:
    """Handles various gradient effects."""

    @staticmethod
    def apply_white_to_grey(text: str) -> str:
        """Apply smooth white-to-grey gradient effect.

        Args:
            text: Text to apply gradient to.

        Returns:
            Text with gradient effect applied.
        """
        if not text or "\033[" in text:
            return text

        result = []
        text_length = len(text)
        grey_levels = ColorPalette.GREY_LEVELS

        for i, char in enumerate(text):
            # Calculate position in gradient (0.0 to 1.0)
            position = i / max(1, text_length - 1)

            # Map to grey level with smooth interpolation
            level_index = position * (len(grey_levels) - 1)
            level_index = min(int(level_index), len(grey_levels) - 1)

            grey_level = grey_levels[level_index]
            color_code = f"\033[38;5;{grey_level}m"
            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)

    @staticmethod
    def apply_dim_white_gradient(text: str) -> str:
        """Apply subtle dim white to dimmer white gradient.

        Args:
            text: Text to apply gradient to.

        Returns:
            Text with dim white gradient applied.
        """
        if not text or "\033[" in text:
            return text

        result = []
        text_length = len(text)
        dim_levels = ColorPalette.DIM_WHITE_LEVELS

        for i, char in enumerate(text):
            # Calculate position in gradient (0.0 to 1.0)
            position = i / max(1, text_length - 1)

            # Map to dim white level with smooth interpolation
            level_index = position * (len(dim_levels) - 1)
            level_index = min(int(level_index), len(dim_levels) - 1)

            dim_level = dim_levels[level_index]
            color_code = f"\033[38;5;{dim_level}m"
            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)

    @staticmethod
    def apply_dim_scheme_gradient(text: str) -> str:
        """Apply ultra-smooth gradient using dim color scheme.

        Automatically uses 256-color fallback when true color
        is not supported by the terminal.

        Args:
            text: Text to apply gradient to.

        Returns:
            Text with dim scheme gradient applied.
        """
        if not text:
            return text

        result = []
        text_length = len(text)
        color_rgb = ColorPalette.DIM_SCHEME_COLORS
        use_true_color = get_color_support() == ColorSupport.TRUE_COLOR

        for i, char in enumerate(text):
            position = i / max(1, text_length - 1)
            scaled_pos = position * (len(color_rgb) - 1)
            color_index = int(scaled_pos)
            t = scaled_pos - color_index

            if color_index >= len(color_rgb) - 1:
                r, g, b = color_rgb[-1]
            else:
                curr_rgb = color_rgb[color_index]
                next_rgb = color_rgb[color_index + 1]

                r = curr_rgb[0] + (next_rgb[0] - curr_rgb[0]) * t
                g = curr_rgb[1] + (next_rgb[1] - curr_rgb[1]) * t
                b = curr_rgb[2] + (next_rgb[2] - curr_rgb[2]) * t

            r, g, b = int(r), int(g), int(b)

            if use_true_color:
                color_code = f"\033[38;2;{r};{g};{b}m"
            else:
                # Fallback to 256-color palette
                color_idx = rgb_to_256(r, g, b)
                color_code = f"\033[38;5;{color_idx}m"

            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)

    @staticmethod
    def apply_custom_gradient(text: str, colors: List[Tuple[int, int, int]]) -> str:
        """Apply custom RGB gradient to text.

        Automatically uses 256-color fallback when true color
        is not supported by the terminal.

        Args:
            text: Text to apply gradient to.
            colors: List of RGB color tuples for gradient stops.

        Returns:
            Text with custom gradient applied.
        """
        if not text or len(colors) < 2:
            return text

        result = []
        text_length = len(text)
        use_true_color = get_color_support() == ColorSupport.TRUE_COLOR

        for i, char in enumerate(text):
            position = i / max(1, text_length - 1)
            scaled_pos = position * (len(colors) - 1)
            color_index = int(scaled_pos)
            t = scaled_pos - color_index

            if color_index >= len(colors) - 1:
                r, g, b = colors[-1]
            else:
                curr_rgb = colors[color_index]
                next_rgb = colors[color_index + 1]

                r = curr_rgb[0] + (next_rgb[0] - curr_rgb[0]) * t
                g = curr_rgb[1] + (next_rgb[1] - curr_rgb[1]) * t
                b = curr_rgb[2] + (next_rgb[2] - curr_rgb[2]) * t

            r, g, b = int(r), int(g), int(b)

            if use_true_color:
                color_code = f"\033[38;2;{r};{g};{b}m"
            else:
                # Fallback to 256-color palette
                color_idx = rgb_to_256(r, g, b)
                color_code = f"\033[38;5;{color_idx}m"

            result.append(f"{color_code}{char}")

        result.append(ColorPalette.RESET)
        return "".join(result)


class ShimmerEffect:
    """Handles shimmer animation effects."""

    def __init__(self, speed: int = 3, wave_width: int = 4):
        """Initialize shimmer effect.

        Args:
            speed: Animation speed (frames between updates).
            wave_width: Width of shimmer wave in characters.
        """
        self.speed = speed
        self.wave_width = wave_width
        self.frame_counter = 0
        self.position = 0

    def configure(self, speed: int, wave_width: int) -> None:
        """Configure shimmer parameters.

        Args:
            speed: Animation speed.
            wave_width: Wave width.
        """
        self.speed = speed
        self.wave_width = wave_width

    def apply_shimmer(self, text: str) -> str:
        """Apply elegant wave shimmer effect to text.

        Args:
            text: Text to apply shimmer to.

        Returns:
            Text with shimmer effect applied.
        """
        if not text:
            return text

        # Update shimmer position
        self.frame_counter = (self.frame_counter + 1) % self.speed
        if self.frame_counter == 0:
            self.position = (self.position + 1) % (len(text) + self.wave_width * 2)

        result = []
        for i, char in enumerate(text):
            distance = abs(i - self.position)

            if distance == 0:
                # Center - bright cyan
                result.append(
                    f"{ColorPalette.BRIGHT_CYAN}{char}{ColorPalette.RESET}"
                )
            elif distance == 1:
                # Adjacent - bright blue
                result.append(
                    f"{ColorPalette.BRIGHT_BLUE}{char}{ColorPalette.RESET}"
                )
            elif distance == 2:
                # Second ring - normal blue
                result.append(
                    f"{ColorPalette.NORMAL_BLUE}{char}{ColorPalette.RESET}"
                )
            elif distance <= self.wave_width:
                # Edge - dim blue
                result.append(f"{ColorPalette.DIM_BLUE}{char}{ColorPalette.RESET}")
            else:
                # Base - darker dim blue
                result.append(f"\033[2;94m{char}{ColorPalette.RESET}")

        return "".join(result)


class StatusColorizer:
    """Handles semantic coloring of status text with ASCII icons."""

    # ASCII icon mapping (no emojis)
    ASCII_ICONS = {
        "checkmark": "√",
        "error": "×",
        "processing": "*",
        "active": "+",
        "inactive": "-",
        "ratio": "::",
        "arrow_right": ">",
        "separator": "|",
        "loading": "...",
        "count": "#",
        "circle_filled": "●",
        "circle_empty": "○",
        "circle_dot": "•",
    }

    @staticmethod
    def get_ascii_icon(icon_type: str) -> str:
        """Get ASCII icon by type.

        Args:
            icon_type: Type of icon to retrieve.

        Returns:
            ASCII character for the icon.
        """
        return StatusColorizer.ASCII_ICONS.get(icon_type, "")

    @staticmethod
    def apply_status_colors(text: str) -> str:
        """Apply semantic colors to status line text with ASCII icons.

        Args:
            text: Status text to colorize.

        Returns:
            Colorized text with ANSI codes and ASCII icons.
        """
        # Replace emoji-style indicators with ASCII equivalents
        text = text.replace(
            "🟢",
            f"{ColorPalette.BRIGHT_GREEN}"
            f"{StatusColorizer.ASCII_ICONS['circle_filled']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "🟡",
            f"{ColorPalette.DIM_YELLOW}"
            f"{StatusColorizer.ASCII_ICONS['circle_filled']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "🔴",
            f"{ColorPalette.DIM_RED}"
            f"{StatusColorizer.ASCII_ICONS['circle_filled']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "✅",
            f"{ColorPalette.BRIGHT_GREEN}"
            f"{StatusColorizer.ASCII_ICONS['checkmark']}"
            f"{ColorPalette.RESET}",
        )
        text = text.replace(
            "❌",
            f"{ColorPalette.DIM_RED}"
            f"{StatusColorizer.ASCII_ICONS['error']}"
            f"{ColorPalette.RESET}",
        )

        # Number/count highlighting (dim cyan for metrics)
        text = re.sub(
            r"\b(\d{1,3}(?:,\d{3})*)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )

        # ASCII icon patterns
        text = re.sub(
            r"\b(✓)\s*",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET} ",
            text,
        )  # Checkmarks
        text = re.sub(
            r"\b(×)\s*",
            f"{ColorPalette.DIM_RED}\\1{ColorPalette.RESET} ",
            text,
        )  # Errors
        text = re.sub(
            r"\b(\*)\s*",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET} ",
            text,
        )  # Processing
        text = re.sub(
            r"\b(\+)\s*",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET} ",
            text,
        )  # Active
        text = re.sub(
            r"(^|\s)(-)\s+",
            f"\\1{ColorPalette.DIM_CYAN}\\2{ColorPalette.RESET} ",
            text,
        )  # Inactive (list markers only)

        # Status indicators
        text = re.sub(
            r"\b(Processing: Yes)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Processing: No)\b",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Ready)\b",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Active)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(On)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Off)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )

        # Queue states
        text = re.sub(
            r"\b(Queue: 0)\b",
            f"{ColorPalette.BRIGHT_GREEN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Queue: [1-9][0-9]*)\b",
            f"{ColorPalette.DIM_YELLOW}\\1{ColorPalette.RESET}",
            text,
        )

        # Time measurements
        text = re.sub(
            r"\b(\d+\.\d+s)\b",
            f"{ColorPalette.DIM_MAGENTA}\\1{ColorPalette.RESET}",
            text,
        )

        # Ratio highlighting (with :: separator)
        text = re.sub(
            r"\b(\d+):(\d+)\b",
            f"{ColorPalette.DIM_BLUE}\\1{ColorPalette.DIM_CYAN}::"
            f"{ColorPalette.DIM_BLUE}\\2{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(Enhanced: \d+/\d+)",
            f"{ColorPalette.DIM_BLUE}\\1{ColorPalette.RESET}",
            text,
        )

        # Percentage highlighting
        text = re.sub(
            r"\b(\d+\.\d+%)\b",
            f"{ColorPalette.DIM_MAGENTA}\\1{ColorPalette.RESET}",
            text,
        )

        # Token highlighting
        text = re.sub(
            r"\b(\d+\s*tok)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )
        text = re.sub(
            r"\b(\d+K\s*tok)\b",
            f"{ColorPalette.DIM_CYAN}\\1{ColorPalette.RESET}",
            text,
        )

        return text


class BannerRenderer:
    """Handles ASCII banner creation and rendering."""

    KOLLABOR_ASCII2 = [
        "██╗  ██╗ ██████╗ ██╗     ██╗      █████╗ ██████╗  ██████╗ ██████╗ ",
        "██║ ██╔╝██╔═══██╗██║     ██║     ██╔══██╗██╔══██╗██╔═══██╗██╔══██╗",
        "█████╔╝ ██║   ██║██║     ██║     ███████║██████╔╝██║   ██║██████╔╝",
        "██╔═██╗ ██║   ██║██║     ██║     ██╔══██║██╔══██╗██║   ██║██╔══██╗",
        "██║  ██╗╚██████╔╝███████╗███████╗██║  ██║██████╔╝╚██████╔╝██║  ██║",
        "╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝",
    ]

    KOLLABOR_ASCII_v1 = [
        "▒█░▄▀ █▀▀█ █░░ █░░ █▀▀█ █▀▀▄ █▀▀█ █▀▀█   █▀▀█ ▀█▀",
        "▒█▀▄░ █░░█ █░░ █░░ █▄▄█ █▀▀▄ █░░█ █▄▄▀   █▄▄█ ░█░",
        "▒█░▒█ ▀▀▀▀ ▀▀▀ ▀▀▀ ▀░░▀ ▀▀▀░ ▀▀▀▀ ▀░▀▀ ▄ ▀░░▀ ▄█▄",
    ]
    KOLLABOR_ASCII_v2 = [
        "\r ──────────────────────────────────────────────── ",
        "\r █ ▄▀ █▀▀█ █   █   █▀▀█ █▀▀▄ █▀▀█ █▀▀█   █▀▀█ ▀█▀  ",
        "\r █▀▄  █  █ █   █   █▄▄█ █▀▀▄ █  █ █▄▄▀   █▄▄█  █   ",
        "\r ▀  ▀ ▀▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀  ▀▀▀▀ ▀ ▀▀ ▀ ▀  ▀ ▀▀▀  ",
        "\r ──────────────────────────────────────────────── ",
    ]
    KOLLABOR_ASCII2 = [
        "\r  ██╗  ██╔════════════════════════════════════════════╗",
        "\r  ██║ ██╔╝                                            ║",
        "\r  █████╔╝ █▀▀█ █   █   █▀▀█ █▀▀▄ █▀▀█ █▀▀█   █▀▀█ ▀█▀ ║",
        "\r  ██╔═██╗ █  █ █   █   █▄▄█ █▀▀▄ █  █ █▄▄▀   █▄▄█  █  ║",
        "\r  ██║  ██╗▀▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀  ▀▀▀▀ ▀ ▀▀ ▀ ▀  ▀ ▀▀▀ ║",
        "\r  ╚═╝  ╚═╩════════════════════════════════════════════╝",
    ] 
    KOLLABOR_ASCII3 = [
        "\r ┌──────────────────────────────────────────────────┐",
        "\r │ ▄█─●─●─█▄  █ ▄▀ █▀▀█ █   █   █▀▀█ █▀▀▄ █▀▀█ █▀▀█ │",
        "\r │ ██ │ │ ██  █▀▄  █  █ █   █   █▄▄█ █▀▀▄ █  █ █▄▄▀ │",
        "\r │ ●──███──●  ▀  ▀ ▀▀▀▀ ▀▀▀ ▀▀▀ ▀  ▀ ▀▀▀  ▀▀▀▀ ▀ ▀▀ │",
        "\r │ ██ │ │ ██      Collaborative Intelligence        │",
        "\r │ ▀█─●─●─█▀                                        │",
        "\r └──────────────────────────────────────────────────┘",
    ]
    
    KOLLABOR_ASCII = [
        "\r ╭──────────────────────────────────────────────────╮",
        "\r │ ▄█─●─●─█▄  █ ▄▀ █▀▀█ █   █   █▀▀█ █▀▀▄ █▀▀█ █▀▀█ │",
        "\r │ ●──███──●  █▀▄  █  █ █   █   █▄▄█ █▀▀▄ █  █ █▄▄▀ │",
        "\r │ ▀█─●─●─█▀  █  █ █▄▄█ █▄▄ █▄▄ █  █ █▄▄▀ █▄▄█ █ █▄ │",
        "\r ╰──────────────────────────────────────────────────╯",
    ]

    @classmethod
    def create_kollabor_banner(cls, version: str = "v1.0.0") -> str:
        """Create beautiful Kollabor ASCII banner with gradient.

        Args:
            version: Version string to display.

        Returns:
            Formatted banner with gradient colors and version.
        """
        gradient_lines = []
        for i, line in enumerate(cls.KOLLABOR_ASCII):
            gradient_line = GradientRenderer.apply_dim_scheme_gradient(line)

            # Add version to first line
            if i == 0:
                gradient_line += f" {ColorPalette.DIM}{version}{ColorPalette.RESET}"

            gradient_lines.append(gradient_line)

        return f"\n{chr(10).join(gradient_lines)}\n"


class VisualEffects:
    """Main visual effects coordinator."""

    def __init__(self):
        """Initialize visual effects system."""
        self.gradient_renderer = GradientRenderer()
        self.shimmer_effect = ShimmerEffect()
        self.status_colorizer = StatusColorizer()
        self.banner_renderer = BannerRenderer()

        # Effect configurations
        self._effects_config: Dict[str, EffectConfig] = {
            "thinking": EffectConfig(EffectType.SHIMMER, speed=3, width=4),
            "gradient": EffectConfig(EffectType.GRADIENT),
            "status": EffectConfig(EffectType.COLOR),
            "banner": EffectConfig(EffectType.GRADIENT),
        }

    def configure_effect(self, effect_name: str, **kwargs) -> None:
        """Configure a specific effect.

        Args:
            effect_name: Name of effect to configure.
            **kwargs: Configuration parameters.
        """
        if effect_name in self._effects_config:
            config = self._effects_config[effect_name]
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        # Special handling for shimmer effect
        if effect_name == "thinking":
            self.shimmer_effect.configure(
                kwargs.get("speed", 3), kwargs.get("width", 4)
            )

    def apply_thinking_effect(self, text: str, effect_type: str = "shimmer") -> str:
        """Apply thinking visualization effect.

        Args:
            text: Text to apply effect to.
            effect_type: Type of effect ("shimmer", "dim", "normal").

        Returns:
            Text with thinking effect applied.
        """
        config = self._effects_config.get("thinking")
        if not config or not config.enabled:
            return text

        if effect_type == "shimmer":
            return self.shimmer_effect.apply_shimmer(text)
        elif effect_type == "dim":
            return f"{ColorPalette.DIM}{text}{ColorPalette.RESET}"
        else:
            return text

    def apply_message_gradient(
        self, text: str, gradient_type: str = "dim_white"
    ) -> str:
        """Apply gradient effect to message text.

        Args:
            text: Text to apply gradient to.
            gradient_type: Type of gradient to apply.

        Returns:
            Text with gradient applied.
        """
        config = self._effects_config.get("gradient")
        if not config or not config.enabled:
            return text

        if gradient_type == "white_to_grey":
            return self.gradient_renderer.apply_white_to_grey(text)
        elif gradient_type == "dim_white":
            return self.gradient_renderer.apply_dim_white_gradient(text)
        elif gradient_type == "dim_scheme":
            return self.gradient_renderer.apply_dim_scheme_gradient(text)
        else:
            return text

    def apply_status_colors(self, text: str) -> str:
        """Apply status colors to text.

        Args:
            text: Text to colorize.

        Returns:
            Colorized text.
        """
        config = self._effects_config.get("status")
        if not config or not config.enabled:
            return text

        return self.status_colorizer.apply_status_colors(text)

    def create_banner(self, version: str = "v1.0.0") -> str:
        """Create application banner.

        Args:
            version: Version string.

        Returns:
            Formatted banner.
        """
        config = self._effects_config.get("banner")
        if not config or not config.enabled:
            return f"KOLLABOR {version}\n"

        return self.banner_renderer.create_kollabor_banner(version)

    def get_effect_stats(self) -> Dict[str, Any]:
        """Get visual effects statistics.

        Returns:
            Dictionary with effect statistics.
        """
        return {
            "shimmer_position": self.shimmer_effect.position,
            "shimmer_frame_counter": self.shimmer_effect.frame_counter,
            "effects_config": {
                name: {
                    "enabled": config.enabled,
                    "type": getattr(config.effect_type, "value", config.effect_type),
                    "intensity": config.intensity,
                }
                for name, config in self._effects_config.items()
            },
        }
