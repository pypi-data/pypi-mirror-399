"""Display controller component for Kollabor CLI.

Responsible for coordinating terminal display updates during input handling.
This is a thin wrapper that manages rendering state and delegates to the terminal renderer.
"""

import asyncio
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DisplayController:
    """Controls display updates during input handling.

    This component manages:
    - Display updates from buffer changes
    - Rendering pause/resume for special effects (Matrix, etc.)
    - Cursor position tracking

    Attributes:
        renderer: Terminal renderer for actual rendering.
        buffer_manager: Buffer manager for getting display content.
        error_handler: Error handler for display errors.
    """

    def __init__(
        self,
        renderer: Any,
        buffer_manager: Any,
        error_handler: Optional[Any] = None,
    ) -> None:
        """Initialize the display controller.

        Args:
            renderer: Terminal renderer instance.
            buffer_manager: Buffer manager for display content.
            error_handler: Optional error handler for display errors.
        """
        self.renderer = renderer
        self.buffer_manager = buffer_manager
        self.error_handler = error_handler

        # Rendering state
        self.rendering_paused = False
        self._last_cursor_pos = 0

        logger.debug("DisplayController initialized")

    async def update_display(self, force_render: bool = False) -> None:
        """Update the terminal display with current buffer state.

        Args:
            force_render: If True, force immediate rendering even if paused.
        """
        try:
            # Skip rendering if paused (during special effects like Matrix)
            if self.rendering_paused and not force_render:
                return

            buffer_content, cursor_pos = self.buffer_manager.get_display_info()

            # Update renderer with buffer content and cursor position
            self.renderer.input_buffer = buffer_content
            self.renderer.cursor_position = cursor_pos

            # Force immediate rendering if requested (needed for paste operations)
            if force_render:
                await self._force_render()

            # Only update cursor if position changed
            if cursor_pos != self._last_cursor_pos:
                # Could implement cursor positioning in renderer
                self._last_cursor_pos = cursor_pos

        except Exception as e:
            if self.error_handler:
                from ..input_errors import ErrorType, ErrorSeverity
                await self.error_handler.handle_error(
                    ErrorType.SYSTEM_ERROR,
                    f"Error updating display: {e}",
                    ErrorSeverity.LOW,
                    {"buffer_manager": self.buffer_manager},
                )
            else:
                logger.error(f"Error updating display: {e}")

    async def _force_render(self) -> None:
        """Force immediate rendering of the display."""
        try:
            if hasattr(
                self.renderer, "render_active_area"
            ) and asyncio.iscoroutinefunction(
                self.renderer.render_active_area
            ):
                await self.renderer.render_active_area()
            elif hasattr(
                self.renderer, "render_input"
            ) and asyncio.iscoroutinefunction(self.renderer.render_input):
                await self.renderer.render_input()
            elif hasattr(self.renderer, "render_active_area"):
                self.renderer.render_active_area()
            elif hasattr(self.renderer, "render_input"):
                self.renderer.render_input()
        except Exception as e:
            logger.debug(f"Force render failed: {e}")
            # Continue without forced render

    def pause_rendering(self) -> None:
        """Pause all UI rendering for special effects."""
        self.rendering_paused = True
        logger.debug("Input rendering paused")

    def resume_rendering(self) -> None:
        """Resume normal UI rendering."""
        self.rendering_paused = False
        logger.debug("Input rendering resumed")

    @property
    def last_cursor_pos(self) -> int:
        """Get the last cursor position."""
        return self._last_cursor_pos

    @last_cursor_pos.setter
    def last_cursor_pos(self, value: int) -> None:
        """Set the last cursor position."""
        self._last_cursor_pos = value
