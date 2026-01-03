"""Slash command system for Kollabor CLI.

This module provides a comprehensive slash command system that integrates
with the EventBus architecture and plugin system.

Key Components:
- Parser: Detects and parses slash commands from user input
- Registry: Manages command registration and discovery
- Executor: Executes commands with proper error handling
- UI: Handles command menus and status area interactions

Example Usage:
    # Register a command in a plugin
    self.register_command(
        name="save",
        handler=self.handle_save,
        description="Save conversation to file",
        mode=CommandMode.INLINE_INPUT
    )

    # Execute a command
    result = await command_executor.execute(command, event_bus)
"""

from ..events.models import (
    CommandMode,
    CommandCategory,
    CommandDefinition,
    SlashCommand,
    CommandResult,
    UIConfig,
    ParameterDefinition
)

__all__ = [
    "CommandMode",
    "CommandCategory",
    "CommandDefinition",
    "SlashCommand",
    "CommandResult",
    "UIConfig",
    "ParameterDefinition"
]