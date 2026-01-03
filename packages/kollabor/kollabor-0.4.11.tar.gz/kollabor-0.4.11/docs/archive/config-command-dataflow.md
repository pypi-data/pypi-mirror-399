# `/config` Command - Complete Data Flow Analysis

## COMMAND OVERVIEW

The `/config` command opens a configuration modal with interactive widgets for modifying system settings. It demonstrates the full modal UI framework with checkbox, slider, dropdown, and text input widgets, plus real-time configuration persistence.

**Command Definition** (`core/commands/system_commands.py:56-74`):
- **Name**: `config`
- **Aliases**: `["settings", "preferences"]`
- **Mode**: `CommandMode.STATUS_TAKEOVER`
- **Icon**: [INFO]
- **Handler**: `SystemCommandsPlugin.handle_config()`

## COMPLETE EXECUTION TRACE

### 1. USER INPUT DETECTION & PARSING

```
User types: "/config"
├─ core/io/input_handler.py:_input_loop():141
│  ├─ select.select() polling detects input:146
│  ├─ os.read() captures "/config" characters:152
│  └─ Character-by-character processing:215
├─ KeyParser.parse_char():271 → KeyPress objects
├─ Command detection on '/':260 → CommandMode.MENU_POPUP
├─ Buffer accumulation: 'c', 'o', 'n', 'f', 'i', 'g'
├─ Enter key triggers command execution:1329
└─ SlashCommandParser.parse_command():1670
   └─ Creates SlashCommand{name: "config", args: [], raw_input: "/config"}
```

### 2. COMMAND REGISTRY LOOKUP & EXECUTION

```
Command Resolution:
├─ core/commands/registry.py:SlashCommandRegistry.get_command("config")
│  └─ Returns CommandDefinition from system_commands.py:56
├─ core/commands/executor.py:CommandExecutor.execute_command():29
│  ├─ EventBus.emit_with_hooks(SLASH_COMMAND_DETECTED):41-49
│  │  └─ Notifies plugins of command detection
│  └─ Calls command handler: SystemCommandsPlugin.handle_config():191
└─ Command mode exit: CommandMode.NORMAL restoration
```

### 3. MODAL CONFIGURATION CREATION

```
SystemCommandsPlugin.handle_config():191
├─ Configuration structure creation:201-248
│  ├─ CommandResult with success=True:201-202
│  ├─ Message: "Configuration modal opened":203
│  └─ UIConfig construction:204-246
│     ├─ type="modal":205
│     ├─ title="System Configuration":206
│     ├─ width=None (dynamic):207
│     └─ modal_config sections:208-245
│        └─ LLM Settings section:210-244
│           ├─ Checkbox widget:212-217
│           │  ├─ key="enabled", label="Enable LLM Processing"
│           │  └─ config_path="core.llm.enabled"
│           ├─ Slider widget:218-227
│           │  ├─ key="temperature", label="Temperature"
│           │  ├─ config_path="core.llm.temperature"
│           │  ├─ min=0.0, max=2.0, step=0.1
│           │  └─ decimal_places=1
│           ├─ Dropdown widget:228-234
│           │  ├─ key="model", label="Model"
│           │  ├─ config_path="core.llm.model"
│           │  └─ options=["qwen3-0.6b", "qwen/qwen3-4b", "qwen/qwen3-8b"]
│           └─ Text input widget:235-243
│              ├─ key="max_tokens", label="Max Tokens"
│              ├─ config_path="core.llm.max_tokens"
│              ├─ placeholder="4096"
│              └─ validation="integer"
├─ display_type="modal":247
└─ Return CommandResult with ui_config
```

### 4. MODAL TRIGGER EVENT & STATE TRANSITION

```
Command executor processes result:
├─ core/commands/executor.py:execute_command():112
│  └─ result.ui_config.type == "modal" detected
├─ core/commands/executor.py:_trigger_modal_mode():113
│  └─ EventBus.emit(MODAL_TRIGGER):214 with ui_config
├─ core/io/input_handler.py:_handle_modal_trigger():1105 ← SAME AS MATRIX
│  ├─ Standard modal detection (NO fullscreen_plugin flag):1137-1145
│  │  ├─ ui_config validation:1138
│  │  ├─ Modal logging: "Modal trigger received: System Configuration":1140
│  │  └─ _enter_modal_mode(ui_config) call:1141 ← Different from Matrix
│  └─ Returns: {"modal_activated": True}
└─ Modal mode activation initiated (ModalRenderer, NOT FullScreenRenderer)
```

### 5. MODAL MODE INITIALIZATION

