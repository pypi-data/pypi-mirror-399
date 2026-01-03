# Kollabor CLI - Complete Data Flow Analysis

## APPLICATION STARTUP FLOW

**Initialization Sequence** (main.py → core/application.py):

```
1. Bootstrap Logging Setup
   └─ main.py:20 → setup_bootstrap_logging()

2. Core Component Initialization
   ├─ TerminalLLMChat.__init__():26
   ├─ .kollabor/ directory creation
   ├─ PluginRegistry.load_all_plugins():34 ← Plugin discovery
   ├─ ConfigService with plugin configs:37
   ├─ StateManager (SQLite):46
   ├─ EventBus (hook system):47
   └─ StatusViewRegistry:49-57

3. I/O System Setup
   ├─ TerminalRenderer:60
   ├─ InputHandler:64 ← Raw mode, key parsing, command system
   └─ Slash command initialization:69-71

4. LLM Core Services
   ├─ KollaborConversationLogger:77
   ├─ LLMHookSystem:78
   ├─ MCPIntegration:79
   ├─ KollaborPluginSDK:80
   └─ LLMService:81-86

5. Plugin Instantiation:99-101
   └─ Dynamic plugin loading with dependency injection
```

## RUNTIME DATA FLOW PATTERNS

**Main Event Loop Architecture**:

```
┌─ main.py:32 asyncio.run(main())
│
├─ Application.start():106
│  ├─ _initialize_llm_core():166
│  ├─ _initialize_plugins():188
│  ├─ _register_core_status_views():295
│  └─ Parallel Tasks:
│     ├─ _render_loop():241 ← Status updates @ 20fps
│     └─ input_handler.start():126 ← User input processing
│
└─ Event Bus Coordination:
   ├─ Hook Registration (plugins → EventBus)
   ├─ Event Emission (components → EventBus)
   └─ Hook Execution (EventBus → plugins)
```

**Input Processing Flow**:

```
User Input → InputHandler._input_loop():141
├─ select.select() polling with 10ms delay:146
├─ Raw data capture via os.read():152 (8KB chunks)
├─ Multi-character paste detection:181-205
│  ├─ Paste bucket storage:198-201 (PASTE_{counter})
│  └─ Placeholder creation:205 → [Pasted #N X lines, Y chars]
├─ Character-by-character processing:215
│  ├─ KeyParser.parse_char():271 → KeyPress objects
│  ├─ Escape sequence handling:177 (arrow keys, function keys)
│  └─ Command mode detection:260 ('/' triggers CommandMode.MENU_POPUP)
├─ BufferManager operations:429
│  ├─ insert_char() with cursor tracking
│  ├─ Validation with 100KB limit:51
│  └─ History management (100 commands):52
├─ Event Bus processing:293-302
│  ├─ EventType.KEY_PRESS emission
│  ├─ Plugin hook execution via HookRegistry
│  └─ prevent_default checking:305
├─ Key handling dispatch:337
│  ├─ Control keys (Ctrl+C, Enter, Backspace):355-363
│  ├─ Arrow navigation with cursor updates:372-390
│  ├─ Status view cycling (Option+comma/period):402-408
│  └─ Printable character insertion:427-436
├─ Slash command processing (if '/' detected):
│  ├─ SlashCommandParser.parse_command():1670
│  ├─ CommandRegistry lookup:system_commands.py
│  ├─ CommandExecutor.execute_command():29
│  └─ Command result handling:1681-1691
├─ Display updates:451
│  ├─ BufferManager.get_display_info():458
│  ├─ TerminalRenderer state sync:461-462
│  └─ Force rendering for cursor moves:465-477
└─ Final event emission:532-536
   ├─ EventType.USER_INPUT (on Enter)
   ├─ Paste expansion via _expand_paste_placeholders():521
   └─ Hook propagation to LLM services
```

## `/matrix` COMMAND DATA FLOW

**Complete Execution Trace with State Changes**:

