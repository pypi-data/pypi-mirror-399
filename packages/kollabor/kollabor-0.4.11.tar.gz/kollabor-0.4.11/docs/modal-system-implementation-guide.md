# Modal System Implementation Guide

## 🎯 Overview

This document provides the complete implementation guide for adding modal/panel UI system to the Kollabor CLI application. The modal system enables rich, interactive configuration interfaces that overlay the chat interface at 80% screen width with smooth animations.

**Core Principle**: Leverage existing rich infrastructure (visual effects, input handling, terminal rendering) while filling minimal gaps to deliver maximum functionality.

## 📋 Table of Contents

1. [Vision & Design](#vision--design)
2. [Current Infrastructure Analysis](#current-infrastructure-analysis)
3. [Implementation Strategy](#implementation-strategy)
4. [4-Phase Development Plan](#4-phase-development-plan)
5. [Complete Code Examples](#complete-code-examples)
6. [Testing & Validation](#testing--validation)

---

## 🎨 Vision & Design

### Visual Mockups

These mockups show the target appearance for each modal command:

#### /config Modal - System Configuration
```
╭───────────────────────────────────────────────────╮
│  /config - System Configuration                   │
│                                                   │
│  General Settings                                 │
│    Theme                    [Dark ▼]              │
│    Auto-save               [✓] Enabled            │
│    Max history             [90] messages          │
│                                                   │
│  LLM Settings                                     │
│    Provider                [Anthropic ▼]          │
│    Model                   [claude-3-sonnet ▼]    │
│    Temperature             [0.7] ──────●──        │
│    Max tokens              [4096]                 │
│                                                   │
│  Terminal Settings                                │
│    Color scheme            [Terminal ▼]           │
│    Font size               [14px]                 │
│    Animations              [✓] Enabled            │
│                                                   │
│  [Save Changes]  [Reset Defaults]  [Cancel]       │
╰───────────────────────────────────────────────────╯
 Tab to navigate · Enter to select · Esc to exit
```

#### /status Modal - System Diagnostics
```
╭──────────────────────────────────────────────────────────────────╮
│  /status - System Diagnostics                                    │
│                                                                  │
│  Application Status                                              │
│    Status           ●  Running                                   │
│    Uptime           2h 34m 12s                                   │
│    Memory Usage     245.2 MB / 512 MB  ████████░░░░ 48%          │
│    CPU Usage        12.3%              ███░░░░░░░░ 12%           │
│    Active Plugins   3 loaded, 3 running                          │
│                                                                  │
│  LLM Connection                                                  │
│    Provider         ●  Anthropic (Connected)                     │
│    Model            claude-3-sonnet-20240229                     │
│    API Latency      234ms (Last request)                         │
│    Rate Limit       47/50 requests remaining                     │
│    Tokens Used      1,247 / 4,096 this session                   │
│                                                                  │
│  Storage & Logs                                                  │
│    Config File      .kollabor-cli/config.json (Modified: 14:23)      │
│    Log File         .kollabor-cli/logs/kollabor.log (Size: 2.4 MB)   │
│    State Database   .kollabor-cli/state.db (15 conv, 342 messages)   │
│    Cache Size       127 MB (Last cleared: 3 days ago)            │
│                                                                  │
│  [Refresh]  [Export Diagnostics]  [Clear Cache]                  │
╰──────────────────────────────────────────────────────────────────╯
 F5 to refresh · S to save report · Esc to exit
```

#### /help Modal - Available Commands
```
╭─────────────────────────────────────────────────────────────────╮
│  /help - Available Commands                                     │
│                                                                 │
│  Slash Commands                                                 │
│    /config      Configure system settings and preferences       │
│    /help        Show this help menu (aliases: h, ?)             │
│    /status      Display system status and diagnostics           │
│    /version     Show application version information (v, ver)   │
│    /clear       Clear conversation history                      │
│    /reset       Reset application state                         │
│    /export      Export conversation to file                     │
│    /plugins     Manage plugins and extensions                   │
│                                                                 │
│  Keyboard Shortcuts                                             │
│    Ctrl+C       Exit application                                │
│    Ctrl+L       Clear screen                                    │
│    Ctrl+R       Refresh/reload                                  │
│    ↑/↓          Navigate command history                        │
│    Tab          Auto-complete (when available)                  │
│                                                                 │
│  Examples                                                       │
│    /help config    Show detailed help for config command        │
│    /status --full  Show comprehensive system diagnostics        │
│    /export json    Export conversation as JSON file             │
│                                                                 │
╰─────────────────────────────────────────────────────────────────╯
 Type command name for quick jump · Esc to exit
```

#### /version Modal - Application Information
```
╭────────────────────────────────────────────────────────────────────────╮
│  /version - Application Information                                    │
│                                                                        │
│  Application                                                           │
│    Name             Kollabor CLI Interface                        │
│    Version          1.2.4                                              │
│    Build            2024.01.15-a7f3d2c                                 │
│    Release Date     January 15, 2024                                   │
│    License          MIT License                                        │
│                                                                        │
│  Dependencies                                                          │
│    Python           3.12.1                                             │
│    Core Libraries   asyncio 3.12.1, aiohttp 3.9.1, rich 13.7.0         │
│    Plugin System    pluggy 1.4.0                                       │
│    Configuration    pydantic 2.5.3                                     │
│                                                                        │
│  System Environment                                                    │
│    Platform         macOS 14.2.1 (23C71) Darwin                        │
│    Architecture     arm64                                              │
│    Terminal         iTerm2 Build 3.4.23                                │
│    Shell            zsh 5.9                                            │
│                                                                        │
│  Latest Changes                                                        │
│    • Enhanced input plugin architecture with modular design            │
│    • LLM service output formatting consistency improvements            │
│    • Message display and error handling enhancements                   │
│    • Event bus system with specialized components                      │
│    • Removal of deprecated conversation tracking files                 │
│                                                                        │
│  [Check Updates]  [View Changelog]  [Report Bug]                       │
╰────────────────────────────────────────────────────────────────────────╯
 U to check updates · C for changelog · Esc to exit
```

#### Plugin Selection Modal Example
```
╭──────────────────────────────────────────────╮
│                                              │
│  Select IDE                                  │
│  Connect to an IDE for integrated developmen │
│                                              │
│   ❯ 1. Cursor ✔                              │
│     2. None                                  │
│                                              │
│  Found 2 other running IDE(s). However, thei │
│  directories do not match the current cwd.   │
│                                              │
│     • Cursor: /Users/malmazan/dev/terminal   │
│     • Cursor: /Users/malmazan/dev/sprouts    │
│                                              │
╰──────────────────────────────────────────────╯
 Enter to confirm · Esc to exit
```

### Modal Specifications

#### Dimensions & Positioning
- **Width**: 80% of terminal width (configurable)
- **Height**: Auto-sized based on content (~50% max)
- **Position**: Centered horizontally and vertically
- **Background**: Dimmed chat interface (still visible)
- **Animation**: Slide down from top with fade-in effect

#### Navigation Flow
```
/ → Command Menu → ↓ → Navigate → Enter → Modal Opens
Modal: ↑↓ Navigate widgets → Enter activates → Tab next widget → Esc closes
```

### JSON Schema for Modal Configuration

#### Basic Modal Definition
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
            "options_provider": "llm_models",
            "fallback_options": ["qwen/qwen3-4b", "gpt-4"]
          },
          {
            "type": "slider",
            "label": "Temperature",
            "key": "temperature",
            "min": 0.0,
            "max": 2.0,
            "step": 0.1
          },
          {
            "type": "checkbox",
            "label": "Enable Streaming",
            "key": "enable_streaming"
          }
        ]
      }
    ],
    "actions": [
      {"label": "Save Changes", "action": "save", "style": "primary"},
      {"label": "Cancel", "action": "cancel", "style": "secondary"}
    ]
  }
}
```

#### Widget Types

**Text Input**
```json
{
  "type": "text_input",
  "label": "API URL",
  "key": "api_url",
  "placeholder": "Enter URL...",
  "validation": "url|required",
  "help_text": "The base URL for your LLM API"
}
```

**Dropdown (Static Options)**
```json
{
  "type": "dropdown",
  "label": "Provider",
  "key": "provider",
  "options": ["anthropic", "openai", "local"],
  "option_labels": ["Anthropic", "OpenAI", "Local Server"]
}
```

**Dropdown (Dynamic Options)**
```json
{
  "type": "dropdown",
  "label": "Model",
  "key": "model",
  "options_provider": "llm_models",
  "refresh_on_focus": true,
  "loading_text": "Discovering models...",
  "fallback_options": ["qwen/qwen3-4b"]
}
```

**Checkbox**
```json
{
  "type": "checkbox",
  "label": "Enable Streaming",
  "key": "enable_streaming",
  "help_text": "Stream responses in real-time"
}
```

**Slider**
```json
{
  "type": "slider",
  "label": "Temperature",
  "key": "temperature",
  "min": 0.0,
  "max": 2.0,
  "step": 0.1,
  "format": "{:.1f}"
}
```

---

## 🏗️ Current Infrastructure Analysis

### ✅ Rich Infrastructure Available

#### Visual Effects System (`core/io/visual_effects.py`)
```python
# EXISTING - Ready to use for modals
class GradientRenderer:     # Modal borders and headers
class ColorPalette:         # DIM_CYAN, DIM_YELLOW for styling
class EffectConfig:         # Animation configurations
class BannerRenderer:       # Modal headers and titles

