"""Tmux integration plugin for managing and viewing tmux sessions.

Provides commands to:
- Create new tmux sessions with commands
- View live tmux session output in alt buffer
- List active sessions
- Kill sessions
"""

import asyncio
import subprocess
import logging
import shutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from core.io.visual_effects import AgnosterSegment

logger = logging.getLogger(__name__)


@dataclass
class TmuxSession:
    """Represents a managed tmux session."""
    name: str
    command: str
    created_at: datetime = field(default_factory=datetime.now)
    pid: Optional[int] = None

    def is_alive(self) -> bool:
        """Check if the tmux session is still running."""
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", self.name],
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False


class TmuxPlugin:
    """Plugin for tmux session management and live viewing."""

    def __init__(self, name: str = "tmux", state_manager=None, event_bus=None,
                 renderer=None, config=None):
        """Initialize the tmux plugin.

        Args:
            name: Plugin name.
            state_manager: State management system.
            event_bus: Event bus for hook registration.
            renderer: Terminal renderer.
            config: Configuration manager.
        """
        self.name = name
        self.version = "1.0.0"
        self.description = "Manage and view tmux sessions"
        self.enabled = True

        self.sessions: Dict[str, TmuxSession] = {}
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config
        self.command_registry = None
        self.input_handler = None
        self._current_session: Optional[str] = None  # Currently viewing session
        self._last_arrow_time: float = 0.0  # For double-arrow detection
        self._last_arrow_dir: Optional[str] = None  # "Left" or "Right"
        self._double_arrow_threshold: float = 0.3  # seconds

        self.logger = logger

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration for tmux plugin."""
        return {
            "plugins": {
                "tmux": {
                    "enabled": True,
                    "show_status": True,
                    "refresh_rate": 0.1,  # Live view refresh rate in seconds
                    "default_shell": "/bin/bash"
                }
            }
        }

    async def initialize(self, event_bus, config, **kwargs) -> None:
        """Initialize the plugin.

        Args:
            event_bus: Application event bus.
            config: Configuration manager.
            **kwargs: Additional parameters including command_registry.
        """
        try:
            self.event_bus = event_bus
            self.config = config
            self.command_registry = kwargs.get('command_registry')
            self.input_handler = kwargs.get('input_handler')
            self.renderer = kwargs.get('renderer')

            # Check if tmux is available
            if not self._check_tmux_available():
                self.logger.warning("tmux not found in PATH - tmux plugin disabled")
                self.enabled = False
                return

            # Register commands
            if self.command_registry:
                self._register_commands()

            # Discover existing sessions
            self._discover_existing_sessions()

            # Register status view
            await self._register_status_view()

            self.logger.info("Tmux plugin initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing tmux plugin: {e}")
            raise

    def _check_tmux_available(self) -> bool:
        """Check if tmux is available on the system."""
        return shutil.which("tmux") is not None

    def _register_commands(self):
        """Register tmux commands with the command registry."""
        from core.events.models import (
            CommandDefinition, CommandMode, CommandCategory
        )

        # /terminal - manage tmux sessions
        terminal_cmd = CommandDefinition(
            name="terminal",
            description="Manage tmux sessions (new/view/list/kill)",
            handler=self._handle_tmux_command,
            plugin_name=self.name,
            category=CommandCategory.SYSTEM,
            mode=CommandMode.INSTANT,
            aliases=["term", "tmux", "t"],
            icon="[>_]"
        )
        self.command_registry.register_command(terminal_cmd)

        self.logger.info("Tmux commands registered")

    async def _handle_tmux_command(self, command) -> "CommandResult":
        """Handle /tmux command with subcommands.

        Usage:
            /tmux new <command> <session_name>  - Create new session
            /tmux view <session_name>           - Live view session
            /tmux list                          - List sessions
            /tmux kill <session_name>           - Kill session
            /tmux attach <session_name>         - Attach to session (exits kollabor)
        """
        from core.events.models import CommandResult

        args = command.args if command.args else []

        if not args:
            # No args - go directly to view mode
            return await self._handle_view_session([])

        subcommand = args[0].lower()

        if subcommand == "new":
            return await self._handle_new_session(args[1:])
        elif subcommand == "view":
            return await self._handle_view_session(args[1:])
        elif subcommand == "list" or subcommand == "ls":
            return await self._handle_list_sessions()
        elif subcommand == "kill":
            return await self._handle_kill_session(args[1:])
        elif subcommand == "attach":
            return await self._handle_attach_session(args[1:])
        elif subcommand == "help" or subcommand == "--help" or subcommand == "-h":
            return CommandResult(
                success=True,
                message=self._get_help_text(),
                display_type="info"
            )
        else:
            return CommandResult(
                success=False,
                message=f"Unknown subcommand: {subcommand}\n\n{self._get_help_text()}",
                display_type="error"
            )

    def _get_help_text(self) -> str:
        """Get help text for terminal command."""
        return """Terminal Session Manager

