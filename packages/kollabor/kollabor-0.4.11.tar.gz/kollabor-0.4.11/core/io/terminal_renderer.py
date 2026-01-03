"""Terminal rendering system for Kollabor CLI.

This module provides comprehensive terminal rendering for the Kollabor CLI
application, including visual effects, layout management, message
display, and terminal state management.
"""

import asyncio
import logging
from collections import deque
from typing import TYPE_CHECKING, List, Optional

from .layout import LayoutManager, ThinkingAnimationManager
from .message_coordinator import MessageDisplayCoordinator
from .message_renderer import MessageRenderer
from .status_renderer import StatusRenderer
from .terminal_state import TerminalState
from .visual_effects import VisualEffects

if TYPE_CHECKING:
    from ..config.manager import ConfigManager
    from .input_handler import InputHandler

logger = logging.getLogger(__name__)


class TerminalRenderer:
    """Advanced terminal renderer with modular architecture.

    Features:
    - Modular visual effects system
    - Advanced layout management
    - Comprehensive status rendering
    - Message formatting and display
    - Terminal state management
    """

    def __init__(
        self, event_bus=None, config: Optional["ConfigManager"] = None
    ) -> None:
        """Initialize the terminal renderer with modern architecture."""
        self.event_bus = event_bus
        self._app_config: Optional["ConfigManager"] = (
            config  # Store config for render cache settings
        )
        self.input_handler: Optional["InputHandler"] = (
            None  # Will be set externally if needed
        )

        # Initialize core components
        self.terminal_state = TerminalState()
        self.visual_effects = VisualEffects()
        self.layout_manager = LayoutManager()
        self.status_renderer = StatusRenderer()
        self.message_renderer = MessageRenderer(
            self.terminal_state, self.visual_effects
        )

        # Initialize thinking animation manager
        self.thinking_animation = ThinkingAnimationManager()

        # Initialize message display coordinator for unified message handling
        self.message_coordinator = MessageDisplayCoordinator(self)

        # Interface properties
        self.input_buffer = ""
        self.cursor_position = 0
        self.thinking_active = False

        # State management
        self.conversation_active = False
        self.writing_messages = False
        self.input_line_written = False
        self.last_line_count = 0
        self.active_area_start_position = (
            None  # Track where active area starts for clean clearing
        )

        # Render optimization: cache to prevent unnecessary writes
        self._last_render_content: List[str] = []  # Cache of last rendered content
        self._render_cache_enabled = True  # Enable/disable render caching

        # Configuration (will be updated by config methods)
        self.thinking_effect = "shimmer"

        logger.info("Advanced terminal renderer initialized")

    def enter_raw_mode(self) -> None:
        """Enter raw terminal mode for character-by-character input."""
        success = self.terminal_state.enter_raw_mode()
        if not success:
            logger.warning("Failed to enter raw mode")

    def exit_raw_mode(self) -> None:
        """Exit raw terminal mode and restore settings."""
        success = self.terminal_state.exit_raw_mode()
        if not success:
            logger.warning("Failed to exit raw mode")

    def create_kollabor_banner(self, version: str = "v1.0.0") -> str:
        """Create a beautiful Kollabor ASCII banner with gradient.

        Args:
            version: Version string to display next to the banner.

        Returns:
            Formatted banner string with gradient colors and version.
        """
        return self.visual_effects.create_banner(version)

    def write_message(self, message: str, apply_gradient: bool = True) -> None:
        """Write a message to the conversation area.

        Args:
            message: The message to write.
            apply_gradient: Whether to apply gradient effect.
        """
        self.message_renderer.write_message(message, apply_gradient)
        logger.debug(f"Wrote message: {message[:50]}...")

    def write_streaming_chunk(self, chunk: str) -> None:
        """Write a streaming chunk to the conversation area immediately.

        Args:
            chunk: The text chunk to write without buffering.
        """
        # Use message renderer for proper formatting
        self.message_renderer.write_streaming_chunk(chunk)
        logger.debug(f"Wrote streaming chunk: {chunk[:20]}...")

    def write_user_message(self, message: str) -> None:
        """Write a user message with gradient effect.

        Args:
            message: The user message to write.
        """
        self.message_renderer.write_user_message(message)

    def write_hook_message(self, content: str, **metadata) -> None:
        """Write a hook message using coordinated display.

        Args:
            content: Hook message content.
            **metadata: Additional metadata.
        """
        # Route hook messages through the coordinator to prevent conflicts
        self.message_coordinator.display_message_sequence(
            [("system", content, metadata)]
        )
        logger.debug(f"Wrote hook message: {content[:50]}...")

    def update_thinking(self, active: bool, message: str = "") -> None:
        """Update the thinking animation state.

        Args:
            active: Whether thinking animation should be active.
            message: Optional thinking message to display.
        """
        self.thinking_active = active

        if active and message:
            self.thinking_animation.start_thinking(message)
            logger.debug(f"Started thinking: {message}")
        elif not active:
            completion_msg = self.thinking_animation.stop_thinking()
            if completion_msg:
                logger.info(completion_msg)

    def set_thinking_effect(self, effect: str) -> None:
        """Set the thinking text effect.

        Args:
            effect: Effect type - "dim", "shimmer", or "normal"
        """
        if effect in ["dim", "shimmer", "normal"]:
            self.thinking_effect = effect
            self.visual_effects.configure_effect("thinking", enabled=True)
            logger.debug(f"Set thinking effect to: {effect}")
        else:
            logger.warning(f"Invalid thinking effect: {effect}")

    def configure_shimmer(self, speed: int, wave_width: int) -> None:
        """Configure shimmer effect parameters.

        Args:
            speed: Number of frames between shimmer updates
            wave_width: Number of characters in the shimmer wave
        """
        self.visual_effects.configure_effect("thinking", speed=speed, width=wave_width)
        logger.debug(f"Configured shimmer: speed={speed}, wave_width={wave_width}")

    def configure_thinking_limit(self, limit: int) -> None:
        """Configure the thinking message limit.

        Args:
            limit: Maximum number of thinking messages to keep
        """
        self.thinking_animation.messages = deque(maxlen=limit)
        logger.debug(f"Configured thinking message limit: {limit}")

    async def render_active_area(self) -> None:
        """Render the active input/status area using modern components.

        This method renders dynamic interface parts:
        thinking animation, input prompt, and status lines.
        """
        # CRITICAL: Skip ALL rendering when modal is active to prevent interference
        if hasattr(self, "input_handler") and self.input_handler:
            try:
                from ..events.models import CommandMode

                if self.input_handler.command_mode in (
                    CommandMode.MODAL,
                    CommandMode.LIVE_MODAL,
                ):
                    return
            except Exception as e:
                logger.error(f"Error checking modal state: {e}")
                pass  # Continue with normal rendering if check fails

        # Skip rendering if currently writing messages, UNLESS we have command menu to display
        if self.writing_messages:
            # Check if any plugin wants to provide enhanced input (like command menu)
            has_enhanced_input = False
            if self.event_bus:
                try:
                    from ..events import EventType

                    result = await self.event_bus.emit_with_hooks(
                        EventType.INPUT_RENDER,
                        {"input_buffer": self.input_buffer},
                        "renderer",
                    )
                    # Check if any plugin provided enhanced input
                    if "main" in result:
                        for hook_result in result["main"].values():
                            if (
                                isinstance(hook_result, dict)
                                and "fancy_input_lines" in hook_result
                            ):
                                has_enhanced_input = True
                                break
                except Exception:
                    pass

            # Only skip rendering if no enhanced input (command menu) is available
            if not has_enhanced_input:
                return

        # Update terminal size and invalidate cache if resized (with 0.9s debouncing)
        old_size = self.terminal_state.get_size()

        # Check if resize has settled (0.9s debounce to prevent rapid re-renders)
        resize_settled = self.terminal_state.check_and_clear_resize_flag()

        size_changed = False
        if resize_settled:
            # Resize has settled - poll actual terminal size
            self.terminal_state.update_size()
            terminal_width, terminal_height = self.terminal_state.get_size()

            # Only trigger aggressive clearing if width reduced by 10% or more
            # Small reductions don't cause artifacts, so we skip clearing for minor changes
            # Height changes don't matter for clearing (only width affects layout)
            width_reduction = (old_size[0] - terminal_width) / old_size[0]
            if terminal_width < old_size[0] and width_reduction >= 0.1:
                size_changed = True
                self.invalidate_render_cache()

                # Note: Input buffer and cursor position are preserved on resize
                # Active area will be cleared by _render_lines() using aggressive clearing
                logger.debug(
                    f"Terminal width reduced by {width_reduction*100:.1f}% ({old_size[0]} -> {terminal_width}) - will use aggressive clearing"
                )
            elif old_size != (terminal_width, terminal_height):
                # Size increased or small reduction - just invalidate cache, no aggressive clearing
                self.invalidate_render_cache()
                logger.debug(
                    f"Terminal size changed: {old_size[0]}x{old_size[1]} -> {terminal_width}x{terminal_height} - cache invalidated, no clearing"
                )
        else:
            # No resize or still debouncing - use current size
            terminal_width, terminal_height = old_size

        self.layout_manager.set_terminal_size(terminal_width, terminal_height)
        self.status_renderer.set_terminal_width(terminal_width)

        lines = []

        # Add safety buffer line at top of active area
        # This provides a "clear zone" for aggressive clearing during resize
        # without deleting conversation content above the active area
        lines.append("")

        # Add thinking animation if active
        if self.thinking_active:
            thinking_lines = self.thinking_animation.get_display_lines(
                lambda text: self.visual_effects.apply_thinking_effect(
                    text, self.thinking_effect
                )
            )
            lines.extend(thinking_lines)

        # Add blank line before input if we have thinking content
        if lines:
            lines.append("")

        # Render input area
        await self._render_input_area(lines)

        # Check if command menu should replace status area
        # logger.info("Checking for command menu lines...")
        command_menu_lines = await self._get_command_menu_lines()
        # logger.info(f"Got {len(command_menu_lines)} command menu lines")
        if command_menu_lines:
            # Replace status with command menu
            lines.extend(command_menu_lines)
        else:
            # Check if status modal should replace status area
            status_modal_lines = await self._get_status_modal_lines()
            if status_modal_lines:
                # Replace status with status modal
                lines.extend(status_modal_lines)
            else:
                # Render status views
                status_lines = self.status_renderer.render_horizontal_layout(
                    self.visual_effects.apply_status_colors
                )
                lines.extend(status_lines)

        # Clear previous render and write new content
        # Pass resize flag to ensure aggressive clearing is used when size changed
        await self._render_lines(lines, size_changed=size_changed)

    async def _render_input_area(self, lines: List[str]) -> None:
        """Render the input area, checking for plugin overrides.

        Args:
            lines: List of lines to append input rendering to.
        """
        # Try to get enhanced input from plugins
        if self.event_bus:
            try:
                from ..events import EventType

                result = await self.event_bus.emit_with_hooks(
                    EventType.INPUT_RENDER,
                    {"input_buffer": self.input_buffer},
                    "renderer",
                )

                # Check if any plugin provided enhanced input
                if "main" in result:
                    for hook_result in result["main"].values():
                        if (
                            isinstance(hook_result, dict)
                            and "fancy_input_lines" in hook_result
                        ):
                            lines.extend(hook_result["fancy_input_lines"])
                            return
            except Exception as e:
                logger.warning(f"Error rendering enhanced input: {e}")

        # Fallback to default input rendering
        if self.thinking_active:
            lines.append(f"> {self.input_buffer}")
        else:
            # Insert cursor at the correct position
            cursor_pos = getattr(self, "cursor_position", 0)
            buffer_text = self.input_buffer

            # Ensure cursor position is within bounds
            cursor_pos = max(0, min(cursor_pos, len(buffer_text)))

            # Debug logging
            logger.debug(
                f"Rendering cursor at position {cursor_pos} in buffer '{buffer_text}'"
            )

            # Insert cursor character at position
            text_with_cursor = buffer_text[:cursor_pos] + "▌" + buffer_text[cursor_pos:]
            lines.append(f"> {text_with_cursor}")

    def _write(self, text: str) -> None:
        """Write text directly to terminal.

        Args:
            text: Text to write.
        """
        # Collect in buffer if buffered mode is active
        if hasattr(self, "_write_buffer") and self._write_buffer is not None:
            self._write_buffer.append(text)
        else:
            self.terminal_state.write_raw(text)

    def _start_buffered_write(self) -> None:
        """Start buffered write mode - collects all writes until flush."""
        self._write_buffer = []

    def _flush_buffered_write(self) -> None:
        """Flush all buffered writes at once to reduce flickering."""
        if hasattr(self, "_write_buffer") and self._write_buffer:
            # Join all buffered content and write in one operation
            self.terminal_state.write_raw("".join(self._write_buffer))
        self._write_buffer = None

    def _get_terminal_width(self) -> int:
        """Get terminal width, with fallback."""
        width, _ = self.terminal_state.get_size()
        return width

    def _apply_status_colors(self, text: str) -> str:
        """Apply semantic colors to status line text (legacy compatibility).

        Args:
            text: The status text to colorize.

        Returns:
            Colorized text with appropriate ANSI codes.
        """
        return self.visual_effects.apply_status_colors(text)

    async def _get_command_menu_lines(self) -> List[str]:
        """Get command menu lines if menu is active.

        Returns:
            List of command menu lines, or empty list if not active.
        """
        if not self.event_bus:
            return []

        try:
            # Check for command menu via COMMAND_MENU_RENDER event
            from ..events import EventType

            # logger.info("🔥 Emitting COMMAND_MENU_RENDER event...")
            result = await self.event_bus.emit_with_hooks(
                EventType.COMMAND_MENU_RENDER,
                {"request": "get_menu_lines"},
                "renderer",
            )
            # logger.info(f"🔥 COMMAND_MENU_RENDER result: {result}")

            # Check if any component provided menu lines
            if "main" in result and "hook_results" in result["main"]:
                for hook_result in result["main"]["hook_results"]:
                    if (
                        isinstance(hook_result, dict)
                        and "result" in hook_result
                        and isinstance(hook_result["result"], dict)
                        and "menu_lines" in hook_result["result"]
                    ):
                        return hook_result["result"]["menu_lines"]

        except Exception as e:
            logger.debug(f"No command menu available: {e}")

        return []

    async def _get_status_modal_lines(self) -> List[str]:
        """Get status modal lines if status modal is active.

        Returns:
            List of status modal lines, or empty list if not active.
        """
        if not self.event_bus:
            return []

        try:
            # Check for status modal via input handler
            from ..events import EventType

            result = await self.event_bus.emit_with_hooks(
                EventType.STATUS_MODAL_RENDER,
                {"request": "get_status_modal_lines"},
                "renderer",
            )

            # Check if any component provided status modal lines
            if "main" in result and "hook_results" in result["main"]:
                for hook_result in result["main"]["hook_results"]:
                    if (
                        isinstance(hook_result, dict)
                        and "result" in hook_result
                        and isinstance(hook_result["result"], dict)
                        and "status_modal_lines" in hook_result["result"]
                    ):
                        return hook_result["result"]["status_modal_lines"]

        except Exception as e:
            logger.debug(f"No status modal available: {e}")

        return []

    async def _render_lines(self, lines: List[str], size_changed: bool = False) -> None:
        """Render lines to terminal with proper clearing.

        Args:
            lines: Lines to render.
            size_changed: True if terminal size changed (triggers aggressive clearing).
        """
        # RENDER OPTIMIZATION: Only render if content actually changed
        # Check if render caching is enabled via config
        if self._app_config is not None:
            cache_enabled = self._app_config.get("terminal.render_cache_enabled", True)
        else:
            cache_enabled = self._render_cache_enabled  # Fallback to local setting

        if cache_enabled and self._last_render_content == lines:
            # Content unchanged - skip rendering entirely
            return

        # Content changed - update cache and proceed with render
        self._last_render_content = lines.copy()

        current_line_count = len(lines)

        # Use buffered write to reduce flickering (especially on Windows)
        # Start buffering BEFORE clearing so clear+redraw happens atomically
        self._start_buffered_write()
        
        if size_changed:
            await asyncio.sleep(1)

        # Clear previous active area (now buffered to reduce flicker)
        if self.input_line_written and hasattr(self, "last_line_count"):
            if size_changed:
                # RESIZE FIX: On resize, restore to saved cursor position (where active area started)
                # and clear everything from there to bottom of screen
                logger.debug(
                    f"🔄 Terminal resize detected (size_changed={size_changed}) - restoring cursor and clearing"
                )

                if self.active_area_start_position:
                    # Restore to where active area started before resize
                    self._write("\033[u")  # Restore cursor position
                    # Move up extra lines to catch box drawing artifacts above saved position
                    self._write("\033[6A")  # Move up 1 line (into safety buffer zone)
                    self._write("\033[1A")  # Move up 1 line (into safety buffer zone)
                    self._write("\n")
                    self._write("\n")
                    self._write("\n")
                    self._write("\n")
                    # Clear from that position to end of screen
                    self._write("\033[J")  # Clear from cursor to end of screen
                else:
                    # Fallback: just clear current line if we don't have saved position
                    self._write("\r\033[2K")  # Clear line
            else:
                # Normal line-by-line clearing when no resize
                self._write("\r\033[2K")  # Clear current line
                for _ in range(self.last_line_count - 1):
                    self._write("\033[A")  # Move cursor up
                    self._write("\r\033[2K")  # Clear line

        # Save cursor position before rendering active area (for future resize handling)
        self._write("\033[s")  # Save cursor position
        self.active_area_start_position = True  # Mark that we have a saved position

        # Write all lines
        for i, line in enumerate(lines):
            if i > 0:
                self._write("\n")
            self._write(f"\r{line}")
             

        # Hide cursor
        self._write("\033[?25l")  # Write hide cursor to buffer too
        
        # Add small sleep to let terminal process ANSI escape sequences on resize
        # This prevents visual artifacts when the terminal is still processing
        if size_changed:
            await asyncio.sleep(.1)
        # Flush all writes at once
        self._flush_buffered_write()

        # Add small sleep to let terminal process ANSI escape sequences on resize
        # This prevents visual artifacts when the terminal is still processing
        if size_changed:
            await asyncio.sleep(.4)

        # Remember line count for next render
        self.last_line_count = current_line_count
        self.input_line_written = True

    def clear_active_area(self, force: bool = False) -> None:
        """Clear the active area before writing conversation messages.

        Args:
            force: If True, clear regardless of input_line_written state.
                   Use for exit cleanup.
        """
        if (force or self.input_line_written) and hasattr(self, "last_line_count"):
            self.terminal_state.clear_line()
            for _ in range(self.last_line_count - 1):
                self.terminal_state.move_cursor_up(1)
                self.terminal_state.clear_line()
            self.input_line_written = False
            self.invalidate_render_cache()  # Force re-render after clearing
            logger.debug("Cleared active area")

    def invalidate_render_cache(self) -> None:
        """Invalidate the render cache to force next render.

        Call this when external changes should force a re-render
        (e.g., terminal resize, configuration changes, manual refresh).
        """
        self._last_render_content.clear()
        logger.debug("Render cache invalidated")

    def set_render_cache_enabled(self, enabled: bool) -> None:
        """Enable or disable render caching.

        Args:
            enabled: True to enable caching, False to disable.
        """
        self._render_cache_enabled = enabled
        if not enabled:
            self._last_render_content.clear()  # Clear cache when disabling
        logger.debug(f"Render cache {'enabled' if enabled else 'disabled'}")

    def get_render_cache_status(self) -> dict:
        """Get render cache status for debugging.

        Returns:
            Dictionary with cache status information.
        """
        return {
            "enabled": self._render_cache_enabled,
            "cached_lines": len(self._last_render_content),
            "last_cached_content": self._last_render_content.copy(),
        }