# Available colors for modals:
ColorPalette.DIM_CYAN      # Modal borders
ColorPalette.DIM_YELLOW    # Modal footers
ColorPalette.BRIGHT        # Widget labels
ColorPalette.DIM           # Help text
```

#### Terminal Infrastructure (`core/io/terminal_renderer.py`)
```python
# EXISTING - Perfect for modal integration
def clear_active_area():         # Clear area for modal overlay
def render_active_area():        # Extend for modal rendering
def _render_lines():             # Core rendering for modals
def _write():                    # Direct terminal output
```

#### Input Handling (`core/io/input_handler.py`)
```python
# EXISTING - Command mode infrastructure ready
self.command_mode = CommandMode.MENU_POPUP  # Pattern to follow
async def _handle_menu_popup_keypress():    # Template for modal input
async def _enter_command_mode():            # Pattern for modal mode
async def _exit_command_mode():             # Pattern for modal exit
```

#### Command System (`core/commands/`)
```python
# EXISTING - Complete command infrastructure
class CommandDefinition:        # ui_config field ready
class UIConfig:                 # Basic structure exists
class CommandResult:            # status_ui pattern to extend
SlashCommandExecutor:           # Ready for modal integration
```

#### Configuration Management (`core/config/`)
```python
# EXISTING - Ready for widget value persistence
ConfigManager:                  # Load/save config.json
get_config_value():             # Read widget values
set_config_value():             # Save widget changes
```

### ❌ Minimal Gaps to Fill

**Missing Components:**
1. `CommandMode.MODAL` (1 line addition to enum)
2. `core/ui/modal_renderer.py` (new file using existing infrastructure)
3. Modal input handling in existing input_handler.py
4. Widget system (BaseWidget + specific widgets)
5. Config merging utilities

---

## 🚀 Implementation Strategy

### Core Principle: Maximum Reuse
- **Leverage existing visual effects** instead of creating new rendering
- **Extend existing command modes** instead of parallel systems
- **Use existing input patterns** instead of new input handling
- **Build on existing config system** instead of new persistence

### Technical Approach
1. **Add** `CommandMode.MODAL` to existing enum
2. **Create** minimal `ModalRenderer` using existing `ColorPalette` and `GradientRenderer`
3. **Extend** existing input handler with modal keypress methods
4. **Modify** existing command executor to detect modal UI configs
5. **Update** existing system commands to return modal configurations

---

## 📅 4-Phase Development Plan

### Phase 1: Basic Modal Infrastructure (Week 1)
**Goal**: `/config` opens modal instead of status takeover

#### Day 1: Core Modal Structure
```bash
mkdir -p core/ui/widgets
```

**Add CommandMode.MODAL**
```python
# In core/events/models.py - ADD ONE LINE
class CommandMode(Enum):
    NORMAL = "normal"
    INSTANT = "instant"
    MENU_POPUP = "menu_popup"
    STATUS_TAKEOVER = "status_takeover"
    INLINE_INPUT = "inline_input"
    MODAL = "modal"                    # ← ADD THIS
