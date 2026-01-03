# `/matrix` Command - Complete Data Flow Analysis

## COMMAND OVERVIEW

The `/matrix` command launches a full-screen Matrix rain effect using the full-screen plugin framework. It demonstrates complete terminal takeover with animation rendering, input isolation, and proper state restoration.

**Command Definition** (`core/commands/system_commands.py:96-113`):
- **Name**: `matrix`
- **Aliases**: `["rain", "code"]`
- **Mode**: `CommandMode.INSTANT`
- **Icon**: 🔋
- **Handler**: `SystemCommandsPlugin.handle_matrix()`

## COMPLETE EXECUTION TRACE

### 1. USER INPUT DETECTION & PARSING

```
User types: "/matrix"
├─ core/io/input_handler.py:_input_loop():141
│  ├─ select.select() polling detects input:146
│  ├─ os.read() captures "/matrix" characters:152
│  └─ Character-by-character processing:215
├─ KeyParser.parse_char():271 → KeyPress objects
├─ Command detection on '/':260 → CommandMode.MENU_POPUP
├─ Buffer accumulation: 'm', 'a', 't', 'r', 'i', 'x'
├─ Enter key triggers command execution:1329
└─ SlashCommandParser.parse_command():1670
   └─ Creates SlashCommand{name: "matrix", args: [], raw_input: "/matrix"}
```

### 2. COMMAND REGISTRY LOOKUP & EXECUTION

```
Command Resolution:
├─ core/commands/registry.py:SlashCommandRegistry.get_command("matrix")
│  └─ Returns CommandDefinition from system_commands.py:96
├─ core/commands/executor.py:CommandExecutor.execute_command():29
│  ├─ EventBus.emit_with_hooks(SLASH_COMMAND_DETECTED):41-49
│  │  └─ Notifies plugins of command detection
│  └─ Calls command handler: SystemCommandsPlugin.handle_matrix():319
└─ Command mode exit: CommandMode.NORMAL restoration
```

### 3. FULLSCREEN FRAMEWORK INITIALIZATION

```
SystemCommandsPlugin.handle_matrix():319
├─ Dynamic imports:330-331
│  ├─ from ..fullscreen import FullScreenManager:330
│  └─ from plugins.fullscreen.matrix_plugin import MatrixRainPlugin:331
├─ Manager lifecycle:334-341
│  ├─ FullScreenManager creation/reuse:334-335
│  ├─ MatrixRainPlugin() instantiation:339
│  ├─ manager.register_plugin(matrix_plugin):340
│  └─ Framework logging: "Registered Matrix plugin":341
└─ Plugin launch: manager.launch_plugin("matrix_rain"):344
```

### 4. MODAL STATE TRANSITION & RENDERING TAKEOVER

```
FullScreenManager.launch_plugin():
├─ EventBus.emit(MODAL_TRIGGER) with fullscreen_plugin flag
├─ core/io/input_handler.py:_handle_modal_trigger():1105
│  ├─ Fullscreen plugin detection:1125-1135
│  │  ├─ CommandMode.MODAL activation:1130
│  │  ├─ _fullscreen_session_active = True:1132
│  │  └─ Input routing to modal mode:1134
│  └─ Returns: {"modal_activated": True, "fullscreen_plugin": True}
├─ Rendering control transfer:
│  ├─ EventBus.emit(PAUSE_RENDERING)
│  └─ input_handler._handle_pause_rendering():995
│     └─ self.rendering_paused = True:998 ← INPUT RENDERING STOPPED
└─ Terminal preparation for full takeover
```

### 5. MATRIX PLUGIN INITIALIZATION

```
MatrixRainPlugin.initialize():37
├─ Super initialization: FullScreenPlugin.initialize():46
├─ Terminal size acquisition:51
│  └─ renderer.get_terminal_size() → (width, height)
├─ MatrixRenderer creation:54
│  └─ core/fullscreen/components/matrix_components.py:MatrixRenderer():111
│     ├─ Terminal dimensions storage:118-119
│     ├─ Empty columns list initialization:120
│     └─ _create_columns() call:124
│        ├─ Loop through terminal width:129
│        ├─ 50% probability for active columns:130
│        └─ MatrixColumn creation:131-134
│           ├─ Random speed assignment:22 (1.5-4.0)
│           ├─ Random length assignment:24 (5-25)
│           ├─ Character set initialization:27-35 (katakana/symbols)
│           └─ Staggered start times:133
└─ Initialization success: True:56
```

### 6. PLUGIN LIFECYCLE ACTIVATION

```
MatrixRainPlugin.on_start():62
├─ Super call: FullScreenPlugin.on_start():64
├─ Animation timing setup:65
│  └─ self.start_time = asyncio.get_event_loop().time()
├─ Framework identification logs:68-69
│  ├─ Logger: "🎯 NEW FRAMEWORK: MatrixRainPlugin.on_start() called"
│  └─ Print: "🎯 NEW FRAMEWORK: Matrix plugin starting via full-screen framework!"
├─ Matrix state reset:72-73
│  └─ self.matrix_renderer.reset() → Fresh column generation
└─ Ready for render loop
```

