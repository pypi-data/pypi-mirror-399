# Kollabor

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, highly customizable terminal-based chat application for interacting with Large Language Models (LLMs). Built with a powerful plugin system and comprehensive hook architecture for complete customization.

**Install:** `pip install kollabor`
**Run:** `kollab`

## Features

- **Event-Driven Architecture**: Everything has hooks - every action triggers customizable hooks that plugins can attach to
- **Advanced Plugin System**: Dynamic plugin discovery and loading with comprehensive SDK
- **Rich Terminal UI**: Beautiful terminal rendering with status areas, visual effects, and modal overlays
- **Conversation Management**: Persistent conversation history with full logging support
- **Model Context Protocol (MCP)**: Built-in support for MCP integration
- **Tool Execution**: Function calling and tool execution capabilities
- **Pipe Mode**: Non-interactive mode for scripting and automation
- **Environment Variable Support**: Complete configuration via environment variables (API settings, system prompts, etc.)
- **Extensible Configuration**: Flexible configuration system with plugin integration
- **Async/Await Throughout**: Modern Python async patterns for responsive performance

## Installation

### From PyPI

```bash
pip install kollabor
```

### From Source

```bash
git clone https://github.com/malmazan/kollabor-cli.git
cd kollabor-cli
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Interactive Mode

Simply run the CLI to start an interactive chat session:

```bash
kollab
```

### Pipe Mode

Process a single query and exit:

```bash
# Direct query
kollab "What is the capital of France?"

# From stdin
echo "Explain quantum computing" | kollab -p

# From file
cat document.txt | kollab -p

# With custom timeout
kollab --timeout 5min "Complex analysis task"
```

## Configuration

On first run, Kollabor creates a `.kollabor-cli` directory in your current working directory:

```
.kollabor-cli/
├── config.json           # User configuration
├── system_prompt/        # System prompt templates
├── logs/                 # Application logs
└── state.db              # Persistent state
```

### Configuration Options

The configuration system uses dot notation:

- `core.llm.*` - LLM service settings
- `terminal.*` - Terminal rendering options
- `application.*` - Application metadata

### Environment Variables

All configuration can be controlled via environment variables, which take precedence over config files:

#### API Configuration

```bash
KOLLABOR_API_ENDPOINT=https://api.example.com/v1/chat/completions
KOLLABOR_API_TOKEN=your-api-token-here        # or KOLLABOR_API_KEY
KOLLABOR_API_MODEL=gpt-4
KOLLABOR_API_MAX_TOKENS=4096
KOLLABOR_API_TEMPERATURE=0.7
KOLLABOR_API_TIMEOUT=30000
```

#### System Prompt Configuration

```bash
# Direct string (highest priority)
KOLLABOR_SYSTEM_PROMPT="You are a helpful coding assistant."

# Custom file path
KOLLABOR_SYSTEM_PROMPT_FILE="./my_custom_prompt.md"
```

#### Using .env Files

Create a `.env` file in your project root:

```bash
KOLLABOR_API_ENDPOINT=https://api.example.com/v1/chat/completions
KOLLABOR_API_TOKEN=your-token-here
KOLLABOR_API_MODEL=gpt-4
KOLLABOR_SYSTEM_PROMPT_FILE="./prompts/specialized.md"
```

Load and run:

```bash
export $(cat .env | xargs)
kollab
```

See [ENV_VARS.md](ENV_VARS.md) for complete documentation and examples.

## Architecture

Kollabor follows a modular, event-driven architecture:

### Core Components

- **Application Core** (`core/application.py`): Main orchestrator
- **Event System** (`core/events/`): Central event bus with hook system
- **LLM Services** (`core/llm/`): API communication, conversation management, tool execution
- **I/O System** (`core/io/`): Terminal rendering, input handling, visual effects
- **Plugin System** (`core/plugins/`): Dynamic plugin discovery and loading
- **Configuration** (`core/config/`): Flexible configuration management
- **Storage** (`core/storage/`): State management and persistence

### Plugin Development

Create custom plugins by inheriting from base plugin classes:

```python
from core.plugins import BasePlugin
from core.events import EventType

class MyPlugin(BasePlugin):
    def register_hooks(self):
        """Register plugin hooks."""
        self.event_bus.register_hook(
            EventType.PRE_USER_INPUT,
            self.on_user_input,
            priority=HookPriority.NORMAL
        )

    async def on_user_input(self, context):
        """Process user input before it's sent to the LLM."""
        # Your custom logic here
        return context

    def get_status_line(self):
        """Provide status information for the status bar."""
        return "MyPlugin: Active"
```

## Hook System

The comprehensive hook system allows plugins to intercept and modify behavior at every stage:

- `pre_user_input` - Before processing user input
- `pre_api_request` - Before API calls to LLM
- `post_api_response` - After receiving LLM responses
- `pre_message_display` - Before displaying messages
- `post_message_display` - After displaying messages
- And many more...

## Project Structure

```
kollabor/
├── core/              # Core application modules
│   ├── application.py # Main orchestrator
│   ├── config/        # Configuration management
│   ├── events/        # Event bus and hooks
│   ├── io/            # Terminal I/O
│   ├── llm/           # LLM services
│   ├── plugins/       # Plugin system
│   └── storage/       # State management
├── plugins/           # Plugin implementations
├── docs/              # Documentation
├── tests/             # Test suite
└── main.py            # Application entry point
```

## Development

### Running Tests

```bash
# All tests
python tests/run_tests.py

# Specific test file
python -m unittest tests.test_llm_plugin

# Individual test case
python -m unittest tests.test_llm_plugin.TestLLMPlugin.test_thinking_tags_removal
```

### Code Quality

```bash
# Format code
python -m black core/ plugins/ tests/ main.py

# Type checking
python -m mypy core/ plugins/

# Linting
python -m flake8 core/ plugins/ tests/ main.py --max-line-length=88

# Clean up cache files and build artifacts
python scripts/clean.py
```

## Requirements

- Python 3.12 or higher
- aiohttp 3.8.0 or higher

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please see the documentation for development guidelines.

## Links

- [Documentation](https://github.com/malmazan/kollabor-cli/blob/main/docs/)
- [Bug Tracker](https://github.com/malmazan/kollabor-cli/issues)
- [Repository](https://github.com/malmazan/kollabor-cli)

## Acknowledgments

Built with modern Python async/await patterns and designed for extensibility and customization.
