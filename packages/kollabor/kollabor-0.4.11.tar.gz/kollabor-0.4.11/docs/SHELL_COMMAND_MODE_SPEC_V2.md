# Shell Command Mode (`!` Prefix) Specification v2

## Overview

Execute shell commands from within Kollabor CLI using `!` prefix:
- `!ls` executes `ls` and displays output in conversation
- Full output stored in LLM history (truncated display)
- Proper hook integration for plugins
- Security controls for dangerous commands
- Cancellation and feedback during execution

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        KeyPressHandler                          │
│  - Detects "!" prefix                                           │
│  - Delegates to ShellCommandService (does NOT execute itself)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ShellCommandService                         │
│  - Validates command (blocklist, allowlist)                     │
│  - Emits SHELL_COMMAND_PRE event (plugins can intercept)        │
│  - Calls shell_executor.run_shell_command()                     │
│  - Emits SHELL_COMMAND_POST event                               │
│  - Coordinates display via MessageCoordinator                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 core/utils/shell_executor.py                    │
│  - ShellResult dataclass                                        │
│  - run_shell_command() async function                           │
│  - Process group management                                     │
│  - Used by both ShellCommandService AND ToolExecutor            │
└─────────────────────────────────────────────────────────────────┘
```

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `core/utils/shell_executor.py` | CREATE | Shared async shell execution |
| `core/llm/shell_command_service.py` | CREATE | Service layer for ! commands |
| `core/events/types.py` | MODIFY | Add SHELL_COMMAND_* events |
| `core/llm/tool_executor.py` | MODIFY | Use shared shell_executor |
| `core/io/input/key_press_handler.py` | MODIFY | Detect ! and delegate |
| `core/config/defaults.py` | MODIFY | Add shell.* config schema |

## Event Types

Add to `core/events/types.py`:

```python
# Shell command events
SHELL_COMMAND_PRE = "shell_command_pre"      # Before execution, can cancel
SHELL_COMMAND_POST = "shell_command_post"    # After execution, has result
SHELL_COMMAND_ERROR = "shell_command_error"  # On error/timeout
SHELL_COMMAND_CANCEL = "shell_command_cancel" # User cancelled
```

Event payloads:

```python
# SHELL_COMMAND_PRE
{
    "command": "ls -la",
    "cwd": "/path/to/dir",
    "timeout": 30,
    "can_cancel": True  # Plugin can set to False to block
}

# SHELL_COMMAND_POST
{
    "command": "ls -la",
    "result": ShellResult,
    "execution_time": 0.05,
    "displayed_lines": 25,
    "total_lines": 100
}

# SHELL_COMMAND_ERROR
{
    "command": "ls -la",
    "error": "Command timed out after 30s",
    "error_type": "timeout"  # timeout | blocked | permission | other
}
```

## Implementation

### Step 1: core/utils/shell_executor.py

```python
"""Shared shell command execution utility.

Used by:
- ShellCommandService (for ! user commands)
- ToolExecutor (for LLM <terminal> tool)
"""

import asyncio
import logging
import os
import signal
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class ShellResult:
    """Result of shell command execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool = False
    cancelled: bool = False
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for event payloads."""
        return {
            "success": self.success,
            "stdout_length": len(self.stdout),
            "stderr_length": len(self.stderr),
            "exit_code": self.exit_code,
            "timed_out": self.timed_out,
            "cancelled": self.cancelled,
            "error": self.error,
            "execution_time": self.execution_time
        }

    @property
    def combined_output(self) -> str:
        """Get combined stdout + stderr."""
        output = self.stdout
        if self.stderr:
            output += ("\n" if output else "") + self.stderr
        return output.rstrip() or "(no output)"


