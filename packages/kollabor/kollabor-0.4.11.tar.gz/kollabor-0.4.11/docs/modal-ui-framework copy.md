# Modal UI Framework for Slash Commands

## 🎯 Vision

Create an animated modal/panel system that allows slash commands to display rich, interactive configuration interfaces. Modals overlay the chat interface at 80% screen width, letting users see the background while interacting with forms, dropdowns, and other widgets.

## 🎨 Design Principles

- **Declarative**: JSON-based configuration, no complex UI code needed
- **Plugin-Friendly**: Easy integration for plugin developers
- **Animated**: Smooth entrance/exit animations
- **Keyboard-First**: Full arrow key navigation, Enter to activate, Esc to cancel
- **Background-Visible**: Modal overlays preserve context
- **Config-Integrated**: Direct integration with `.kollabor-cli/config.json`

## 📐 Modal Specifications

### Dimensions & Positioning
- **Width**: 80% of terminal width (configurable per command)
- **Height**: ~50% of terminal height (auto-size based on content)
- **Position**: Centered horizontally, vertically centered
- **Background**: Dimmed chat interface still visible
- **Animation**: Slide down from top with fade-in effect

### Navigation Flow
```
/ → Command Menu
↓ → Navigate to command
Enter → Opens modal/panel
↑↓ → Navigate within modal
Enter → Activate/toggle widget
Tab → Next widget
Shift+Tab → Previous widget
Esc → Close modal, return to chat
```

## 🏗️ JSON Schema

### Basic Modal Definition
```json
{
  "command": "/config",
  "ui": {
    "type": "modal",
    "title": "System Configuration",
    "width": 80,
    "height": "auto",
    "animation": "slide_down",
    "sections": [
      {
        "title": "LLM Settings",
        "config_path": "core.llm",
        "widgets": [
          {
            "type": "text_input",
            "label": "API URL",
            "key": "api_url",
            "placeholder": "http://localhost:1234",
            "validation": "url"
          },
          {
            "type": "dropdown",
            "label": "Model",
            "key": "model",
            "options": [
              "qwen/qwen3-4b",
              "gpt-4",
              "claude-3-sonnet"
            ]
          },
          {
            "type": "slider",
            "label": "Temperature",
            "key": "temperature",
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "format": "{:.1f}"
          }
        ]
      }
    ],
    "actions": [
      {
        "label": "Save Changes",
        "action": "save",
        "style": "primary",
        "shortcut": "Ctrl+S"
      },
      {
        "label": "Reset to Defaults",
        "action": "reset",
        "style": "secondary"
      },
      {
        "label": "Cancel",
        "action": "cancel",
        "style": "tertiary",
        "shortcut": "Esc"
      }
    ]
  }
}
```

### Widget Types

#### Text Input
```json
{
  "type": "text_input",
  "label": "API URL",
  "key": "api_url",
  "placeholder": "Enter URL...",
  "validation": "url|required|min:10",
  "help_text": "The base URL for your LLM API endpoint"
}
```

#### Dropdown (Static Options)
```json
{
  "type": "dropdown",
  "label": "Provider",
  "key": "provider",
  "options": ["anthropic", "openai", "local"],
  "option_labels": ["Anthropic", "OpenAI", "Local Server"]
}
```

#### Dropdown (Dynamic Options)
```json
{
  "type": "dropdown",
  "label": "Model",
  "key": "model",
  "options_provider": "llm_models",
  "fallback_options": ["qwen/qwen3-4b", "gpt-4"],
  "refresh_on_focus": true,
  "loading_text": "Loading models..."
}
```

#### Checkbox
```json
{
  "type": "checkbox",
  "label": "Enable Streaming",
  "key": "enable_streaming",
  "help_text": "Stream responses in real-time"
}
```

#### Slider
```json
{
  "type": "slider",
  "label": "Max History",
  "key": "max_history",
  "min": 10,
  "max": 500,
  "step": 10,
  "format": "{} messages"
}
```

#### Radio Group
```json
{
  "type": "radio",
  "label": "Log Level",
  "key": "log_level",
  "options": ["DEBUG", "INFO", "WARNING", "ERROR"],
  "layout": "horizontal"
}
```

#### Progress Bar (Read-only)
```json
{
  "type": "progress",
  "label": "Memory Usage",
  "value": 0.65,
  "format": "{:.1%}",
  "color": "blue",
  "show_value": true
}
```

## 🔄 Dynamic Option Population System

### Concept
Instead of hardcoding dropdown options, the app queries endpoints and services to populate options dynamically. This ensures the UI always shows current, accurate data.