```

**Create Basic ModalRenderer**
```python
# core/ui/modal_renderer.py
class ModalRenderer:
    def __init__(self, terminal_renderer, visual_effects):
        self.terminal_renderer = terminal_renderer
        self.visual_effects = visual_effects
        self.gradient_renderer = GradientRenderer()

    async def show_modal(self, ui_config: UIConfig) -> Dict[str, Any]:
        # Use existing clear_active_area
        self.terminal_renderer.clear_active_area()

        # Render using existing visual effects
        modal_lines = self._render_modal_box(ui_config)
        await self._animate_entrance(modal_lines)

        return await self._handle_modal_input(ui_config)

    def _render_modal_box(self, ui_config: UIConfig) -> List[str]:
        # Use existing ColorPalette for styling
        border_color = ColorPalette.DIM_CYAN
        width = int(ui_config.width or 80)
        title = ui_config.title or "Modal"

        lines = []
        lines.append(f"{border_color}╭{'─' * (width-2)}╮{ColorPalette.RESET}")

        # Title with existing gradient effects
        title_line = f"│{title.center(width-2)}│"
        lines.append(f"{border_color}{title_line}{ColorPalette.RESET}")

        lines.append(f"{border_color}├{'─' * (width-2)}┤{ColorPalette.RESET}")

        # Content area
        content_lines = self._render_modal_content(ui_config.modal_config or {}, width)
        lines.extend(content_lines)

        lines.append(f"{border_color}╰{'─' * (width-2)}╯{ColorPalette.RESET}")

        # Footer with existing colors
        footer = "Enter to select • Esc to close"
        lines.append(f"{ColorPalette.DIM_YELLOW}{footer.center(width)}{ColorPalette.RESET}")

        return lines
