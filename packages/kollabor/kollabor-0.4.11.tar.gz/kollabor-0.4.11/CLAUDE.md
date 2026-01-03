# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Kollabor CLI Interface** - an advanced, highly customizable terminal-based chat application for interacting with LLMs. The core principle is that **everything has hooks** - every action triggers customizable hooks that plugins can attach to for complete customization.

## Architecture

The application follows a modular, event-driven architecture:

- **Core Application** (`core/application.py`): Main orchestrator that initializes all components
- **Event System** (`core/events/`): Central event bus with hook system for plugins
- **LLM Core** (`core/llm/`): Essential LLM services including API communication, conversation management, and tool execution
- **I/O System** (`core/io/`): Terminal rendering, input handling, visual effects, and layout management
- **Plugin System** (`core/plugins/`, `plugins/`): Dynamic plugin discovery and loading
- **Storage** (`core/storage/`): State management and persistence
- **Configuration** (`core/config/`): Flexible configuration management

## Key Components

### LLM Core Services (`core/llm/`)
- `llm_service.py`: Main LLM orchestration service
- `api_communication_service.py`: API communication with rate limiting
- `conversation_logger.py`: Conversation persistence and logging (KollaborConversationLogger)
- `conversation_manager.py`: Conversation state and history management
- `tool_executor.py`: Tool/function calling execution
- `hook_system.py`: LLM-specific hook management
- `message_display_service.py`: Response formatting and display
- `mcp_integration.py`: Model Context Protocol integration
- `plugin_sdk.py`: Plugin development interface (KollaborPluginSDK)
- `model_router.py`: Model selection and routing
- `response_processor.py`: Response processing and formatting
- `response_parser.py`: Response parsing utilities

### Terminal I/O System (`core/io/`)
- `terminal_renderer.py`: Main terminal rendering with status areas
- `input_handler.py`: Raw mode input handling with key parsing
- `layout.py`: Terminal layout management and thinking animations
- `visual_effects.py`: Color palettes, visual effects, and terminal color capability detection
- `status_renderer.py`: Multi-area status display system
- `message_coordinator.py`: **CRITICAL** - Message flow AND render state coordination
- `message_renderer.py`: Message display rendering
- `buffer_manager.py`: Terminal buffer management
- `key_parser.py`: Keyboard input parsing
- `terminal_state.py`: Terminal state management
- `core_status_views.py`: Core status view implementations
- `config_status_view.py`: Configuration status display

#### CRITICAL: Render State Management Rules

**NEVER directly manipulate these `terminal_renderer` properties:**
- `input_line_written`
- `last_line_count`
- `_last_render_content` (render cache)
- `writing_messages`

**ALWAYS use `MessageDisplayCoordinator` methods instead:**

```python
# For displaying messages:
renderer.message_coordinator.display_message_sequence([...])

# For modal/fullscreen transitions:
renderer.message_coordinator.enter_alternate_buffer()  # Before opening modal
renderer.message_coordinator.exit_alternate_buffer()   # After modal closes (resets to clean state)
renderer.message_coordinator.exit_alternate_buffer(restore_state=True)  # Restore previous state

# For debugging queue status:
renderer.message_coordinator.get_queue_status()
```

**Why this matters:** Direct state manipulation causes bugs like duplicate input boxes, stale renders, and incorrect clearing after buffer transitions. The coordinator uses flag-based coordination - `enter_alternate_buffer()` sets `writing_messages=True` to block the render loop, and `display_queued_messages()` resets the flags on completion.

**Modal exit patterns:**
```python
# Standard exit - restores state and renders input
await self._exit_modal_mode()

# Minimal exit - for commands that display their own content (e.g., /branch)
# This prevents duplicate input boxes when command will render messages
await self._exit_modal_mode_minimal()
```

**The only safe direct calls:**
- `terminal_renderer.clear_active_area()` - uses state correctly
- `terminal_renderer.invalidate_render_cache()` - just clears cache

### Plugin Architecture
- Plugin discovery from `plugins/` directory
- Dynamic instantiation with dependency injection
- Hook registration for event interception
- Configuration merging from plugin configs

## Development Commands

### Installation & Setup
```bash
# Install from source (development mode)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install from PyPI (for users)
pip install kollabor
```