```
InputHandler._enter_modal_mode():1468
├─ ModalRenderer import and creation:1475-1483
│  ├─ from ..ui.modal_renderer import ModalRenderer:1476
│  ├─ ModalRenderer instantiation:1479-1483
│  │  ├─ terminal_renderer=self.renderer
│  │  ├─ visual_effects=getattr(self.renderer, 'visual_effects', None)
│  │  └─ config_service=self.config
│  └─ Modal renderer initialization:
│     ├─ core/ui/modal_renderer.py:__init__():23
│     ├─ ModalOverlayRenderer creation:38
│     ├─ ModalStateManager creation:39
│     └─ ModalActionHandler creation:50
├─ Input area clearing:1485-1487
│  ├─ self.renderer.writing_messages = True:1486
│  └─ self.renderer.clear_active_area():1487
├─ Modal mode activation:1489-1491
│  ├─ self.command_mode = CommandMode.MODAL:1490
│  └─ Logging: "Command mode set to: MODAL":1491
├─ Modal display initiation:1494-1495
│  └─ await self.modal_renderer.show_modal(ui_config):1495
└─ Writing flag reset:1498
```

### 6. MODAL RENDERING & WIDGET CREATION

```
  
├─ Modal content generation:66
│  └─ modal_lines = self._render_modal_box(ui_config)
│     ├─ Widget creation from config:
│     │  ├─ CheckboxWidget("enabled", "Enable LLM Processing")
│     │  ├─ SliderWidget("temperature", "Temperature", 0.0-2.0)
│     │  ├─ DropdownWidget("model", "Model", options)
│     │  └─ TextInputWidget("max_tokens", "Max Tokens")
│     ├─ Config value loading:
│     │  ├─ config.get("core.llm.enabled") → checkbox state
│     │  ├─ config.get("core.llm.temperature") → slider value
│     │  ├─ config.get("core.llm.model") → dropdown selection
│     │  └─ config.get("core.llm.max_tokens") → text input value
│     ├─ Visual rendering:
│     │  ├─ Modal border creation with title
│     │  ├─ Widget layout calculation
│     │  ├─ Color styling application
│     │  └─ Focus indicator setup (first widget focused)
│     └─ Return: List[str] of rendered lines
├─ Modal display:69
│  └─ await self._render_modal_lines(modal_lines)
│     ├─ ModalStateManager.prepare_modal_display():
│     │  ├─ Terminal state capture
│     │  ├─ Alternate buffer activation (if available)
│     │  └─ Modal display area setup
│     └─ ModalOverlayRenderer.render_modal_content():
│        ├─ Line-by-line rendering to screen
│        ├─ Cursor positioning
│        └─ Display flush
└─ Modal input handling:71
   └─ await self._handle_modal_input(ui_config)
```

### 7. MODAL INPUT PROCESSING LOOP

```
ModalRenderer._handle_modal_input():
├─ Input capture loop (modal takes control):
│  ├─ Widget focus management:
│  │  ├─ Tab/Shift+Tab navigation between widgets
│  │  ├─ Arrow key navigation
│  │  └─ Focus indicator updates
│  ├─ Widget-specific interactions:
│  │  ├─ CheckboxWidget: Space/Enter toggle:
│  │  │  ├─ State change: checked ↔ unchecked
│  │  │  ├─ Config update: config.set("core.llm.enabled", new_value)
│  │  │  └─ Visual refresh
│  │  ├─ SliderWidget: Left/Right arrows:
│  │  │  ├─ Value adjustment by step (0.1)
│  │  │  ├─ Range validation (0.0-2.0)
│  │  │  ├─ Config update: config.set("core.llm.temperature", new_value)
│  │  │  └─ Visual refresh with new position
│  │  ├─ DropdownWidget: Enter to open, arrows to select:
│  │  │  ├─ Option list display
│  │  │  ├─ Selection highlighting
│  │  │  ├─ Config update: config.set("core.llm.model", selected_option)
│  │  │  └─ Dropdown close and refresh
│  │  └─ TextInputWidget: Character input:
│     │     ├─ Character accumulation
│     │     ├─ Integer validation (for max_tokens)
│     │     ├─ Config update: config.set("core.llm.max_tokens", int(value))
│     │     └─ Visual refresh with new text
│  ├─ Real-time config persistence:
│  │  ├─ ConfigService.set() calls for each change
│  │  ├─ Configuration file updates (.kollabor/config.json)
│  │  └─ In-memory config updates for immediate effect
│  └─ Modal navigation:
│     ├─ Enter: Save and exit modal
│     ├─ Escape: Cancel and exit modal
│     └─ Tab/Shift+Tab: Widget navigation
└─ Modal result return
```

