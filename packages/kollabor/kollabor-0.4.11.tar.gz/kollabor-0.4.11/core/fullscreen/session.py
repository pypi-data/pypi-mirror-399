"""Full-screen session management."""

import asyncio
import logging
import sys
from typing import Optional
from dataclasses import dataclass

# Platform-specific imports for input handling
IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import msvcrt
else:
    import select

from ..io.key_parser import KeyParser, KeyPress
from .plugin import FullScreenPlugin
from .renderer import FullScreenRenderer

logger = logging.getLogger(__name__)


@dataclass
class SessionStats:
    """Statistics for a full-screen session."""
    start_time: float
    end_time: Optional[float] = None
    frame_count: int = 0
    input_events: int = 0
    average_fps: float = 0.0

    @property
    def duration(self) -> float:
        """Get session duration in seconds."""
        end = self.end_time or asyncio.get_event_loop().time()
        return end - self.start_time


class FullScreenSession:
    """Manages a full-screen plugin execution session.

    This class handles the complete lifecycle of running a full-screen plugin,
    including terminal setup, input handling, rendering loop, and cleanup.
    """

    def __init__(self, plugin: FullScreenPlugin, event_bus=None, target_fps: float = 60.0):
        """Initialize a full-screen session.

        Args:
            plugin: The plugin to run.
            event_bus: Event bus for input routing (optional, falls back to direct stdin).
            target_fps: Target frame rate for rendering.
        """
        self.plugin = plugin
        self.event_bus = event_bus
        self.target_fps = target_fps
        self.frame_delay = 1.0 / target_fps

        # Session state
        self.running = False
        self.renderer = FullScreenRenderer()
        self.key_parser = KeyParser()
        self.stats = SessionStats(start_time=0)

        # CRITICAL FIX: Input routing through events
        self.pending_input = asyncio.Queue()
        self.input_hook_registered = False

        logger.info(f"Created session for plugin: {plugin.name}")

    async def _register_input_hook(self):
        """Register hook to receive input from InputHandler."""
        if self.event_bus and not self.input_hook_registered:
            try:
                from ..events.models import Hook, HookPriority, EventType
                hook = Hook(
                    name="fullscreen_input",
                    plugin_name=f"fullscreen_session_{self.plugin.name}",
                    event_type=EventType.FULLSCREEN_INPUT,
                    priority=HookPriority.DISPLAY.value,
                    callback=self._handle_fullscreen_input
                )
                success = await self.event_bus.register_hook(hook)
                if success:
                    self.input_hook_registered = True
                    logger.info(f"✅ Registered FULLSCREEN_INPUT hook for {self.plugin.name}")
                else:
                    logger.error(f"❌ Failed to register FULLSCREEN_INPUT hook for {self.plugin.name}")
            except Exception as e:
                logger.error(f"Error registering fullscreen input hook: {e}")

    async def _handle_fullscreen_input(self, event_data, context=None):
        """Handle FULLSCREEN_INPUT events from InputHandler."""
        try:
            print(f"🎯 CRITICAL: Session received FULLSCREEN_INPUT event: {event_data}")
            key_press = event_data.get('key_press')
            if key_press:
                print(f"🎯 CRITICAL: Adding key to pending_input queue: {key_press.name} ({key_press.char})")
                logger.info(f"🎯 Session received input: {key_press.name}")
                await self.pending_input.put(key_press)
                return {"success": True, "handled": True}
            print(f"❌ CRITICAL: No key_press in event data: {event_data}")
            return {"success": False, "error": "No key_press in event data"}
        except Exception as e:
            print(f"❌ CRITICAL: Exception in _handle_fullscreen_input: {e}")
            logger.error(f"Error handling fullscreen input: {e}")
            return {"success": False, "error": str(e)}

    async def run(self) -> bool:
        """Run the full-screen session.

        Returns:
            True if session completed successfully, False if error occurred.
        """
        try:
            # Initialize session
            if not await self._initialize():
                return False

            logger.info(f"Starting full-screen session for {self.plugin.name}")
            self.running = True
            self.stats.start_time = asyncio.get_event_loop().time()

            # Main session loop
            await self._session_loop()

            logger.info(f"Session completed for {self.plugin.name}")
            return True

        except Exception as e:
            logger.error(f"Session error for {self.plugin.name}: {e}")
            return False

        finally:
            await self._cleanup()

    async def _initialize(self) -> bool:
        """Initialize the session.

        Returns:
            True if initialization successful, False otherwise.
        """
        try:
            # CRITICAL FIX: Register input hook before terminal setup
            try:
                await self._register_input_hook()
            except Exception as e:
                logger.warning(f"Input hook registration failed: {e}")
                # Continue anyway, input might still work via fallback

            # Setup terminal
            if not self.renderer.setup_terminal():
                logger.error("Failed to setup terminal")
                return False

            # Initialize plugin
            if not await self.plugin.initialize(self.renderer):
                logger.error(f"Failed to initialize plugin {self.plugin.name}")
                return False

            # Start plugin
            await self.plugin.on_start()

            return True

        except Exception as e:
            logger.error(f"Session initialization failed: {e}")
            return False

    async def _session_loop(self):
        """Main session loop handling rendering and input."""
        last_frame_time = asyncio.get_event_loop().time()

        while self.running:
            current_time = asyncio.get_event_loop().time()
            delta_time = current_time - last_frame_time

            try:
                # Handle input
                if await self._handle_input():
                    break  # Exit requested

                # Render frame
                if not await self.plugin.render_frame(delta_time):
                    break  # Plugin requested exit

                self.stats.frame_count += 1
                last_frame_time = current_time

                # Frame rate limiting
                await asyncio.sleep(max(0, self.frame_delay - delta_time))

            except Exception as e:
                logger.error(f"Error in session loop: {e}")
                break

    async def _handle_input(self) -> bool:
        """Handle input events.

        Returns:
            True if exit was requested, False otherwise.
        """
        try:
            # Check for available input (non-blocking)
            if not sys.stdin.isatty():
                return False

            # Platform-specific input checking
            has_input = False
            char = None

            if IS_WINDOWS:
                # Windows: Use msvcrt to check for input
                if msvcrt.kbhit():
                    has_input = True
                    char_bytes = msvcrt.getch()
                    char = char_bytes.decode("utf-8", errors="ignore") if char_bytes else None

                    # Handle extended keys on Windows (arrow keys, etc.)
                    if char_bytes and char_bytes[0] in (0, 224):
                        ext_char = msvcrt.getch()
                        ext_code = ext_char[0] if ext_char else 0
                        # Map Windows extended key codes to escape sequences
                        win_key_map = {
                            72: "\x1b[A",  # ArrowUp
                            80: "\x1b[B",  # ArrowDown
                            75: "\x1b[D",  # ArrowLeft
                            77: "\x1b[C",  # ArrowRight
                            71: "\x1b[H",  # Home
                            79: "\x1b[F",  # End
                            83: "\x1b[3~",  # Delete
                        }
                        if ext_code in win_key_map:
                            # Process escape sequence character by character
                            for c in win_key_map[ext_code]:
                                if not hasattr(self, '_key_parser'):
                                    self._key_parser = KeyParser()
                                key_press = self._key_parser.parse_char(c)
                            if key_press:
                                self.stats.input_events += 1
                                return await self.plugin.handle_input(key_press)
                        return False
            else:
                # Unix: Use select to check for input without blocking
                ready, _, _ = select.select([sys.stdin], [], [], 0)
                if ready:
                    has_input = True
                    char = sys.stdin.read(1)

            if not has_input or not char:
                return False

            # Use the actual key parser for proper parsing
            if not hasattr(self, '_key_parser'):
                self._key_parser = KeyParser()

            # Parse the input character properly
            key_press = self._key_parser.parse_char(char)
            if not key_press:
                # Check for standalone ESC key
                key_press = self._key_parser.check_for_standalone_escape()
                if not key_press:
                    return False

            self.stats.input_events += 1

            # Let plugin handle input (plugin decides if it wants to exit)
            return await self.plugin.handle_input(key_press)

        except Exception as e:
            logger.error(f"Error handling input: {e}")
            return False

    async def _cleanup(self):
        """Clean up session resources."""
        try:
            self.running = False
            self.stats.end_time = asyncio.get_event_loop().time()

            # Calculate final stats
            if self.stats.duration > 0:
                self.stats.average_fps = self.stats.frame_count / self.stats.duration

            # Stop plugin
            await self.plugin.on_stop()

            # Restore terminal
            self.renderer.restore_terminal()

            # Unregister input hook if it was registered
            if self.input_hook_registered and self.event_bus:
                try:
                    hook_id = f"fullscreen_session_{self.plugin.name}.fullscreen_input"
                    await self.event_bus.unregister_hook(hook_id)
                    self.input_hook_registered = False
                    logger.info(f"✅ Unregistered FULLSCREEN_INPUT hook for {self.plugin.name}")
                except Exception as e:
                    logger.error(f"Error unregistering hook: {e}")

            # Cleanup plugin
            await self.plugin.cleanup()

            logger.info(f"Session cleanup complete for {self.plugin.name}")
            logger.info(f"Session stats: {self.stats.frame_count} frames, "
                       f"{self.stats.average_fps:.1f} fps, "
                       f"{self.stats.input_events} inputs, "
                       f"{self.stats.duration:.1f}s duration")

        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")

    def stop(self):
        """Stop the session gracefully."""
        self.running = False
        logger.info(f"Stop requested for session: {self.plugin.name}")

    def get_stats(self) -> SessionStats:
        """Get current session statistics.

        Returns:
            Current session statistics.
        """
        return self.stats