### Option Providers

#### Built-in Providers
```python
class OptionProviders:
    @staticmethod
    async def llm_models(config_path: str) -> List[dict]:
        """Query LLM endpoint for available models"""
        api_url = get_config_value(config_path + ".api_url")
        try:
            # Query /v1/models endpoint
            models = await query_llm_models(api_url)
            return [{"value": m["id"], "label": m["name"]} for m in models]
        except Exception:
            return [{"value": "qwen/qwen3-4b", "label": "Qwen 3 4B (fallback)"}]

    @staticmethod
    async def plugins_list() -> List[dict]:
        """Get list of available plugins"""
        plugins = get_loaded_plugins()
        return [{"value": p.name, "label": f"{p.display_name} ({p.version})"} for p in plugins]

    @staticmethod
    async def log_levels() -> List[dict]:
        """Get available log levels"""
        return [
            {"value": "DEBUG", "label": "Debug (Verbose)"},
            {"value": "INFO", "label": "Info (Normal)"},
            {"value": "WARNING", "label": "Warning (Important only)"},
            {"value": "ERROR", "label": "Error (Critical only)"}
        ]
```

#### Custom Plugin Providers
```python
class MyPlugin(BasePlugin):
    def register_option_providers(self):
        self.register_option_provider("my_custom_options", self.get_custom_options)

    async def get_custom_options(self, context: dict) -> List[dict]:
        """Custom option provider for this plugin"""
        return [
            {"value": "option1", "label": "Custom Option 1"},
            {"value": "option2", "label": "Custom Option 2"}
        ]
```

### Dynamic Widget Configuration

#### Initialization Phase
```python
class AppInitializer:
    async def initialize_dynamic_options(self):
        """Query all option providers during app startup"""
        self.option_cache = {}

        # Query LLM models for each configured endpoint
        for llm_config in get_llm_configs():
            models = await OptionProviders.llm_models(llm_config.path)
            self.option_cache[f"llm_models_{llm_config.name}"] = models

        # Cache other dynamic options
        self.option_cache["plugins"] = await OptionProviders.plugins_list()
        self.option_cache["log_levels"] = await OptionProviders.log_levels()
```

#### Runtime Refresh
```python
class ModalRenderer:
    async def refresh_widget_options(self, widget_config: dict):
        """Refresh options for a specific widget"""
        if "options_provider" in widget_config:
            provider_name = widget_config["options_provider"]

            # Show loading state
            widget.set_loading_state(widget_config.get("loading_text", "Loading..."))

            try:
                # Query provider
                new_options = await self.option_provider.get_options(provider_name)
                widget.update_options(new_options)
            except Exception as e:
                # Fall back to cached or default options
                fallback = widget_config.get("fallback_options", [])
                widget.update_options(fallback)
                widget.show_error_state(f"Failed to load: {e}")
```

### Enhanced JSON Configuration

#### LLM Model Dropdown
```json
{
  "type": "dropdown",
  "label": "Model",
  "key": "model",
  "options_provider": "llm_models",
  "provider_context": {
    "api_url_key": "api_url",
    "provider_key": "provider"
  },
  "fallback_options": [
    {"value": "qwen/qwen3-4b", "label": "Qwen 3 4B"},
    {"value": "local-model", "label": "Local Model"}
  ],
  "refresh_on_focus": true,
  "refresh_on_api_change": true,
  "loading_text": "Discovering models...",
  "error_text": "Failed to load models",
  "cache_duration": 300,
  "validation": "required"
}
```

#### Plugin Selection Dropdown
```json
{
  "type": "dropdown",
  "label": "Select Plugin",
  "key": "active_plugin",
  "options_provider": "available_plugins",
  "refresh_on_focus": false,
  "show_plugin_status": true,
  "group_by": "category",
  "filter_enabled_only": true
}
```

#### Theme Selection (File-based)
```json
{
  "type": "dropdown",
  "label": "Color Theme",
  "key": "theme",
  "options_provider": "theme_files",
  "provider_context": {
    "directory": "./themes",
    "extension": ".json"
  },
  "fallback_options": [
    {"value": "dark", "label": "Dark"},
    {"value": "light", "label": "Light"}
  ]
}
```

### Caching Strategy

#### Cache Levels
1. **Startup Cache**: Populated during app initialization
2. **Session Cache**: Updated during user session (5-10 minutes)
3. **Widget Cache**: Per-widget cache with custom TTL
4. **Fallback Cache**: Persistent cache for offline scenarios