### Running the Application
```bash
# Using installed CLI command (after pip install)
kollab

# Using main.py directly (development)
python main.py

# Pipe mode examples
kollab "What is Python?"
echo "Explain async/await" | kollab -p
cat document.txt | kollab -p --timeout 5min
```

### Testing
```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
python -m unittest tests.test_llm_plugin
python -m unittest tests.test_config_manager
python -m unittest tests.test_plugin_registry

# Run individual test case
python -m unittest tests.test_llm_plugin.TestLLMPlugin.test_thinking_tags_removal
```

### Code Quality
```bash
# Install dependencies
pip install -r requirements.txt

# Format code (Black is configured for 88-character line length)
python -m black core/ plugins/ tests/ main.py

# Type checking (if mypy is available)
python -m mypy core/ plugins/

# Run linting (if flake8 is available)
python -m flake8 core/ plugins/ tests/ main.py --max-line-length=88

# Clean up cache files and build artifacts
python scripts/clean.py
```

### Building & Publishing
```bash
# Clean previous builds
python scripts/clean.py

# Build distribution packages
python -m build

# Upload to TestPyPI (for testing)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

### Debugging
- Application logs to `.kollabor-cli/logs/kollabor.log` with daily rotation
- Configuration stored in `.kollabor-cli/config.json`
- State persistence in `.kollabor-cli/state.db`
- Use `logging.getLogger(__name__)` in modules for consistent logging

## Entry Points

The application has two entry points:

1. **`kollab` command** (after `pip install kollabor`):
   - Entry point defined in `pyproject.toml` as `kollab = "kollabor_cli_main:cli_main"`
   - Uses `kollabor_cli_main.py` → `core/cli.py` → `core/application.py`
   - Preferred for end users and production use

2. **`python main.py`** (development mode):
   - Direct execution for development
   - Imports from local `core/` directory
   - Used during active development

Both entry points initialize the `TerminalLLMChat` application orchestrator in `core/application.py`.

## Configuration System

Configuration uses dot notation (e.g., `config.get("core.llm.max_history", 90)`):
- Core LLM settings: `core.llm.*`
- Terminal rendering: `terminal.*`
- Application metadata: `application.*`

### Configuration Directories

The application uses a **priority-based configuration directory system** (see `core/utils/config_utils.py`):

**Resolution order:**
1. **Local** `.kollabor-cli/` in current directory (project-specific override)
2. **Global** `~/.kollabor-cli/` in home directory (default for most users)

If local `.kollabor-cli/` exists, it takes precedence over global.

**Directory contents:**
- `config.json` - User configuration with plugin settings
- `logs/` - Application logs with daily rotation
- `state.db` - Persistent state and conversation history
- `conversations/` - Conversation logs
- `system_prompt/` - System prompt files (default.md, etc.)

### System Prompt Initialization

On first run (`initialize_system_prompt()` in `config_utils.py`):

1. If **local** `.kollabor-cli/system_prompt/` exists with `.md` files → use local (project-specific)
2. If global `~/.kollabor-cli/system_prompt/` doesn't exist → create from bundled `system_prompt/default.md`
3. Copy all prompts from global to local for project-specific customization

This ensures each project can have its own customized system prompts while maintaining a global default.

### Dynamic System Prompts with `<trender>` Tags

System prompts support dynamic content rendering at runtime using `<trender>` tags (implemented in `core/utils/prompt_renderer.py`):

**Available Tags:**
```markdown
<!-- Project structure -->
<trender type="project_tree" />
<trender type="project_tree" max_depth="3" />

<!-- File listings -->
<trender type="file_list" pattern="**/*.py" />
<trender type="file_list" pattern="core/**/*.py" exclude="__pycache__" />

<!-- File contents -->
<trender type="file_content" path="README.md" />
<trender type="file_content" path="ARCHITECTURE.md" />

<!-- Metadata -->
<trender type="timestamp" />
<trender type="timestamp" format="%Y-%m-%d %H:%M:%S" />
```

**Usage in System Prompts:**
```markdown
# System Prompt

You are a coding assistant for the Kollabor project.

## Project Structure
<trender type="project_tree" max_depth="2" />

## Recent Changes
<trender type="file_content" path="CHANGELOG.md" />