class ShellExecutor:
    """Async shell command executor with cancellation support."""

    def __init__(self):
        self._current_process: Optional[asyncio.subprocess.Process] = None
        self._cancelled = False

    async def run(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        max_output_bytes: int = 10 * 1024 * 1024  # 10MB default
    ) -> ShellResult:
        """Execute shell command asynchronously.

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds
            cwd: Working directory (defaults to current)
            env: Environment variables (defaults to filtered os.environ)
            max_output_bytes: Max output size before truncation

        Returns:
            ShellResult with stdout, stderr, exit_code, etc.
        """
        import time
        start_time = time.time()

        if not command.strip():
            return ShellResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error="Empty command"
            )

        cwd = cwd or Path.cwd()
        self._cancelled = False

        # Filter sensitive environment variables
        if env is None:
            env = self._filter_env(os.environ.copy())

        try:
            # Create process with new process group for clean kill
            self._current_process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env=env,
                start_new_session=True  # Create new process group
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    self._current_process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                await self._kill_process_group()
                return ShellResult(
                    success=False,
                    stdout="",
                    stderr="",
                    exit_code=-1,
                    timed_out=True,
                    error=f"Command timed out after {timeout}s",
                    execution_time=time.time() - start_time
                )
            except asyncio.CancelledError:
                await self._kill_process_group()
                return ShellResult(
                    success=False,
                    stdout="",
                    stderr="",
                    exit_code=-1,
                    cancelled=True,
                    error="Command cancelled by user",
                    execution_time=time.time() - start_time
                )

            # Check if cancelled during execution
            if self._cancelled:
                return ShellResult(
                    success=False,
                    stdout="",
                    stderr="",
                    exit_code=-1,
                    cancelled=True,
                    error="Command cancelled by user",
                    execution_time=time.time() - start_time
                )

            # Decode output with size limit
            stdout_text = self._decode_output(stdout, max_output_bytes)
            stderr_text = self._decode_output(stderr, max_output_bytes)

            return ShellResult(
                success=(self._current_process.returncode == 0),
                stdout=stdout_text,
                stderr=stderr_text,
                exit_code=self._current_process.returncode,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            logger.error(f"Shell execution failed: {e}")
            return ShellResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                error=str(e),
                execution_time=time.time() - start_time
            )
        finally:
            self._current_process = None

    async def cancel(self) -> None:
        """Cancel currently running command."""
        self._cancelled = True
        await self._kill_process_group()

    async def _kill_process_group(self) -> None:
        """Kill process and all its children."""
        if self._current_process is None:
            return

        try:
            # Kill entire process group
            pgid = os.getpgid(self._current_process.pid)
            os.killpg(pgid, signal.SIGTERM)

            # Wait briefly for graceful shutdown
            try:
                await asyncio.wait_for(
                    self._current_process.wait(),
                    timeout=2.0
                )
            except asyncio.TimeoutError:
                # Force kill if still running
                os.killpg(pgid, signal.SIGKILL)
                await self._current_process.wait()

        except (ProcessLookupError, PermissionError):
            # Process already dead
            pass

    def _filter_env(self, env: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive environment variables."""
        sensitive_patterns = [
            "API_KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL",
            "AWS_", "AZURE_", "GCP_", "ANTHROPIC_", "OPENAI_"
        ]
        return {
            k: v for k, v in env.items()
            if not any(pattern in k.upper() for pattern in sensitive_patterns)
        }

    def _decode_output(self, data: bytes, max_bytes: int) -> str:
        """Decode output with size limit and binary detection."""
        if len(data) > max_bytes:
            data = data[:max_bytes]
            truncated = True
        else:
            truncated = False

        # Detect binary content
        if b'\x00' in data[:1024]:
            return "[binary output not displayed]"

        text = data.decode('utf-8', errors='replace')

        if truncated:
            text += f"\n[output truncated at {max_bytes // 1024}KB]"

        return text


# Module-level convenience function
_default_executor = ShellExecutor()

async def run_shell_command(
    command: str,
    timeout: int = 30,
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    max_output_bytes: int = 10 * 1024 * 1024
) -> ShellResult:
    """Execute shell command using default executor."""
    return await _default_executor.run(
        command, timeout, cwd, env, max_output_bytes
    )
```

### Step 2: core/llm/shell_command_service.py

```python
"""Shell command service for ! prefix commands.

Handles validation, hook integration, and display coordination.
"""

import asyncio
import logging
import re
from pathlib import Path
from typing import Optional, Set

from ..events.types import EventType
from ..utils.shell_executor import ShellExecutor, ShellResult

logger = logging.getLogger(__name__)


class ShellCommandService:
    """Service for executing user shell commands via ! prefix."""

    # Commands that require confirmation
    DANGEROUS_PATTERNS = [
        r"rm\s+(-[rf]+\s+)*[/~]",  # rm -rf /
        r"rm\s+-rf",
        r"mkfs\.",
        r"dd\s+.*of=/dev",
        r">\s*/dev/sd",
        r"chmod\s+-R\s+777",
        r":\(\)\s*{\s*:\|:&\s*}",  # fork bomb
    ]

    # Commands that won't work (need TTY)
    INTERACTIVE_COMMANDS = {
        "vim", "vi", "nano", "emacs", "less", "more", "top", "htop",
        "man", "ssh", "telnet", "ftp", "python", "node", "irb"
    }

    def __init__(self, event_bus, config, renderer):
        self.event_bus = event_bus
        self.config = config
        self.renderer = renderer
        self.executor = ShellExecutor()
        self._current_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = {
            "total_commands": 0,
            "successful": 0,
            "failed": 0,
            "cancelled": 0,
            "blocked": 0
        }

    async def execute(self, command: str) -> None:
        """Execute a shell command from ! prefix input.

        Args:
            command: Full input including ! prefix (e.g., "!ls -la")
        """
        # Strip ! prefix
        shell_cmd = command[1:].strip() if command.startswith("!") else command.strip()

        if not shell_cmd:
            return

        # Check if enabled
        if not self.config.get("shell.enabled", True):
            await self._display_error(shell_cmd, "Shell commands are disabled")
            return

        # Check for interactive commands
        base_cmd = shell_cmd.split()[0] if shell_cmd.split() else ""
        if base_cmd in self.INTERACTIVE_COMMANDS:
            await self._display_error(
                shell_cmd,
                f"'{base_cmd}' requires an interactive terminal and cannot run here"
            )
            return

        # Check for dangerous commands
        if self._is_dangerous(shell_cmd):
            # Could add confirmation prompt here
            await self._display_error(
                shell_cmd,
                "Command blocked: matches dangerous pattern. Use terminal directly."
            )
            self.stats["blocked"] += 1
            return

        # Get config
        timeout = self.config.get("shell.timeout", 30)
        max_lines = self.config.get("shell.display_lines", 25)
        max_chars = self.config.get("shell.display_chars", 5000)
        show_exit = self.config.get("shell.show_exit_code", True)
        show_cwd = self.config.get("shell.show_cwd", True)

        # Emit PRE event - plugins can cancel
        cwd = Path.cwd()
        pre_data = {
            "command": shell_cmd,
            "cwd": str(cwd),
            "timeout": timeout,
            "can_cancel": True
        }

        result = await self.event_bus.emit_with_hooks(
            EventType.SHELL_COMMAND_PRE,
            pre_data,
            "shell_command_service"
        )

        # Check if plugin cancelled
        if result.get("can_cancel") is False:
            await self._display_error(shell_cmd, "Command blocked by plugin")
            self.stats["blocked"] += 1
            return

        # Show execution indicator
        self._show_executing(shell_cmd)

        self.stats["total_commands"] += 1

        try:
            # Execute with cancellation support
            self._current_task = asyncio.current_task()
            shell_result = await self.executor.run(
                shell_cmd,
                timeout=timeout,
                cwd=cwd
            )

            if shell_result.cancelled:
                self.stats["cancelled"] += 1
                await self._emit_cancel_event(shell_cmd)
                self._hide_executing()
                return

            if shell_result.error and not shell_result.timed_out:
                self.stats["failed"] += 1
                await self._emit_error_event(shell_cmd, shell_result)
                await self._display_error(shell_cmd, shell_result.error)
                self._hide_executing()
                return

            if shell_result.timed_out:
                self.stats["failed"] += 1
                await self._emit_error_event(shell_cmd, shell_result)
                await self._display_error(shell_cmd, f"Timed out after {timeout}s")
                self._hide_executing()
                return

            # Success
            if shell_result.success:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1

            # Hide executing indicator
            self._hide_executing()

            # Format output
            output = shell_result.combined_output
            output = self._strip_ansi(output)

            # Build full content for LLM history
            full_content = self._format_full_output(
                shell_cmd, output, shell_result.exit_code, show_exit, show_cwd, cwd
            )

            # Build truncated content for display
            display_content = self._format_display_output(
                shell_cmd, output, shell_result.exit_code,
                show_exit, show_cwd, cwd, max_lines, max_chars
            )

            # Emit POST event
            await self.event_bus.emit_with_hooks(
                EventType.SHELL_COMMAND_POST,
                {
                    "command": shell_cmd,
                    "result": shell_result.to_dict(),
                    "execution_time": shell_result.execution_time,
                    "total_lines": len(output.split("\n")),
                    "displayed_lines": min(max_lines, len(output.split("\n")))
                },
                "shell_command_service"
            )

            # Add to conversation history (full output, not displayed)
            await self.event_bus.emit_with_hooks(
                EventType.ADD_MESSAGE,
                {
                    "messages": [{"role": "user", "content": full_content}],
                    "options": {
                        "display_messages": False,
                        "add_to_history": True,
                        "log_messages": True,
                        "trigger_llm": False,
                        "show_loading": False
                    }
                },
                "shell_command_service"
            )

            # Display truncated output
            self.renderer.message_coordinator.display_message_sequence([
                ("user", display_content, {})
            ])

        except asyncio.CancelledError:
            self.stats["cancelled"] += 1
            await self.executor.cancel()
            await self._emit_cancel_event(shell_cmd)
            self._hide_executing()
        finally:
            self._current_task = None

    async def cancel(self) -> None:
        """Cancel currently running shell command."""
        await self.executor.cancel()
        if self._current_task:
            self._current_task.cancel()

    def _is_dangerous(self, command: str) -> bool:
        """Check if command matches dangerous patterns."""
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True
        return False

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from output."""
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]')
        return ansi_pattern.sub('', text)

    def _format_full_output(
        self, cmd: str, output: str, exit_code: int,
        show_exit: bool, show_cwd: bool, cwd: Path
    ) -> str:
        """Format full output for LLM history."""
        parts = []
        if show_cwd:
            parts.append(f"[{cwd}]")
        parts.append(f"$ {cmd}")
        parts.append(output)
        if show_exit and exit_code != 0:
            parts.append(f"[exit: {exit_code}]")
        return "\n".join(parts)

    def _format_display_output(
        self, cmd: str, output: str, exit_code: int,
        show_exit: bool, show_cwd: bool, cwd: Path,
        max_lines: int, max_chars: int
    ) -> str:
        """Format truncated output for terminal display."""
        lines = output.split("\n")
        total_lines = len(lines)

        # Truncate by lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            lines.append(f"... [{total_lines - max_lines} more lines]")

        truncated_output = "\n".join(lines)

        # Truncate by characters (for single long lines)
        if len(truncated_output) > max_chars:
            truncated_output = truncated_output[:max_chars]
            truncated_output += f"\n... [truncated at {max_chars} chars]"

        parts = []
        if show_cwd:
            parts.append(f"[{cwd}]")
        parts.append(f"$ {cmd}")
        parts.append(truncated_output)
        if show_exit and exit_code != 0:
            parts.append(f"[exit: {exit_code}]")
        return "\n".join(parts)

    def _show_executing(self, command: str) -> None:
        """Show execution indicator in status area."""
        # TODO: Integrate with status renderer
        logger.debug(f"Executing: {command}")

    def _hide_executing(self) -> None:
        """Hide execution indicator."""
        logger.debug("Execution complete")

    async def _display_error(self, command: str, error: str) -> None:
        """Display error message in conversation."""
        content = f"$ {command}\n[error] {error}"
        await self.event_bus.emit_with_hooks(
            EventType.ADD_MESSAGE,
            {
                "messages": [{"role": "user", "content": content}],
                "options": {
                    "display_messages": True,
                    "add_to_history": True,
                    "log_messages": True,
                    "trigger_llm": False,
                    "show_loading": False
                }
            },
            "shell_command_service"
        )

    async def _emit_error_event(self, command: str, result: ShellResult) -> None:
        """Emit error event for plugins."""
        error_type = "timeout" if result.timed_out else "other"
        await self.event_bus.emit_with_hooks(
            EventType.SHELL_COMMAND_ERROR,
            {
                "command": command,
                "error": result.error,
                "error_type": error_type
            },
            "shell_command_service"
        )

    async def _emit_cancel_event(self, command: str) -> None:
        """Emit cancel event for plugins."""
        await self.event_bus.emit_with_hooks(
            EventType.SHELL_COMMAND_CANCEL,
            {"command": command},
            "shell_command_service"
        )

    def get_stats(self) -> dict:
        """Get execution statistics."""
        return self.stats.copy()