### 7. TERMINAL STATE CHANGES & DISPLAY CONTROL

```
FullScreenRenderer Terminal Control:
├─ Alternate buffer activation:
│  └─ Terminal escape: \033[?1049h (smcup)
├─ Cursor management:
│  ├─ Hide cursor: \033[?25l
│  └─ Position control for animation
├─ Raw mode maintenance:
│  └─ Preserves existing InputHandler raw mode
├─ Screen clearing preparation:
│  └─ Ready for Matrix animation frames
└─ Core application render loop status:
   ├─ application.py:_render_loop():241 continues running
   ├─ Status area updates still function (20fps)
   ├─ InputHandler.rendering_paused = True → input area disabled
   └─ Matrix plugin gains exclusive display control
```

### 8. MATRIX ANIMATION EXECUTION LOOP

```
MatrixRainPlugin.render_frame():75 (Continuous Loop)
├─ Time calculation:89
│  └─ current_time = asyncio.get_event_loop().time() - self.start_time
├─ Matrix state update:92
│  └─ self.matrix_renderer.update(current_time)
│     ├─ Column updates (matrix_components.py:143-149):
│     │  ├─ Active column filtering:144-147
│     │  └─ New column spawning:151-156 (2% chance, spacing rules)
│     └─ Individual column updates:
│        ├─ MatrixColumn.update():46-81
│        │  ├─ Timing check:55-57 (speed-based updates)
│        │  ├─ Position advancement:61-62 (positions[i] += 1)
│        │  ├─ Off-screen cleanup:65-67
│        │  ├─ Character mutation:77-79 (5% chance)
│        │  └─ Column lifecycle:70-74 (restart probability)
│        └─ Return: bool (active/inactive status)
├─ Rendering execution:95
│  └─ self.matrix_renderer.render(self.renderer)
│     ├─ Screen clearing:165 → renderer.clear_screen()
│     ├─ Column rendering loop:168
│     │  └─ For each active column: column.render(renderer)
│     │     ├─ Position validation:90 (0 <= pos < height)
│     │     ├─ Color gradient calculation:92-102
│     │     │  ├─ Head character: ColorPalette.BRIGHT_WHITE:93
│     │     │  ├─ Recent (3 chars): ColorPalette.BRIGHT_GREEN:96
│     │     │  ├─ Middle (8 chars): ColorPalette.GREEN:99
│     │     │  └─ Tail: ColorPalette.DIM_GREEN:102
│     │     └─ Character placement:105
│     │        └─ renderer.write_at(x, pos, char, color)
│     └─ Output flush:172 → renderer.flush()
├─ Performance tracking:98
│  └─ self.update_frame_stats() → Frame rate monitoring
└─ Loop continuation:100 → return True (continue animation)
```

### 9. INPUT HANDLING IN FULLSCREEN MODE

```
Input Processing During Matrix:
├─ InputHandler._process_character():250
│  └─ Command mode routing:286 → CommandMode.MODAL detected
├─ InputHandler._handle_command_mode_keypress():1221
│  └─ Modal mode dispatch:1235 → CommandMode.MODAL
├─ InputHandler._handle_modal_keypress():1396
│  ├─ Fullscreen session detection:1407
│  │  └─ hasattr(self, '_fullscreen_session_active') and self._fullscreen_session_active
│  ├─ Exit key detection:1409
│  │  └─ key_press.char in ['q', '\x1b'] or key_press.name == "Escape"
│  ├─ Immediate exit path:1410-1415
│  │  ├─ self._fullscreen_session_active = False:1411
│  │  ├─ CommandMode.NORMAL restoration:1413
│  │  └─ Force display update:1414
│  └─ Plugin input routing:1418-1426
│     └─ EventBus.emit(FULLSCREEN_INPUT) → MatrixRainPlugin.handle_input()
└─ MatrixRainPlugin.handle_input():106
   ├─ Exit condition check:116
   │  └─ key_press.char in ['q', '\x1b'] or key_press.name == "Escape"
   ├─ Return True → Signal exit to framework:117
   └─ Return False → Continue animation for other keys:120
```

### 10. EXIT SEQUENCE & COMPLETE STATE RESTORATION

