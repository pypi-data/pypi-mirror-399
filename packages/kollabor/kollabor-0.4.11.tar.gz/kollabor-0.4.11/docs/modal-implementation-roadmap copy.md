# Modal UI Implementation Roadmap

## 🎯 Current State Analysis

### ✅ What We Have (Solid Foundation)
```
core/commands/
├── registry.py         # SlashCommandRegistry - command management
├── executor.py         # SlashCommandExecutor - command execution
├── parser.py           # SlashCommandParser - /command parsing
├── menu_renderer.py    # CommandMenuRenderer - basic overlay system
└── system_commands.py  # SystemCommands - /config, /status handlers

core/events/models.py   # UIConfig, CommandDefinition, CommandMode enums
core/io/input_handler.py # Command mode handling (MENU_POPUP, STATUS_TAKEOVER)
```

### 🔄 Current Command Flow
```
User types "/" → MENU_POPUP mode → Arrow navigation → Enter
    ↓
CommandExecutor.execute_command() → SystemCommands.handle_config()
    ↓
Returns CommandResult(status_ui=SystemConfigUI) → STATUS_TAKEOVER mode
    ↓
Status area gets replaced with config interface
```

### ❌ What's Missing (To Build)
```
core/ui/                # New directory - modal system
├── modal_renderer.py   # Modal overlay system (80% width)
├── animations.py       # Slide-down entrance effects
├── widgets/           # Widget library
│   ├── base_widget.py
│   ├── text_input.py
│   ├── dropdown.py
│   ├── checkbox.py
│   └── slider.py
└── config_merger.py   # Deep config merging utilities
```

## 🚀 Implementation Strategy

### Phase 1: Bridge Current → Modal (Week 1)
**Goal**: Make `/config` open a modal instead of status takeover

#### Step 1.1: Create Core UI Structure
```bash
mkdir -p core/ui/widgets
```

#### Step 1.2: Extend UIConfig Model
```python
# In core/events/models.py - extend existing UIConfig
@dataclass
class UIConfig:
    type: str  # "list", "tree", "form", "table", "menu", "modal" ← ADD THIS
    navigation: List[str] = field(default_factory=lambda: ["↑↓", "Enter", "Esc"])
    height: int = 10
    width: Optional[int] = None  # For modals: 80 = 80% of screen
    scrollable: bool = True
    title: str = ""
    footer: str = ""

    # NEW MODAL FIELDS
    modal_config: Optional[Dict] = None  # JSON widget configuration
    background_dim: bool = True
    animation: str = "slide_down"
    center_position: bool = True
```

#### Step 1.3: Create Basic ModalRenderer
```python
# core/ui/modal_renderer.py
class ModalRenderer:
    def __init__(self, terminal_renderer):
        self.terminal_renderer = terminal_renderer

    async def show_modal(self, ui_config: UIConfig) -> bool:
        """Show modal with basic animation"""
        # Phase 1: Simple box with title, no widgets yet
        modal_lines = self._render_basic_modal(ui_config)
        await self._animate_entrance(modal_lines)
        return await self._handle_modal_input()

    def _render_basic_modal(self, ui_config: UIConfig) -> List[str]:
        """Render basic modal box (no widgets yet)"""
        width = ui_config.width or 80
        lines = []
        lines.append("╭" + "─" * (width-2) + "╮")
        lines.append("│" + ui_config.title.center(width-2) + "│")
        lines.append("├" + "─" * (width-2) + "┤")
        lines.append("│" + " " * (width-2) + "│")
        lines.append("│  [Press Esc to close]".ljust(width-2) + "│")
        lines.append("╰" + "─" * (width-2) + "╯")
        return lines
```