```
1. USER INPUT: "/matrix"
   ├─ core/io/input_handler.py:_input_loop():141 → Raw terminal capture
   ├─ KeyParser.parse_char():271 → KeyPress('/') + remaining chars
   ├─ Command mode detection:260 → CommandMode.MENU_POPUP triggered
   ├─ SlashCommandParser.parse_command():1670 → SlashCommand{name:"matrix"}
   └─ BufferManager → Command validation and storage

2. COMMAND REGISTRY & EXECUTION
   ├─ core/commands/registry.py:SlashCommandRegistry.get_command("matrix")
   ├─ core/commands/executor.py:CommandExecutor.execute_command():29
   ├─ EventBus.emit_with_hooks(SLASH_COMMAND_DETECTED):41-49
   └─ core/commands/system_commands.py:SystemCommandsPlugin.handle_matrix():319

3. FULLSCREEN FRAMEWORK SETUP
   ├─ from ..fullscreen import FullScreenManager:330
   ├─ from plugins.fullscreen.matrix_plugin import MatrixRainPlugin:331
   ├─ FullScreenManager creation/reuse:334-335
   ├─ MatrixRainPlugin() instantiation:339
   ├─ Manager.register_plugin(matrix_plugin):340
   └─ Manager.launch_plugin("matrix_rain"):344

4. MODAL STATE TRANSITION & RENDERING CONTROL
   ├─ FullScreenManager.launch_plugin() → EventBus.emit(MODAL_TRIGGER)
   ├─ core/io/input_handler.py:_handle_modal_trigger():1105
   │  ├─ CommandMode.MODAL activation:1120
   │  ├─ _fullscreen_session_active = True:1132
   │  └─ Modal input routing enabled:1134
   ├─ EventBus.emit(PAUSE_RENDERING):
   │  └─ input_handler._handle_pause_rendering():995
   │     └─ self.rendering_paused = True:998 ← INPUT RENDERING STOPPED
   └─ Terminal takeover preparation

5. MATRIX PLUGIN INITIALIZATION
   ├─ plugins/fullscreen/matrix_plugin.py:MatrixRainPlugin.initialize():37
   │  ├─ renderer.get_terminal_size():51 → (width, height)
   │  └─ core/fullscreen/components/matrix_components.py:MatrixRenderer():54
   │     ├─ MatrixColumn creation for each x position:129-134
   │     ├─ Character set initialization (katakana/symbols):27-35
   │     └─ Random speed/length assignment:22-24
   ├─ MatrixRainPlugin.on_start():62
   │  ├─ Distinctive log: "🎯 NEW FRAMEWORK: Matrix plugin starting":68-69
   │  └─ MatrixRenderer.reset():73 → Fresh animation state
   └─ Animation loop preparation

6. TERMINAL STATE CHANGES & RENDERING TAKEOVER
   ├─ FullScreenRenderer terminal control:
   │  ├─ Alternate buffer activation (smcup)
   │  ├─ Cursor hiding (\033[?25l)
   │  └─ Raw mode maintenance
   ├─ Core render loop bypass:
   │  ├─ application.py:_render_loop():241 → status updates continue
   │  ├─ InputHandler.rendering_paused = True → input area cleared
   │  └─ Matrix plugin owns display output
   └─ Input routing change: normal → fullscreen modal

7. MATRIX ANIMATION EXECUTION LOOP
   ├─ MatrixRainPlugin.render_frame():75 (main animation loop)
   │  ├─ asyncio.get_event_loop().time() - start_time:89 → current_time
   │  ├─ MatrixRenderer.update(current_time):92
   │  │  ├─ matrix_components.py:MatrixColumn.update():46-81
   │  │  │  ├─ Position advancement: positions[i] += 1:62
   │  │  │  ├─ Off-screen removal: positions.pop(0):65-67
   │  │  │  ├─ Character mutation (5% chance):77-79
   │  │  │  └─ New column spawning (2% chance):151-156
   │  │  └─ Column lifecycle management:143-149
   │  ├─ MatrixRenderer.render(renderer):95
   │  │  ├─ renderer.clear_screen():165
   │  │  ├─ MatrixColumn.render() for each column:168
   │  │  │  ├─ Color calculation based on position:92-102
   │  │  │  │  ├─ Head: ColorPalette.BRIGHT_WHITE:93
   │  │  │  │  ├─ Recent: ColorPalette.BRIGHT_GREEN:96
   │  │  │  │  ├─ Middle: ColorPalette.GREEN:99
   │  │  │  │  └─ Tail: ColorPalette.DIM_GREEN:102
   │  │  │  └─ renderer.write_at(x, pos, char, color):105
   │  │  └─ renderer.flush():172
   │  └─ update_frame_stats():98 → Performance tracking
   └─ Continuous loop until exit condition

8. INPUT HANDLING IN FULLSCREEN MODE
   ├─ InputHandler._process_character():250 → Modal mode routing:286
   ├─ _handle_command_mode_keypress():1221 → CommandMode.MODAL:1235
   ├─ _handle_modal_keypress():1396
   │  ├─ Fullscreen session check:1407 → _fullscreen_session_active
   │  ├─ Exit key detection:1409 → 'q', ESC, Escape
   │  └─ EventBus.emit(FULLSCREEN_INPUT):1418-1426 → Plugin routing
   └─ MatrixRainPlugin.handle_input():106 → Exit decision

9. EXIT SEQUENCE & STATE RESTORATION
   ├─ MatrixRainPlugin.handle_input():106 → key_press.char in ['q', '\x1b']:116
   ├─ MatrixRainPlugin.on_stop():122 → Cleanup preparation
   ├─ FullScreenManager cleanup:129
   │  ├─ Terminal state restoration (rmcup - main buffer)
   │  ├─ Cursor restoration (\033[?25h)
   │  └─ Plugin deregistration
   ├─ Modal state reset:
   │  ├─ EventBus.emit(MODAL_HIDE) → _handle_modal_hide():1029
   │  ├─ CommandMode.NORMAL restoration:1034
   │  ├─ _fullscreen_session_active = False:1037
   │  └─ InputHandler routing restoration
   ├─ Rendering restoration:
   │  ├─ EventBus.emit(RESUME_RENDERING) → _handle_resume_rendering():1001
   │  ├─ self.rendering_paused = False:1004 ← INPUT RENDERING RESUMED
   │  └─ Force display update:1006
   └─ Return to normal terminal state:
      ├─ application.py:_render_loop() resumes control
      ├─ InputHandler normal processing restored
      └─ Status areas and input buffer redisplay
```