### 8. INPUT ROUTING IN MODAL MODE

```
During modal display, input flows through:
├─ InputHandler._process_character():250
│  └─ Command mode routing:286 → CommandMode.MODAL detected
├─ InputHandler._handle_command_mode_keypress():1221
│  └─ Modal mode dispatch:1235 → CommandMode.MODAL
├─ InputHandler._handle_modal_keypress():1396
│  ├─ Modal renderer validation:1429-1433
│  ├─ Widget navigation handling:1438-1443
│  │  ├─ self.modal_renderer._handle_widget_navigation(key_press)
│  │  └─ Tab/Arrow key processing for focus changes
│  ├─ Widget input handling:1445-1450
│  │  ├─ self.modal_renderer._handle_widget_input(key_press)
│  │  └─ Widget-specific key processing
│  ├─ Modal refresh:1449-1450
│  │  └─ await self._refresh_modal_display()
│  ├─ Exit handling:1452-1455
│  │  └─ Escape key → await self._exit_modal_mode()
│  └─ Save handling:1456-1460
│     └─ Enter key → await self._save_and_exit_modal()
└─ All other input blocked (modal isolation)
```

### 9. CONFIGURATION PERSISTENCE

```
Real-time config updates during modal interaction:
├─ Widget value changes trigger:
│  ├─ ModalActionHandler.handle_widget_change()
│  ├─ ConfigService.set(config_path, new_value)
│  │  ├─ Dot notation parsing: "core.llm.enabled" → ["core", "llm", "enabled"]
│  │  ├─ Nested dict update in memory
│  │  └─ JSON file write to .kollabor/config.json
│  ├─ Validation and type conversion:
│  │  ├─ Integer validation for max_tokens
│  │  ├─ Float validation for temperature
│  │  ├─ Boolean conversion for enabled
│  │  └─ String validation for model
│  └─ Immediate effect application:
│     ├─ LLM service parameter updates
│     ├─ Runtime behavior changes
│     └─ Plugin configuration propagation
└─ File system persistence:
   ├─ .kollabor/config.json atomic writes
   ├─ Backup creation for safety
   └─ Error handling for write failures
```

### 10. MODAL EXIT & STATE RESTORATION

```
Modal exit triggered by Enter or Escape:
├─ Save and exit (Enter key):1456-1460
│  ├─ ModalActionHandler.handle_action("save", widgets):1542
│  ├─ Final configuration validation and save
│  └─ await self._exit_modal_mode():1548
├─ Cancel exit (Escape key):1452-1455
│  └─ await self._exit_modal_mode():1454
└─ Modal cleanup process:1553-1591
   ├─ Terminal state restoration:1557-1565
   │  ├─ self.renderer.clear_active_area():1559
   │  ├─ Message buffer clearing:1562-1564
   │  └─ Modal artifact removal
   ├─ Modal renderer cleanup:1566-1575
   │  ├─ self.modal_renderer.close_modal():1569 ← STATE RESTORATION
   │  │  ├─ ModalStateManager.restore_terminal_state()
   │  │  ├─ Alternate buffer exit (if used)
   │  │  └─ Cursor and display restoration
   │  ├─ Widget cleanup: self.modal_renderer.widgets = []:1572
   │  ├─ Focus reset: self.modal_renderer.focused_widget_index = 0:1573
   │  └─ Renderer nullification: self.modal_renderer = None:1574
   ├─ Command mode restoration:1577
   │  └─ self.command_mode = CommandMode.NORMAL
   ├─ Display restoration:1579-1581
   │  ├─ self.renderer.clear_active_area():1580
   │  └─ await self._update_display(force_render=True):1581
   └─ Normal input processing resumption
```

## STATE VARIABLES AFFECTED

### InputHandler State Changes
- `self.command_mode`: NORMAL → MENU_POPUP → MODAL → NORMAL
- `self.modal_renderer`: None → ModalRenderer instance → None
- `self.current_status_modal_config`: None → UIConfig → None

### ModalRenderer State Changes
- `self.widgets`: [] → [CheckboxWidget, SliderWidget, DropdownWidget, TextInputWidget] → []
- `self.focused_widget_index`: 0 → variable (0-3) → 0
- `self.current_ui_config`: None → UIConfig → None

### Configuration State Changes
- `core.llm.enabled`: current → user modified
- `core.llm.temperature`: current → user modified (0.0-2.0)
- `core.llm.model`: current → user selected option
- `core.llm.max_tokens`: current → user input (validated integer)