```

### Step 3: Modify KeyPressHandler

In `core/io/input/key_press_handler.py`, add to `_handle_enter()`:

```python
# Near top of _handle_enter(), after getting message from buffer:
if message.strip().startswith("!"):
    # Delegate to shell command service - do NOT process here
    await self.shell_command_service.execute(message.strip())
    return
```

The KeyPressHandler does NOT contain shell execution logic - it only detects and delegates.

### Step 4: Modify ToolExecutor

In `core/llm/tool_executor.py`, refactor `_execute_terminal_command()`:

```python
from ..utils.shell_executor import run_shell_command

async def _execute_terminal_command(self, tool_data: Dict[str, Any]) -> ToolExecutionResult:
    """Execute a terminal command using shared executor."""
    command = tool_data.get("command", "").strip()
    tool_id = tool_data.get("id", "unknown")

    if not command:
        return ToolExecutionResult(
            tool_id=tool_id,
            tool_type="terminal",
            success=False,
            error="Empty command"
        )

    result = await run_shell_command(command, timeout=self.terminal_timeout)

    if result.error:
        return ToolExecutionResult(
            tool_id=tool_id,
            tool_type="terminal",
            success=False,
            error=result.error
        )

    output = result.stdout if result.success else result.stderr
    error = "" if result.success else f"Exit code {result.exit_code}: {result.stderr}"

    return ToolExecutionResult(
        tool_id=tool_id,
        tool_type="terminal",
        success=result.success,
        output=output,
        error=error
    )
