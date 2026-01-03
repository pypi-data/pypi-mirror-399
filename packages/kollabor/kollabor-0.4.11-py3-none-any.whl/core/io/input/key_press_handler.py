"""Key press handler component for Kollabor CLI.

Responsible for processing keyboard input and dispatching to appropriate handlers.
Handles character processing, key press dispatch, Enter/Escape keys, and hook integration.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable, Awaitable

from ...events import EventType
from ...events.models import CommandMode
from ..key_parser import KeyParser, KeyPress, KeyType as KeyTypeEnum

logger = logging.getLogger(__name__)


class KeyPressHandler:
    """Handles key press processing and dispatch.

    This component manages:
    - Character processing with paste detection hooks
    - Key press event emission and plugin integration
    - Key dispatch to specific handlers (Enter, Escape, arrows, etc.)
    - Command mode detection and routing
    - Status view navigation (Alt+Left/Right arrows)

    Attributes:
        buffer_manager: Buffer manager for text manipulation.
        key_parser: Parser for converting raw input to KeyPress objects.
        event_bus: Event bus for emitting key press events.
        error_handler: Error handler for key processing errors.
        display_controller: Controller for display updates.
        renderer: Terminal renderer for display clearing.
    """

    def __init__(
        self,
        buffer_manager: Any,
        key_parser: KeyParser,
        event_bus: Any,
        error_handler: Any,
        display_controller: Any,
        paste_processor: Any,
        renderer: Any,
        command_mode_handler: Optional[Any] = None,
    ) -> None:
        """Initialize the key press handler.

        Args:
            buffer_manager: Buffer manager instance.
            key_parser: Key parser instance.
            event_bus: Event bus for emitting events.
            error_handler: Error handler for key processing errors.
            display_controller: Display controller for UI updates.
            paste_processor: Paste processor for paste detection.
            renderer: Terminal renderer for display clearing.
            command_mode_handler: Optional handler for command mode operations.
        """
        self.buffer_manager = buffer_manager
        self.key_parser = key_parser
        self.event_bus = event_bus
        self.error_handler = error_handler
        self.display_controller = display_controller
        self.paste_processor = paste_processor
        self.renderer = renderer
        self.command_mode_handler = command_mode_handler

        # Callbacks for methods we don't own (set by parent)
        self._enter_command_mode_callback: Optional[Callable[[], Awaitable[None]]] = None
        self._handle_command_mode_keypress_callback: Optional[
            Callable[[KeyPress], Awaitable[bool]]
        ] = None
        self._handle_status_view_previous_callback: Optional[
            Callable[[], Awaitable[None]]
        ] = None
        self._handle_status_view_next_callback: Optional[
            Callable[[], Awaitable[None]]
        ] = None
        self._expand_paste_placeholders_callback: Optional[
            Callable[[str], str]
        ] = None

        # State tracking
        self._command_mode = CommandMode.NORMAL

        logger.debug("KeyPressHandler initialized")

    def set_callbacks(
        self,
        enter_command_mode: Optional[Callable[[], Awaitable[None]]] = None,
        handle_command_mode_keypress: Optional[
            Callable[[KeyPress], Awaitable[bool]]
        ] = None,
        handle_status_view_previous: Optional[Callable[[], Awaitable[None]]] = None,
        handle_status_view_next: Optional[Callable[[], Awaitable[None]]] = None,
        expand_paste_placeholders: Optional[Callable[[str], str]] = None,
    ) -> None:
        """Set callbacks for methods owned by parent InputHandler.

        Args:
            enter_command_mode: Callback to enter command mode.
            handle_command_mode_keypress: Callback to handle command mode keys.
            handle_status_view_previous: Callback to switch to previous status view.
            handle_status_view_next: Callback to switch to next status view.
            expand_paste_placeholders: Callback to expand paste placeholders.
        """
        self._enter_command_mode_callback = enter_command_mode
        self._handle_command_mode_keypress_callback = handle_command_mode_keypress
        self._handle_status_view_previous_callback = handle_status_view_previous
        self._handle_status_view_next_callback = handle_status_view_next
        self._expand_paste_placeholders_callback = expand_paste_placeholders

    @property
    def command_mode(self) -> CommandMode:
        """Get current command mode.

        Delegates to command_mode_handler if available for consistent state.
        """
        if self.command_mode_handler:
            return self.command_mode_handler.command_mode
        return self._command_mode

    @command_mode.setter
    def command_mode(self, value: CommandMode) -> None:
        """Set current command mode."""
        if self.command_mode_handler:
            self.command_mode_handler.command_mode = value
        self._command_mode = value

    async def process_character(self, char: str) -> None:
        """Process a single character input.

        Args:
            char: Character received from terminal.
        """
        try:
            current_time = time.time()

            # Check for slash command initiation
            # (before parsing for immediate response)
            if (
                char == "/"
                and self.buffer_manager.is_empty
                and self.command_mode == CommandMode.NORMAL
            ):
                if self._enter_command_mode_callback:
                    await self._enter_command_mode_callback()
                else:
                    logger.warning(
                        "Slash command detected but no enter_command_mode callback set"
                    )
                return

            # SECONDARY PASTE DETECTION:
            # Character-by-character timing (DISABLED)
            # This is a fallback system - primary chunk detection
            # above handles most cases
            if self.paste_processor.paste_detection_enabled:
                # Currently False - secondary system disabled
                paste_handled = await self.paste_processor.simple_paste_detection(
                    char, current_time
                )
                if paste_handled:
                    # Character consumed by paste detection,
                    # skip normal processing
                    return

            # Parse character into structured key press
            # (this handles escape sequences)
            key_press = self.key_parser.parse_char(char)
            if not key_press:
                # For modal modes, add timeout-based
                # standalone escape detection
                if self.command_mode in (CommandMode.MODAL, CommandMode.STATUS_MODAL, CommandMode.LIVE_MODAL):
                    # Schedule delayed check for standalone escape
                    # (100ms delay)
                    async def delayed_escape_check():
                        await asyncio.sleep(0.1)
                        standalone_escape = (
                            self.key_parser.check_for_standalone_escape()
                        )
                        if standalone_escape:
                            if self._handle_command_mode_keypress_callback:
                                await self._handle_command_mode_keypress_callback(
                                    standalone_escape
                                )

                    asyncio.create_task(delayed_escape_check())
                # Incomplete escape sequence - wait for more characters
                return

            # Check for slash command mode handling AFTER parsing
            # (so arrow keys work)
            if self.command_mode != CommandMode.NORMAL:
                logger.info(
                    f"Processing key '{key_press.name}' "
                    f"in command mode: {self.command_mode}"
                )
                if self._handle_command_mode_keypress_callback:
                    handled = await self._handle_command_mode_keypress_callback(
                        key_press
                    )
                    if handled:
                        return

            # Emit key press event for plugins
            key_result = await self.event_bus.emit_with_hooks(
                EventType.KEY_PRESS,
                {
                    "key": key_press.name,
                    "char_code": key_press.code,
                    "key_type": key_press.type.value,
                    "modifiers": key_press.modifiers,
                },
                "input",
            )

            # Check if any plugin handled this key
            prevent_default = self._check_prevent_default(key_result)

            # Process key if not prevented by plugins
            if not prevent_default:
                await self._handle_key_press(key_press)

            # Update renderer
            await self.display_controller.update_display()

        except Exception as e:
            from ..input_errors import ErrorType, ErrorSeverity

            await self.error_handler.handle_error(
                ErrorType.PARSING_ERROR,
                f"Error processing character: {e}",
                ErrorSeverity.MEDIUM,
                {"char": repr(char), "buffer_manager": self.buffer_manager},
            )

    def _check_prevent_default(self, key_result: Dict[str, Any]) -> bool:
        """Check if plugins want to prevent default key handling.

        Args:
            key_result: Result from key press event.

        Returns:
            True if default handling should be prevented.
        """
        if "main" in key_result:
            for hook_result in key_result["main"].values():
                if isinstance(hook_result, dict) and hook_result.get(
                    "prevent_default"
                ):
                    return True
        return False

    async def _handle_key_press(self, key_press: KeyPress) -> None:
        """Handle a parsed key press.

        Args:
            key_press: Parsed key press event.
        """
        # Process key press
        try:
            # Log all key presses for debugging
            logger.info(
                f"Key press: name='{key_press.name}', "
                f"char='{key_press.char}', code={key_press.code}, "
                f"type={key_press.type}, "
                f"modifiers={getattr(key_press, 'modifiers', None)}"
            )

            # CRITICAL FIX: Modal input isolation
            # capture ALL input when in modal mode
            if self.command_mode == CommandMode.MODAL:
                logger.info(
                    f"Modal mode active - routing ALL input "
                    f"to modal handler: {key_press.name}"
                )
                if self._handle_command_mode_keypress_callback:
                    await self._handle_command_mode_keypress_callback(key_press)
                return

            # Handle control keys
            if self.key_parser.is_control_key(key_press, "Ctrl+C"):
                logger.info("Ctrl+C received")
                raise KeyboardInterrupt

            elif self.key_parser.is_control_key(key_press, "Enter"):
                await self._handle_enter()

            elif self.key_parser.is_control_key(key_press, "Backspace"):
                self.buffer_manager.delete_char()

            elif key_press.name == "Escape":
                await self._handle_escape()

            elif key_press.name == "Delete":
                self.buffer_manager.delete_forward()

            # Handle arrow keys for cursor movement and history
            elif key_press.name == "ArrowLeft":
                moved = self.buffer_manager.move_cursor("left")
                if moved:
                    logger.debug(
                        f"Arrow Left: cursor moved to position {self.buffer_manager.cursor_position}"
                    )
                    await self.display_controller.update_display(force_render=True)

            elif key_press.name == "ArrowRight":
                moved = self.buffer_manager.move_cursor("right")
                if moved:
                    logger.debug(
                        f"Arrow Right: cursor moved to position {self.buffer_manager.cursor_position}"
                    )
                    await self.display_controller.update_display(force_render=True)

            elif key_press.name == "ArrowUp":
                self.buffer_manager.navigate_history("up")
                await self.display_controller.update_display(force_render=True)

            elif key_press.name == "ArrowDown":
                self.buffer_manager.navigate_history("down")
                await self.display_controller.update_display(force_render=True)

            # Handle Home/End keys
            elif key_press.name == "Home":
                self.buffer_manager.move_to_start()
                await self.display_controller.update_display(force_render=True)

            elif key_press.name == "End":
                self.buffer_manager.move_to_end()
                await self.display_controller.update_display(force_render=True)

            # Handle Option/Alt+Arrow keys for status view navigation
            # Support both Alt+Arrow and Alt+b/f (macOS terminals often send the latter)
            elif key_press.name in ("Alt+ArrowLeft", "Alt+b"):
                logger.info(
                    f"{key_press.name} detected - switching to previous status view"
                )
                if self._handle_status_view_previous_callback:
                    await self._handle_status_view_previous_callback()

            elif key_press.name in ("Alt+ArrowRight", "Alt+f"):
                logger.info(
                    f"{key_press.name} detected - switching to next status view"
                )
                if self._handle_status_view_next_callback:
                    await self._handle_status_view_next_callback()

            # Handle Cmd key combinations (mapped to Ctrl sequences on macOS)
            elif self.key_parser.is_control_key(key_press, "Ctrl+A"):
                logger.info("Ctrl+A (Cmd+Left) - moving cursor to start")
                self.buffer_manager.move_to_start()
                await self.display_controller.update_display(force_render=True)

            elif self.key_parser.is_control_key(key_press, "Ctrl+E"):
                logger.info("Ctrl+E (Cmd+Right) - moving cursor to end")
                self.buffer_manager.move_to_end()
                await self.display_controller.update_display(force_render=True)

            elif self.key_parser.is_control_key(key_press, "Ctrl+U"):
                logger.info("Ctrl+U (Cmd+Backspace) - clearing line")
                self.buffer_manager.clear()
                await self.display_controller.update_display(force_render=True)

            # Handle printable characters
            elif self.key_parser.is_printable_char(key_press):
                # Normal character processing
                success = self.buffer_manager.insert_char(key_press.char)
                if not success:
                    from ..input_errors import ErrorType, ErrorSeverity

                    await self.error_handler.handle_error(
                        ErrorType.BUFFER_ERROR,
                        "Failed to insert character - buffer limit reached",
                        ErrorSeverity.LOW,
                        {
                            "char": key_press.char,
                            "buffer_manager": self.buffer_manager,
                        },
                    )

            # Handle other special keys (F1-F12, etc.)
            elif key_press.type == KeyTypeEnum.EXTENDED:
                logger.debug(f"Extended key pressed: {key_press.name}")
                # Could emit special events for function keys, etc.

        except Exception as e:
            from ..input_errors import ErrorType, ErrorSeverity

            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling key press: {e}",
                ErrorSeverity.MEDIUM,
                {
                    "key_press": key_press,
                    "buffer_manager": self.buffer_manager,
                },
            )

    async def _handle_enter(self) -> None:
        """Handle Enter key press with enhanced validation."""
        try:
            if self.buffer_manager.is_empty:
                return

            # Validate input before processing
            validation_errors = self.buffer_manager.validate_content()
            if validation_errors:
                for error in validation_errors:
                    logger.warning(f"Input validation warning: {error}")

            # Get message and clear buffer
            message = self.buffer_manager.get_content_and_clear()

            # Check if this is a slash command - handle immediately without paste expansion
            if message.strip().startswith("/"):
                logger.info(
                    f"Detected slash command, bypassing paste expansion: '{message}'"
                )
                expanded_message = message
            else:
                # GENIUS PASTE BUCKET: Immediate expansion - no waiting needed!
                logger.debug(f"GENIUS SUBMIT: Original message: '{message}'")
                logger.debug(
                    f"GENIUS SUBMIT: Paste bucket contains: {list(self.paste_processor.paste_bucket.keys())}"
                )

                if self._expand_paste_placeholders_callback:
                    expanded_message = self._expand_paste_placeholders_callback(
                        message
                    )
                else:
                    # Fallback to direct expansion if callback not set
                    expanded_message = self.paste_processor.expand_paste_placeholders(
                        message
                    )

                logger.debug(
                    f"GENIUS SUBMIT: Final expanded: '{expanded_message[:100]}...' ({len(expanded_message)} chars)"
                )

            # Add to history (with expanded content)
            self.buffer_manager.add_to_history(expanded_message)

            # CRITICAL: Clear the input display before emitting event
            # This matches the original InputHandler._handle_enter behavior
            self.renderer.input_buffer = ""
            self.renderer.clear_active_area()

            # Emit user input event (with expanded content!)
            await self.event_bus.emit_with_hooks(
                EventType.USER_INPUT,
                {
                    "message": expanded_message,
                    "validation_errors": validation_errors,
                },
                "user",
            )

            logger.debug(
                f"Processed user input: {message[:100]}..."
                if len(message) > 100
                else f"Processed user input: {message}"
            )

        except Exception as e:
            from ..input_errors import ErrorType, ErrorSeverity

            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling Enter key: {e}",
                ErrorSeverity.HIGH,
                {"buffer_manager": self.buffer_manager},
            )

    async def _handle_escape(self) -> None:
        """Handle Escape key press for request cancellation."""
        try:
            logger.info("_handle_escape called - emitting CANCEL_REQUEST event")

            # Emit cancellation event
            result = await self.event_bus.emit_with_hooks(
                EventType.CANCEL_REQUEST,
                {"reason": "user_escape", "source": "input_handler"},
                "input",
            )

            logger.info(
                f"ESC key pressed - cancellation request sent, result: {result}"
            )

        except Exception as e:
            from ..input_errors import ErrorType, ErrorSeverity

            await self.error_handler.handle_error(
                ErrorType.EVENT_ERROR,
                f"Error handling Escape key: {e}",
                ErrorSeverity.MEDIUM,
                {"buffer_manager": self.buffer_manager},
            )