#### Cache Implementation
```python
class OptionCache:
    def __init__(self):
        self.caches = {
            "startup": {},     # App lifetime
            "session": {},     # 10 minutes
            "widget": {},      # 5 minutes
            "fallback": {}     # Persistent
        }

    async def get_options(self, provider: str, context: dict = None) -> List[dict]:
        # Check cache levels in order
        for cache_level in ["widget", "session", "startup", "fallback"]:
            if self.is_cached(provider, cache_level):
                return self.get_cached(provider, cache_level)

        # Fetch fresh data
        options = await self.fetch_fresh_options(provider, context)
        self.cache_options(provider, options, "widget")
        return options
```

### Auto-Refresh Triggers

#### Configuration Changes
- When user changes API URL → refresh model list
- When user enables/disables plugin → refresh plugin lists
- When user changes provider → refresh provider-specific options

#### Focus Events
- When user focuses dropdown → refresh if stale
- When modal opens → refresh all dynamic widgets
- When user manually triggers refresh → force update all

#### Implementation
```python
class DynamicDropdownWidget(BaseWidget):
    async def on_focus(self):
        if self.config.get("refresh_on_focus", False):
            await self.refresh_options()

    async def on_related_config_change(self, changed_key: str):
        refresh_triggers = self.config.get("refresh_on_api_change", [])
        if changed_key in refresh_triggers:
            await self.refresh_options()

    async def refresh_options(self):
        self.show_loading_state()
        try:
            new_options = await self.option_provider.get_options(
                self.config["options_provider"],
                self.get_provider_context()
            )
            self.update_options(new_options)
        except Exception as e:
            self.show_error_state(str(e))
            self.fallback_to_cached_options()
```

## 🔧 Implementation Architecture

### Core Components

#### 1. ModalRenderer (`core/ui/modal_renderer.py`)
```python
class ModalRenderer:
    def __init__(self, terminal_renderer, config_manager):
        self.terminal_renderer = terminal_renderer
        self.config_manager = config_manager

    async def show_modal(self, modal_config: dict) -> dict:
        """Display modal and handle user interaction"""

    async def animate_entrance(self, modal_config: dict):
        """Slide down animation"""

    async def handle_navigation(self, key_press):
        """Arrow key navigation within modal"""

    async def save_changes(self, changes: dict):
        """Merge changes into config and notify plugins"""
```

#### 2. ModalWidgetSystem (`core/ui/widgets/`)
```python
# Base widget class
class BaseWidget:
    def render(self) -> List[str]:
        """Render widget to terminal lines"""

    def handle_input(self, key_press) -> bool:
        """Handle user input, return True if consumed"""

    def get_value(self) -> Any:
        """Get current widget value"""

    def set_value(self, value: Any):
        """Set widget value from config"""

# Specific widgets
class TextInputWidget(BaseWidget): ...
class DropdownWidget(BaseWidget): ...
class CheckboxWidget(BaseWidget): ...
class SliderWidget(BaseWidget): ...
```

#### 3. ConfigMerger (`core/config/merger.py`)
```python
class ConfigMerger:
    @staticmethod
    def merge_deep(base_config: dict, updates: dict) -> dict:
        """Deep merge configuration updates"""

    @staticmethod
    def apply_changes(config_path: str, changes: dict):
        """Apply changes to config.json and notify affected plugins"""

    @staticmethod
    def notify_plugins(affected_sections: List[str]):
        """Notify plugins that their config changed"""
```

### Modal Registration System

#### In Plugin SDK
```python
class BasePlugin:
    def register_modal_ui(self, command_name: str, ui_config: dict):
        """Register modal UI configuration for a command"""
        self.event_bus.emit(EventType.REGISTER_MODAL_UI, {
            "command": command_name,
            "plugin": self.name,
            "ui_config": ui_config
        })
```

#### Usage in Plugins
```python
class EnhancedInputPlugin(BasePlugin):
    def initialize(self):
        # Register modal UI for /input-config command
        self.register_modal_ui("/input-config", {
            "title": "Enhanced Input Settings",
            "sections": [{
                "title": "Appearance",
                "config_path": "plugins.enhanced_input",
                "widgets": [
                    {
                        "type": "dropdown",
                        "label": "Style",
                        "key": "style",
                        "options": ["rounded", "square", "minimal"]
                    },
                    {
                        "type": "checkbox",
                        "label": "Show Placeholder",
                        "key": "show_placeholder"
                    }
                ]
            }]
        })
```

## 🎬 Animation System