```

#### Day 2: Input Integration
**Extend Existing Input Handler**
```python
# In core/io/input_handler.py - ADD to _handle_command_mode_keypress
elif self.command_mode == CommandMode.MODAL:
    return await self._handle_modal_keypress(key_press)

# ADD new method to input_handler.py
async def _handle_modal_keypress(self, key_press: KeyPress) -> bool:
    """Handle modal input using existing patterns."""
    try:
        if key_press.name == "Escape":
            await self._exit_modal_mode()
            return True
        elif key_press.name == "Enter":
            await self._exit_modal_mode()
            return True
        return True
    except Exception as e:
        logger.error(f"Error handling modal keypress: {e}")
        await self._exit_modal_mode()
        return False

async def _enter_modal_mode(self, ui_config: UIConfig):
    """Enter modal mode."""
    self.command_mode = CommandMode.MODAL
    # Integration with existing modal renderer happens here

async def _exit_modal_mode(self):
    """Exit modal mode using existing patterns."""
    self.command_mode = CommandMode.NORMAL
    await self._update_display()
```

#### Day 3: Command Integration
**Modify Command Executor**
```python
# In core/commands/executor.py - ADD to execute_command
if result.ui_config and result.ui_config.type == "modal":
    await self._trigger_modal_mode(result.ui_config)

async def _trigger_modal_mode(self, ui_config: UIConfig):
    """Trigger modal through event bus."""
    await self.event_bus.emit_with_hooks(
        EventType.COMMAND_MODAL_OPEN,
        {"ui_config": ui_config},
        "command_executor"
    )
```

**Update /config Command**
```python
# In core/commands/system_commands.py - REPLACE handle_config
async def handle_config(self, command: SlashCommand) -> CommandResult:
    return CommandResult(
        success=True,
        message="Configuration modal opened",
        ui_config=UIConfig(
            type="modal",
            title="System Configuration",
            width=80,
            modal_config={
                "sections": [{
                    "title": "LLM Settings",
                    "content": "Temperature, Model, API URL (widgets in Phase 2)"
                }]
            }
        ),
        display_type="modal"
    )
```

#### Day 4: Animation & Polish
```python
async def _animate_entrance(self, lines: List[str]):
    """Animate using existing visual effects."""
    # Use existing ColorPalette for fade-in
    for opacity in [0.3, 0.6, 1.0]:
        if opacity < 1.0:
            dimmed_lines = [f"{ColorPalette.DIM}{line}{ColorPalette.RESET}" for line in lines]
            await self._render_modal_lines(dimmed_lines)
        else:
            await self._render_modal_lines(lines)
        await asyncio.sleep(0.1)
