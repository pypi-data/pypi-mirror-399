"""Box drawing styles for enhanced input plugin."""

import random
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class BoxStyle:
    """Represents a box drawing style with all character components."""

    top_left: str
    top_right: str
    bottom_left: str
    bottom_right: str
    horizontal: str
    vertical: str


class BoxStyleRegistry:
    """Registry for managing and providing box drawing styles."""

    def __init__(self):
        """Initialize the registry with all available styles."""
        self._styles = self._build_styles()
        self._curated_random_styles = [
            # User's confirmed favorites
            "dots_only", "brackets", "dotted", "dashed", "square",
            # Clean classics
            "rounded", "double", "thick", "underline", "minimal",
            # Sophisticated mixed-weight styles
            "mixed_weight", "typography", "sophisticated", "editorial",
            "clean_corners", "refined", "gradient_line",
            # Clean minimal lines
            "lines_only", "thick_lines", "double_lines"
        ]

    def get_style(self, name: str) -> BoxStyle:
        """Get a style by name.

        Args:
            name: Style name.

        Returns:
            BoxStyle object.

        Raises:
            KeyError: If style doesn't exist.
        """
        if name not in self._styles:
            raise KeyError(f"Unknown box style: {name}")
        return self._styles[name]

    def get_random_style(self) -> BoxStyle:
        """Get a random style from curated collection.

        Returns:
            Random BoxStyle object.
        """
        style_name = random.choice(self._curated_random_styles)
        return self.get_style(style_name)

    def get_random_style_name(self) -> str:
        """Get a random style name from curated collection.

        Returns:
            Random style name.
        """
        return random.choice(self._curated_random_styles)

    def list_styles(self) -> List[str]:
        """Get list of all available style names.

        Returns:
            List of style names.
        """
        return list(self._styles.keys())

    def register_style(self, name: str, style: BoxStyle) -> None:
        """Register a new style.

        Args:
            name: Style name.
            style: BoxStyle object.
        """
        self._styles[name] = style

    def _build_styles(self) -> Dict[str, BoxStyle]:
        """Build the complete styles dictionary.

        Returns:
            Dictionary of all box styles.
        """
        return {
            # Classic box styles
            "rounded": BoxStyle("╭", "╮", "╰", "╯", "─", "│"),
            "square": BoxStyle("┌", "┐", "└", "┘", "─", "│"),
            "double": BoxStyle("╔", "╗", "╚", "╝", "═", "║"),
            "thick": BoxStyle("┏", "┓", "┗", "┛", "━", "┃"),
            "dotted": BoxStyle("┌", "┐", "└", "┘", "┄", "┆"),
            "dashed": BoxStyle("┌", "┐", "└", "┘", "┅", "┇"),
            "thin": BoxStyle("┌", "┐", "└", "┘", "─", ""),

            # Minimal styles
            "minimal": BoxStyle(" ", " ", " ", " ", "─", " "),
            "brackets": BoxStyle("⌜", "⌝", "⌞", "⌟", " ", " "),
            "underline": BoxStyle("", "", "", "", "_", ""),

            # Line-only styles
            "lines_only": BoxStyle("", "", "", "", "─", ""),
            "thick_lines": BoxStyle("", "", "", "", "━", ""),
            "double_lines": BoxStyle("", "", "", "", "═", ""),
            "dots_only": BoxStyle("", "", "", "", "┄", ""),
            "gradient_line": BoxStyle("", "", "", "", "▁", ""),

            # Decorative styles
            "stars": BoxStyle("★", "★", "★", "★", "✦", "✧"),
            "arrows": BoxStyle("↖", "↗", "↙", "↘", "→", "↕"),
            "diamonds": BoxStyle("◆", "◆", "◆", "◆", "◇", "◈"),
            "circles": BoxStyle("●", "●", "●", "●", "○", "◐"),
            "waves": BoxStyle("~", "~", "~", "~", "≈", "∿"),

            # Mixed weight styles
            "mixed_weight": BoxStyle("┏", "┓", "┗", "┛", "┄", "│"),
            "typography": BoxStyle("┌", "┐", "└", "┘", "━", "┆"),
            "sophisticated": BoxStyle("╭", "╮", "╰", "╯", "━", "┆"),
            "editorial": BoxStyle("┌", "┐", "└", "┘", "─", ""),
            "clean_corners": BoxStyle("┌", "┐", "└", "┘", "", ""),
            "refined": BoxStyle("╭", "╮", "╰", "╯", "", ""),

            # Futuristic styles
            "neon": BoxStyle("▓", "▓", "▓", "▓", "▔", "▐"),
            "cyber": BoxStyle("◢", "◣", "◥", "◤", "▬", "▌"),
            "matrix": BoxStyle("╔", "╗", "╚", "╝", "▓", "▓"),
            "holo": BoxStyle("◊", "◊", "◊", "◊", "◈", "◈"),
            "quantum": BoxStyle("⟨", "⟩", "⟨", "⟩", "⟷", "⟁"),
            "neural": BoxStyle("⊙", "⊙", "⊙", "⊙", "⊚", "⊜"),
            "plasma": BoxStyle("◬", "◭", "◪", "◫", "◯", "◎"),
            "circuit": BoxStyle("┫", "┣", "┳", "┻", "╋", "╂"),
            "laser": BoxStyle("", "", "", "", "▇", ""),
            "scan": BoxStyle("", "", "", "", "▓", ""),
            "energy": BoxStyle("", "", "", "", "-", ""),
        }