## Current Time
<trender type="timestamp" />
```

**Priority Order for System Prompts:**
1. `KOLLABOR_SYSTEM_PROMPT` environment variable (direct string)
2. `KOLLABOR_SYSTEM_PROMPT_FILE` environment variable (file path)
3. Local `.kollabor-cli/system_prompt/default.md`
4. Global `~/.kollabor-cli/system_prompt/default.md`
5. Built-in fallback

All prompts are rendered through `render_system_prompt()` before being sent to the LLM, which processes `<trender>` tags and injects dynamic content.

## Core Architecture Patterns

### Event-Driven Design
The application uses an event bus (`core/events/bus.py`) that coordinates between:
- **HookRegistry** (`core/events/registry.py`): Manages hook registration and lookup by event type
- **HookExecutor** (`core/events/executor.py`): Handles hook execution with error handling and priority ordering
- **EventProcessor** (`core/events/processor.py`): Processes events through registered hooks in sequence
- **EventBus** (`core/events/bus.py`): Central coordinator that combines the above components

### Plugin Lifecycle
1. **Discovery**: `PluginDiscovery` scans `plugins/` directory for plugin modules
2. **Registry**: `PluginRegistry` maintains loaded plugin metadata and configurations
3. **Factory**: `PluginFactory` instantiates plugins with dependency injection (event_bus, config, renderer, state_manager)
4. **Initialization**: Plugins call `initialize()` and `register_hooks()` during application startup
5. **Execution**: Events trigger registered hooks through the event bus with priority ordering
6. **Cleanup**: Plugins call `shutdown()` during application teardown

### LLM Service Architecture
The `LLMService` (`core/llm/llm_service.py`) orchestrates multiple specialized services:
- **APICommunicationService**: HTTP client with rate limiting and retry logic
- **KollaborConversationLogger**: Persistent conversation history to `.kollabor-cli/conversations/`
- **MessageDisplayService**: Response formatting, streaming, and display coordination
- **ToolExecutor**: Function calling execution and tool result processing
- **MCPIntegration**: Model Context Protocol server discovery and integration
- **KollaborPluginSDK**: Plugin development interface with helper methods
- **LLMHookSystem**: LLM-specific hook management for request/response interception

### Plugin System Details
Plugins are discovered from two possible locations (in order):
1. Package installation directory: `<package_root>/plugins/` (for pip install)
2. Current working directory: `./plugins/` (for development mode)

Each plugin can:
- Register hooks at any priority level (CRITICAL, HIGH, NORMAL, LOW)
- Access shared services via dependency injection
- Contribute status line items to areas A, B, or C
- Merge custom configuration into the global config
- Register slash commands via the CommandRegistry

## Hook System

The application's hook system allows plugins to:
- Intercept user input before processing (`pre_user_input`)
- Transform LLM requests before API calls (`pre_api_request`)
- Process responses before display (`post_api_response`)
- Add custom status indicators via `get_status_line()`
- Create new terminal UI elements

## Plugin Development

Plugins should:
1. Inherit from base plugin classes in `core/plugins/`
2. Register hooks in `register_hooks()` method using `EventType` enum
3. Provide status line information via `get_status_line()`
4. Implement `initialize()` and `shutdown()` lifecycle methods
5. Follow the async/await pattern for all hook handlers

## Project Structure

```
.
├── core/                           # Core application modules
│   ├── application.py             # Main orchestrator
│   ├── config/                    # Configuration management
│   ├── events/                    # Event bus and hook system
│   ├── io/                        # Terminal I/O, rendering, input handling
│   ├── llm/                       # LLM services (API, conversation, tools)
│   ├── models/                    # Data models
│   ├── plugins/                   # Plugin system (discovery, registry)
│   ├── storage/                   # State management
│   ├── utils/                     # Utility functions
│   ├── commands/                  # Command system (parser, registry, executor)
│   ├── ui/                        # UI system (modals, widgets, rendering)
│   ├── effects/                   # Visual effects (matrix rain, etc.)
│   └── logging/                   # Logging configuration
├── plugins/                       # Plugin implementations
│   ├── enhanced_input/           # Enhanced input plugin modules
│   ├── enhanced_input_plugin.py  # Main enhanced input plugin
│   ├── hook_monitoring_plugin.py # Hook system monitoring
│   └── [other plugins]
├── tests/                         # Test suite
│   ├── run_tests.py              # Test runner
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── visual/                   # Visual effect tests
│   ├── test_*.py                 # Component tests
│   └── README.md                 # Test documentation
├── docs/                          # Comprehensive documentation
│   ├── project-management/       # Project processes and templates
│   ├── reference/                # API docs and architecture
│   ├── sdlc/                     # Software development lifecycle
│   ├── sop/                      # Standard operating procedures
│   └── standards/                # Coding and quality standards
├── main.py                       # Application entry point
├── .kollabor-cli/                # Runtime data (created at startup)
│   ├── config.json              # User configuration
│   ├── logs/                    # Application logs
│   └── state.db                 # Persistent state
└── .github/scripts/              # Repository automation
```

Key directories:
- **`core/`**: Modular core functionality with clear separation of concerns
- **`plugins/`**: Dynamic plugin system with auto-discovery
- **`tests/`**: Comprehensive test coverage with multiple test types
- **`docs/`**: Extensive documentation following enterprise standards
- **`.kollabor-cli/`**: Runtime configuration, logs, and state (created automatically)

## Development Guidelines

### Git Workflow and Branch Protection

The repository enforces a strict issue-tracking workflow via git hooks:

**Pre-commit Hook Requirements:**
- All commits to `core/`, `plugins/`, or `tests/` must reference a GitHub issue
- Branch naming: `issue-123-description` or `feature/issue-123-description`
- Commit messages must include: `fixes #123`, `closes #123`, `resolves #123`, or `#123`
- Main branch is protected - no direct pushes allowed