```

**Phase 1 Success Criteria:**
- [ ] `/config` opens modal instead of status takeover
- [ ] Modal uses existing visual effects (DIM_CYAN borders, DIM_YELLOW footer)
- [ ] Esc key closes modal and returns to normal input
- [ ] Modal is 80% width and centered
- [ ] Background chat is visible (dimmed)

### Phase 2: Widget System (Week 2)
**Goal**: Interactive widgets in modals

#### Widget Base Architecture
```python
# core/ui/widgets/base_widget.py
class BaseWidget:
    def __init__(self, config: dict, config_path: str):
        self.config = config
        self.config_path = config_path  # "core.llm.temperature"
        self.focused = False

    def render(self) -> List[str]:
        """Render widget using existing ColorPalette."""
        pass

    def handle_input(self, key_press: KeyPress) -> bool:
        """Handle input, return True if consumed."""
        pass

    def get_value(self) -> Any:
        """Get current value from config."""
        from ..config import get_config_value
        return get_config_value(self.config_path)

    def set_value(self, value: Any):
        """Set value (will be saved in Phase 3)."""
        self._pending_value = value
```

#### Specific Widget Implementations
```python
# core/ui/widgets/checkbox.py
class CheckboxWidget(BaseWidget):
    def render(self) -> List[str]:
        check = "✓" if self.get_value() else " "
        label = self.config.get("label", "Option")

        # Use existing ColorPalette
        if self.focused:
            return [f"{ColorPalette.BRIGHT}  [{check}] {label}{ColorPalette.RESET}"]
        else:
            return [f"  [{check}] {label}"]

    def handle_input(self, key_press: KeyPress) -> bool:
        if key_press.name == "Enter" or key_press.char == " ":
            self.set_value(not self.get_value())
            return True
        return False

# core/ui/widgets/dropdown.py
class DropdownWidget(BaseWidget):
    def render(self) -> List[str]:
        current = self.get_value()
        label = self.config.get("label", "Select")

        if self.focused:
            return [f"{ColorPalette.BRIGHT}  {label}: [{current} ▼]{ColorPalette.RESET}"]
        else:
            return [f"  {label}: [{current} ▼]"]

    def handle_input(self, key_press: KeyPress) -> bool:
        if key_press.name == "Enter":
            # Show dropdown options (Phase 2B)
            return True
        return False

# core/ui/widgets/text_input.py
class TextInputWidget(BaseWidget):
    def render(self) -> List[str]:
        value = str(self.get_value() or "")
        label = self.config.get("label", "Input")

        if self.focused:
            # Show cursor using existing effects
            return [f"{ColorPalette.BRIGHT}  {label}: [{value}▌]{ColorPalette.RESET}"]
        else:
            return [f"  {label}: [{value}]"]

