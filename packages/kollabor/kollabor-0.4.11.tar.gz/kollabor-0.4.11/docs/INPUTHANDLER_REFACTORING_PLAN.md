# InputHandler Refactoring Plan

## Executive Summary

The `core/io/input_handler.py` file is a 2,752-line monolithic class that violates
the Single Responsibility Principle. This document outlines a phased refactoring
approach using the GLM Massive Refactoring Pattern to decompose it into focused,
testable modules.

## Current State Analysis

### File Statistics
- Total Lines: 2,752
- Single Class: `InputHandler`
- Methods: 60+
- Responsibilities: 8+ distinct domains

### Identified Responsibilities

| Domain | Lines (Est.) | Description |
|--------|-------------|-------------|
| Input Loop | ~200 | Main loop, platform I/O |
| Key Processing | ~300 | Character parsing, key handlers |
| Display Management | ~100 | Render updates, pause/resume |
| Paste System | ~250 | Detection, placeholders, expansion |
| Hook Registration | ~400 | 10+ hooks, event handlers |
| Slash Commands | ~400 | Menu, filtering, execution |
| Modal System | ~700 | Regular, status, live modals |
| Status Rendering | ~200 | Modal line generation |

### Current Dependencies
```
InputHandler
  +-- event_bus (EventBus)
  +-- renderer (TerminalRenderer)
  +-- config (ConfigManager)
  +-- key_parser (KeyParser)
  +-- buffer_manager (BufferManager)
  +-- slash_parser (SlashCommandParser)
  +-- command_registry (SlashCommandRegistry)
  +-- command_executor (SlashCommandExecutor)
  +-- command_menu_renderer (CommandMenuRenderer)
  +-- error_handler (InputErrorHandler)
  +-- modal_renderer (ModalRenderer) [lazy]
  +-- live_modal_renderer (LiveModalRenderer) [lazy]
```

## Target Architecture

### Directory Structure
```
core/io/input/
    __init__.py              # Public API exports
    models.py                # Shared types, enums, InputState
    interfaces.py            # Component interfaces/protocols
    facade.py                # InputHandler facade (delegator)
    input_loop.py            # InputLoopManager
    key_handler.py           # KeyPressHandler
    display_controller.py    # DisplayController
    paste_processor.py       # PasteProcessor
    hook_registrar.py        # HookRegistrar
    command_mode_handler.py  # CommandModeHandler (slash commands)
    modal_controller.py      # ModalController (all modal types)
    status_modal_renderer.py # StatusModalRenderer
```

### Shared State Model

The `InputState` dataclass provides shared state across components:

```python
# models.py
@dataclass
class InputState:
    """Shared state for input components."""
    command_mode: CommandMode = CommandMode.NORMAL
    command_menu_active: bool = False
    selected_command_index: int = 0
    rendering_paused: bool = False
    current_status_modal_config: Optional[Any] = None
    pending_save_confirm: bool = False
    fullscreen_session_active: bool = False
```

### Event Ownership Boundaries

| Component | Event Types Owned |
|-----------|-------------------|
| HookRegistrar | KEY_PRESS, USER_INPUT, CANCEL_REQUEST |
| ModalController | MODAL_TRIGGER, MODAL_HIDE, MODAL_COMMAND_SELECTED |
| CommandModeHandler | COMMAND_MENU_SHOW, COMMAND_MENU_HIDE, COMMAND_MENU_FILTER |
| DisplayController | PAUSE_RENDERING, RESUME_RENDERING |

### Circular Dependency Mitigations

Three potential circular dependencies identified with solutions:

1. **DisplayController <-> PasteProcessor**
   - Risk: PasteProcessor needs DisplayController for placeholder updates
   - Solution: PasteProcessor receives DisplayController reference (unidirectional)
   - Alternative: Use events for placeholder updates if needed