Usage:
  /terminal new <name> <command>  Create new session running command
  /terminal view [name]           Live view session (</> to cycle)
  /terminal list                  List all sessions
  /terminal kill <name>           Kill a session
  /terminal attach <name>         Attach to session (leaves kollabor)

Examples:
  /terminal new myserver python -m http.server 8080
  /terminal new logs tail -f /var/log/syslog
  /terminal view
  /terminal kill myserver

Aliases: /t, /term, /tmux"""

    async def _handle_new_session(self, args: List[str]) -> "CommandResult":
        """Create a new tmux session."""
        from core.events.models import CommandResult

        if len(args) < 1:
            return CommandResult(
                success=False,
                message="Usage: /terminal new <session_name> [command]",
                display_type="error"
            )

        session_name = args[0]
        command = " ".join(args[1:]) if len(args) > 1 else None

        # Check if session already exists
        if session_name in self.sessions and self.sessions[session_name].is_alive():
            return CommandResult(
                success=False,
                message=f"Session '{session_name}' already exists",
                display_type="error"
            )

        try:
            # Create detached tmux session with interactive bash shell
            result = subprocess.run(
                ["tmux", "new-session", "-d", "-s", session_name, "bash", "-i"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return CommandResult(
                    success=False,
                    message=f"Failed to create session: {result.stderr}",
                    display_type="error"
                )

            # Send the command to the new session (if provided)
            if command:
                send_result = subprocess.run(
                    ["tmux", "send-keys", "-t", session_name, command, "Enter"],
                    capture_output=True,
                    text=True
                )

                if send_result.returncode != 0:
                    self.logger.warning(f"Session created but failed to send command: {send_result.stderr}")

            # Track the session
            self.sessions[session_name] = TmuxSession(
                name=session_name,
                command=command or "bash"
            )

            msg = f"Created session '{session_name}'"
            if command:
                msg += f" running: {command}"
            return CommandResult(
                success=True,
                message=msg,
                display_type="success"
            )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error creating session: {e}",
                display_type="error"
            )

    async def _handle_view_session(self, args: List[str]) -> "CommandResult":
        """View a tmux session live in alt buffer."""
        from core.events.models import CommandResult

        # If no args, get first available session
        if not args:
            sessions = self._get_all_tmux_sessions()
            if not sessions:
                return CommandResult(
                    success=False,
                    message="No tmux sessions found. Use '/tmux new <name> <command>' to create one.",
                    display_type="error"
                )
            session_name = sessions[0]
        else:
            session_name = args[0]
            # Check if session exists (in tmux, not just our tracking)
            if not self._session_exists(session_name):
                return CommandResult(
                    success=False,
                    message=f"Session '{session_name}' not found",
                    display_type="error"
                )

        # Emit live modal trigger event
        if self.event_bus:
            from core.ui.live_modal_renderer import LiveModalConfig
            from core.events.models import EventType

            # Content generator - uses self._current_session for dynamic switching
            async def get_tmux_content() -> List[str]:
                # Show session name as header line
                sessions = self._get_all_tmux_sessions()
                session_idx = sessions.index(self._current_session) + 1 if self._current_session in sessions else 1
                header = f"[Session: {self._current_session}] ({session_idx}/{len(sessions)})"
                content = self._capture_tmux_pane(self._current_session)
                return [header, "─" * len(header)] + content

            # Input callback for passthrough
            async def handle_input(key_press) -> bool:
                if key_press.name == "Escape":
                    return True  # Exit

                # Key8776 (≈) kills the current session
                if key_press.code == 8776:
                    try:
                        subprocess.run(
                            ["tmux", "kill-session", "-t", self._current_session],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        logger.info(f"Killed tmux session: {self._current_session}")
                        return True  # Exit modal after killing session
                    except Exception as e:
                        logger.error(f"Failed to kill tmux session {self._current_session}: {e}")
                        return False

                # Use Opt+Right (Alt+ArrowRight) and Opt+Left (Alt+ArrowLeft) to cycle sessions
                # Support both Alt+Arrow and Alt+letter sequences

                if key_press.name == "Alt+ArrowRight":
                    new_session = self._cycle_session(forward=True)
                    if new_session:
                        self._current_session = new_session
                    return False
                elif key_press.name == "Alt+ArrowLeft":
                    new_session = self._cycle_session(forward=False)
                    if new_session:
                        self._current_session = new_session
                    return False
                # Also support Alt+f and Alt+b for terminals that use these sequences
                elif key_press.name == "Alt+f":
                    new_session = self._cycle_session(forward=True)
                    if new_session:
                        self._current_session = new_session
                    return False
                elif key_press.name == "Alt+b":
                    new_session = self._cycle_session(forward=False)
                    if new_session:
                        self._current_session = new_session
                    return False

                # Only forward keys if we have an active session
                if self._current_session is None:
                    return False

                # Forward arrow keys to tmux
                if key_press.name in ("ArrowLeft", "ArrowRight"):
                    self._send_keys_to_tmux(self._current_session, key_press.name.replace("Arrow", ""))
                    return False

                # Handle Ctrl+C - send to tmux (interrupt)
                if key_press.char and ord(key_press.char) == 3:
                    self._send_keys_to_tmux(self._current_session, "C-c")
                    return False

                # Map special keys to tmux key names
                key_map = {
                    "Enter": "Enter",
                    "Backspace": "BSpace",
                    "Tab": "Tab",
                    "ArrowUp": "Up",
                    "ArrowDown": "Down",
                    "Home": "Home",
                    "End": "End",
                    "PageUp": "PageUp",
                    "PageDown": "PageDown",
                    "Delete": "DC",
                }

                # Forward special keys
                if key_press.name in key_map:
                    self._send_keys_to_tmux(self._current_session, key_map[key_press.name])
                # Forward regular character keys
                elif key_press.char:
                    self._send_keys_to_tmux(self._current_session, key_press.char)

                return False

            # Configure the live modal with streaming-friendly refresh rate
            config = LiveModalConfig(
                title="terminal",
                footer="Esc: exit | Opt+Left/Right: cycle | Opt+x: kills session",
                refresh_rate=self.config.get("plugins.tmux.refresh_rate", 2.0),  # 2 seconds - much slower
                passthrough_input=True
            )

            # Store current session
            self._current_session = session_name

            # Emit event to trigger live modal (input handler will handle it)
            await self.event_bus.emit_with_hooks(
                EventType.LIVE_MODAL_TRIGGER,
                {
                    "content_generator": get_tmux_content,
                    "config": config,
                    "input_callback": handle_input
                },
                "live_modal"
            )

            return CommandResult(
                success=True,
                message="",  # No message needed, modal takes over
                display_type="none"
            )
        else:
            return CommandResult(
                success=False,
                message="Live view not available - event bus not configured",
                display_type="error"
            )

    def _capture_tmux_pane(self, session_name: str) -> List[str]:
        """Capture current content of a tmux pane."""
        try:
            # Capture only the last 5 lines to reduce overhead
            result = subprocess.run(
                ["tmux", "capture-pane", "-p", "-S", "-5", "-t", session_name],
                capture_output=True,
                text=True,
                timeout=2  # Add timeout to prevent hanging
            )
            if result.returncode == 0:
                # Split on \n and handle empty lines properly
                content = result.stdout
                # Remove trailing empty lines but keep internal empty lines
                while content.endswith('\n'):
                    content = content[:-1]

                lines = content.split('\n')

                # Clean up captured content for display
                cleaned = []
                for line in lines:
                    # Strip ANSI escape sequences and trailing whitespace
                    import re
                    line = re.sub(r'\x1b\[[0-9;]*m', '', line)  # Remove ANSI colors
                    line = line.rstrip()
                    # Only add non-empty lines or empty lines that have meaningful content
                    if line or (cleaned and cleaned[-1] and not cleaned[-1].isspace()):
                        cleaned.append(line)
                return cleaned
            else:
                return [f"Error capturing pane: {result.stderr}"]
        except subprocess.TimeoutExpired:
            return [f"Session capture timed out - session might be unresponsive"]
        except Exception as e:
            return [f"Error: {e}"]

    def _send_keys_to_tmux(self, session_name: str, keys: str):
        """Send keys to a tmux session."""
        try:
            subprocess.run(
                ["tmux", "send-keys", "-t", session_name, keys],
                capture_output=True
            )
        except Exception as e:
            self.logger.error(f"Error sending keys to tmux: {e}")

    async def _handle_list_sessions(self) -> "CommandResult":
        """List all tmux sessions (both managed and discovered)."""
        from core.events.models import CommandResult

        # Discover all existing tmux sessions
        all_sessions = self._get_all_tmux_sessions()

        if not all_sessions:
            return CommandResult(
                success=True,
                message="No tmux sessions found. Use '/tmux new <name> <command>' to create one.",
                display_type="info"
            )

        # Build list of sessions, one per line
        lines = ["Terminal Sessions:"]
        for session_name in all_sessions:
            # Check if it's a managed session
            if session_name in self.sessions:
                session = self.sessions[session_name]
                status = "[MANAGED]" if session.is_alive() else "[MANAGED-DEAD]"
                lines.append(f"{status} {session_name}")
            else:
                lines.append(f"[EXTERNAL] {session_name}")

        message = "\n".join(lines)

        return CommandResult(
            success=True,
            message=message,
            display_type="info"
        )

    async def _handle_kill_session(self, args: List[str]) -> "CommandResult":
        """Kill a tmux session."""
        from core.events.models import CommandResult

        if not args:
            return CommandResult(
                success=False,
                message="Usage: /tmux kill <session_name>",
                display_type="error"
            )

        session_name = args[0]

        try:
            result = subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Remove from tracking
                if session_name in self.sessions:
                    del self.sessions[session_name]
                return CommandResult(
                    success=True,
                    message=f"Killed session '{session_name}'",
                    display_type="info"
                )
            else:
                return CommandResult(
                    success=False,
                    message=f"Failed to kill session: {result.stderr}",
                    display_type="error"
                )

        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Error killing session: {e}",
                display_type="error"
            )

    async def _handle_attach_session(self, args: List[str]) -> "CommandResult":
        """Attach to a tmux session (exits kollabor)."""
        from core.events.models import CommandResult

        if not args:
            return CommandResult(
                success=False,
                message="Usage: /tmux attach <session_name>",
                display_type="error"
            )

        session_name = args[0]

        if not self._session_exists(session_name):
            return CommandResult(
                success=False,
                message=f"Session '{session_name}' not found",
                display_type="error"
            )

        return CommandResult(
            success=True,
            message=f"To attach to '{session_name}', exit kollabor and run:\n  tmux attach -t {session_name}",
            display_type="info"
        )

    def _session_exists(self, session_name: str) -> bool:
        """Check if a tmux session exists."""
        try:
            result = subprocess.run(
                ["tmux", "has-session", "-t", session_name],
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def _cycle_session(self, forward: bool = True) -> Optional[str]:
        """Cycle to next/previous tmux session.

        Args:
            forward: True for next session, False for previous.

        Returns:
            New session name, or None if no other sessions.
        """
        sessions = self._get_all_tmux_sessions()
        if len(sessions) <= 1:
            return None

        try:
            current_idx = sessions.index(self._current_session)
            if forward:
                new_idx = (current_idx + 1) % len(sessions)
            else:
                new_idx = (current_idx - 1) % len(sessions)
            return sessions[new_idx]
        except ValueError:
            # Current session not in list, return first
            return sessions[0] if sessions else None

    def _refresh_session_status(self):
        """Refresh status of all tracked sessions."""
        dead_sessions = []
        for name, session in self.sessions.items():
            if not session.is_alive():
                dead_sessions.append(name)

        # Optionally remove dead sessions from tracking
        # For now, keep them but show as [DEAD]

    def _get_all_tmux_sessions(self) -> List[str]:
        """Get list of all existing tmux sessions."""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.returncode == 0:
                # Parse output: each line is a session name
                sessions = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        sessions.append(line)
                return sessions
            return []
        except subprocess.CalledProcessError:
            # No sessions or tmux not running
            return []
        except Exception as e:
            self.logger.error(f"Error listing tmux sessions: {e}")
            return []

    def _discover_existing_sessions(self):
        """Discover existing tmux sessions (optional bootstrap)."""
        try:
            result = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                existing = result.stdout.strip().split("\n")
                self.logger.debug(f"Found existing tmux sessions: {existing}")
        except Exception:
            pass

    async def _register_status_view(self) -> None:
        """Register tmux sessions status view."""
        try:
            # Check if renderer has status registry
            if (hasattr(self.renderer, 'status_renderer') and
                self.renderer.status_renderer and
                hasattr(self.renderer.status_renderer, 'status_registry') and
                self.renderer.status_renderer.status_registry):

                from core.io.status_renderer import StatusViewConfig, BlockConfig

                # Create tmux sessions view
                tmux_view = StatusViewConfig(
                    name="Tmux Sessions",
                    plugin_source="tmux",
                    priority=500,  # Between core views and plugin views
                    blocks=[
                        BlockConfig(
                            width_fraction=1.0,
                            content_provider=self._get_tmux_sessions_content,
                            title="Tmux Sessions",
                            priority=100
                        )
                    ],
                )

                registry = self.renderer.status_renderer.status_registry
                registry.register_status_view("tmux", tmux_view)
                logger.info("Registered 'Tmux Sessions' status view")

            else:
                logger.debug("Status registry not available - cannot register status view")

        except Exception as e:
            logger.error(f"Failed to register tmux status view: {e}")

    def _get_tmux_sessions_content(self) -> List[str]:
        """Get tmux sessions content for status view (agnoster style)."""
        try:
            seg = AgnosterSegment()

            if not self.enabled:
                seg.add_neutral("Tmux: Disabled", "dark")
                return [seg.render()]

            # Get all tmux sessions
            all_sessions = self._get_all_tmux_sessions()
            session_count = len(all_sessions)

            if session_count == 0:
                seg.add_lime("Tmux", "dark")
                seg.add_neutral("No sessions", "mid")
                return [seg.render()]

            # Build agnoster bar: Tmux | count | session names | hint
            seg.add_lime("Tmux", "dark")
            seg.add_cyan(f"{session_count} active", "dark")

            # Show first few session names
            max_show = 3
            if all_sessions:
                names = all_sessions[:max_show]
                names_str = " | ".join(names)
                if session_count > max_show:
                    names_str += f" +{session_count - max_show}"
                seg.add_lime(names_str)

            seg.add_neutral("/terminal", "mid")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Error getting tmux sessions content: {e}")
            seg = AgnosterSegment()
            seg.add_neutral("Tmux: Error", "dark")
            return [seg.render()]

    def get_status_line(self) -> Dict[str, List[str]]:
        """Get status line (no longer used - using status view instead)."""
        # Return empty - we use the dedicated status view now
        return {"A": [], "B": [], "C": []}

    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        try:
            # Clear session tracking
            self._current_session = None
            self.logger.info("Tmux plugin shutdown completed")

        except Exception as e:
            self.logger.error(f"Error shutting down tmux plugin: {e}")

    async def register_hooks(self) -> None:
        """Register event hooks."""
        # Could register hooks for live modal input handling
        pass

    @staticmethod
    def get_config_widgets() -> Optional[Dict[str, Any]]:
        """Get configuration widgets for the config modal."""
        return {
            "title": "Tmux Settings",
            "widgets": [
                {
                    "type": "checkbox",
                    "label": "Show Status",
                    "config_path": "plugins.tmux.show_status",
                    "help": "Show tmux session count in status bar"
                },
                {
                    "type": "slider",
                    "label": "Refresh Rate (ms)",
                    "config_path": "plugins.tmux.refresh_rate_ms",
                    "min_value": 50,
                    "max_value": 1000,
                    "step": 50,
                    "help": "Live view refresh rate in milliseconds"
                }
            ]
        }
