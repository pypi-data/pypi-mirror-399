"""Command menu renderer for interactive slash command display."""

import logging
from typing import List, Dict, Any, Optional
from ..events.models import CommandCategory

logger = logging.getLogger(__name__)


class CommandMenuRenderer:
    """Renders interactive command menu overlay.

    Provides a command menu that appears when the user
    types '/' and allows filtering and selection of available commands.
    """

    def __init__(self, terminal_renderer) -> None:
        """Initialize the command menu renderer.

        Args:
            terminal_renderer: Terminal renderer for display operations.
        """
        self.renderer = terminal_renderer
        self.logger = logger
        self.menu_active = False
        self.current_commands = []
        self.selected_index = 0
        self.filter_text = ""
        self.current_menu_lines = []  # Store menu content for event system

    def show_command_menu(self, commands: List[Dict[str, Any]], filter_text: str = "") -> None:
        """Display command menu when user types '/'.

        Args:
            commands: List of available commands to display.
            filter_text: Current filter text (excluding the leading '/').
        """
        try:
            self.menu_active = True
            self.current_commands = commands
            self.filter_text = filter_text
            self.selected_index = 0

            # Render the menu
            self._render_menu()

            self.logger.info(f"Command menu shown with {len(commands)} commands")

        except Exception as e:
            self.logger.error(f"Error showing command menu: {e}")

    def set_selected_index(self, index: int) -> None:
        """Set the selected command index for navigation.

        Args:
            index: Index of the command to select.
        """
        if 0 <= index < len(self.current_commands):
            self.selected_index = index
            # Note: No auto-render here - caller will trigger render to avoid duplicates
            logger.debug(f"Selected command index set to: {index}")

    def hide_menu(self) -> None:
        """Hide command menu and return to normal input."""
        try:
            if self.menu_active:
                self.menu_active = False
                self.current_commands = []
                self.selected_index = 0
                self.filter_text = ""

                # Clear menu from display
                self._clear_menu()

                self.logger.info("Command menu hidden")

        except Exception as e:
            self.logger.error(f"Error hiding command menu: {e}")

    def filter_commands(self, commands: List[Dict[str, Any]], filter_text: str, reset_selection: bool = True) -> None:
        """Filter visible commands as user types.

        Args:
            commands: Filtered list of commands to display.
            filter_text: Current filter text.
            reset_selection: Whether to reset selection to top (True for typing, False for navigation).
        """
        try:
            if not self.menu_active:
                return

            self.current_commands = commands
            self.filter_text = filter_text

            # Only reset selection when filtering by typing, not during navigation
            if reset_selection:
                self.selected_index = 0  # Reset selection to top
            else:
                # Ensure selected index is still valid after filtering
                if self.selected_index >= len(commands):
                    self.selected_index = max(0, len(commands) - 1)

            # Re-render with filtered commands
            self._render_menu()

            self.logger.debug(f"Filtered to {len(commands)} commands with '{filter_text}', reset_selection={reset_selection}")

        except Exception as e:
            self.logger.error(f"Error filtering commands: {e}")

    def navigate_selection(self, direction: str) -> bool:
        """Handle arrow key navigation in menu.

        Args:
            direction: Direction to navigate ("up" or "down").

        Returns:
            True if navigation was handled, False otherwise.
        """
        try:
            if not self.menu_active or not self.current_commands:
                return False

            if direction == "up":
                self.selected_index = max(0, self.selected_index - 1)
            elif direction == "down":
                self.selected_index = min(len(self.current_commands) - 1, self.selected_index + 1)
            else:
                return False

            # Re-render with new selection
            self._render_menu()
            return True

        except Exception as e:
            self.logger.error(f"Error navigating menu: {e}")
            return False

    def get_selected_command(self) -> Optional[Dict[str, Any]]:
        """Get currently selected command.

        Returns:
            Selected command dictionary or None if no selection.
        """
        if (self.menu_active and
            self.current_commands and
            0 <= self.selected_index < len(self.current_commands)):
            return self.current_commands[self.selected_index]
        return None

    def _render_menu(self) -> None:
        """Render the command menu overlay."""
        try:
            if not self.menu_active:
                return

            # Create menu content
            menu_lines = self._create_menu_lines()

            # Display menu overlay
            self._display_menu_overlay(menu_lines)

        except Exception as e:
            self.logger.error(f"Error rendering menu: {e}")

    def _create_menu_lines(self) -> List[str]:
        """Create lines for menu display.

        Returns:
            List of formatted menu lines.
        """
        lines = []

        # Header (input display handled by enhanced input plugin)
        # Note: Removed separator line as requested

        # Group commands by category for organized display
        categorized_commands = self._group_commands_by_category()

        # Render each category
        for category, commands in categorized_commands.items():
            if not commands:
                continue

            # Category header (if multiple categories)
            if len(categorized_commands) > 1:
                category_name = self._format_category_name(category)
                lines.append(f"  {category_name}")

            # Render commands in this category
            for cmd in commands:
                line = self._format_command_line(cmd)
                lines.append(line)

            # Add spacing between categories
            if len(categorized_commands) > 1:
                lines.append("")

        # If no commands, show message
        if not self.current_commands:
            lines.append("  No matching commands found")

        return lines

    def _group_commands_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """Group commands by category for organized display.

        Returns:
            Dictionary mapping category names to command lists.
        """
        categorized = {}

        for i, cmd in enumerate(self.current_commands):
            category = cmd.get("category", "custom")
            if category not in categorized:
                categorized[category] = []

            # Add selection info to command
            cmd_with_selection = cmd.copy()
            cmd_with_selection["_is_selected"] = (i == self.selected_index)
            cmd_with_selection["_index"] = i

            categorized[category].append(cmd_with_selection)

        return categorized

    def _format_category_name(self, category: str) -> str:
        """Format category name for display.

        Args:
            category: Category identifier.

        Returns:
            Formatted category name.
        """
        category_names = {
            "system": "Core System",
            "conversation": "Conversation Management",
            "agent": "Agent Management",
            "development": "Development Tools",
            "file": "File Management",
            "task": "Task Management",
            "custom": "Plugin Commands"
        }
        return category_names.get(category, category.title())

    def _format_command_line(self, cmd: Dict[str, Any]) -> str:
        """Format a single command line for display.

        Args:
            cmd: Command dictionary with display info.

        Returns:
            Formatted command line string.
        """
        # Selection indicator
        indicator = "❯ " if cmd.get("_is_selected", False) else "  "

        # Command name with aliases
        name_part = f"/{cmd['name']}"
        if cmd.get("aliases"):
            aliases_str = ", ".join(cmd["aliases"])
            name_part += f" ({aliases_str})"

        # Description
        description = cmd.get("description", "")

        # Format the complete line
        line = f"{indicator}{name_part:<30} {description}"

        return line

    def _display_menu_overlay(self, menu_lines: List[str]) -> None:
        """Display menu as overlay on terminal.

        Args:
            menu_lines: Formatted menu lines to display.
        """
        try:
            # Store menu content for INPUT_RENDER event response
            self.current_menu_lines = menu_lines

            # Log menu for debugging
            self.logger.info("=== COMMAND MENU ===")
            for line in menu_lines:
                self.logger.info(line)
            self.logger.info("=== END MENU ===")

        except Exception as e:
            self.logger.error(f"Error preparing menu display: {e}")

    def _clear_menu(self) -> None:
        """Clear menu from display."""
        try:
            # Clear overlay if renderer supports it
            if hasattr(self.renderer, 'hide_overlay'):
                self.renderer.hide_overlay()
            elif hasattr(self.renderer, 'clear_menu'):
                self.renderer.clear_menu()
            else:
                # Fallback: log clear
                self.logger.info("Command menu cleared")

        except Exception as e:
            self.logger.error(f"Error clearing menu: {e}")

    def get_menu_stats(self) -> Dict[str, Any]:
        """Get menu statistics for debugging.

        Returns:
            Dictionary with menu statistics.
        """
        return {
            "active": self.menu_active,
            "command_count": len(self.current_commands),
            "selected_index": self.selected_index,
            "filter_text": self.filter_text,
            "selected_command": self.get_selected_command()
        }