2. **ModalController <-> CommandModeHandler**
   - Risk: Both modify command_mode state
   - Solution: State centralized in InputState dataclass (no direct reference)
   - Components read/write state independently

3. **HookRegistrar -> All Components**
   - Risk: HookRegistrar needs component references for delegation
   - Solution: HookRegistrar receives handler callbacks, not component references
   - Components emit events through event_bus, not HookRegistrar

### Error Handling Strategy

All components receive shared `InputErrorHandler` instance:

```python
# Error propagation pattern
class ComponentBase:
    def __init__(self, error_handler: InputErrorHandler, ...):
        self.error_handler = error_handler

    async def safe_operation(self):
        try:
            await self._do_work()
        except Exception as e:
            await self.error_handler.handle_error(
                ErrorType.COMPONENT_ERROR,
                f"Error in {self.__class__.__name__}: {e}",
                ErrorSeverity.MEDIUM,
                {"component": self.__class__.__name__}
            )
```

### Component Responsibilities

#### 1. InputLoopManager (`input_loop.py`)
- Main input loop execution
- Platform-specific input checking (Windows/Unix)
- Chunk reading and routing
- Start/stop lifecycle
- Error handling via InputErrorHandler
- Cleanup operations
- Windows extended key mapping (arrow keys, F1-F12, Home/End, etc.)

```python
class InputLoopManager:
    def __init__(self, key_handler, paste_processor, error_handler, state, config): ...
    async def start(self): ...
    async def stop(self): ...
    async def cleanup(self): ...
    async def _input_loop(self): ...
    async def _check_input_available(self) -> bool: ...
    async def _read_input_chunk(self) -> str: ...

    # Windows extended key mapping dictionary (preserved from lines 331-354)
    WIN_KEY_MAP = {
        72: b"\x1b[A",   # ArrowUp
        80: b"\x1b[B",   # ArrowDown
        75: b"\x1b[D",   # ArrowLeft
        77: b"\x1b[C",   # ArrowRight
        # ... full mapping preserved
    }
```

#### 2. KeyPressHandler (`key_handler.py`)
- Process individual characters
- Route to appropriate handler (normal, command mode)
- Handle control keys (Ctrl+C, Enter, arrows, etc.)
- Emit KEY_PRESS events
- Key event validation

```python
class KeyPressHandler:
    def __init__(self, key_parser, buffer_manager, event_bus, state): ...
    async def process_character(self, char: str): ...
    async def handle_key_press(self, key_press: KeyPress): ...
    async def handle_enter(self): ...
    async def handle_escape(self): ...
    async def handle_arrow_keys(self, direction: str): ...
    def check_prevent_default(self, key_result: Dict) -> bool: ...
    # Internal helpers (extracted from nested functions)
    def is_escape_sequence(self, text: str) -> bool: ...
    async def delayed_escape_check(self): ...
```

#### 3. DisplayController (`display_controller.py`)
- Update terminal display
- Manage rendering pause/resume
- Status view navigation
- Coordinate with renderer

```python
class DisplayController:
    def __init__(self, renderer, buffer_manager): ...
    async def update_display(self, force_render: bool = False): ...
    def pause_rendering(self): ...
    def resume_rendering(self): ...
    async def handle_status_view_previous(self): ...
    async def handle_status_view_next(self): ...
```

#### 4. PasteProcessor (`paste_processor.py`)
- Primary paste detection (chunk-based)
- Secondary paste detection (timing-based)
- Placeholder creation and expansion
- Paste bucket management
- Sync and async paste handling

```python
class PasteProcessor:
    def __init__(self, buffer_manager, display_controller, state): ...
    async def handle_paste_chunk(self, chunk: str) -> bool: ...
    async def create_paste_placeholder(self, paste_id: str): ...
    async def update_paste_placeholder(self): ...
    def expand_paste_placeholders(self, message: str) -> str: ...
    async def simple_paste_detection(self, char: str, time: float) -> bool: ...
    # Sync methods for edge cases
    def flush_paste_buffer_as_keystrokes_sync(self): ...
    def process_simple_paste_sync(self): ...
    # Async wrappers
    async def flush_paste_buffer_as_keystrokes(self): ...
    async def process_simple_paste(self): ...
```

