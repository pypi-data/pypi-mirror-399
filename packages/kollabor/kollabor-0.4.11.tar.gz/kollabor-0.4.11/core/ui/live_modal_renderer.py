"""Live modal renderer for streaming/updating content.

Uses ModalStateManager for proper terminal state isolation,
with a refresh loop for continuously updating content.
"""

import asyncio
import logging
from typing import List, Callable, Optional, Dict, Any, Awaitable, Union
from dataclasses import dataclass

from ..io.terminal_state import TerminalState
from ..io.visual_effects import ColorPalette
from ..io.key_parser import KeyPress
from .modal_state_manager import ModalStateManager, ModalLayout, ModalDisplayMode

logger = logging.getLogger(__name__)


@dataclass
class LiveModalConfig:
    """Configuration for live modal display."""
    title: str = "Live View"
    footer: str = "Esc to exit"
    refresh_rate: float = 0.5  # Seconds between refreshes
    show_border: bool = True
    passthrough_input: bool = False  # Forward input to external process


class LiveModalRenderer:
    """Renders live-updating content using ModalStateManager.

    Uses the same infrastructure as config/status modals for proper
    terminal state isolation, with an added refresh loop for live content.
    """

    def __init__(self, terminal_state: TerminalState):
        """Initialize live modal renderer.

        Args:
            terminal_state: TerminalState for terminal control.
        """
        self.terminal_state = terminal_state
        self.state_manager = ModalStateManager(terminal_state)
        self.modal_active = False
        self.config: Optional[LiveModalConfig] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._input_callback: Optional[Callable[[KeyPress], Awaitable[bool]]] = None
        self._content_generator: Optional[Callable[[], Union[List[str], Awaitable[List[str]]]]] = None
        self._should_exit = False

    def start_live_modal(
        self,
        content_generator: Callable[[], Union[List[str], Awaitable[List[str]]]],
        config: Optional[LiveModalConfig] = None,
        input_callback: Optional[Callable[[KeyPress], Awaitable[bool]]] = None
    ) -> bool:
        """Start live modal (non-blocking).

        Args:
            content_generator: Function that returns current content lines.
            config: Modal configuration.
            input_callback: Optional callback for input handling.

        Returns:
            True if modal started successfully.
        """
        try:
            self.config = config or LiveModalConfig()
            self._content_generator = content_generator
            self._input_callback = input_callback
            self._should_exit = False

            # Get terminal size for layout
            width, height = self.terminal_state.get_size()

            # Create layout for fullscreen modal
            layout = ModalLayout(
                width=width - 4,  # Leave margin
                height=height - 2,
                start_row=1,
                start_col=2,
                center_horizontal=True,
                center_vertical=False,
                padding=1,
                border_style="box"
            )

            # Use ModalStateManager to prepare display (enters alt buffer)
            success = self.state_manager.prepare_modal_display(
                layout,
                ModalDisplayMode.FULLSCREEN
            )

            if not success:
                logger.error("Failed to prepare modal display")
                return False

            self.modal_active = True
            logger.info(f"Live modal started: {self.config.title}")

            # Start refresh loop as a background task
            self._refresh_task = asyncio.create_task(self._refresh_loop())

            return True

        except Exception as e:
            logger.error(f"Error starting live modal: {e}")
            return False

    async def _refresh_loop(self):
        """Main refresh loop - updates display continuously."""
        try:
            while self.modal_active and not self._should_exit:
                # Get fresh content
                content = await self._get_content()

                # Render frame using state manager
                self._render_frame(content)

                # Sleep for refresh rate
                await asyncio.sleep(self.config.refresh_rate)

        except asyncio.CancelledError:
            logger.debug("Refresh loop cancelled")
        except Exception as e:
            logger.error(f"Error in refresh loop: {e}")

    async def _get_content(self) -> List[str]:
        """Get content from generator (handles sync/async)."""
        try:
            if asyncio.iscoroutinefunction(self._content_generator):
                return await self._content_generator()
            else:
                return self._content_generator()
        except Exception as e:
            logger.error(f"Error getting content: {e}")
            return [f"Error: {e}"]

    def _render_frame(self, content_lines: List[str]):
        """Render a single frame using ModalStateManager."""
        try:
            if not self.state_manager.current_layout:
                return

            layout = self.state_manager.current_layout

            # Build modal lines with border
            if self.config.show_border:
                modal_lines = self._build_bordered_content(content_lines, layout.width, layout.height)
            else:
                modal_lines = content_lines[:layout.height]

            # Use state manager to render
            self.state_manager.render_modal_content(modal_lines)

        except Exception as e:
            logger.error(f"Error rendering frame: {e}")

    def _build_bordered_content(self, content_lines: List[str], width: int, height: int) -> List[str]:
        """Build content with border and title/footer."""
        border_color = ColorPalette.GREY
        title_color = ColorPalette.WHITE
        reset = ColorPalette.RESET

        lines = []
        inner_width = width - 2  # Account for borders

        # Top border with title
        title = self.config.title
        title_padding = max(0, inner_width - len(title) - 2)
        left_pad = title_padding // 2
        right_pad = title_padding - left_pad
        top_border = f"{border_color}╭{'─' * left_pad} {title_color}{title}{reset}{border_color} {'─' * right_pad}╮{reset}"
        lines.append(top_border)

        # Content area (height - 2 for top/bottom borders)
        content_height = height - 2
        for i in range(content_height):
            if i < len(content_lines):
                line = content_lines[i]
                # Strip ANSI for length calculation
                visible_len = len(self._strip_ansi(line))
                if visible_len > inner_width:
                    # Truncate line
                    line = line[:inner_width - 3] + "..."
                    visible_len = inner_width
                padding = max(0, inner_width - visible_len)
                content_line = f"{border_color}│{reset}{line}{' ' * padding}{border_color}│{reset}"
            else:
                # Empty line
                content_line = f"{border_color}│{' ' * inner_width}│{reset}"
            lines.append(content_line)

        # Bottom border with footer
        footer = self.config.footer
        footer_padding = max(0, inner_width - len(footer) - 2)
        left_pad = footer_padding // 2
        right_pad = footer_padding - left_pad
        bottom_border = f"{border_color}╰{'─' * left_pad} {footer} {'─' * right_pad}╯{reset}"
        lines.append(bottom_border)

        return lines

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text."""
        import re
        return re.sub(r'\033\[[0-9;]*m', '', text)

    async def handle_input(self, key_press: KeyPress) -> bool:
        """Handle input during live modal.

        Args:
            key_press: Key press event.

        Returns:
            True if modal should close.
        """
        try:
            # Always handle Escape to exit
            if key_press.name == "Escape":
                self._should_exit = True
                return True

            # Ctrl+C also exits
            if key_press.char and ord(key_press.char) == 3:
                self._should_exit = True
                return True

            # If passthrough enabled and callback provided, forward input
            if self.config.passthrough_input and self._input_callback:
                should_close = await self._input_callback(key_press)
                if should_close:
                    self._should_exit = True
                return should_close

            return False

        except Exception as e:
            logger.error(f"Error handling live modal input: {e}")
            return False

    def request_exit(self):
        """Request the modal to exit (thread-safe)."""
        self._should_exit = True

    async def close_modal(self):
        """Close the live modal and restore terminal."""
        try:
            if not self.modal_active:
                return

            self.modal_active = False
            self._should_exit = True

            # Cancel refresh task if running
            if self._refresh_task and not self._refresh_task.done():
                self._refresh_task.cancel()
                try:
                    await self._refresh_task
                except asyncio.CancelledError:
                    pass

            # Use state manager to restore terminal (exits alt buffer)
            self.state_manager.restore_terminal_state()

            logger.info("Live modal closed")

        except Exception as e:
            logger.error(f"Error closing live modal: {e}")
            # Force restore on error
            self.state_manager.restore_terminal_state()

    def is_active(self) -> bool:
        """Check if live modal is currently active."""
        return self.modal_active