```
Matrix Exit Triggered by 'q', ESC, or Escape:
├─ MatrixRainPlugin.handle_input():106 → return True:117
├─ Framework exit processing:
│  ├─ MatrixRainPlugin.on_stop():122
│  │  └─ FullScreenPlugin.on_stop():124 (cleanup preparation)
│  ├─ MatrixRainPlugin.cleanup():129
│  │  ├─ self.matrix_renderer = None:131
│  │  └─ FullScreenPlugin.cleanup():132 (resource cleanup)
│  └─ FullScreenManager deregistration
├─ Terminal state restoration:
│  ├─ Alternate buffer exit: \033[?1049l (rmcup)
│  ├─ Cursor restoration: \033[?25h (show cursor)
│  ├─ Screen clearing for main buffer
│  └─ Terminal dimensions preserved
├─ Modal system cleanup:
│  ├─ EventBus.emit(MODAL_HIDE)
│  ├─ InputHandler._handle_modal_hide():1029
│  │  ├─ CommandMode.NORMAL restoration:1034
│  │  ├─ _fullscreen_session_active = False:1037
│  │  └─ Modal deactivation logging:1039
│  └─ Force display refresh:1042
├─ Rendering system restoration:
│  ├─ EventBus.emit(RESUME_RENDERING)
│  ├─ InputHandler._handle_resume_rendering():1001
│  │  ├─ self.rendering_paused = False:1004 ← INPUT RENDERING RESUMED
│  │  └─ Force display update:1006
│  └─ Normal render pipeline restoration
└─ Application state restoration:
   ├─ application.py:_render_loop():241 resumes input area control
   ├─ InputHandler normal key processing restored
   ├─ Status areas redisplay with current data
   ├─ Input buffer and cursor repositioning
   └─ Complete return to pre-matrix state
```

## STATE VARIABLES AFFECTED

### InputHandler State Changes
- `self.command_mode`: NORMAL → MENU_POPUP → MODAL → NORMAL
- `self.rendering_paused`: False → True → False
- `self._fullscreen_session_active`: None → True → False

### Terminal State Changes
- **Buffer**: Main → Alternate → Main
- **Cursor**: Visible → Hidden → Visible
- **Raw Mode**: Maintained throughout
- **Display Control**: Core App → Matrix Plugin → Core App

### Rendering Pipeline Changes
- **Input Area**: Active → Paused → Restored
- **Status Areas**: Active → Active → Active (never paused)
- **Message Display**: Active → Suppressed → Restored
- **Animation Loop**: None → Matrix → None

## PERFORMANCE CHARACTERISTICS

- **Animation Frame Rate**: Variable (based on MatrixColumn speeds 1.2-3.5)
- **Character Update Rate**: 5% mutation chance per frame
- **Column Spawning**: 2% chance per frame with spacing constraints
- **Memory Usage**: Grows with active columns (max terminal_width columns)
- **CPU Usage**: Continuous rendering loop until exit
- **Input Latency**: Immediate exit on 'q'/ESC detection

## DEBUGGING MARKERS

### Framework Activation Logs
```
🎯 NEW FRAMEWORK: MatrixRainPlugin.on_start() called - using full-screen plugin framework!
🎯 NEW FRAMEWORK: Matrix plugin starting via full-screen framework!
```

### State Transition Logs
```
"Registered Matrix plugin with full-screen framework"
"🎯 Command mode set to MODAL for full-screen plugin: matrix_rain"
"🎯 Fullscreen session marked as active for input routing"
"🔄 MODAL_HIDE event received - exiting modal mode"
"🔄 Fullscreen session marked as inactive"
```

### Input Control Logs
```
"🛑 PAUSE_RENDERING event received - pausing input rendering"
"▶️ RESUME_RENDERING event received - resuming input rendering"
```

## IMPORTANT CORRECTION: HOOK SYSTEM ANALYSIS

**CRITICAL FINDING: Both Matrix and Config use the IDENTICAL hook system!**

The key difference is NOT that Matrix uses hooks while Config doesn't. Both commands trigger the same `MODAL_TRIGGER` event and use the same `InputHandler._handle_modal_trigger()` handler.

### The Real Difference: Event Data Content

**Matrix event data:**
```
EventBus.emit(MODAL_TRIGGER) with:
{
  "fullscreen_plugin": True,     ← This flag triggers alternate buffer
  "plugin_name": "matrix_rain"
}
```

**Config event data:**
```
EventBus.emit(MODAL_TRIGGER) with:
{
  "ui_config": UIConfig(...),    ← This triggers ModalRenderer
  "action": "show_modal"
}
```

### Same Handler, Different Branches

```python
# InputHandler._handle_modal_trigger():1105
async def _handle_modal_trigger(self, event_data):
    if event_data.get('fullscreen_plugin'):
        # Matrix path - sets _fullscreen_session_active = True
        # This activates alternate buffer system
        self._fullscreen_session_active = True

    else:
        # Config path - uses ui_config
        ui_config = event_data.get('ui_config')
        await self._enter_modal_mode(ui_config)  # ModalRenderer
```

**Both commands use hooks - the event data determines behavior!**

## ERROR HANDLING

### Initialization Failures
- MatrixRenderer creation failure → return False:59
- Terminal size unavailable → fallback handling
- Plugin registration failure → error return:352-357

### Runtime Failures
- Render frame exceptions → return False:103-104
- Input handling errors → graceful exit:1463-1466
- State restoration failures → emergency cleanup:1587-1591

### Recovery Mechanisms
- Automatic modal mode exit on errors
- Force rendering restoration on cleanup
- Terminal state emergency restoration
- CommandMode.NORMAL fallback on exceptions