**Core Data Structures**:

```
MatrixColumn:8 {
  x: int,                    ← Column position
  chars: List[str],          ← Character array (katakana/symbols)
  positions: List[int],      ← Y positions for each char
  speed: float,             ← Fall speed (1.2-3.5)
  length: int               ← Column length (5-25)
}

MatrixRenderer:108 {
  terminal_width: int,
  terminal_height: int,
  columns: List[MatrixColumn],
  start_time: float
}
```

**Event Bus Integration**:
- EventType.SLASH_COMMAND_DETECTED → Command system
- Hook execution through HookRegistry/HookExecutor
- Plugin lifecycle events (start/stop/cleanup)
- Status area updates for real-time display

**Framework Architecture**:
- FullScreenManager: Plugin registry and lifecycle
- FullScreenRenderer: Terminal takeover and rendering
- FullScreenPlugin: Base class with standard lifecycle
- FullScreenSession: Session management and cleanup

## KEY ARCHITECTURAL PATTERNS

### Event-Driven Design
The application uses an event bus (`core/events/bus.py`) that coordinates between:
- **HookRegistry**: Manages hook registration and lookup
- **HookExecutor**: Handles hook execution with error handling
- **EventProcessor**: Processes events through registered hooks

### Plugin Lifecycle
1. **Discovery**: `PluginDiscovery` scans `plugins/` directory
2. **Factory**: `PluginFactory` instantiates plugins with dependency injection
3. **Registration**: Plugins register hooks during initialization
4. **Execution**: Events trigger hooks through the event bus

### LLM Service Architecture
The `LLMService` (`core/llm/llm_service.py`) orchestrates:
- **APICommunicationService**: HTTP client with rate limiting
- **KollaborConversationLogger**: Persistent conversation history
- **MessageDisplayService**: Response formatting and display
- **ToolExecutor**: Function calling execution
- **MCPIntegration**: Model Context Protocol support
- **KollaborPluginSDK**: Plugin development interface
- **LLMHookSystem**: LLM-specific hook management

## COMPONENT INTERACTIONS

### Configuration System
Configuration uses dot notation (e.g., `config.get("core.llm.max_history", 90)`):
- Core LLM settings: `core.llm.*`
- Terminal rendering: `terminal.*`
- Application metadata: `application.*`

### Status Display System
- Multi-area status rendering (A, B, C areas)
- Plugin status collection via `get_status_line()`
- Real-time updates at configurable FPS (default 20fps)
- Spinner animations for processing states

### Input System Flow
```
Terminal Input → Raw Mode → KeyParser → BufferManager → CommandParser
                    ↓
Event Bus ← CommandExecutor ← SlashCommandRegistry ← Command Lookup
```

### Rendering Pipeline
```
StatusViewRegistry → TerminalRenderer → Screen Buffer → Terminal Output
       ↑                    ↑
Plugin Status Lines    Modal/Effect Overlays
```

## FILE STRUCTURE REFERENCE

```
core/
├── application.py             # Main orchestrator
├── config/                    # Configuration management
├── events/                    # Event bus and hook system
│   ├── bus.py                # Central event coordination
│   ├── registry.py           # Hook registration
│   └── executor.py           # Hook execution
├── io/                        # Terminal I/O, rendering, input
│   ├── input_handler.py      # Raw input processing
│   ├── terminal_renderer.py  # Screen rendering
│   └── key_parser.py         # Key sequence parsing
├── llm/                       # LLM services
├── commands/                  # Command system
│   ├── parser.py             # Slash command parsing
│   ├── registry.py           # Command registration
│   ├── executor.py           # Command execution
│   └── system_commands.py    # Core system commands
├── fullscreen/               # Full-screen plugin framework
│   ├── manager.py            # Plugin lifecycle management
│   ├── renderer.py           # Full-screen rendering
│   └── components/           # Reusable components
└── plugins/                  # Plugin system

plugins/
├── fullscreen/
│   └── matrix_plugin.py      # Matrix rain implementation
└── enhanced_input/           # Input enhancement plugins
```

## PERFORMANCE CHARACTERISTICS

- **Render Loop**: 20fps default (configurable)
- **Input Polling**: 10ms delay (configurable)
- **Buffer Limits**: 100KB input buffer, 100 command history
- **Matrix Animation**: 1.2-3.5 speed range, 5-25 character columns
- **Event Processing**: Asynchronous with priority-based hook execution
- **Memory Management**: SQLite state persistence, rotating logs

## DEBUGGING ENTRY POINTS

- Application logs: `.kollabor/logs/kollabor.log`
- Configuration: `.kollabor/config.json`
- State persistence: `.kollabor/state.db`
- Framework activation logs: Search for "🎯 NEW FRAMEWORK" in logs
- Event bus stats: Available via `EventBus.get_registry_stats()`