# core/ui/widgets/slider.py
class SliderWidget(BaseWidget):
    def render(self) -> List[str]:
        value = float(self.get_value() or 0)
        min_val = self.config.get("min", 0)
        max_val = self.config.get("max", 1)
        label = self.config.get("label", "Value")

        # Create visual slider using existing characters
        progress = (value - min_val) / (max_val - min_val)
        bar_width = 20
        filled = int(progress * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        if self.focused:
            return [f"{ColorPalette.BRIGHT}  {label}: {value:.1f} [{bar}]{ColorPalette.RESET}"]
        else:
            return [f"  {label}: {value:.1f} [{bar}]"]
```

#### Modal Widget Integration
```python
# Extend ModalRenderer to support widgets
class ModalRenderer:
    def _create_widgets(self, modal_config: dict) -> List[BaseWidget]:
        widgets = []
        for section in modal_config.get("sections", []):
            for widget_config in section.get("widgets", []):
                widget = self._create_widget(widget_config)
                widgets.append(widget)
        return widgets

    def _create_widget(self, config: dict) -> BaseWidget:
        widget_type = config["type"]
        config_path = f"{config.get('config_path', '')}.{config['key']}"

        if widget_type == "checkbox":
            return CheckboxWidget(config, config_path)
        elif widget_type == "dropdown":
            return DropdownWidget(config, config_path)
        elif widget_type == "text_input":
            return TextInputWidget(config, config_path)
        elif widget_type == "slider":
            return SliderWidget(config, config_path)
        else:
            raise ValueError(f"Unknown widget type: {widget_type}")
```

**Phase 2 Success Criteria:**
- [ ] Modal contains working checkboxes and dropdowns
- [ ] Arrow keys navigate between widgets (focus highlighting)
- [ ] Enter toggles checkboxes, opens dropdowns
- [ ] Text inputs accept character input
- [ ] Sliders respond to arrow keys
- [ ] All widgets use existing ColorPalette consistently

### Phase 3: Config Persistence (Week 3)
**Goal**: Widget changes save to `.kollabor-cli/config.json`

#### Config Merger System
```python
# core/ui/config_merger.py
class ConfigMerger:
    @staticmethod
    def apply_widget_changes(widget_changes: Dict[str, Any]):
        """Apply widget changes to config.json using existing config system."""
        from ..config import ConfigManager

        config_manager = ConfigManager()

        for path, value in widget_changes.items():
            # Use existing config system
            config_manager.set_config_value(path, value)

        # Save config using existing system
        config_manager.save_config()

        # Notify plugins using existing event bus
        ConfigMerger.notify_plugins_config_changed(widget_changes.keys())

    @staticmethod
    def notify_plugins_config_changed(changed_paths: List[str]):
        """Notify plugins their config changed using existing event system."""
        # Use existing event bus to notify plugins
        pass
```

#### Save/Cancel Actions
```python
# Extend ModalRenderer with action handling
async def _handle_modal_actions(self, action: str) -> bool:
    if action == "save":
        changes = self._collect_widget_changes()
        ConfigMerger.apply_widget_changes(changes)
        await self._show_save_confirmation()
        return True  # Close modal
    elif action == "cancel":
        await self._show_cancel_confirmation()
        return True  # Close modal without saving
    return False

def _collect_widget_changes(self) -> Dict[str, Any]:
    """Collect all widget value changes."""
    changes = {}
    for widget in self.widgets:
        if hasattr(widget, '_pending_value'):
            changes[widget.config_path] = widget._pending_value
    return changes
```

#### Live Config Updates
```python
# Extend widgets to support live config updates
class BaseWidget:
    def apply_change_immediately(self):
        """Apply change immediately for live preview."""
        if hasattr(self, '_pending_value'):
            from ..config import set_config_value
            set_config_value(self.config_path, self._pending_value)

            # Notify affected systems immediately
            self._notify_live_change()
```

**Phase 3 Success Criteria:**
- [ ] Checkbox changes persist to config.json
- [ ] Dropdown changes update config paths correctly
- [ ] Text input changes save with proper validation
- [ ] Slider changes save with correct precision
- [ ] "Save" button persists all changes atomically
- [ ] "Cancel" button discards all changes
- [ ] Plugins receive notification of config changes

### Phase 4: Dynamic Options & Polish (Week 4)
**Goal**: Production-ready modal system

#### Dynamic Option Providers
```python
# core/ui/option_providers.py
class OptionProviders:
    @staticmethod
    async def llm_models(config_path: str) -> List[dict]:
        """Query LLM endpoint for available models."""
        from ..config import get_config_value

        api_url = get_config_value(f"{config_path}.api_url")
        try:
            # Query /v1/models endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{api_url}/v1/models") as response:
                    models_data = await response.json()

            return [
                {"value": model["id"], "label": model.get("name", model["id"])}
                for model in models_data.get("data", [])
            ]
        except Exception as e:
            # Fallback to static options
            return [{"value": "qwen/qwen3-4b", "label": "Qwen 3 4B (fallback)"}]

    @staticmethod
    async def plugins_list() -> List[dict]:
        """Get available plugins."""
        # Use existing plugin system
        return [
            {"value": plugin.name, "label": f"{plugin.display_name} ({plugin.version})"}
            for plugin in get_loaded_plugins()
        ]
```

#### Enhanced Animations
```python
# core/ui/animations.py
class ModalAnimations:
    def __init__(self, visual_effects):
        self.visual_effects = visual_effects

    async def slide_down_entrance(self, lines: List[str]):
        """Smooth slide-down animation using existing visual effects."""
        terminal_height = self.visual_effects.get_terminal_height()

        for frame in range(15):
            # Calculate slide position
            y_offset = -len(lines) + (frame * len(lines) // 15)

            # Apply frame-based dimming using existing ColorPalette
            opacity = min(1.0, frame / 10)

            # Render frame
            await self._render_at_offset(lines, y_offset, opacity)
            await asyncio.sleep(0.03)
```

#### Plugin SDK Integration
```python
# Extend BasePlugin for modal registration
class BasePlugin:
    def register_modal_command(self, name: str, modal_config: dict):
        """Register modal command using existing command system."""
        ui_config = UIConfig(
            type="modal",
            modal_config=modal_config
        )

        # Use existing command registration
        self.register_command(
            name=name,
            handler=lambda cmd: self._create_modal_result(modal_config),
            mode=CommandMode.INSTANT,
            ui_config=ui_config
        )

    def _create_modal_result(self, modal_config: dict) -> CommandResult:
        return CommandResult(
            success=True,
            message=f"Modal {modal_config.get('title', 'Dialog')} opened",
            ui_config=UIConfig(type="modal", modal_config=modal_config)
        )
```

**Phase 4 Success Criteria:**
- [ ] Smooth slide-down entrance animation
- [ ] Model dropdown queries LLM endpoint dynamically
- [ ] Plugin can register custom modal commands
- [ ] Status area widgets can be toggled on/off in modals
- [ ] Modal system handles terminal resize gracefully
- [ ] Error states show helpful messages

---

## 💻 Complete Code Examples

### Example 1: Basic Modal Configuration

```python
# /config command modal
config_modal = {
    "title": "System Configuration",
    "sections": [
        {
            "title": "LLM Settings",
            "config_path": "core.llm",
            "widgets": [
                {
                    "type": "text_input",
                    "label": "API URL",
                    "key": "api_url",
                    "validation": "url"
                },
                {
                    "type": "dropdown",
                    "label": "Model",
                    "key": "model",
                    "options_provider": "llm_models"
                },
                {
                    "type": "slider",
                    "label": "Temperature",
                    "key": "temperature",
                    "min": 0.0,
                    "max": 2.0,
                    "step": 0.1
                }
            ]
        }
    ]
}
```

### Example 2: Plugin Modal Registration

```python
# In hook_monitoring_plugin.py
class HookMonitoringPlugin(BasePlugin):
    def initialize(self):
        self.register_modal_command("monitor-config", {
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
                        "max": 1000
                    }
                ]
            }]
        })