**Development Workflow:**
```bash
# 1. Create issue on GitHub (or find existing issue number)
gh issue create --title "Fix version display"

# 2. Create branch with issue number
git checkout -b issue-8-version-display-fix

# 3. Make changes and commit with issue reference
git commit -m "Fix version display in development mode fixes #8"

# 4. Push to remote
git push -u kollaborai issue-8-version-display-fix

# 5. Create pull request
gh pr create --title "Fix version display" --body "Fixes #8"
```

**Pre-push Hook:**
- Blocks direct pushes to `main` branch
- Requires all changes to go through pull request workflow
- Emergency hotfixes should use `hotfix/issue-123-description` branches

### Version Management

Version number is managed centrally in `pyproject.toml`. The application detects whether it's running from source or installed package:

**Development mode** (`python main.py`):
- Reads version from `pyproject.toml` at runtime
- Located via `Path(__file__).parent.parent / "pyproject.toml"`
- Displayed in banner and used for config metadata

**Production mode** (installed via pip):
- Uses package metadata from `importlib.metadata.version("kollabor")`
- Version set during `pip install` from `pyproject.toml`

**Files that read version:**
- `core/application.py` - Banner display
- `core/cli.py` - CLI version flag
- `core/config/loader.py` - Config version metadata

To update version for a release, only modify `pyproject.toml` - all other files read from it automatically.

### Code Standards
- Follow PEP 8 with 88-character line length (Black formatter)
- Use double quotes for strings, single quotes for character literals
- All async functions should use proper `async`/`await` patterns
- Type hints required for all public functions and methods
- Comprehensive docstrings for classes and public methods
- Use `logging.getLogger(__name__)` for consistent logging across modules

### Async/Await Patterns
The application uses async/await throughout for responsive performance:
- **Main event loop**: `asyncio.run()` in `cli_main()` starts the application
- **Concurrent tasks**: Render loop and input handler run concurrently using `asyncio.gather()`
- **Background tasks**: Use `app.create_background_task()` for proper task tracking and cleanup
- **Cleanup**: All tasks cancelled in `app.cleanup()` with guaranteed execution via `finally` block
- **Plugin hooks**: Must be async (`async def`) even if not using await internally

### Testing Strategy
- Unit tests in `tests/unit/` for individual components
- Integration tests in `tests/integration/` for cross-component functionality
- Visual tests in `tests/visual/` for terminal rendering
- Component tests (`test_*.py`) for specific modules
- Use unittest framework with descriptive test method names
- Test coverage includes LLM plugins, configuration, and plugin registry

### Hook Development
When creating hooks, consider:
- Hook priority using `HookPriority` enum (CRITICAL, HIGH, NORMAL, LOW)
- Error handling - hooks should not crash the application (errors are caught by HookExecutor)
- Performance - hooks are in the hot path for user interaction
- State management - avoid shared mutable state between hooks
- Return modified context from hooks (context is passed through hook chain)
- All hook handlers must be async functions

## Key Features