```

## Configuration

### Schema

```python
"shell": {
    "enabled": True,              # Enable ! commands
    "timeout": 30,                # Seconds (min: 1, max: 300)
    "display_lines": 25,          # Max lines shown (min: 5, max: 500)
    "display_chars": 5000,        # Max chars shown (min: 100, max: 50000)
    "max_output_bytes": 10485760, # 10MB max output
    "show_exit_code": True,       # Show [exit: N] on non-zero
    "show_cwd": True,             # Show working directory
    "strip_ansi": True,           # Remove ANSI escape codes
    "dangerous_command_action": "block"  # block | warn | allow
}
```

### Validation

```python
def validate_shell_config(config: dict) -> dict:
    """Validate and clamp shell config values."""
    return {
        "enabled": bool(config.get("enabled", True)),
        "timeout": max(1, min(300, config.get("timeout", 30))),
        "display_lines": max(5, min(500, config.get("display_lines", 25))),
        "display_chars": max(100, min(50000, config.get("display_chars", 5000))),
        "max_output_bytes": max(1024, min(100*1024*1024, config.get("max_output_bytes", 10*1024*1024))),
        "show_exit_code": bool(config.get("show_exit_code", True)),
        "show_cwd": bool(config.get("show_cwd", True)),
        "strip_ansi": bool(config.get("strip_ansi", True)),
        "dangerous_command_action": config.get("dangerous_command_action", "block")
    }