### Entrance Animation (slide_down)
```
Frame 1: Modal at -100% Y position (hidden above screen)
Frame 2: Modal at -80% Y position
Frame 3: Modal at -60% Y position
...
Frame N: Modal at final position (centered)
```

### Background Dimming
```
Frame 1: Background at 100% brightness
Frame 2: Background at 80% brightness
Frame 3: Background at 60% brightness
Frame N: Background at 40% brightness (dimmed)
```

## 🎯 Core Command Examples

### /config Command Modal
- **Section 1**: LLM Settings (core.llm)
  - API URL (text_input)
  - Model (dropdown)
  - Temperature (slider)
  - Enable Streaming (checkbox)

- **Section 2**: Terminal Settings (terminal)
  - Render FPS (slider)
  - Thinking Effect (dropdown)
  - Status Lines (slider)

- **Section 3**: Plugin Settings (plugins)
  - Enhanced Input Enabled (checkbox)
  - Hook Monitoring Debug (checkbox)

### /status Command Modal (Read-only)
- **Section 1**: System Status
  - Uptime (display)
  - Memory Usage (progress_bar)
  - CPU Usage (progress_bar)

- **Section 2**: LLM Connection
  - Provider Status (display)
  - API Latency (display)
  - Rate Limit (progress_bar)

### /help Command Modal
- **Section 1**: Available Commands (list)
- **Section 2**: Keyboard Shortcuts (list)
- **Section 3**: Examples (list)

### /version Command Modal (Read-only)
- **Section 1**: Application Info
  - Name (display)
  - Version (display)
  - Build (display)

- **Section 2**: Dependencies (list)
- **Section 3**: System Environment (list)

## 🔗 Status Area Widget Control

Plugins can register status widgets that appear in the bottom status area:

```json
{
  "status_widgets": [
    {
      "id": "llm_status",
      "plugin": "core",
      "priority": 100,
      "enabled": true,
      "config_path": "core.llm.show_status"
    },
    {
      "id": "input_stats",
      "plugin": "enhanced_input",
      "priority": 50,
      "enabled": true,
      "config_path": "plugins.enhanced_input.show_status"
    }
  ]
}
```

Users can toggle these widgets on/off in the `/config` modal under a "Status Area" section.

## 🛠️ Implementation Plan

### Phase 1: Core Infrastructure
1. Create `ModalRenderer` class
2. Implement basic widget system (text_input, checkbox, dropdown)
3. Add animation system (slide_down entrance)
4. Create `ConfigMerger` utilities

### Phase 2: Command Integration
1. Extend `CommandDefinition` to support `ui_config`
2. Modify command executor to detect modal commands
3. Implement `/config` modal for core settings
4. Add keyboard navigation (Tab, Shift+Tab, Arrow keys)

### Phase 3: Plugin SDK
1. Add modal registration to `BasePlugin`
2. Create documentation and examples
3. Implement status widget control system
4. Test with hook monitoring plugin

### Phase 4: Enhanced Widgets
1. Add slider, radio, progress widgets
2. Implement validation system
3. Add help text and tooltips
4. Create advanced layout options (tabs, nested sections)

## 🧪 Testing Strategy

### Hook Monitoring Plugin Integration
Use the existing hook monitoring plugin to test the modal system:

```python
# In hook_monitoring_plugin.py
def register_modal_ui(self):
    self.register_modal_ui("/monitor-config", {
        "title": "Hook Monitoring Settings",
        "sections": [{
            "title": "Debug Options",
            "config_path": "plugins.hook_monitoring",
            "widgets": [
                {
                    "type": "checkbox",
                    "label": "Debug Logging",
                    "key": "debug_logging"
                },
                {
                    "type": "checkbox",
                    "label": "Log All Events",
                    "key": "log_all_events"
                },
                {
                    "type": "slider",
                    "label": "Performance Threshold (ms)",
                    "key": "performance_threshold_ms",
                    "min": 10,
                    "max": 1000,
                    "step": 10
                }
            ]
        }]
    })
```

## 📋 File Structure

```
core/
├── ui/
│   ├── modal_renderer.py
│   ├── animations.py
│   └── widgets/
│       ├── __init__.py
│       ├── base_widget.py
│       ├── text_input.py
│       ├── dropdown.py
│       ├── checkbox.py
│       ├── slider.py
│       └── progress.py
├── config/
│   └── merger.py
└── commands/
    └── modal_integration.py

docs/
├── plugin-sdk/
│   └── modal-ui-guide.md
└── examples/
    └── modal-configurations.json
```

This framework will make it incredibly easy for plugin developers to create rich, interactive configuration interfaces while maintaining a consistent user experience across all commands!