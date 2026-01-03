"""System prompt dynamic command renderer.

Processes <trender>command</trender> tags in system prompts by executing
the commands and replacing tags with their output.
"""

import logging
import re
import subprocess
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PromptRenderer:
    """Renders dynamic content in system prompts by executing commands."""

    # Pattern to match <trender>command</trender> tags
    # Excludes matches that are inside backticks (code examples)
    TRENDER_PATTERN = re.compile(r'(?<!`)<trender>(.*?)</trender>(?!`)', re.DOTALL)

    def __init__(self, timeout: int = 5):
        """Initialize the prompt renderer.

        Args:
            timeout: Maximum seconds to wait for each command execution.
        """
        self.timeout = timeout
        self._command_cache: Dict[str, str] = {}

    def render(self, prompt_content: str) -> str:
        """Render all <trender> tags in the prompt content.

        Args:
            prompt_content: System prompt content with <trender> tags.

        Returns:
            Processed prompt with commands replaced by their output.
        """
        if not prompt_content:
            return prompt_content

        # Find all trender tags
        matches = list(self.TRENDER_PATTERN.finditer(prompt_content))

        if not matches:
            logger.debug("No <trender> tags found in system prompt")
            return prompt_content

        logger.info(f"Found {len(matches)} <trender> tag(s) to process")

        # Process matches in reverse order to maintain string positions
        result = prompt_content
        for match in reversed(matches):
            command = match.group(1).strip()
            start_pos = match.start()
            end_pos = match.end()

            # Execute command and get output
            output = self._execute_command(command)

            # Replace the tag with the output
            result = result[:start_pos] + output + result[end_pos:]

        return result

    def _execute_command(self, command: str) -> str:
        """Execute a shell command and return its output.

        Args:
            command: Shell command to execute.

        Returns:
            Command output or error message.
        """
        # Check cache first
        if command in self._command_cache:
            logger.debug(f"Using cached output for: {command}")
            return self._command_cache[command]

        try:
            logger.debug(f"Executing trender command: {command}")

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd="."  # Execute in current directory
            )

            # Get output (prefer stdout, fallback to stderr)
            output = result.stdout if result.stdout else result.stderr
            output = output.strip()

            if result.returncode != 0:
                error_msg = f"[trender error: command exited with code {result.returncode}]"
                if result.stderr:
                    error_msg += f"\n{result.stderr.strip()}"
                logger.warning(f"Command failed: {command} (exit code: {result.returncode})")
                output = error_msg

            # Cache successful results
            if result.returncode == 0:
                self._command_cache[command] = output

            logger.debug(f"Command output ({len(output)} chars): {output[:100]}")
            return output

        except subprocess.TimeoutExpired:
            error_msg = f"[trender error: command timed out after {self.timeout}s]"
            logger.error(f"Command timed out: {command}")
            return error_msg

        except Exception as e:
            error_msg = f"[trender error: {type(e).__name__}: {str(e)}]"
            logger.error(f"Failed to execute command '{command}': {e}")
            return error_msg

    def clear_cache(self):
        """Clear the command output cache."""
        self._command_cache.clear()
        logger.debug("Cleared trender command cache")

    def get_all_commands(self, prompt_content: str) -> List[str]:
        """Extract all commands from trender tags without executing.

        Args:
            prompt_content: System prompt content with <trender> tags.

        Returns:
            List of commands found in trender tags.
        """
        matches = self.TRENDER_PATTERN.findall(prompt_content)
        commands = [cmd.strip() for cmd in matches]
        return commands


def render_system_prompt(prompt_content: str, timeout: int = 5) -> str:
    """Convenience function to render a system prompt.

    Args:
        prompt_content: System prompt content with <trender> tags.
        timeout: Maximum seconds to wait for each command execution.

    Returns:
        Processed prompt with commands replaced by their output.
    """
    renderer = PromptRenderer(timeout=timeout)
    return renderer.render(prompt_content)