```

## Security

### Dangerous Command Detection

Commands matching these patterns are blocked by default:
- `rm -rf /` or `rm -rf ~`
- `mkfs.*` (filesystem format)
- `dd ... of=/dev/...` (disk write)
- `chmod -R 777`
- Fork bombs

### Environment Variable Filtering

Sensitive variables are NOT passed to shell commands:
- `*API_KEY*`, `*SECRET*`, `*TOKEN*`, `*PASSWORD*`
- `AWS_*`, `AZURE_*`, `GCP_*`
- `ANTHROPIC_*`, `OPENAI_*`

### Process Group Killing

Uses `start_new_session=True` and `os.killpg()` to kill entire process tree on timeout/cancel, preventing orphaned processes.

### Output Size Limits

- Max 10MB output by default
- Binary content detection (null bytes)
- Character truncation for display

### Audit Logging

All shell commands logged via standard logger:
- Command executed
- Exit code
- Execution time
- Whether blocked/cancelled

Plugins can hook SHELL_COMMAND_POST for additional audit logging.

## UX Considerations

### Feedback During Execution

- Status area shows `[EXEC] command...` during execution
- Spinner/animation while waiting

### Cancellation

- Ctrl+C during shell execution triggers cancel
- SHELL_COMMAND_CANCEL event emitted
- Process group killed cleanly

### Output Handling

| Scenario | Handling |
|----------|----------|
| Binary output | Shows `[binary output not displayed]` |
| ANSI codes | Stripped by default |
| Very long lines | Character truncation |
| Many lines | Line truncation with count |
| Empty output | Shows `(no output)` |
| stderr only | Combined with stdout |

### Interactive Commands

Commands requiring TTY (vim, top, python REPL) are detected and blocked with helpful message.

### Working Directory

Shown in output: `[/path/to/cwd]` before command.

## Edge Cases

| Case | Behavior |
|------|----------|
| `!` alone | Ignored (empty command) |
| `!!` | Executes `!` as command (shell history expansion) |
| `! ls` (space) | Executes `ls` (stripped) |
| `!ls \| grep foo` | Works (shell handles pipe) |
| `!ls > file.txt` | Works, output goes to file |
| `!cd /tmp` | Works but doesn't change app's cwd |
| Unicode in command | Supported |
| Background `!sleep &` | Runs, but parent exits immediately |

## Platform Support

### Unix/macOS
- Full support
- Uses `/bin/sh -c` for execution

### Windows
- Partial support
- Uses `cmd.exe /c` or PowerShell
- Process group killing uses different API
- Some commands won't work (grep, ls without aliases)

## Testing

### Unit Tests

```python
# tests/unit/test_shell_executor.py
class TestShellExecutor:
    async def test_simple_command(self):
        result = await run_shell_command("echo hello")
        assert result.success
        assert result.stdout.strip() == "hello"

    async def test_timeout(self):
        result = await run_shell_command("sleep 10", timeout=1)
        assert result.timed_out
        assert not result.success

    async def test_binary_detection(self):
        result = await run_shell_command("head -c 100 /dev/urandom")
        assert "binary" in result.stdout.lower()

    async def test_env_filtering(self):
        result = await run_shell_command("env")
        assert "API_KEY" not in result.stdout

    async def test_exit_code(self):
        result = await run_shell_command("exit 42")
        assert not result.success
        assert result.exit_code == 42

