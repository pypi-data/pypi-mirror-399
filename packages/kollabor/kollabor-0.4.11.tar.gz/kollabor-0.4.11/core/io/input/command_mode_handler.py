"""Command mode handler component for Kollabor CLI.

Responsible for managing slash command mode interactions including:
- Command menu popup navigation
- Status view cycling
- Command execution
- Modal transitions
"""

import logging
from typing import Dict, Any, List, Callable, Optional

from ...events.models import CommandMode, EventType
from ..key_parser import KeyPress

logger = logging.getLogger(__name__)


class CommandModeHandler:
    """Handles slash command mode interactions and navigation.

    This component manages:
    - Entering/exiting command mode
    - Command menu popup with filtering
    - Arrow key navigation in menu
    - Command execution
    - Status view cycling (Ctrl+Left/Right)
    - Status takeover mode

    Attributes:
        buffer_manager: Buffer manager for command text.
        renderer: Terminal renderer for status access.
        event_bus: Event bus for emitting command events.
        command_registry: Registry of available commands.
        command_executor: Executor for running commands.
        command_menu_renderer: Renderer for command menu display.
        slash_parser: Parser for slash command syntax.
    """

    def __init__(
        self,
        buffer_manager: Any,
        renderer: Any,
        event_bus: Any,
        command_registry: Any,
        command_executor: Any,
        command_menu_renderer: Any,
        slash_parser: Any,
        error_handler: Optional[Any] = None,
    ) -> None:
        """Initialize the command mode handler.

        Args:
            buffer_manager: Buffer manager for command text.
            renderer: Terminal renderer for status access.
            event_bus: Event bus for emitting command events.
            command_registry: Registry of available commands.
            command_executor: Executor for running commands.
            command_menu_renderer: Renderer for command menu display.
            slash_parser: Parser for slash command syntax.
            error_handler: Optional error handler for command errors.
        """
        self.buffer_manager = buffer_manager
        self.renderer = renderer
        self.event_bus = event_bus
        self.command_registry = command_registry
        self.command_executor = command_executor
        self.command_menu_renderer = command_menu_renderer
        self.slash_parser = slash_parser
        self.error_handler = error_handler

        # Command mode state
        self.command_mode = CommandMode.NORMAL
        self.command_menu_active = False
        self.selected_command_index = 0

        # Callbacks for operations that require access to parent InputHandler
        self._update_display_callback: Optional[Callable] = None
        self._exit_modal_callback: Optional[Callable] = None

        # Callbacks for modal mode handling (delegated to ModalController)
        self._handle_modal_keypress_callback: Optional[Callable] = None
        self._handle_status_modal_keypress_callback: Optional[Callable] = None
        self._handle_live_modal_keypress_callback: Optional[Callable] = None

        logger.debug("CommandModeHandler initialized")

    def set_update_display_callback(self, callback: Callable) -> None:
        """Set callback for updating display.

        Args:
            callback: Async function to call for display updates.
        """
        self._update_display_callback = callback

    def set_exit_modal_callback(self, callback: Callable) -> None:
        """Set callback for exiting modal mode.

        Args:
            callback: Async function to call for modal exit.
        """
        self._exit_modal_callback = callback

    def set_modal_callbacks(
        self,
        handle_modal_keypress: Optional[Callable] = None,
        handle_status_modal_keypress: Optional[Callable] = None,
        handle_live_modal_keypress: Optional[Callable] = None,
    ) -> None:
        """Set callbacks for modal mode handling.

        These callbacks delegate to ModalController for actual handling.

        Args:
            handle_modal_keypress: Callback for MODAL mode key handling.
            handle_status_modal_keypress: Callback for STATUS_MODAL mode key handling.
            handle_live_modal_keypress: Callback for LIVE_MODAL mode key handling.
        """
        self._handle_modal_keypress_callback = handle_modal_keypress
        self._handle_status_modal_keypress_callback = handle_status_modal_keypress
        self._handle_live_modal_keypress_callback = handle_live_modal_keypress

    async def enter_command_mode(self) -> None:
        """Enter slash command mode and show command menu."""
        try:
            logger.info("Entering slash command mode")
            self.command_mode = CommandMode.MENU_POPUP
            self.command_menu_active = True

            # Reset selection to first command
            self.selected_command_index = 0

            # Add the '/' character to buffer for visual feedback
            self.buffer_manager.insert_char("/")

            # Show command menu via renderer
            available_commands = self._get_available_commands()
            self.command_menu_renderer.show_command_menu(available_commands, "")

            # Emit command menu show event
            await self.event_bus.emit_with_hooks(
                EventType.COMMAND_MENU_SHOW,
                {"available_commands": available_commands, "filter_text": ""},
                "commands",
            )

            # Update display to show command mode
            if self._update_display_callback:
                await self._update_display_callback(force_render=True)

            logger.info("Command menu activated")

        except Exception as e:
            logger.error(f"Error entering command mode: {e}")
            await self.exit_command_mode()

    async def exit_command_mode(self) -> None:
        """Exit command mode and restore normal input."""
        try:
            import traceback

            logger.info("Exiting slash command mode")
            logger.debug(f"Exit called from: {traceback.format_stack()[-2].strip()}")

            # Hide command menu via renderer
            self.command_menu_renderer.hide_menu()

            # Emit command menu hide event
            if self.command_menu_active:
                await self.event_bus.emit_with_hooks(
                    EventType.COMMAND_MENU_HIDE,
                    {"reason": "manual_exit"},
                    "commands",
                )

            self.command_mode = CommandMode.NORMAL
            self.command_menu_active = False

            # Clear command buffer (remove the '/' and any partial command)
            self.buffer_manager.clear()

            # Update display
            if self._update_display_callback:
                await self._update_display_callback(force_render=True)

            logger.info("Returned to normal input mode")

        except Exception as e:
            logger.error(f"Error exiting command mode: {e}")

    async def handle_command_mode_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress while in command mode (supports arrow keys).

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled, False to fall through to normal processing.
        """
        try:
            if self.command_mode == CommandMode.MENU_POPUP:
                return await self.handle_menu_popup_keypress(key_press)
            elif self.command_mode == CommandMode.STATUS_TAKEOVER:
                return await self.handle_status_takeover_keypress(key_press)
            elif self.command_mode == CommandMode.MODAL:
                # Delegate to ModalController via callback
                if self._handle_modal_keypress_callback:
                    return await self._handle_modal_keypress_callback(key_press)
                else:
                    logger.warning("MODAL mode active but no callback set")
                    return False
            elif self.command_mode == CommandMode.STATUS_MODAL:
                # Delegate to ModalController via callback
                if self._handle_status_modal_keypress_callback:
                    return await self._handle_status_modal_keypress_callback(key_press)
                else:
                    logger.warning("STATUS_MODAL mode active but no callback set")
                    return False
            elif self.command_mode == CommandMode.LIVE_MODAL:
                # Delegate to ModalController via callback
                if self._handle_live_modal_keypress_callback:
                    return await self._handle_live_modal_keypress_callback(key_press)
                else:
                    logger.warning("LIVE_MODAL mode active but no callback set")
                    return False
            else:
                # Unknown command mode, exit to normal
                await self.exit_command_mode()
                return False

        except Exception as e:
            logger.error(f"Error handling command mode keypress: {e}")
            await self.exit_command_mode()
            return False

    async def handle_command_mode_input(self, char: str) -> bool:
        """Handle input while in command mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled, False to fall through to normal processing.
        """
        try:
            if self.command_mode == CommandMode.MENU_POPUP:
                return await self.handle_menu_popup_input(char)
            elif self.command_mode == CommandMode.STATUS_TAKEOVER:
                return await self.handle_status_takeover_input(char)
            elif self.command_mode == CommandMode.STATUS_MODAL:
                # STATUS_MODAL input is handled via keypress callback
                # Character input falls through to keypress handler
                return False
            elif self.command_mode == CommandMode.LIVE_MODAL:
                # LIVE_MODAL input is handled via keypress callback
                # Character input falls through to keypress handler
                return False
            else:
                # Unknown command mode, exit to normal
                await self.exit_command_mode()
                return False

        except Exception as e:
            logger.error(f"Error handling command mode input: {e}")
            await self.exit_command_mode()
            return False

    async def handle_menu_popup_input(self, char: str) -> bool:
        """Handle input during menu popup mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled.
        """
        # Handle special keys first
        if ord(char) == 27:  # Escape key
            await self.exit_command_mode()
            return True
        elif ord(char) == 13:  # Enter key
            await self._execute_selected_command()
            return True
        elif ord(char) == 8 or ord(char) == 127:  # Backspace or Delete
            # If buffer only has '/', exit command mode
            if len(self.buffer_manager.content) <= 1:
                await self.exit_command_mode()
                return True
            else:
                # Remove character and update command filter
                self.buffer_manager.delete_char()
                await self._update_command_filter()
                return True

        # Handle printable characters (add to command filter)
        if char.isprintable():
            self.buffer_manager.insert_char(char)
            await self._update_command_filter()
            return True

        # Let other keys fall through for now
        return False

    async def handle_menu_popup_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress during menu popup mode with arrow key navigation.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        try:
            # Handle arrow key navigation
            if key_press.name == "ArrowUp":
                await self._navigate_menu("up")
                return True
            elif key_press.name == "ArrowDown":
                await self._navigate_menu("down")
                return True
            elif key_press.name == "Enter":
                await self._execute_selected_command()
                return True
            elif key_press.name == "Escape":
                await self.exit_command_mode()
                return True

            # Handle printable characters (for filtering)
            elif key_press.char and key_press.char.isprintable():
                self.buffer_manager.insert_char(key_press.char)
                await self._update_command_filter()
                return True

            # Handle backspace/delete
            elif key_press.name in ["Backspace", "Delete"]:
                # If buffer only has '/', exit command mode
                if len(self.buffer_manager.content) <= 1:
                    await self.exit_command_mode()
                    return True
                else:
                    # Remove character and update command filter
                    self.buffer_manager.delete_char()
                    await self._update_command_filter()
                    return True

            # Other keys not handled
            return False

        except Exception as e:
            logger.error(f"Error handling menu popup keypress: {e}")
            await self.exit_command_mode()
            return False

    async def handle_status_takeover_input(self, char: str) -> bool:
        """Handle input during status area takeover mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled.
        """
        # For now, just handle Escape to exit
        if ord(char) == 27:  # Escape key
            await self.exit_command_mode()
            return True

        # TODO: Implement status area navigation
        return True

    async def handle_status_takeover_keypress(self, key_press: KeyPress) -> bool:
        """Handle KeyPress during status area takeover mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        # For now, just handle Escape to exit
        if key_press.name == "Escape":
            await self.exit_command_mode()
            return True

        # TODO: Implement status area navigation
        return True

    async def handle_status_view_previous(self) -> None:
        """Handle comma key press for previous status view."""
        try:
            logger.info("Attempting to switch to previous status view")
            # Check if renderer has a status registry
            if (
                hasattr(self.renderer, "status_renderer")
                and self.renderer.status_renderer
            ):
                status_renderer = self.renderer.status_renderer
                logger.info(
                    f"[ok] Found status_renderer: {type(status_renderer).__name__}"
                )
                if (
                    hasattr(status_renderer, "status_registry")
                    and status_renderer.status_registry
                ):
                    registry = status_renderer.status_registry
                    logger.info(
                        f"[ok] Found status_registry with {len(registry.views)} views"
                    )
                    if hasattr(registry, "cycle_previous"):
                        previous_view = registry.cycle_previous()
                        if previous_view:
                            logger.info(
                                f"[ok] Switched to previous status view: '{previous_view.name}'"
                            )
                        else:
                            logger.info("No status views available to cycle to")
                    else:
                        logger.info("cycle_previous method not found in registry")
                else:
                    logger.info("No status registry available for view cycling")
            else:
                logger.info("No status renderer available for view cycling")

        except Exception as e:
            if self.error_handler:
                from ..input_errors import ErrorType, ErrorSeverity
                await self.error_handler.handle_error(
                    ErrorType.EVENT_ERROR,
                    f"Error handling status view previous: {e}",
                    ErrorSeverity.LOW,
                    {"key": "Ctrl+ArrowLeft"},
                )

    async def handle_status_view_next(self) -> None:
        """Handle Ctrl+Right arrow key press for next status view."""
        try:
            # Check if renderer has a status registry
            if (
                hasattr(self.renderer, "status_renderer")
                and self.renderer.status_renderer
            ):
                status_renderer = self.renderer.status_renderer
                if (
                    hasattr(status_renderer, "status_registry")
                    and status_renderer.status_registry
                ):
                    next_view = status_renderer.status_registry.cycle_next()
                    if next_view:
                        logger.debug(
                            f"Switched to next status view: '{next_view.name}'"
                        )
                    else:
                        logger.debug("No status views available to cycle to")
                else:
                    logger.debug("No status registry available for view cycling")
            else:
                logger.debug("No status renderer available for view cycling")

        except Exception as e:
            if self.error_handler:
                from ..input_errors import ErrorType, ErrorSeverity
                await self.error_handler.handle_error(
                    ErrorType.EVENT_ERROR,
                    f"Error handling status view next: {e}",
                    ErrorSeverity.LOW,
                    {"key": "Ctrl+ArrowRight"},
                )

    # ==================== PRIVATE HELPER METHODS ====================

    async def _navigate_menu(self, direction: str) -> None:
        """Navigate the command menu up or down.

        Args:
            direction: "up" or "down"
        """
        try:
            # Get current filtered commands
            current_input = self.buffer_manager.content
            filter_text = (
                current_input[1:] if current_input.startswith("/") else current_input
            )
            filtered_commands = self._filter_commands(filter_text)

            if not filtered_commands:
                return

            # Update selection index
            if direction == "up":
                self.selected_command_index = max(0, self.selected_command_index - 1)
            elif direction == "down":
                self.selected_command_index = min(
                    len(filtered_commands) - 1, self.selected_command_index + 1
                )

            # Update menu renderer with new selection (don't reset selection during navigation)
            self.command_menu_renderer.set_selected_index(
                self.selected_command_index
            )
            self.command_menu_renderer.filter_commands(
                filtered_commands, filter_text, reset_selection=False
            )

            # Note: No need to call _update_display - filter_commands already renders the menu

        except Exception as e:
            logger.error(f"Error navigating menu: {e}")

    async def _update_command_filter(self) -> None:
        """Update command menu based on current buffer content."""
        try:
            # Get current input (minus the leading '/')
            current_input = self.buffer_manager.content
            filter_text = (
                current_input[1:] if current_input.startswith("/") else current_input
            )

            # Update menu renderer with filtered commands
            filtered_commands = self._filter_commands(filter_text)

            # Reset selection when filtering
            self.selected_command_index = 0
            self.command_menu_renderer.set_selected_index(
                self.selected_command_index
            )
            self.command_menu_renderer.filter_commands(
                filtered_commands, filter_text
            )

            # Emit filter update event
            await self.event_bus.emit_with_hooks(
                EventType.COMMAND_MENU_FILTER,
                {
                    "filter_text": filter_text,
                    "available_commands": self._get_available_commands(),
                    "filtered_commands": filtered_commands,
                },
                "commands",
            )

            # Update display
            if self._update_display_callback:
                await self._update_display_callback(force_render=True)

        except Exception as e:
            logger.error(f"Error updating command filter: {e}")

    async def _execute_selected_command(self) -> None:
        """Execute the currently selected command."""
        try:
            # Get the full command string from buffer (includes arguments)
            command_string = self.buffer_manager.content

            # If buffer is empty or just '/', use the selected command from menu
            if not command_string or command_string == "/":
                selected_command = self.command_menu_renderer.get_selected_command()
                if not selected_command:
                    logger.warning("No command selected")
                    await self.exit_command_mode()
                    return
                command_string = f"/{selected_command['name']}"

            # Parse the command
            command = self.slash_parser.parse_command(command_string)
            if command:
                logger.info(f"Executing selected command: {command.name}")

                # Exit command mode first
                await self.exit_command_mode()

                # Execute the command
                result = await self.command_executor.execute_command(
                    command, self.event_bus
                )

                # Handle the result
                if result.success:
                    logger.info(f"Command {command.name} completed successfully")

                    # Modal display is handled by event bus trigger, not here
                    if result.message:
                        # Display success message in status area
                        logger.info(f"Command result: {result.message}")
                        # TODO: Display in status area
                else:
                    logger.warning(
                        f"Command {command.name} failed: {result.message}"
                    )
                    # TODO: Display error message in status area
            else:
                logger.warning("Failed to parse selected command")
                await self.exit_command_mode()

        except Exception as e:
            logger.error(f"Error executing command: {e}")
            await self.exit_command_mode()

    def _get_available_commands(self) -> List[Dict[str, Any]]:
        """Get list of available commands for menu display.

        Returns:
            List of command dictionaries for menu rendering.
        """
        commands = []
        command_defs = self.command_registry.list_commands()

        for cmd_def in command_defs:
            commands.append(
                {
                    "name": cmd_def.name,
                    "description": cmd_def.description,
                    "aliases": cmd_def.aliases,
                    "category": cmd_def.category.value,
                    "plugin": cmd_def.plugin_name,
                    "icon": cmd_def.icon,
                }
            )

        return commands

    def _filter_commands(self, filter_text: str) -> List[Dict[str, Any]]:
        """Filter commands based on input text.

        Args:
            filter_text: Text to filter commands by.

        Returns:
            List of filtered command dictionaries.
        """
        if not filter_text:
            return self._get_available_commands()

        # Use registry search functionality
        matching_defs = self.command_registry.search_commands(filter_text)

        filtered_commands = []
        for cmd_def in matching_defs:
            filtered_commands.append(
                {
                    "name": cmd_def.name,
                    "description": cmd_def.description,
                    "aliases": cmd_def.aliases,
                    "category": cmd_def.category.value,
                    "plugin": cmd_def.plugin_name,
                    "icon": cmd_def.icon,
                }
            )

        return filtered_commands
