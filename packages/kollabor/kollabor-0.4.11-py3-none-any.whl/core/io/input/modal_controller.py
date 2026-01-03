"""Modal controller component for managing modal interactions.

This component handles all modal-related operations including:
- Standard modals (full-screen with widgets)
- Status modals (confined to status area)
- Live modals (continuously updating content)
- Modal event handling and state management

Extracted from InputHandler as part of the refactoring effort.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable

from ...events.models import CommandMode, EventType

logger = logging.getLogger(__name__)


class ModalController:
    """Manages modal display and interaction logic.

    This component coordinates between different modal types and handles
    modal-specific input events, state transitions, and rendering.

    Responsibilities:
    - Handle modal trigger events (MODAL_TRIGGER, STATUS_MODAL_TRIGGER, LIVE_MODAL_TRIGGER)
    - Manage modal state (command_mode, current_status_modal_config, modal_renderer)
    - Process modal keypresses and input
    - Coordinate modal entry/exit with proper state management
    - Handle save confirmations and modal data persistence
    """

    def __init__(
        self,
        renderer,
        event_bus,
        config,
        status_modal_renderer,
        update_display_callback: Callable,
        exit_command_mode_callback: Callable,
        set_command_mode_callback: Optional[Callable] = None,
    ) -> None:
        """Initialize the modal controller.

        Args:
            renderer: Terminal renderer for display operations.
            event_bus: Event bus for emitting modal events.
            config: Configuration service.
            status_modal_renderer: StatusModalRenderer for status area modals.
            update_display_callback: Callback to update display (async).
            exit_command_mode_callback: Callback to exit command mode (async).
            set_command_mode_callback: Callback to set command_mode (syncs with parent).
        """
        self.renderer = renderer
        self.event_bus = event_bus
        self.config = config
        self._status_modal_renderer = status_modal_renderer
        self._update_display = update_display_callback
        self._exit_command_mode = exit_command_mode_callback
        self._set_command_mode_callback = set_command_mode_callback

        # Modal state
        self._command_mode = CommandMode.NORMAL
        self.current_status_modal_config = None
        self.modal_renderer = None  # ModalRenderer instance when active
        self.live_modal_renderer = None  # LiveModalRenderer instance when active
        self.live_modal_content_generator = None  # Content generator function
        self.live_modal_input_callback = None  # Input callback for passthrough
        self._pending_save_confirm = False  # For modal save confirmation
        self._fullscreen_session_active = False  # For fullscreen plugin sessions

        logger.info("ModalController initialized")

    @property
    def command_mode(self) -> CommandMode:
        """Get current command mode."""
        return self._command_mode

    @command_mode.setter
    def command_mode(self, value: CommandMode) -> None:
        """Set command mode and notify parent via callback."""
        self._command_mode = value
        if self._set_command_mode_callback:
            self._set_command_mode_callback(value)

    # ==================== EVENT HANDLERS ====================

    async def _handle_modal_trigger(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle modal trigger events to show modals.

        Args:
            event_data: Event data containing modal configuration.
            context: Hook execution context.

        Returns:
            Dictionary with modal result.
        """
        try:
            # Check if this is a Matrix effect trigger
            if event_data.get("matrix_effect"):
                logger.info(
                    "Matrix effect modal trigger received - setting modal mode for complete terminal control"
                )
                # Set modal mode directly for Matrix effect (no UI config needed)
                self.command_mode = CommandMode.MODAL
                logger.info("Command mode set to MODAL for Matrix effect")
                return {
                    "success": True,
                    "modal_activated": True,
                    "matrix_mode": True,
                }

            # Check if this is a full-screen plugin trigger
            if event_data.get("fullscreen_plugin"):
                plugin_name = event_data.get("plugin_name", "unknown")
                logger.info(
                    f"Full-screen plugin modal trigger received: {plugin_name}"
                )

                # Use coordinator to save state before fullscreen (handles writing_messages, etc.)
                if hasattr(self.renderer, 'message_coordinator'):
                    self.renderer.message_coordinator.enter_alternate_buffer()

                self.renderer.clear_active_area()

                # Set modal mode for full-screen plugin (no UI config needed)
                self.command_mode = CommandMode.MODAL
                # CRITICAL FIX: Mark fullscreen session as active for input routing
                self._fullscreen_session_active = True
                logger.info(
                    f"Command mode set to MODAL for full-screen plugin: {plugin_name}"
                )
                logger.info(
                    "Fullscreen session marked as active for input routing"
                )
                return {
                    "success": True,
                    "modal_activated": True,
                    "fullscreen_plugin": True,
                    "plugin_name": plugin_name,
                }

            # Standard modal with UI config
            ui_config = event_data.get("ui_config")
            if ui_config:
                logger.info(f"Modal trigger received: {ui_config.title}")
                await self._enter_modal_mode(ui_config)
                return {"success": True, "modal_activated": True}
            else:
                logger.warning("Modal trigger received without ui_config")
                return {"success": False, "error": "Missing ui_config"}

        except Exception as e:
            logger.error(f"Error handling modal trigger: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_modal_hide(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle modal hide event to exit modal mode.

        NOTE: This is called AFTER fullscreen renderer has already restored
        the terminal (exited alternate buffer with \033[?1049l). We must NOT
        call clear_active_area() here as it would clear the just-restored screen.
        """
        logger.info("MODAL_HIDE event received - exiting modal mode")
        try:
            # Set render state flags (alternate buffer was already exited by fullscreen renderer)
            self.renderer.writing_messages = False
            # DON'T set input_line_written=True here!
            # Fullscreen uses alternate buffer - when it exits, the ORIGINAL screen is restored
            # with the OLD input box in place. No clearing needed - just render at correct position.
            # Setting input_line_written=True would cause clearing from wrong cursor position.
            self.renderer.input_line_written = False
            self.renderer.last_line_count = 0
            self.renderer.invalidate_render_cache()

            self.command_mode = CommandMode.NORMAL
            # Clear fullscreen session flag when exiting modal
            if hasattr(self, "_fullscreen_session_active"):
                self._fullscreen_session_active = False
                logger.info("Fullscreen session marked as inactive")
            logger.info("Command mode reset to NORMAL after modal hide")

            # Force refresh of display when exiting modal mode
            await self._update_display(force_render=True)
            return {"success": True, "modal_deactivated": True}
        except Exception as e:
            logger.error(f"Error handling modal hide: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_modal_keypress(self, key_press) -> bool:
        """Handle KeyPress during modal mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        try:
            # CRITICAL FIX: Check if this is a fullscreen plugin session first
            if (
                hasattr(self, "_fullscreen_session_active")
                and self._fullscreen_session_active
            ):
                # SIMPLE SOLUTION: Check for exit keys directly
                if key_press.char in ["q", "\x1b"] or key_press.name == "Escape":
                    # Exit fullscreen mode immediately
                    self._fullscreen_session_active = False
                    self.command_mode = CommandMode.NORMAL
                    await self._update_display(force_render=True)
                    return True

                # Route input to fullscreen session through event bus
                await self.event_bus.emit_with_hooks(
                    EventType.FULLSCREEN_INPUT,
                    {"key_press": key_press, "source": "input_handler"},
                    "input_handler",
                )
                return True

            # Initialize modal renderer if needed
            if not self.modal_renderer:
                logger.warning(
                    "Modal keypress received but no modal renderer active"
                )
                await self._exit_modal_mode()
                return True

            # Handle save confirmation if active
            if self._pending_save_confirm:
                handled = await self._handle_save_confirmation(key_press)
                if handled:
                    return True

            # Handle navigation and widget interaction
            logger.info(f"Modal processing key: {key_press.name}")

            nav_handled = self.modal_renderer._handle_widget_navigation(key_press)
            logger.info(f"Widget navigation handled: {nav_handled}")
            if nav_handled:
                # Re-render modal with updated focus
                await self._refresh_modal_display()
                return True

            # Debug: Check modal_renderer state before handling input
            logger.info(f"modal_renderer state: has_command_sections={getattr(self.modal_renderer, 'has_command_sections', 'N/A')}, "
                        f"command_items_len={len(getattr(self.modal_renderer, 'command_items', [])) if hasattr(self.modal_renderer, 'command_items') else 'N/A'}, "
                        f"widgets_len={len(getattr(self.modal_renderer, 'widgets', [])) if hasattr(self.modal_renderer, 'widgets') else 'N/A'}")
            input_handled = self.modal_renderer._handle_widget_input(key_press)
            logger.info(f"Widget input handled: {input_handled}")
            if input_handled:
                # Check if a command was selected (for command-style modals)
                logger.info(f"Checking was_command_selected: {self.modal_renderer.was_command_selected() if hasattr(self.modal_renderer, 'was_command_selected') else 'N/A'}")
                if self.modal_renderer.was_command_selected():
                    selected_cmd = self.modal_renderer.get_selected_command()
                    logger.info(f"Command selected: {selected_cmd}")
                    # Exit modal based on exit_mode or action type
                    # Commands that display their own messages need minimal exit (no input render)
                    exit_mode = selected_cmd.get("exit_mode", "normal") if selected_cmd else "normal"
                    action = selected_cmd.get("action", "") if selected_cmd else ""
                    # Actions that will display messages should use minimal exit to prevent duplicate input boxes
                    minimal_actions = ["resume_session", "branch_select_session", "branch_execute"]
                    if exit_mode == "minimal" or action in minimal_actions:
                        await self._exit_modal_mode_minimal()
                    else:
                        await self._exit_modal_mode()
                    # Emit event for plugins to handle modal command selection
                    if selected_cmd:
                        context = {"command": selected_cmd, "source": "modal"}
                        results = await self.event_bus.emit_with_hooks(
                            EventType.MODAL_COMMAND_SELECTED,
                            context,
                            "input_handler"
                        )
                        # Get modified data from hook results (main phase final_data)
                        final_data = results.get("main", {}).get("final_data", {}) if results else {}
                        # Display messages if plugin returned them
                        if final_data.get("display_messages"):
                            if hasattr(self, 'renderer') and self.renderer:
                                if hasattr(self.renderer, 'message_coordinator'):
                                    self.renderer.message_coordinator.display_message_sequence(
                                        final_data["display_messages"]
                                    )
                                    # DON'T call _update_display here - render loop will handle it.
                                    # The display_message_sequence() finally block already:
                                    # - Sets writing_messages=False (unblocks render loop)
                                    # - Resets input_line_written=False, last_line_count=0
                                    # - Invalidates render cache
                                    # Calling _update_display here causes duplicate input boxes.
                        # Show modal if plugin returned one
                        if final_data.get("show_modal"):
                            from ...events.models import UIConfig
                            modal_config = final_data["show_modal"]
                            ui_config = UIConfig(type="modal", title=modal_config.get("title", ""), modal_config=modal_config)
                            await self._enter_modal_mode(ui_config)
                    return True
                # Re-render modal with updated widget state
                await self._refresh_modal_display()
                return True

            # Check for custom action keys defined in modal config
            if self.modal_renderer and hasattr(self.modal_renderer, 'current_ui_config'):
                ui_config = self.modal_renderer.current_ui_config
                if ui_config and hasattr(ui_config, 'modal_config') and ui_config.modal_config:
                    actions = ui_config.modal_config.get('actions', [])
                    key_char = key_press.char or ""
                    key_name = key_press.name or ""

                    for action_def in actions:
                        action_key = action_def.get('key', '')
                        # Match by key name or char (case-insensitive for single chars)
                        if (action_key == key_name or
                            (len(action_key) == 1 and action_key.lower() == key_char.lower())):

                            action_name = action_def.get('action', '')
                            # Skip standard actions handled below
                            if action_name in ('select', 'cancel', 'submit'):
                                break

                            logger.info(f"Custom action key '{action_key}' matched: {action_name}")

                            # Get the currently selected command item if any
                            selected_cmd = None
                            if self.modal_renderer.has_command_sections:
                                selected_cmd = self.modal_renderer.get_selected_command()

                            # Exit modal and emit event with action and selected item
                            await self._exit_modal_mode()

                            context = {
                                "command": {
                                    "action": action_name,
                                    "profile_name": selected_cmd.get("profile_name") if selected_cmd else None,
                                    "agent_name": selected_cmd.get("agent_name") if selected_cmd else None,
                                    "skill_name": selected_cmd.get("skill_name") if selected_cmd else None,
                                },
                                "source": "modal_action_key"
                            }
                            results = await self.event_bus.emit_with_hooks(
                                EventType.MODAL_COMMAND_SELECTED,
                                context,
                                "input_handler"
                            )

                            # Handle results
                            final_data = results.get("main", {}).get("final_data", {}) if results else {}
                            if final_data.get("display_messages"):
                                if hasattr(self.renderer, 'message_coordinator'):
                                    self.renderer.message_coordinator.display_message_sequence(
                                        final_data["display_messages"]
                                    )
                            if final_data.get("show_modal"):
                                from ...events.models import UIConfig
                                modal_config = final_data["show_modal"]
                                new_ui_config = UIConfig(type="modal", title=modal_config.get("title", ""), modal_config=modal_config)
                                await self._enter_modal_mode(new_ui_config)

                            return True

            if key_press.name in ("Escape", "Ctrl+C"):
                logger.info("Processing Escape/Ctrl+C key for modal exit")
                # Check for unsaved changes
                if self.modal_renderer and self._has_pending_modal_changes():
                    self._pending_save_confirm = True
                    await self._show_save_confirmation()
                    return True
                await self._exit_modal_mode()
                return True
            elif key_press.name == "Ctrl+S":
                logger.info("Processing Ctrl+S for modal save")
                await self._save_and_exit_modal()
                return True
            elif key_press.name == "Enter":
                logger.info(
                    "ENTER KEY HIJACKED - This should not happen if widget handled it!"
                )
                # Try to save modal changes and exit
                await self._save_and_exit_modal()
                return True

            return True
        except Exception as e:
            logger.error(f"Error handling modal keypress: {e}")
            await self._exit_modal_mode()
            return False

    # ==================== LIVE MODAL HANDLERS ====================

    async def _handle_live_modal_trigger(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle live modal trigger events to show live modals.

        Args:
            event_data: Event data containing content_generator, config, input_callback.
            context: Hook execution context.

        Returns:
            Dictionary with live modal result.
        """
        try:
            content_generator = event_data.get("content_generator")
            config = event_data.get("config")
            input_callback = event_data.get("input_callback")

            if content_generator:
                logger.info(f"Live modal trigger received: {config.title if config else 'untitled'}")
                # Enter live modal mode (this will block until modal closes)
                result = await self.enter_live_modal_mode(
                    content_generator,
                    config,
                    input_callback
                )
                return {"success": True, "live_modal_activated": True, "result": result}
            else:
                logger.warning("Live modal trigger received without content_generator")
                return {"success": False, "error": "Missing content_generator"}
        except Exception as e:
            logger.error(f"Error handling live modal trigger: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_live_modal_keypress(self, key_press) -> bool:
        """Handle keypress during live modal mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled.
        """
        try:
            logger.info(
                f"LIVE_MODAL_KEY: name='{key_press.name}', char='{key_press.char}', code={key_press.code}"
            )

            # Forward to live modal renderer
            if self.live_modal_renderer:
                should_close = await self.live_modal_renderer.handle_input(key_press)
                if should_close:
                    await self._exit_live_modal_mode()
                return True

            # Fallback: Escape always exits
            if key_press.name == "Escape":
                await self._exit_live_modal_mode()
                return True

            return True

        except Exception as e:
            logger.error(f"Error handling live modal keypress: {e}")
            await self._exit_live_modal_mode()
            return False

    async def _handle_live_modal_input(self, char: str) -> bool:
        """Handle character input during live modal mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled.
        """
        try:
            # Convert char to KeyPress for consistent handling
            from ..key_parser import KeyPress
            key_press = KeyPress(char=char, name=None, code=ord(char) if char else 0)
            return await self._handle_live_modal_keypress(key_press)

        except Exception as e:
            logger.error(f"Error handling live modal input: {e}")
            await self._exit_live_modal_mode()
            return False

    async def enter_live_modal_mode(
        self,
        content_generator,
        config=None,
        input_callback=None
    ) -> Dict[str, Any]:
        """Enter live modal mode with continuously updating content.

        This is non-blocking - it starts the modal and returns immediately.
        The input loop continues to process keys, routing them to the modal.
        Press Escape to exit the modal.

        Args:
            content_generator: Function returning List[str] of current content.
            config: LiveModalConfig instance.
            input_callback: Optional callback for input passthrough.

        Returns:
            Result dict indicating modal was started.
        """
        try:
            from ...ui.live_modal_renderer import LiveModalRenderer, LiveModalConfig

            # Store state
            self.command_mode = CommandMode.LIVE_MODAL
            self.live_modal_content_generator = content_generator
            self.live_modal_input_callback = input_callback

            # Create and store the live modal renderer
            terminal_state = self.renderer.terminal_state
            self.live_modal_renderer = LiveModalRenderer(terminal_state)

            # Use default config if none provided
            if config is None:
                config = LiveModalConfig()

            logger.info(f"Entering live modal mode: {config.title}")

            # Start the live modal (non-blocking)
            # The refresh loop runs as a background task
            # Input will be handled by _handle_live_modal_keypress
            success = self.live_modal_renderer.start_live_modal(
                content_generator,
                config,
                input_callback
            )

            if success:
                return {"success": True, "modal_started": True}
            else:
                await self._exit_live_modal_mode()
                return {"success": False, "error": "Failed to start modal"}

        except Exception as e:
            logger.error(f"Error entering live modal mode: {e}")
            await self._exit_live_modal_mode()
            return {"success": False, "error": str(e)}

    async def _exit_live_modal_mode(self):
        """Exit live modal mode and restore terminal."""
        try:
            logger.info("Exiting live modal mode...")

            # Close the live modal renderer (restores from alt buffer)
            if self.live_modal_renderer:
                await self.live_modal_renderer.close_modal()

            # Reset state
            self.command_mode = CommandMode.NORMAL
            self.live_modal_renderer = None
            self.live_modal_content_generator = None
            self.live_modal_input_callback = None

            # Force display refresh with full redraw
            self.renderer.clear_active_area()
            await self._update_display(force_render=True)

            logger.info("Live modal mode exited successfully")

        except Exception as e:
            logger.error(f"Error exiting live modal mode: {e}")
            self.command_mode = CommandMode.NORMAL

    # ==================== STATUS MODAL HANDLERS ====================

    async def _handle_status_modal_trigger(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle status modal trigger events to show status modals.

        Args:
            event_data: Event data containing modal configuration.
            context: Hook execution context.

        Returns:
            Dictionary with status modal result.
        """
        try:
            ui_config = event_data.get("ui_config")
            if ui_config:
                logger.info(f"Status modal trigger received: {ui_config.title}")
                logger.info(f"Status modal trigger UI config type: {ui_config.type}")
                await self._enter_status_modal_mode(ui_config)
                return {"success": True, "status_modal_activated": True}
            else:
                logger.warning("Status modal trigger received without ui_config")
                return {"success": False, "error": "Missing ui_config"}
        except Exception as e:
            logger.error(f"Error handling status modal trigger: {e}")
            return {"success": False, "error": str(e)}

    async def _enter_status_modal_mode(self, ui_config):
        """Enter status modal mode - modal confined to status area.

        Args:
            ui_config: Status modal configuration.
        """
        try:
            # Set status modal mode
            self.command_mode = CommandMode.STATUS_MODAL
            self.current_status_modal_config = ui_config
            logger.info(f"Entered status modal mode: {ui_config.title}")

            # Unlike full modals, status modals don't take over the screen
            # They just appear in the status area via the renderer
            await self._update_display(force_render=True)

        except Exception as e:
            logger.error(f"Error entering status modal mode: {e}")
            await self._exit_command_mode()

    async def _handle_status_modal_keypress(self, key_press) -> bool:
        """Handle keypress during status modal mode.

        Args:
            key_press: Parsed key press to process.

        Returns:
            True if key was handled, False otherwise.
        """
        try:
            logger.info(
                f"Status modal received key: name='{key_press.name}', char='{key_press.char}', code={key_press.code}"
            )

            if key_press.name == "Escape":
                logger.info("Escape key detected, closing status modal")
                await self._exit_status_modal_mode()
                return True
            elif key_press.name == "Enter":
                logger.info("Enter key detected, closing status modal")
                await self._exit_status_modal_mode()
                return True
            elif key_press.char and ord(key_press.char) == 3:  # Ctrl+C
                logger.info("Ctrl+C detected, closing status modal")
                await self._exit_status_modal_mode()
                return True
            else:
                logger.info(f"Unhandled key in status modal: {key_press.name}")
                return True

        except Exception as e:
            logger.error(f"Error handling status modal keypress: {e}")
            await self._exit_status_modal_mode()
            return False

    async def _handle_status_modal_input(self, char: str) -> bool:
        """Handle input during status modal mode.

        Args:
            char: Character input to process.

        Returns:
            True if input was handled, False otherwise.
        """
        try:
            # For now, ignore character input in status modals
            # Could add search/filter functionality later
            return True
        except Exception as e:
            logger.error(f"Error handling status modal input: {e}")
            await self._exit_status_modal_mode()
            return False

    async def _exit_status_modal_mode(self):
        """Exit status modal mode and return to normal input."""
        try:
            logger.info("Exiting status modal mode...")
            self.command_mode = CommandMode.NORMAL
            self.current_status_modal_config = None
            logger.info("Status modal mode exited successfully")

            # Refresh display to remove the status modal
            await self._update_display(force_render=True)
            logger.info("Display updated after status modal exit")

        except Exception as e:
            logger.error(f"Error exiting status modal mode: {e}")
            self.command_mode = CommandMode.NORMAL

    async def _handle_status_modal_render(
        self, event_data: Dict[str, Any], context: str = None
    ) -> Dict[str, Any]:
        """Handle status modal render events to provide modal display lines.

        Args:
            event_data: Event data containing render request.
            context: Hook execution context.

        Returns:
            Dictionary with status modal lines if active.
        """
        try:
            if (
                self.command_mode == CommandMode.STATUS_MODAL
                and self.current_status_modal_config
            ):

                # Generate status modal display lines
                modal_lines = self._generate_status_modal_lines(
                    self.current_status_modal_config
                )

                return {"success": True, "status_modal_lines": modal_lines}
            else:
                return {"success": True, "status_modal_lines": []}

        except Exception as e:
            logger.error(f"Error handling status modal render: {e}")
            return {"success": False, "status_modal_lines": []}

    def _generate_status_modal_lines(self, ui_config) -> List[str]:
        """Generate formatted lines for status modal display using visual effects.

        Delegates to StatusModalRenderer component (Phase 1 extraction).

        Args:
            ui_config: UI configuration for the status modal.

        Returns:
            List of formatted lines for display.
        """
        return self._status_modal_renderer.generate_status_modal_lines(ui_config)

    # ==================== STANDARD MODAL OPERATIONS ====================

    async def _show_modal_from_result(self, result):
        """Show a modal from a command result.

        Args:
            result: CommandResult with ui_config for modal display.
        """
        if result and result.ui_config:
            await self._enter_modal_mode(result.ui_config)

    async def _enter_modal_mode(self, ui_config):
        """Enter modal mode and show modal renderer.

        Args:
            ui_config: Modal configuration.
        """
        try:
            # Import modal renderer here to avoid circular imports
            from ...ui.modal_renderer import ModalRenderer

            # Create modal renderer instance with proper config service
            self.modal_renderer = ModalRenderer(
                terminal_renderer=self.renderer,
                visual_effects=getattr(self.renderer, "visual_effects", None),
                config_service=self.config,  # Use config as config service
            )

            # Pause render loop during modal
            self.renderer.writing_messages = True
            self.renderer.clear_active_area()

            # Set modal mode
            self.command_mode = CommandMode.MODAL
            logger.info(f"Command mode set to: {self.command_mode}")

            # Show the modal (handles its own alternate buffer)
            await self.modal_renderer.show_modal(ui_config)

            logger.info("Entered modal mode")

        except Exception as e:
            logger.error(f"Error entering modal mode: {e}")
            self.command_mode = CommandMode.NORMAL
            self.renderer.writing_messages = False

    async def _refresh_modal_display(self):
        """Refresh modal display after widget interactions."""
        try:
            if self.modal_renderer and hasattr(
                self.modal_renderer, "current_ui_config"
            ):

                # CRITICAL FIX: Force complete display clearing to prevent duplication
                # Clear active area completely before refresh
                self.renderer.clear_active_area()

                # Clear any message buffers that might accumulate content
                if hasattr(self.renderer, "message_renderer"):
                    if hasattr(self.renderer.message_renderer, "buffer"):
                        self.renderer.message_renderer.buffer.clear_buffer()
                    # Also clear any accumulated messages in the renderer
                    if hasattr(self.renderer.message_renderer, "clear_messages"):
                        self.renderer.message_renderer.clear_messages()

                # Re-render the modal with current widget states (preserve widgets!)
                modal_lines = self.modal_renderer._render_modal_box(
                    self.modal_renderer.current_ui_config,
                    preserve_widgets=True,
                )
                # FIXED: Use state_manager.render_modal_content() instead of _render_modal_lines()
                # to avoid re-calling prepare_modal_display() which causes buffer switching
                if self.modal_renderer.state_manager:
                    self.modal_renderer.state_manager.render_modal_content(
                        modal_lines
                    )
                else:
                    # Fallback to old method if state_manager not available
                    await self.modal_renderer._render_modal_lines(modal_lines)
            else:
                pass
        except Exception as e:
            logger.error(f"Error refreshing modal display: {e}")

    def _has_pending_modal_changes(self) -> bool:
        """Check if there are unsaved changes in modal widgets."""
        if not self.modal_renderer or not self.modal_renderer.widgets:
            return False
        for widget in self.modal_renderer.widgets:
            if hasattr(widget, '_pending_value') and widget._pending_value is not None:
                # Check if pending value differs from current config value
                current = widget.get_value() if hasattr(widget, 'get_value') else None
                if widget._pending_value != current:
                    return True
        return False

    async def _show_save_confirmation(self):
        """Show save confirmation prompt in modal."""
        # Update modal footer to show confirmation prompt
        if self.modal_renderer:
            self.modal_renderer._save_confirm_active = True
            await self._refresh_modal_display()

    async def _handle_save_confirmation(self, key_press) -> bool:
        """Handle y/n input for save confirmation."""
        if key_press.char and key_press.char.lower() == 'y':
            logger.info("User confirmed save")
            self._pending_save_confirm = False
            if self.modal_renderer:
                self.modal_renderer._save_confirm_active = False
            await self._save_and_exit_modal()
            return True
        elif key_press.char and key_press.char.lower() == 'n':
            logger.info("User declined save")
            self._pending_save_confirm = False
            if self.modal_renderer:
                self.modal_renderer._save_confirm_active = False
            await self._exit_modal_mode()
            return True
        elif key_press.name == "Escape":
            # Cancel confirmation, stay in modal
            logger.info("User cancelled confirmation")
            self._pending_save_confirm = False
            if self.modal_renderer:
                self.modal_renderer._save_confirm_active = False
            await self._refresh_modal_display()
            return True
        return False

    async def _save_and_exit_modal(self):
        """Save modal changes and exit modal mode."""
        try:
            if self.modal_renderer:
                # Check if this is a form modal with form_action
                modal_config = getattr(self.modal_renderer, 'current_ui_config', None)
                form_action = None
                if modal_config and hasattr(modal_config, 'modal_config'):
                    form_action = modal_config.modal_config.get('form_action')

                if form_action and self.modal_renderer.widgets:
                    # Collect form data from widgets
                    form_data = {}
                    for widget in self.modal_renderer.widgets:
                        widget_type = widget.__class__.__name__
                        config_path = getattr(widget, 'config_path', None)
                        pending = getattr(widget, '_pending_value', 'NO_ATTR')
                        logger.info(f"Widget: {widget_type}, config_path={config_path}, _pending_value={pending}")

                        if hasattr(widget, 'config_path') and widget.config_path:
                            # Use field name (last part of config path)
                            field_name = widget.config_path.split('.')[-1]
                            # Always use get_pending_value() which returns:
                            # - _pending_value if user modified the field
                            # - Original value from config if not modified
                            # This ensures edit forms preserve unmodified values
                            if hasattr(widget, 'get_pending_value'):
                                form_data[field_name] = widget.get_pending_value()
                            elif hasattr(widget, '_pending_value') and widget._pending_value is not None:
                                form_data[field_name] = widget._pending_value
                            else:
                                form_data[field_name] = ""

                    logger.info(f"Form submission: action={form_action}, data={form_data}")

                    # Get any extra fields from modal_config (like edit_profile_name)
                    extra_fields = {}
                    if modal_config and hasattr(modal_config, 'modal_config'):
                        mc = modal_config.modal_config
                        # Pass through known extra fields for edit operations
                        for field in ['edit_profile_name', 'edit_agent_name', 'edit_skill_name']:
                            if field in mc:
                                extra_fields[field] = mc[field]

                    # Exit modal first
                    await self._exit_modal_mode()

                    # Emit MODAL_COMMAND_SELECTED with form action and data
                    context = {
                        "command": {
                            "action": form_action,
                            "form_data": form_data,
                            **extra_fields,  # Include edit_profile_name etc.
                        },
                        "source": "modal_form"
                    }
                    results = await self.event_bus.emit_with_hooks(
                        EventType.MODAL_COMMAND_SELECTED,
                        context,
                        "input_handler"
                    )

                    # Get modified data from hook results
                    final_data = results.get("main", {}).get("final_data", {}) if results else {}

                    # Display messages if returned
                    if final_data.get("display_messages"):
                        if hasattr(self.renderer, 'message_coordinator'):
                            self.renderer.message_coordinator.display_message_sequence(
                                final_data["display_messages"]
                            )

                    # Show modal if plugin returned one
                    if final_data.get("show_modal"):
                        from ...events.models import UIConfig
                        modal_config = final_data["show_modal"]
                        ui_config = UIConfig(type="modal", title=modal_config.get("title", ""), modal_config=modal_config)
                        await self._enter_modal_mode(ui_config)

                    return

                # Fallback: use action handler for config-based modals
                if hasattr(self.modal_renderer, "action_handler"):
                    result = await self.modal_renderer.action_handler.handle_action(
                        "save", self.modal_renderer.widgets
                    )
                    if not result.get("success"):
                        logger.warning(
                            f"Failed to save modal changes: {result.get('message', 'Unknown error')}"
                        )

            await self._exit_modal_mode()
        except Exception as e:
            logger.error(f"Error saving and exiting modal: {e}")
            await self._exit_modal_mode()

    async def _exit_modal_mode(self):
        """Exit modal mode using existing patterns."""
        try:
            # Close modal renderer (handles its own terminal restoration)
            if self.modal_renderer:
                _ = self.modal_renderer.close_modal()
                self.modal_renderer.widgets = []
                self.modal_renderer.focused_widget_index = 0
                self.modal_renderer = None

            # Return to normal mode
            self.command_mode = CommandMode.NORMAL

            # Resume render loop
            self.renderer.writing_messages = False
            self.renderer.invalidate_render_cache()
            await self._update_display(force_render=True)

        except Exception as e:
            logger.error(f"Error exiting modal mode: {e}")
            self.command_mode = CommandMode.NORMAL
            self.modal_renderer = None
            self.renderer.writing_messages = False

    async def _exit_modal_mode_minimal(self):
        """Exit modal mode WITHOUT rendering input - for commands that display their own content.

        Use this when a command (like /branch, /resume) will immediately display its own
        content after modal closes. This prevents duplicate input boxes.

        CRITICAL STATE MANAGEMENT:
        - input_line_written=True: Marks content exists on screen
        - last_line_count=0: Prevents clear_active_area() from clearing stale lines
          (after modal exit, the stale last_line_count could clear into banner)
        """
        try:
            # Close modal renderer (handles its own terminal restoration via alternate buffer)
            if self.modal_renderer:
                _ = self.modal_renderer.close_modal()
                self.modal_renderer.widgets = []
                self.modal_renderer.focused_widget_index = 0
                self.modal_renderer = None

            # Return to normal mode
            self.command_mode = CommandMode.NORMAL

            # KEEP writing_messages=True to block render loop!
            # The calling command's display_message_sequence() will set it False when done.
            # This prevents the race condition where render loop runs before command displays.
            # self.renderer.writing_messages = False  # DON'T DO THIS - causes race condition

            # After modal closes (alternate buffer exit), the OLD input box from before
            # the modal is restored on screen. We need clear_active_area() in
            # display_message_sequence() to clear it.
            #
            # CRITICAL: Set input_line_written=True so clear_active_area() will actually clear!
            # When the modal opened, clear_active_area() set input_line_written=False.
            # Now that we're back to main buffer with old input box, we need this True.
            self.renderer.input_line_written = True
            # last_line_count should still have the correct value from before modal opened
            self.renderer.invalidate_render_cache()
            # NOTE: No _update_display() call here - command will handle display

        except Exception as e:
            logger.error(f"Error exiting modal mode (minimal): {e}")
            self.command_mode = CommandMode.NORMAL
            self.modal_renderer = None
            # Keep render state as-is for clearing
            self.renderer.invalidate_render_cache()