#### Step 1.4: Modify Command Execution Flow
```python
# In core/commands/executor.py - extend existing execute_command
async def execute_command(self, command: SlashCommand, event_bus) -> CommandResult:
    result = await handler(command)

    # EXISTING: Handle status_ui for STATUS_TAKEOVER
    if result.status_ui:
        # Current behavior - status area takeover

    # NEW: Handle modal UI
    if result.ui_config and result.ui_config.type == "modal":
        modal_renderer = ModalRenderer(self.terminal_renderer)
        await modal_renderer.show_modal(result.ui_config)
```

#### Step 1.5: Update /config Command
```python
# In core/commands/system_commands.py - modify handle_config
async def handle_config(self, command: SlashCommand) -> CommandResult:
    return CommandResult(
        success=True,
        message="Configuration modal opened",
        ui_config=UIConfig(
            type="modal",
            title="System Configuration",
            width=80,
            height=20,
            modal_config={
                "sections": [
                    {"title": "Coming Soon", "content": "Widget system in Phase 2"}
                ]
            }
        )
    )
```

**Phase 1 Result**: `/config` opens a modal box instead of status takeover!

### Phase 2: Widget System (Week 2)
**Goal**: Add interactive widgets to modals

#### Step 2.1: Create Widget Base Classes
```python
# core/ui/widgets/base_widget.py
class BaseWidget:
    def __init__(self, config: dict, value_path: str):
        self.config = config
        self.value_path = value_path  # "core.llm.temperature"

    def render(self) -> List[str]:
        """Render widget to terminal lines"""

    def handle_input(self, key_press: KeyPress) -> bool:
        """Handle user input, return True if consumed"""

    def get_value(self) -> Any:
        """Get current widget value"""

    def set_value(self, value: Any):
        """Set widget value"""
```

#### Step 2.2: Implement Key Widgets
```python
# core/ui/widgets/checkbox.py
class CheckboxWidget(BaseWidget):
    def render(self) -> List[str]:
        check = "✓" if self.get_value() else " "
        label = self.config.get("label", "Option")
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
        options = self.config.get("options", [])
        label = self.config.get("label", "Select")
        return [f"  {label}: [{current} ▼]"]
```

#### Step 2.3: Integrate Widgets into ModalRenderer
```python
# Extend ModalRenderer to support widgets
def _create_widgets(self, modal_config: dict) -> List[BaseWidget]:
    widgets = []
    for section in modal_config.get("sections", []):
        for widget_config in section.get("widgets", []):
            widget = self._create_widget(widget_config)
            widgets.append(widget)
    return widgets

def _create_widget(self, config: dict) -> BaseWidget:
    widget_type = config["type"]
    if widget_type == "checkbox":
        return CheckboxWidget(config, config["key"])
    elif widget_type == "dropdown":
        return DropdownWidget(config, config["key"])
    # etc...
```

**Phase 2 Result**: Modals contain interactive widgets that actually work!

### Phase 3: Config Integration (Week 3)
**Goal**: Widget changes automatically update `.kollabor-cli/config.json`

#### Step 3.1: Create ConfigMerger
```python
# core/ui/config_merger.py
class ConfigMerger:
    @staticmethod
    def apply_widget_changes(widget_changes: Dict[str, Any]):
        """Apply widget changes to config.json"""
        config = load_config()

        for path, value in widget_changes.items():
            set_nested_value(config, path, value)  # "core.llm.temperature" → 0.8

        save_config(config)
        notify_plugins_config_changed(widget_changes.keys())
```

#### Step 3.2: Add Save/Cancel Actions
```python
# Extend ModalRenderer with action handling
async def _handle_modal_actions(self, action: str) -> bool:
    if action == "save":
        changes = self._collect_widget_changes()
        ConfigMerger.apply_widget_changes(changes)
        return True  # Close modal
    elif action == "cancel":
        return True  # Close modal without saving
    return False
```

**Phase 3 Result**: Modal changes actually persist to config and affect the app!

### Phase 4: Polish & Enhancement (Week 4)
**Goal**: Animations, dynamic options, plugin integration

