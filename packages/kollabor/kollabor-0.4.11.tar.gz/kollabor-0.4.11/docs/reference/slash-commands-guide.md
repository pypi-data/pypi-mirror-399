
# Slash Commands Guide

## Overview

Slash commands in the Kollabor system are implemented through an event-driven architecture that integrates with the input handling system. When users type commands starting with `/`, they are parsed, registered, and executed through a comprehensive command framework.

## Architecture

The slash command system is built around several core components defined in `core/events/models.py` and implemented in `core/commands/`:

### Core Data Models

The system uses several key data models defined in `core/events/models.py`:

- **SlashCommand**: Represents a parsed command with name, arguments, and metadata
- **CommandDefinition**: Defines a command with handler, metadata, and configuration
- **CommandResult**: Represents the result of command execution
- **CommandMode**: Enum defining different command execution modes
- **CommandCategory**: Enum for organizing commands by category

### Core Components

1. **Command Parser** (`core/commands/parser.py`)
   - Detects slash commands in user input
   - Parses command names and arguments using shell-like parsing
   - Handles quoted arguments and parameter extraction
   - Validates command structure

2. **Command Registry** (`core/commands/registry.py`)
   - Manages command registration and discovery
   - Handles command aliases and conflict detection
   - Organizes commands by plugin and category
   - Provides search and lookup functionality

3. **Command Executor** (`core/commands/executor.py`)
   - Executes registered commands with proper error handling
   - Integrates with event bus for lifecycle events
   - Handles different command modes (INSTANT, STATUS_TAKEOVER, etc.)
   - Manages UI configuration for modal commands

4. **System Commands** (`core/commands/system_commands.py`)
   - Provides built-in system commands
   - Registers core functionality like help, config, status
   - Implements command handlers for essential system operations

5. **Menu Renderer** (`core/commands/menu_renderer.py`)
   - Renders interactive command menu overlay
   - Handles command filtering and selection
   - Provides visual feedback for command navigation

## Command Structure

### Basic Syntax

```
/command_name [argument1] [argument2] [--flag=value]
```

### Parsing Features

The parser supports:

- **Quoted arguments**: `/save "my file.txt"`
- **Flag arguments**: `/config --theme=dark --verbose`
- **Short flags**: `/run -f script.py`
- **Boolean flags**: `/debug --enable`

### Command Detection

Commands are detected in the input handler when:
1. User input starts with `/`
2. Input is parsed by `SlashCommandParser`
3. Command is looked up in the registry
4. Command is executed through the executor

## Command Registration

### Command Definition Structure

Commands are registered using `CommandDefinition`:

```python
from core.events.models import CommandDefinition, CommandMode, CommandCategory

command_def = CommandDefinition(
    name="help",
    description="Show available commands",
    handler=self.handle_help,
    plugin_name="system",
    category=CommandCategory.SYSTEM,
    mode=CommandMode.INSTANT,
    aliases=["h", "?"],
    icon="❓"
)
```

### Registration Process

1. **System Commands**: Registered in `SystemCommandsPlugin.register_commands()`
2. **Plugin Commands**: Registered through plugin initialization
3. **Validation**: Registry validates command definitions
4. **Conflict Detection**: Prevents duplicate command names
5. **Alias Resolution**: Maps aliases to command names

### Command Modes

Different modes affect how commands are displayed and handled:

- **INSTANT**: Commands that execute immediately and show results
- **STATUS_TAKEOVER**: Commands that take over the status area
- **MODAL**: Commands that open modal overlays
- **MENU_POPUP**: Commands that show interactive menus

## Available System Commands

### Core System Commands

Built-in commands provided by `SystemCommandsPlugin`:

- `/help` (aliases: `h`, `?`) - Show available commands and usage
- `/config` (aliases: `settings`, `preferences`) - Open system configuration panel
- `/status` (aliases: `info`, `diagnostics`) - Show system status and diagnostics
- `/version` (aliases: `v`, `ver`) - Show application version information
- `/resume` (aliases: `restore`, `continue`) - Resume a previous conversation session

### Command Categories

Commands are organized into categories:

- **SYSTEM**: Core system management commands
- **CONVERSATION**: Conversation and chat management
  - `/resume` - Resume previous conversation sessions
- **AGENT**: Agent-related operations
- **DEVELOPMENT**: Development tools and utilities
- **FILE**: File management operations
- **TASK**: Task management commands
- **CUSTOM**: Plugin-specific commands

## Command Implementation

### Handler Function Signature

Command handlers must accept a `SlashCommand` object:

```python
async def handle_help(self, command: SlashCommand) -> CommandResult:
    """Handle help command."""
    try:
        if command.args:
            # Show help for specific command
            return await self._show_command_help(command.args[0])
        else:
            # Show all commands
            return await self._show_all_commands()
    except Exception as e:
        return CommandResult(
            success=False,
            message=f"Error displaying help: {str(e)}",
            display_type="error"
        )
```

### Command Result Structure

Commands return `CommandResult` objects:

```python
return CommandResult(
    success=True,
    message="Command completed successfully",
    display_type="info",  # info, success, warning, error
    data={"key": "value"},  # Optional additional data
    ui_config=None  # Optional UI configuration for modals
)
```

### UI Configuration

Commands can specify UI configurations for different display modes:

```python
from core.events.models import UIConfig

ui_config = UIConfig(
    type="modal",
    title="Configuration",
    width=80,
    height=20,
    modal_config={
        "sections": [...],
        "footer": "Navigation instructions"
    }
)
```

## Integration with Input System

### Command Detection Flow