### Terminal State Changes
- **Display**: Normal → Modal overlay → Normal
- **Input Focus**: Input buffer → Modal widgets → Input buffer
- **Cursor**: Input area → Widget focus indicators → Input area
- **Buffer**: Main buffer (no alternate buffer for modals)

## WIDGET INTERACTION DETAILS

### CheckboxWidget Behavior
```
State: unchecked ↔ checked
Triggers: Space, Enter
Visual: [ ] ↔ [✓]
Config: boolean true/false
```

### SliderWidget Behavior
```
State: value (0.0-2.0), step 0.1
Triggers: Left/Right arrows
Visual: [██████░░░░] value
Config: float with decimal precision
```

### DropdownWidget Behavior
```
State: closed/open, selected index
Triggers: Enter (open), Up/Down (navigate), Enter (select)
Visual: [Model ▼] → expanded options list
Config: string selection from options
```

### TextInputWidget Behavior
```
State: text content, cursor position
Triggers: Printable chars, Backspace, Delete
Visual: [text content|] with cursor
Config: validated input (integer for max_tokens)
```

## PERFORMANCE CHARACTERISTICS

- **Modal Rendering**: Immediate display without animation delay
- **Input Responsiveness**: Direct widget updates, no buffering
- **Config Persistence**: Real-time file writes on each change
- **Memory Usage**: Widget instances + modal state (minimal)
- **Display Updates**: Incremental widget refreshes only

## DEBUGGING MARKERS

### Modal Activation Logs
```
"Modal trigger received: System Configuration"
"Command mode set to: MODAL"
"Entered modal mode with persistent input loop"
```

### Widget Interaction Logs
```
"Widget navigation handled: true/false"
"Widget input handled: true/false"
"Configuration updated: core.llm.temperature = 1.2"
```

### Modal Exit Logs
```
"Processing Escape key for modal exit"
"Command mode reset to NORMAL after modal hide"
"Display updated after status modal exit"
```

## IMPORTANT CORRECTION: HOOK SYSTEM ANALYSIS

**CRITICAL FINDING: Config and Matrix use the IDENTICAL hook system!**

The original analysis incorrectly suggested that Config bypassed hooks while Matrix used them. In reality, both commands trigger the same `MODAL_TRIGGER` event through the same `EventBus.emit()` call and use the same `InputHandler._handle_modal_trigger()` handler.

### The Real Difference: Event Data Content

**Config trigger path:**
```
1. SystemCommandsPlugin.handle_config() returns CommandResult with ui_config
2. CommandExecutor._trigger_modal_mode():113
3. EventBus.emit(MODAL_TRIGGER) with:
   {
     "ui_config": UIConfig(...),    ← Triggers ModalRenderer
     "action": "show_modal"
   }
4. InputHandler._handle_modal_trigger():1105 (SAME as Matrix)
5. ui_config branch → _enter_modal_mode() → ModalRenderer
```

**Matrix trigger path:**
```
1. SystemCommandsPlugin.handle_matrix() → FullScreenManager.launch_plugin()
2. EventBus.emit(MODAL_TRIGGER) with:
   {
     "fullscreen_plugin": True,     ← Triggers alternate buffer
     "plugin_name": "matrix_rain"
   }
3. InputHandler._handle_modal_trigger():1105 (SAME handler)
4. fullscreen_plugin branch → _fullscreen_session_active = True
```

### Same Handler, Different Execution Paths

```python
# InputHandler._handle_modal_trigger():1105
async def _handle_modal_trigger(self, event_data):
    if event_data.get('fullscreen_plugin'):
        # Matrix path - alternate buffer system
        self._fullscreen_session_active = True
        self.command_mode = CommandMode.MODAL

    else:
        # Config path - overlay modal system
        ui_config = event_data.get('ui_config')
        await self._enter_modal_mode(ui_config)
```

**The hook infrastructure is identical - only the event data differs!**

This explains why Config has clean overlay behavior while Matrix switches to alternate buffer: it's the `fullscreen_plugin` flag in the event data that determines which rendering system gets activated.

## ERROR HANDLING

### Initialization Failures
- ModalRenderer creation failure → CommandMode.NORMAL:1504
- Widget creation errors → Error display and exit
- Config service unavailable → Read-only mode

### Runtime Failures
- Widget validation errors → Visual feedback, no save
- Config persistence errors → User notification
- Display refresh failures → Graceful degradation

### Recovery Mechanisms
- Automatic modal exit on critical errors
- Terminal state emergency restoration
- Configuration rollback on validation failures
- CommandMode.NORMAL fallback guarantee