#### Step 4.1: Add Slide-Down Animation
```python
# core/ui/animations.py
class ModalAnimations:
    async def slide_down_entrance(self, lines: List[str]):
        """Animate modal sliding down from top"""
        for frame in range(10):
            y_offset = -len(lines) + (frame * len(lines) // 10)
            self._render_at_offset(lines, y_offset)
            await asyncio.sleep(0.05)
```

#### Step 4.2: Add Dynamic Options (from framework design)
```python
# Implement option providers for dropdowns
class OptionProviders:
    @staticmethod
    async def llm_models(api_url: str) -> List[dict]:
        # Query /v1/models endpoint
        # Return [{"value": "model-id", "label": "Model Name"}]
```

#### Step 4.3: Plugin SDK Integration
```python
# Extend BasePlugin to support modal registration
class BasePlugin:
    def register_modal_command(self, name: str, modal_config: dict):
        """Register a command that opens a modal"""
        self.register_command(
            name=name,
            handler=lambda cmd: self._open_modal(modal_config),
            mode=CommandMode.INSTANT,
            ui_config=UIConfig(type="modal", modal_config=modal_config)
        )
```

## 🔧 Migration Strategy

### Backward Compatibility
- Keep existing STATUS_TAKEOVER mode working
- Add new `type="modal"` to UIConfig without breaking existing commands
- Gradually migrate commands from status takeover to modals

### Progressive Enhancement
1. **Week 1**: Basic modal overlay (replaces status takeover)
2. **Week 2**: Interactive widgets (checkboxes, dropdowns)
3. **Week 3**: Config persistence (changes actually save)
4. **Week 4**: Animations + polish (slide effects, dynamic options)

### Testing with Hook Monitoring Plugin
```python
# Test the system by adding modal config to hook monitoring
def register_modal_ui(self):
    modal_config = {
        "sections": [{
            "title": "Debug Settings",
            "widgets": [
                {"type": "checkbox", "label": "Debug Logging", "key": "plugins.hook_monitoring.debug_logging"},
                {"type": "checkbox", "label": "Log All Events", "key": "plugins.hook_monitoring.log_all_events"}
            ]
        }]
    }
    self.register_modal_command("monitor-config", modal_config)
```

## 📁 File Structure (After Implementation)

```
core/
├── commands/           # EXISTING - command system
│   ├── registry.py
│   ├── executor.py     # ← MODIFY: Add modal support
│   ├── parser.py
│   ├── menu_renderer.py
│   └── system_commands.py  # ← MODIFY: Use modals
├── ui/                # NEW - modal system
│   ├── modal_renderer.py
│   ├── animations.py
│   ├── config_merger.py
│   └── widgets/
│       ├── base_widget.py
│       ├── checkbox.py
│       ├── dropdown.py
│       ├── text_input.py
│       └── slider.py
├── events/
│   └── models.py      # ← MODIFY: Extend UIConfig
└── io/
    └── input_handler.py   # ← MODIFY: Add modal input handling
```

## 🎯 Success Metrics

### Phase 1 Complete When:
- [ ] `/config` opens a modal box instead of status takeover
- [ ] Modal has slide-down animation
- [ ] Modal responds to Esc key to close
- [ ] Background is dimmed and chat visible

### Phase 2 Complete When:
- [ ] Modal contains working checkboxes and dropdowns
- [ ] Arrow keys navigate between widgets
- [ ] Enter toggles checkboxes, opens dropdowns
- [ ] Widget values display correctly

### Phase 3 Complete When:
- [ ] Checkbox changes persist to `.kollabor-cli/config.json`
- [ ] Dropdown changes update config paths
- [ ] "Save" button actually saves changes
- [ ] "Cancel" button discards changes
- [ ] Plugins get notified of config changes

### Phase 4 Complete When:
- [ ] Smooth slide-down entrance animation
- [ ] Model dropdown queries LLM endpoint dynamically
- [ ] Plugin can register custom modal commands
- [ ] Status area widgets can be toggled on/off

This roadmap builds incrementally on your existing solid foundation rather than requiring a complete rewrite!