```

### Example 3: Complete Widget Implementation

```python
# Complete checkbox widget
class CheckboxWidget(BaseWidget):
    def __init__(self, config: dict, config_path: str):
        super().__init__(config, config_path)
        self.label = config.get("label", "Option")
        self.help_text = config.get("help_text", "")

    def render(self) -> List[str]:
        # Get current value from config
        current_value = self.get_value()
        check = "✓" if current_value else " "

        # Apply focus styling using existing ColorPalette
        if self.focused:
            line = f"{ColorPalette.BRIGHT}  [{check}] {self.label}{ColorPalette.RESET}"
        else:
            line = f"  [{check}] {self.label}"

        lines = [line]

        # Add help text if available
        if self.help_text and self.focused:
            help_line = f"{ColorPalette.DIM}    {self.help_text}{ColorPalette.RESET}"
            lines.append(help_line)

        return lines

    def handle_input(self, key_press: KeyPress) -> bool:
        if key_press.name == "Enter" or key_press.char == " ":
            new_value = not self.get_value()
            self.set_value(new_value)
            return True
        return False

    def get_display_width(self) -> int:
        return len(f"  [ ] {self.label}")
```

---

## 🧪 Testing & Validation

### Testing Strategy Using Hook Monitoring Plugin

```python
# Test modal system with existing plugin
def test_modal_integration():
    """Test modal system with hook monitoring plugin."""

    # 1. Test modal opening
    result = await execute_slash_command("/monitor-config")
    assert result.ui_config.type == "modal"

    # 2. Test widget rendering
    modal_renderer = ModalRenderer(terminal_renderer, visual_effects)
    widgets = modal_renderer._create_widgets(result.ui_config.modal_config)
    assert len(widgets) == 3  # debug_logging, log_all_events, performance_threshold

    # 3. Test widget interaction
    checkbox_widget = widgets[0]
    assert checkbox_widget.handle_input(KeyPress("Enter")) == True

    # 4. Test config persistence
    changes = {"plugins.hook_monitoring.debug_logging": True}
    ConfigMerger.apply_widget_changes(changes)
    assert get_config_value("plugins.hook_monitoring.debug_logging") == True
