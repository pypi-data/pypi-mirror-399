"""Status modal rendering component.

Responsible for generating formatted lines for status modal display.
This is a pure rendering component with no state management.
"""

import logging
from typing import List, Any

logger = logging.getLogger(__name__)


class StatusModalRenderer:
    """Renders status modal content with borders and styling.

    This component handles the visual presentation of status modals,
    including box borders, content formatting, and optional styling
    when the enhanced input plugin is available.

    Attributes:
        renderer: Terminal renderer for accessing terminal state.
    """

    def __init__(self, renderer: Any) -> None:
        """Initialize the status modal renderer.

        Args:
            renderer: Terminal renderer instance for accessing terminal state.
        """
        self.renderer = renderer

    def generate_status_modal_lines(self, ui_config: Any) -> List[str]:
        """Generate formatted lines for status modal display using visual effects.

        Args:
            ui_config: UI configuration for the status modal.

        Returns:
            List of formatted lines for display.
        """
        try:
            # Get dynamic terminal width
            terminal_width = getattr(self.renderer.terminal_state, "width", 80)
            # Reserve space for borders and padding (| content | = 4 chars total)
            content_width = terminal_width - 6  # Leave 6 for borders/padding
            max_line_length = content_width - 4  # Additional safety margin

            content_lines = []

            # Modal content based on config (no duplicate headers)
            modal_config = ui_config.modal_config or {}

            if "sections" in modal_config:
                for section in modal_config["sections"]:
                    # Skip section title since it's redundant with modal title
                    # Display commands directly
                    commands = section.get("commands", [])
                    for cmd in commands:
                        name = cmd.get("name", "")
                        description = cmd.get("description", "")

                        # Format command line with better alignment, using dynamic width
                        cmd_line = f"{name:<28} {description}"
                        if len(cmd_line) > max_line_length:
                            cmd_line = cmd_line[: max_line_length - 3] + "..."

                        content_lines.append(cmd_line)

            # Add spacing before footer
            content_lines.append("")

            # Modal footer with special styling marker
            footer = modal_config.get(
                "footer",
                "Press Esc to close . Use /help <command> for detailed help",
            )
            content_lines.append(f"__FOOTER__{footer}")

            # Clean content lines for box rendering (no ANSI codes)
            clean_content = []
            for line in content_lines:
                if line.startswith("__FOOTER__"):
                    footer_text = line.replace("__FOOTER__", "")
                    clean_content.append(footer_text)
                else:
                    clean_content.append(line)

            # Use BoxRenderer from enhanced input plugin if available
            try:
                from ...plugins.enhanced_input.box_renderer import BoxRenderer
                from ...plugins.enhanced_input.box_styles import BoxStyleRegistry
                from ...plugins.enhanced_input.color_engine import ColorEngine
                from ...plugins.enhanced_input.geometry import GeometryCalculator
                from ...plugins.enhanced_input.text_processor import TextProcessor

                # Initialize components
                style_registry = BoxStyleRegistry()
                color_engine = ColorEngine()
                geometry = GeometryCalculator()
                text_processor = TextProcessor()
                box_renderer = BoxRenderer(
                    style_registry, color_engine, geometry, text_processor
                )

                # Render with clean rounded style first, using dynamic width
                bordered_lines = box_renderer.render_box(
                    clean_content, content_width, "rounded"
                )

                # Add title to top border
                title = ui_config.title or "Status Modal"
                if bordered_lines:
                    _ = bordered_lines[0]
                    # Create title border: ╭─ Title ─────...─╮
                    title_text = f"─ {title} "
                    remaining_width = max(
                        0, content_width - 2 - len(title_text)
                    )  # content_width - 2 border chars - title length
                    titled_border = f"╭{title_text}{'─' * remaining_width}╮"
                    bordered_lines[0] = titled_border

                # Apply styling to content lines after border rendering
                styled_lines = []
                for i, line in enumerate(bordered_lines):
                    if i == 0 or i == len(bordered_lines) - 1:
                        # Border lines - keep as is
                        styled_lines.append(line)
                    elif line.strip() and "│" in line:
                        # Content lines with borders
                        if any(
                            footer in line for footer in ["Press Esc", "Use /help"]
                        ):
                            # Footer line - apply cyan
                            styled_line = line.replace("│", "│\033[2;36m", 1)
                            styled_line = styled_line.replace("│", "\033[0m│", -1)
                            styled_lines.append(styled_line)
                        elif line.strip() != "│" + " " * 76 + "│":  # Not empty line
                            # Command line - apply dim
                            styled_line = line.replace("│", "│\033[2m", 1)
                            styled_line = styled_line.replace("│", "\033[0m│", -1)
                            styled_lines.append(styled_line)
                        else:
                            # Empty line
                            styled_lines.append(line)
                    else:
                        styled_lines.append(line)

                return styled_lines

            except ImportError:
                # Fallback to simple manual borders if enhanced input not available
                return self._create_simple_bordered_content(clean_content)

        except Exception as e:
            logger.error(f"Error generating status modal lines: {e}")
            return [f"Error displaying status modal: {e}"]

    def _create_simple_bordered_content(self, content_lines: List[str]) -> List[str]:
        """Create simple bordered content as fallback.

        Args:
            content_lines: Content lines to border.

        Returns:
            Lines with simple borders.
        """
        # Get dynamic terminal width
        terminal_width = getattr(self.renderer.terminal_state, "width", 80)
        # Reserve space for borders and padding
        width = terminal_width - 6  # Leave 6 for borders/padding
        lines = []

        # Simple top border
        lines.append("╭" + "─" * (width + 2) + "╮")

        # Content with side borders
        for line in content_lines:
            padded_line = f"{line:<{width}}"
            lines.append(f"│ {padded_line} │")

        # Simple bottom border
        lines.append("╰" + "─" * (width + 2) + "╯")

        return lines