#### 5. HookRegistrar (`hook_registrar.py`)
- Register all input-related hooks (9 hook types)
- Hook callback handlers (9 handlers)
- Centralized hook management

```python
class HookRegistrar:
    def __init__(self, event_bus, modal_controller, command_handler, display_controller): ...
    async def register_all_hooks(self): ...

    # Hook registrations (9 total)
    async def _register_command_menu_render_hook(self): ...
    async def _register_modal_trigger_hook(self): ...
    async def _register_status_modal_trigger_hook(self): ...
    async def _register_live_modal_trigger_hook(self): ...
    async def _register_status_modal_render_hook(self): ...
    async def _register_command_output_display_hook(self): ...
    async def _register_pause_rendering_hook(self): ...
    async def _register_resume_rendering_hook(self): ...
    async def _register_modal_hide_hook(self): ...

    # Hook handlers (9 total)
    async def handle_command_menu_render(self, event_data, context): ...
    async def handle_modal_trigger(self, event_data, context): ...
    async def handle_status_modal_trigger(self, event_data, context): ...
    async def handle_live_modal_trigger(self, event_data, context): ...
    async def handle_status_modal_render(self, event_data, context): ...
    async def handle_command_output_display(self, event_data, context): ...
    async def handle_pause_rendering(self, event_data, context): ...
    async def handle_resume_rendering(self, event_data, context): ...
    async def handle_modal_hide(self, event_data, context): ...
```

#### 6. CommandModeHandler (`command_mode_handler.py`)
- Slash command mode management
- Menu popup navigation
- Command filtering and execution
- Command registry interaction

```python
class CommandModeHandler:
    def __init__(self, registry, executor, menu_renderer, buffer, event_bus, state): ...
    async def enter_command_mode(self): ...
    async def exit_command_mode(self): ...
    async def handle_command_mode_keypress(self, key_press) -> bool: ...
    async def handle_command_mode_input(self, char: str) -> bool: ...
    async def handle_menu_popup_keypress(self, key_press) -> bool: ...
    async def handle_menu_popup_input(self, char: str) -> bool: ...
    async def navigate_menu(self, direction: str): ...
    async def update_command_filter(self): ...
    async def execute_selected_command(self): ...
    def get_available_commands(self) -> List[Dict[str, Any]]: ...
    def filter_commands(self, filter_text: str) -> List[Dict]: ...
```

#### 7. ModalController (`modal_controller.py`)
- Regular modal mode management
- Status modal mode management
- Live modal mode management
- Modal state transitions
- Save confirmation flow

```python
class ModalController:
    def __init__(self, renderer, event_bus, config, status_renderer): ...

    # Regular modal
    async def enter_modal_mode(self, ui_config): ...
    async def exit_modal_mode(self): ...
    async def exit_modal_mode_minimal(self): ...
    async def handle_modal_keypress(self, key_press): ...
    async def refresh_modal_display(self): ...
    def has_pending_modal_changes(self) -> bool: ...
    async def show_save_confirmation(self): ...
    async def handle_save_confirmation(self, key_press): ...
    async def save_and_exit_modal(self): ...

    # Status modal
    async def enter_status_modal_mode(self, ui_config): ...
    async def exit_status_modal_mode(self): ...
    async def handle_status_modal_keypress(self, key_press): ...
    async def handle_status_modal_input(self, char: str): ...
    async def handle_status_takeover_keypress(self, key_press): ...
    async def handle_status_takeover_input(self, char: str): ...

    # Live modal
    async def enter_live_modal_mode(self, generator, config, callback): ...
    async def exit_live_modal_mode(self): ...
    async def handle_live_modal_keypress(self, key_press): ...
    async def handle_live_modal_input(self, char: str): ...
```