### Interactive Mode
Standard terminal-based chat interface with:
- Real-time status updates across three status areas (A, B, C)
- Thinking animations during LLM processing
- Multi-line input with visual input box
- Conversation history with scrollback
- Plugin-driven extensibility

### Pipe Mode
Non-interactive mode for scripting and automation:
- Process single query and exit: `kollab "query here"`
- Read from stdin: `echo "query" | kollab -p`
- Configurable timeout: `kollab --timeout 5min "complex task"`
- Suppresses interactive UI elements (status bar, cursor, exit messages)
- Full plugin support (plugins can check `app.pipe_mode` flag)
- Automatically waits for LLM processing and tool calls to complete

### Other Features
- **Modal System**: Full-screen modal overlays with widget support (dropdowns, checkboxes, sliders, text inputs)
- **Command System**: Extensible slash command parser and executor with menu rendering
- **Plugin System**: Dynamic plugin discovery with comprehensive SDK
- **Visual Effects**: Matrix rain effect and customizable color palettes
- **Status Display**: Multi-area status rendering with flexible view registry
- **Configuration**: Dot notation config system with plugin integration
- **Message Processing**: Advanced response parsing with thinking tag removal

### Terminal Color Support

The application automatically detects terminal color capabilities and adjusts output accordingly:

**Supported Color Modes:**
- **TRUE_COLOR (24-bit)**: Full RGB colors (16 million colors)
- **EXTENDED (256-color)**: 256-color palette fallback
- **BASIC (16-color)**: Basic ANSI colors
- **NONE**: No colors (monochrome)

**Auto-detection checks:**
1. `COLORTERM` env var (`truecolor`, `24bit`)
2. `TERM_PROGRAM` (iTerm2, VS Code, Alacritty, Kitty, etc.)
3. `TERM` variable (`xterm-256color`, etc.)
4. Apple Terminal.app is detected as 256-color only

**Manual Override:**
```bash
# Force specific color mode
KOLLABOR_COLOR_MODE=256 kollab        # 256-color mode
KOLLABOR_COLOR_MODE=truecolor kollab  # Force true color
KOLLABOR_COLOR_MODE=none kollab       # Disable colors

# Add to shell config for persistence
export KOLLABOR_COLOR_MODE=256
```

**Valid values for `KOLLABOR_COLOR_MODE`:**
- `truecolor`, `24bit`, `true` → 24-bit RGB
- `256`, `256color`, `extended` → 256-color palette
- `16`, `basic` → 16 basic colors
- `none`, `off`, `no` → No colors

**Programmatic control:**
```python
from core.io.visual_effects import set_color_support, ColorSupport

set_color_support(ColorSupport.EXTENDED)  # Force 256-color
set_color_support(ColorSupport.TRUE_COLOR)  # Force true color
```

All color operations in `ColorPalette`, `GradientRenderer`, and plugin color engines automatically use the detected/configured color mode

## Slash Commands

The application includes an extensible slash command system with menu-based command discovery:

**Built-in Commands:**
- `/help` - Show available commands
- `/save` - Save conversation to file or clipboard (JSON, markdown, text)
- `/terminal` (aliases: `/tmux`, `/term`, `/t`) - Manage tmux sessions
- `/matrix` - Enter the Matrix with falling code rain effect
- `/version` - Show application version

**Command Menu Behavior:**
- Triggered by typing `/` in input
- Filters commands as you type with prefix matching
- Arrow keys navigate, Enter executes
- Prioritizes name matches over alias matches (e.g., `/t` shows `/terminal` first, not `/save` via "transcript" alias)

**Adding Custom Commands:**
Plugins can register commands via `CommandRegistry`:
```python
from core.commands.registry import SlashCommandRegistry, CommandDefinition, CommandCategory

registry = SlashCommandRegistry()
registry.register_command(CommandDefinition(
    name="mycommand",
    description="My custom command",
    category=CommandCategory.CUSTOM,
    aliases=["mc", "mycmd"],
    handler=my_handler_function
))
```

## Current State

Recent development focused on:
- Command menu filtering improvements (prefix matching prioritization)
- Dynamic system prompt rendering with `<trender>` tags
- Environment variable configuration system
- Version management automation (reads from pyproject.toml)
- Git workflow enforcement via pre-commit/pre-push hooks
- Windows compatibility and cross-platform support
- Tmux plugin with live modal viewing
- Save conversation plugin with multiple formats

The codebase uses Python 3.12+ and follows async/await patterns throughout.