1. **Input Detection**: `InputHandler` detects `/` at start of input
2. **Command Mode Entry**: System enters `CommandMode.MENU_POPUP`
3. **Menu Display**: Interactive menu shows available commands
4. **Command Filtering**: Menu filters as user types
5. **Command Selection**: User selects command with arrow keys
6. **Command Execution**: Selected command is parsed and executed

### Event Integration

The command system integrates with the event bus:

- **SLASH_COMMAND_DETECTED**: Emitted when command is detected
- **SLASH_COMMAND_EXECUTE**: Emitted when command starts execution
- **SLASH_COMMAND_COMPLETE**: Emitted when command finishes
- **SLASH_COMMAND_ERROR**: Emitted when command fails
- **COMMAND_MENU_SHOW/HIDE**: Emitted for menu lifecycle events

### Hook System

Commands can register hooks for:

- **COMMAND_MENU_RENDER**: Provide menu content for display
- **MODAL_TRIGGER**: Handle modal display requests
- **STATUS_MODAL_TRIGGER**: Handle status modal requests
- **COMMAND_OUTPUT_DISPLAY**: Display command results

## Error Handling

### Validation Layers

1. **Input Validation**: Parser validates command structure
2. **Registry Validation**: Registry validates command definitions
3. **Execution Validation**: Executor validates command state
4. **Handler Validation**: Individual handlers validate arguments

### Error Types

Common error scenarios:

- **Command Not Found**: Unknown command name
- **Invalid Arguments**: Missing or malformed arguments
- **Permission Denied**: Insufficient permissions
- **Handler Error**: Exception in command handler
- **System Error**: Internal system failures

### Error Response Format

```python
CommandResult(
    success=False,
    message="Error: Command 'unknown' not found",
    display_type="error",
    error_code="COMMAND_NOT_FOUND",
    data={"suggestions": ["help", "status"]}
)
```

## Testing Commands

### Unit Tests

Located in `tests/unit/test_slash_commands.py`:

- Test command parsing and validation
- Test registry operations
- Test executor functionality
- Test error handling scenarios

### Integration Tests

Located in `tests/integration/test_slash_commands_integration.py`:

- Test end-to-end command flow
- Test system commands registration
- Test menu functionality
- Test event integration

## Extending the System

### Adding New Commands

1. **Create Command Handler**: Implement handler function
2. **Create Command Definition**: Define command metadata
3. **Register Command**: Add to registry during initialization
4. **Add Tests**: Write unit and integration tests

### Plugin Commands

Plugins can register commands:

```python
class MyPlugin:
    async def initialize(self, event_bus, config, **kwargs):
        command_registry = kwargs.get('command_registry')
        if command_registry:
            command_def = CommandDefinition(
                name="mycommand",
                description="My custom command",
                handler=self.handle_my_command,
                plugin_name=self.name,
                category=CommandCategory.CUSTOM
            )
            command_registry.register_command(command_def)
```

### Custom Command Categories

Extend `CommandCategory` enum in `core/events/models.py`:

```python
class CommandCategory(Enum):
    SYSTEM = "system"
    CONVERSATION = "conversation"
    # Add new categories
    MY_CATEGORY = "my_category"
```

## Performance Considerations

### Registry Optimization

- Commands are indexed by name for fast lookup
- Aliases are mapped to canonical names
- Categories are cached for efficient grouping

### Memory Management

- Command definitions are stored once in registry
- Parsed commands are lightweight objects
- Event emissions are minimized for performance

### Async Operations

- All command handlers should be async
- Long-running operations should use await
- Event emissions are non-blocking

## Security

### Input Sanitization

- Command names are validated against allowed characters
- Arguments are processed safely using shlex.split()
- Control characters are filtered from input

### Permission System

Commands can specify permission requirements:

```python
command_def = CommandDefinition(
    name="admin",
    description="Admin-only command",
    handler=self.handle_admin,
    permission="admin"  # Required permission level
)
```

### Sandboxing

Consider sandboxing for:

- File operations in plugin commands
- Network access in untrusted commands
- System command execution

## Debugging

### Logging

Enable debug logging for command system:

```python
import logging
logging.getLogger("core.commands").setLevel(logging.DEBUG)
```

### Registry Statistics

Get registry information for debugging:

```python
stats = command_registry.get_registry_stats()
print(f"Commands: {stats['total_commands']}")
print(f"Plugins: {stats['plugins']}")
```

### Command Tracing

Trace command execution through events:

```python
# Hook into command events for debugging
await event_bus.register_hook(Hook(
    name="debug_commands",
    event_type=EventType.SLASH_COMMAND_EXECUTE,
    callback=self.trace_command_execution
))
```

## Future Enhancements

### Planned Features

1. **Command Autocomplete**: Tab completion for commands and arguments
2. **Command History**: Navigate through previous commands
3. **Command Pipelines**: Chain commands together
4. **Custom Shortcuts**: User-defined command aliases
5. **Interactive Help**: Context-sensitive help system

### Extension Points

1. **Custom Parsers**: Plugin-specific argument parsers
2. **Result Formatters**: Custom output formatting
3. **Validation Rules**: Custom argument validation
4. **Middleware**: Pre/post processing hooks

## Conclusion

The slash command system provides a robust, extensible framework for user interaction in Kollabor. By following the established patterns and interfaces, developers can create powerful commands that integrate seamlessly with the existing architecture.

For implementation details, refer to the source code in `core/commands/` and the test files in `tests/`.

---

## Related Documentation

- **[Resume Command Specification](../features/RESUME_COMMAND_SPEC.md)** - Complete specification for the `/resume` command
- **[Config Command Enhancement Spec](../CONFIG_COMMAND_ENHANCEMENT_SPEC.md)** - Detailed configuration system documentation
- **[Modal System Implementation Guide](../modal-system-implementation-guide.md)** - Modal UI framework documentation