#### 8. StatusModalRenderer (`status_modal_renderer.py`)
- Generate status modal display lines
- Box rendering with borders
- Content formatting
- Fallback simple rendering

```python
class StatusModalRenderer:
    def __init__(self, renderer, visual_effects): ...
    def generate_status_modal_lines(self, ui_config) -> List[str]: ...
    def create_simple_bordered_content(self, lines) -> List[str]: ...
```

#### 9. InputHandler Facade (`facade.py`)
- Public API (backward compatible)
- Delegates to specialized components
- Orchestrates component interactions
- Maintains existing interface
- Aggregates status from all components

```python
class InputHandler:
    """Facade maintaining backward compatibility."""

    def __init__(self, event_bus, renderer, config):
        # Shared state across components
        self.state = InputState()

        # Core services (shared)
        self.key_parser = KeyParser()
        self.buffer_manager = BufferManager(...)
        self.error_handler = InputErrorHandler(...)

        # Components (all receive shared state)
        self.display_controller = DisplayController(renderer, self.buffer_manager, self.state)
        self.paste_processor = PasteProcessor(self.buffer_manager, self.display_controller, self.state)
        self.key_handler = KeyPressHandler(self.key_parser, self.buffer_manager, event_bus, self.state)
        self.command_handler = CommandModeHandler(registry, executor, menu_renderer, self.buffer_manager, self.state)
        self.status_renderer = StatusModalRenderer(renderer)
        self.modal_controller = ModalController(renderer, event_bus, config, self.status_renderer, self.state)
        self.hook_registrar = HookRegistrar(event_bus, self._get_hook_handlers())
        self.loop_manager = InputLoopManager(self.key_handler, self.paste_processor, self.error_handler, self.state)

    async def start(self): ...      # Delegates to loop_manager
    async def stop(self): ...       # Delegates to loop_manager
    async def cleanup(self): ...    # Delegates to loop_manager
    def get_status(self) -> Dict:   # Aggregates from all components
    def pause_rendering(self): ...  # Delegates to display_controller
    def resume_rendering(self): ... # Delegates to display_controller
    # ... other public methods delegate to components
```

## Refactoring Phases

### Phase A: Foundation (Parallel)
Create base infrastructure and models.

| Agent | Task | Deliverable |
|-------|------|-------------|
| PhaseA-Models | Extract shared types/enums | `input/models.py` |
| PhaseA-Interfaces | Define component interfaces | `input/interfaces.py` |
| PhaseA-Directory | Create directory structure | `input/__init__.py` |

### Phase B: Core Components (Parallel)
Extract independent components with TDD.

| Agent | Task | Deliverable |
|-------|------|-------------|
| PhaseB-PasteProcessor | Extract paste handling | `paste_processor.py` + tests |
| PhaseB-DisplayController | Extract display logic | `display_controller.py` + tests |
| PhaseB-KeyHandler | Extract key processing | `key_handler.py` + tests |

### Phase C: Dependent Components (Parallel)
Components that depend on Phase B outputs.

| Agent | Task | Deliverable |
|-------|------|-------------|
| PhaseC-CommandMode | Extract slash command system | `command_mode_handler.py` + tests |
| PhaseC-StatusRenderer | Extract status modal render | `status_modal_renderer.py` + tests |
| PhaseC-ModalController | Extract modal management | `modal_controller.py` + tests |
| PhaseC-HookRegistrar | Extract hook registration | `hook_registrar.py` + tests |
| PhaseC-InputLoop | Extract main loop | `input_loop.py` + tests |

### Phase D: Integration (Sequential)
Create facade and integrate components.

| Agent | Task | Deliverable |
|-------|------|-------------|
| PhaseD-Facade | Create InputHandler facade | `facade.py` |
| PhaseD-Wiring | Wire all components | Updated `__init__.py` |