```

### Manual Testing Checklist

#### Phase 1 Testing
- [ ] Type `/config` → Modal opens (not status takeover)
- [ ] Modal has proper borders using DIM_CYAN
- [ ] Modal title displays correctly
- [ ] Press Esc → Modal closes, returns to normal input
- [ ] Background chat is visible but dimmed
- [ ] Modal is centered and 80% terminal width

#### Phase 2 Testing
- [ ] Arrow keys navigate between widgets
- [ ] Focused widget has bright highlighting
- [ ] Enter toggles checkboxes
- [ ] Enter opens dropdown options
- [ ] Text input accepts typing
- [ ] Slider responds to left/right arrows
- [ ] Tab moves to next widget
- [ ] Shift+Tab moves to previous widget

#### Phase 3 Testing
- [ ] Change checkbox → Press Save → Value persists in config.json
- [ ] Change dropdown → Press Save → Value updates correctly
- [ ] Change text input → Press Save → Value validates and saves
- [ ] Change slider → Press Save → Value saves with correct precision
- [ ] Press Cancel → All changes discarded
- [ ] Plugin receives config change notification

#### Phase 4 Testing
- [ ] Modal slides down smoothly on open
- [ ] Modal fades out smoothly on close
- [ ] Dynamic dropdown loads models from API
- [ ] Error states display helpful messages
- [ ] Modal handles terminal resize gracefully

### Performance Validation

```python
# Performance benchmarks
async def test_modal_performance():
    """Ensure modal system doesn't impact app performance."""

    # Modal opening should be < 100ms
    start_time = time.time()
    await show_modal(config_modal)
    open_time = time.time() - start_time
    assert open_time < 0.1

    # Widget rendering should be < 50ms
    start_time = time.time()
    widget_lines = widget.render()
    render_time = time.time() - start_time
    assert render_time < 0.05

    # Config saves should be < 200ms
    start_time = time.time()
    ConfigMerger.apply_widget_changes(test_changes)
    save_time = time.time() - start_time
    assert save_time < 0.2
```

---

## 📁 Final File Structure

```
core/
├── commands/              # EXISTING - command system
│   ├── registry.py
│   ├── executor.py        # MODIFY - add modal support
│   ├── parser.py
│   ├── menu_renderer.py
│   └── system_commands.py # MODIFY - use modals
├── ui/                    # NEW - modal system
│   ├── __init__.py
│   ├── modal_renderer.py  # NEW - uses existing visual effects
│   ├── animations.py      # NEW - uses existing ColorPalette
│   ├── config_merger.py   # NEW - uses existing config system
│   ├── option_providers.py # NEW - dynamic option loading
│   └── widgets/
│       ├── __init__.py
│       ├── base_widget.py
│       ├── checkbox.py
│       ├── dropdown.py
│       ├── text_input.py
│       └── slider.py
├── events/
│   └── models.py          # MODIFY - add CommandMode.MODAL
├── io/                    # EXISTING - leverage for modals
│   ├── visual_effects.py  # USE - ColorPalette, GradientRenderer
│   ├── terminal_renderer.py # USE - clear_active_area, _render_lines
│   └── input_handler.py   # MODIFY - add modal input handling
└── config/                # EXISTING - use for persistence
    └── manager.py         # USE - config loading/saving
```

---

## 🎯 Success Metrics

### Overall Success Criteria
- [ ] Modal system integrates seamlessly with existing architecture
- [ ] `/config` command provides rich, interactive configuration interface
- [ ] All widget changes persist correctly to `.kollabor-cli/config.json`
- [ ] Plugin developers can easily create custom modal interfaces
- [ ] System maintains existing performance characteristics
- [ ] User experience is intuitive and responsive

### Implementation Milestones
- **Week 1**: Basic modal overlay working
- **Week 2**: Interactive widgets functional
- **Week 3**: Config persistence working
- **Week 4**: Production-ready with polish

This unified implementation guide provides the complete roadmap for building a production-ready modal system that leverages the existing rich infrastructure while delivering the comprehensive widget system envisioned in the original framework design.