# tests/unit/test_shell_command_service.py
class TestShellCommandService:
    async def test_dangerous_command_blocked(self):
        # Mock service
        await service.execute("!rm -rf /")
        assert service.stats["blocked"] == 1

    async def test_interactive_command_blocked(self):
        await service.execute("!vim")
        # Should show error, not hang

    async def test_hooks_called(self):
        # Verify SHELL_COMMAND_PRE and POST events emitted
```

### Integration Tests

```python
# tests/integration/test_shell_commands.py
class TestShellCommandIntegration:
    async def test_output_in_conversation_history(self):
        # Execute !ls, verify output added to LLM history

    async def test_cancellation(self):
        # Start !sleep 30, send cancel, verify clean exit

    async def test_display_truncation(self):
        # Execute command with 100 lines, verify only 25 shown
```

## Documentation Updates

1. **User Guide**: Add "Shell Commands" section explaining ! prefix
2. **CLAUDE.md**: Add shell command section to features
3. **Plugin Development**: Document SHELL_COMMAND_* events
4. **Security**: Document dangerous command handling
5. **Changelog**: Add user-facing entry

## Migration

### From v1 (if any code written)

1. Move any shell logic from KeyPressHandler to ShellCommandService
2. Add new EventTypes to types.py
3. Register ShellCommandService in application.py
4. Wire up cancellation to Ctrl+C handler

### Existing ToolExecutor

- Remains unchanged except using shared shell_executor
- Existing <terminal> tool behavior preserved