### Phase E: Validation (Parallel)
Verify integration and update imports.

| Agent | Task | Deliverable |
|-------|------|-------------|
| PhaseE-IntegrationTests | Full integration tests | `tests/integration/` |
| PhaseE-ImportUpdates | Update all imports | Modified files |
| PhaseE-Documentation | Update CLAUDE.md | Documentation |

## Commit Strategy

Commit after each phase completion:

```bash
# After Phase A
git commit -m "refactor(input): Phase A - foundation infrastructure"

# After Phase B
git commit -m "refactor(input): Phase B - extract core components"

# After Phase C
git commit -m "refactor(input): Phase C - extract dependent components"

# After Phase D
git commit -m "refactor(input): Phase D - create facade and integrate"

# After Phase E
git commit -m "refactor(input): Phase E - validation and cleanup"
```

## Risk Mitigation

### Backup Strategy
```bash
cp core/io/input_handler.py core/io/input_handler.py.backup
```

### Rollback Points
- Each phase commit is a rollback point
- Facade pattern ensures backward compatibility
- Original file preserved as `.backup`

### Testing Requirements
- Each component must have unit tests
- Tests written BEFORE implementation (TDD)
- Integration tests verify full flow
- All existing functionality preserved

## Success Criteria

1. **Code Organization**
   - No file exceeds 400 lines
   - Each class has single responsibility
   - Clear dependency graph

2. **Test Coverage**
   - Unit tests for each component
   - Integration tests for facade
   - All existing tests pass

3. **Backward Compatibility**
   - `InputHandler` API unchanged
   - No import changes required for consumers
   - Same event/hook behavior

4. **Performance**
   - No regression in input latency
   - Efficient delegation pattern
   - Minimal memory overhead

## State Ownership Matrix

Each component owns specific state variables:

| Component | State Variables |
|-----------|-----------------|
| InputLoopManager | `running`, `polling_delay`, `error_delay`, `error_handler` |
| KeyPressHandler | `_last_cursor_pos`, key parser state |
| DisplayController | `rendering_paused`, cursor tracking |
| PasteProcessor | `_paste_bucket`, `_paste_counter`, `_current_paste_id`, `_last_paste_time`, `_paste_buffer`, `paste_detection_enabled` |
| CommandModeHandler | `command_mode` (MENU_POPUP), `command_menu_active`, `selected_command_index` |
| ModalController | `command_mode` (MODAL/STATUS_MODAL/LIVE_MODAL), `modal_renderer`, `live_modal_renderer`, `current_status_modal_config`, `_pending_save_confirm`, `_fullscreen_session_active` |
| HookRegistrar | Hook references only (stateless) |
| Facade | References to all components, `buffer_manager`, `command_mode` (delegated) |

## Agent Launch Commands

```bash
# Phase A (parallel)
tglm PhaseAModels "Extract shared types from input_handler.py.backup to input/models.py"
tglm PhaseAInterfaces "Define component interfaces in input/interfaces.py"
tglm PhaseADirectory "Create input/ directory structure with __init__.py"

# Phase B (parallel) - after Phase A completes
tglm PhaseBPaste "Extract paste handling to paste_processor.py with TDD"
tglm PhaseBDisplay "Extract display logic to display_controller.py with TDD"
tglm PhaseBKey "Extract key processing to key_handler.py with TDD"

# Phase C (parallel) - after Phase B completes
tglm PhaseCCommand "Extract slash command system to command_mode_handler.py with TDD"
tglm PhaseCStatus "Extract status modal render to status_modal_renderer.py with TDD"
tglm PhaseCModal "Extract modal management to modal_controller.py with TDD"
tglm PhaseCHook "Extract hook registration to hook_registrar.py with TDD"
tglm PhaseCLoop "Extract main loop to input_loop.py with TDD"

# Phase D (sequential)
tglm PhaseDFacade "Create InputHandler facade in facade.py delegating to all components"

# Phase E (parallel)
tglm PhaseEIntegration "Write integration tests for refactored InputHandler"
tglm PhaseEImports "Update all imports across codebase"
tglm PhaseEDocs "Update CLAUDE.md with new architecture"
```

## Estimated Complexity

| Phase | Components | Estimated Time | Risk Level |
|-------|-----------|----------------|------------|
| Phase A | 3 | Low | Low |
| Phase B | 3 | Medium | Low |
| Phase C | 5 | Medium | Medium |
| Phase D | 2 | High | High |
| Phase E | 3 | Medium | Low |

## Notes

- Phase D is sequential due to integration complexity
- Use `.backup` file as source of truth during extraction
- Each agent should verify tests pass before marking complete
- Facade must maintain 100% API compatibility

## Implementation Progress

### Current State (2025-12-27 Audit)

**CRITICAL: Components extracted but NOT integrated.**

The original `input_handler.py` remains at 2,752 lines. Components were created
in `core/io/input/` but InputHandler does NOT import or delegate to them.

| Component | File | Lines | Tests | Integrated? |
|-----------|------|-------|-------|-------------|
| StatusModalRenderer | status_modal_renderer.py | 184 | 7 pass | NO |
| PasteProcessor | paste_processor.py | 320 | 22 pass | NO |
| DisplayController | display_controller.py | 128 | 15 pass | NO |
| KeyPressHandler | key_press_handler.py | 498 | - | NO |
| CommandModeHandler | command_mode_handler.py | 596 | - | NO |
| ModalController | modal_controller.py | 870 | - | NO |
| HookRegistrar | hook_registrar.py | 286 | - | NO |
| __init__.py | __init__.py | 23 | - | - |
| **Total extracted** | | **2,905** | **44 pass** | |

**Original file:** `core/io/input_handler.py` = 2,752 lines (UNCHANGED)

### What Was Actually Done

1. Created `core/io/input/` directory structure
2. Extracted component code to separate files
3. Wrote unit tests for some components (44 tests pass)
4. Components are standalone but NOT wired to InputHandler

### What Was NOT Done

1. InputHandler does not import from `core.io.input`
2. No delegation/property proxies implemented
3. Original code NOT removed from InputHandler
4. Integration testing not performed

### Remaining Work

| Phase | Task | Status |
|-------|------|--------|
| Integration | Wire InputHandler to use components | TODO |
| Integration | Add imports from core.io.input | TODO |
| Integration | Create property proxies for state | TODO |
| Cleanup | Remove duplicated code from InputHandler | TODO |
| Testing | Integration tests with wired components | TODO |
| Testing | Manual smoke test of full system | TODO |

### Integration Strategy

Two options for completing the refactoring:

**Option A: Gradual Migration (Safer)**
1. Import one component at a time
2. Add property proxy for that component's state
3. Delegate methods to component
4. Remove duplicated code
5. Test after each component
6. Repeat for all 7 components

**Option B: Full Facade (Riskier)**
1. Create new InputHandler that only delegates
2. Wire all components at once
3. Replace old InputHandler entirely
4. Higher risk but cleaner result

Recommended: Option A - gradual migration with testing at each step.

## Original Phase Details (for reference)

### Phase 1-3: Component Extraction
Components were extracted to separate files with unit tests.
See files in `core/io/input/` for implementations.

### Phase 4-7: Additional Components
Additional components extracted but integration claims were incorrect.
Files exist but are not used by InputHandler.

## Revision History

| Date | Change |
|------|--------|
| 2025-12-15 | Initial plan created |
| 2025-12-15 | V2-V5: Plan refinements and method coverage |
| 2025-12-15 | V6: Started extraction, Phase 1 complete |
| 2025-12-15 | V7: Claimed completion (INCORRECT - see V8) |
| 2025-12-27 | V8: AUDIT - Found components NOT integrated. InputHandler still 2,752 lines. Updated status to reflect reality. |
