# InputHandler Refactoring Audit

Generated: 2025-12-27
Updated: 2025-12-27 (Critical bugs fixed, InputLoopManager added)

## Summary

| Category | Count |
|----------|-------|
| Original methods in input_handler.py | 79 |
| Methods in extracted components | 77 |
| Mapped (have equivalent) | 69 |
| Remain in facade | 2 |
| New helper methods in components | ~20 |

## Original InputHandler Methods (79 total)

Line numbers from `core/io/input_handler.py` (2,752 lines)

### Lifecycle & Core Loop (6 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 41 | `__init__` | InputHandler (facade) | KEEP |
| 123 | `start` | InputLoopManager | EXISTS (start) |
| 171 | `stop` | InputLoopManager | EXISTS (stop) |
| 181 | `_input_loop` | InputLoopManager | EXISTS (_input_loop) |
| 880 | `cleanup` | InputLoopManager | EXISTS (cleanup) |
| 861 | `get_status` | InputHandler (facade) | KEEP |

### Platform I/O (2 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 296 | `_check_input_available` | InputLoopManager | EXISTS (_check_input_available) |
| 309 | `_read_input_chunk` | InputLoopManager | EXISTS (_read_input_chunk) |

### Key Processing (6 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 385 | `_process_character` | KeyPressHandler | EXISTS (process_character) |
| 197 | `is_escape_sequence` (nested) | KeyPressHandler | EXISTS (nested in process_character) |
| 427 | `delayed_escape_check` (nested) | KeyPressHandler | EXISTS (nested in process_character) |
| 482 | `_check_prevent_default` | KeyPressHandler | EXISTS (_check_prevent_default) |
| 499 | `_handle_key_press` | KeyPressHandler | EXISTS (_handle_key_press) |
| 698 | `_handle_enter` | KeyPressHandler | EXISTS (_handle_enter) |
| 760 | `_handle_escape` | KeyPressHandler | EXISTS (_handle_escape) |

### Display Control (4 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 641 | `_update_display` | DisplayController | EXISTS (update_display) |
| 688 | `pause_rendering` | DisplayController | EXISTS (pause_rendering) |
| 693 | `resume_rendering` | DisplayController | EXISTS (resume_rendering) |
| - | `_force_render` | DisplayController | NEW (not in original) |

### Status View Navigation (2 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 784 | `_handle_status_view_previous` | CommandModeHandler | EXISTS (handle_status_view_previous) |
| 828 | `_handle_status_view_next` | CommandModeHandler | EXISTS (handle_status_view_next) |

### Paste Processing (10 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 896 | `_expand_paste_placeholders` | PasteProcessor | EXISTS (expand_paste_placeholders) |
| 939 | `_create_paste_placeholder` | PasteProcessor | EXISTS (create_paste_placeholder) |
| 960 | `_update_paste_placeholder` | PasteProcessor | EXISTS (update_paste_placeholder) |
| 969 | `_simple_paste_detection` | PasteProcessor | EXISTS (simple_paste_detection) |
| 1009 | `_flush_paste_buffer_as_keystrokes_sync` | PasteProcessor | EXISTS (_flush_paste_buffer_as_keystrokes_sync) |
| 1020 | `_process_simple_paste_sync` | PasteProcessor | EXISTS (_process_simple_paste_sync) |
| 1059 | `_flush_paste_buffer_as_keystrokes` | PasteProcessor | EXISTS (flush_paste_buffer_as_keystrokes) |
| 1063 | `_process_simple_paste` | PasteProcessor | EXISTS (process_simple_paste) |
| - | `start_new_paste` | PasteProcessor | NEW (helper) |
| - | `append_to_current_paste` | PasteProcessor | NEW (helper) |
| - | `should_merge_paste` | PasteProcessor | NEW (helper) |

### Hook Registration (9 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 1070 | `_register_command_menu_render_hook` | HookRegistrar | EXISTS |
| 1122 | `_register_modal_trigger_hook` | HookRegistrar | EXISTS |
| 1143 | `_register_status_modal_trigger_hook` | HookRegistrar | EXISTS |
| 1164 | `_register_live_modal_trigger_hook` | HookRegistrar | EXISTS |
| 1218 | `_register_status_modal_render_hook` | HookRegistrar | EXISTS |
| 1239 | `_register_command_output_display_hook` | HookRegistrar | EXISTS |
| 1269 | `_register_pause_rendering_hook` | HookRegistrar | EXISTS |
| 1290 | `_register_resume_rendering_hook` | HookRegistrar | EXISTS |
| 1329 | `_register_modal_hide_hook` | HookRegistrar | EXISTS |

### Hook Handlers (8 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 1093 | `_handle_command_menu_render` | HookRegistrar | MISSING (uses callback) |
| 1311 | `_handle_pause_rendering` | HookRegistrar | MISSING (uses callback) |
| 1319 | `_handle_resume_rendering` | HookRegistrar | MISSING (uses callback) |
| 1350 | `_handle_modal_hide` | ModalController | EXISTS (_handle_modal_hide) |
| 1387 | `_handle_command_output_display` | HookRegistrar | MISSING (uses callback) |
| 1444 | `_handle_modal_trigger` | ModalController | EXISTS (_handle_modal_trigger) |
| 1185 | `_handle_live_modal_trigger` | ModalController | EXISTS (_handle_live_modal_trigger) |
| 2309 | `_handle_status_modal_trigger` | ModalController | EXISTS (_handle_status_modal_trigger) |
| 2563 | `_handle_status_modal_render` | ModalController | EXISTS (_handle_status_modal_render) |

### Command Mode (12 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 1520 | `_enter_command_mode` | CommandModeHandler | EXISTS (enter_command_mode) |
| 1553 | `_exit_command_mode` | CommandModeHandler | EXISTS (exit_command_mode) |
| 1588 | `_handle_command_mode_keypress` | CommandModeHandler | EXISTS (handle_command_mode_keypress) |
| 1618 | `_handle_command_mode_input` | CommandModeHandler | EXISTS (handle_command_mode_input) |
| 1646 | `_handle_menu_popup_input` | CommandModeHandler | EXISTS (handle_menu_popup_input) |
| 1682 | `_handle_menu_popup_keypress` | CommandModeHandler | EXISTS (handle_menu_popup_keypress) |
| 1732 | `_handle_status_takeover_input` | CommandModeHandler | EXISTS (handle_status_takeover_input) |
| 1749 | `_handle_status_takeover_keypress` | CommandModeHandler | EXISTS (handle_status_takeover_keypress) |
| 2128 | `_navigate_menu` | CommandModeHandler | EXISTS (_navigate_menu) |
| 2166 | `_update_command_filter` | CommandModeHandler | EXISTS (_update_command_filter) |
| 2204 | `_execute_selected_command` | CommandModeHandler | EXISTS (_execute_selected_command) |
| 2254 | `_get_available_commands` | CommandModeHandler | EXISTS (_get_available_commands) |
| 2277 | `_filter_commands` | CommandModeHandler | EXISTS (_filter_commands) |

### Regular Modal (10 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 1766 | `_handle_modal_keypress` | ModalController | EXISTS (_handle_modal_keypress) |
| 1909 | `_show_modal_from_result` | ModalController | EXISTS (_show_modal_from_result) |
| 1918 | `_enter_modal_mode` | ModalController | EXISTS (_enter_modal_mode) |
| 1953 | `_refresh_modal_display` | ModalController | EXISTS (_refresh_modal_display) |
| 1991 | `_has_pending_modal_changes` | ModalController | EXISTS (_has_pending_modal_changes) |
| 2003 | `_show_save_confirmation` | ModalController | EXISTS (_show_save_confirmation) |
| 2010 | `_handle_save_confirmation` | ModalController | EXISTS (_handle_save_confirmation) |
| 2036 | `_save_and_exit_modal` | ModalController | EXISTS (_save_and_exit_modal) |
| 2058 | `_exit_modal_mode` | ModalController | EXISTS (_exit_modal_mode) |
| 2082 | `_exit_modal_mode_minimal` | ModalController | EXISTS (_exit_modal_mode_minimal) |

### Status Modal (5 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 2335 | `_enter_status_modal_mode` | ModalController | EXISTS (_enter_status_modal_mode) |
| 2355 | `_handle_status_modal_keypress` | ModalController | EXISTS (_handle_status_modal_keypress) |
| 2390 | `_handle_status_modal_input` | ModalController | EXISTS (_handle_status_modal_input) |
| 2408 | `_exit_status_modal_mode` | ModalController | EXISTS (_exit_status_modal_mode) |

### Live Modal (4 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 2427 | `enter_live_modal_mode` | ModalController | EXISTS (enter_live_modal_mode) |
| 2485 | `_handle_live_modal_keypress` | ModalController | EXISTS (_handle_live_modal_keypress) |
| 2518 | `_handle_live_modal_input` | ModalController | EXISTS (_handle_live_modal_input) |
| 2538 | `_exit_live_modal_mode` | ModalController | EXISTS (_exit_live_modal_mode) |

### Status Modal Rendering (2 methods)
| Line | Method | Target Component | Status |
|------|--------|------------------|--------|
| 2594 | `_generate_status_modal_lines` | StatusModalRenderer | EXISTS (generate_status_modal_lines) |
| 2726 | `_create_simple_bordered_content` | StatusModalRenderer | EXISTS (_create_simple_bordered_content) |

---

## Component Method Summary

### StatusModalRenderer (status_modal_renderer.py) - 184 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `generate_status_modal_lines` | `_generate_status_modal_lines` (line 2594) |
| `_create_simple_bordered_content` | `_create_simple_bordered_content` (line 2726) |

### PasteProcessor (paste_processor.py) - 320 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `paste_bucket` (property) | NEW |
| `current_paste_id` (property) | NEW |
| `last_paste_time` (property) | NEW |
| `expand_paste_placeholders` | `_expand_paste_placeholders` (line 896) |
| `create_paste_placeholder` | `_create_paste_placeholder` (line 939) |
| `update_paste_placeholder` | `_update_paste_placeholder` (line 960) |
| `simple_paste_detection` | `_simple_paste_detection` (line 969) |
| `_flush_paste_buffer_as_keystrokes_sync` | `_flush_paste_buffer_as_keystrokes_sync` (line 1009) |
| `_process_simple_paste_sync` | `_process_simple_paste_sync` (line 1020) |
| `flush_paste_buffer_as_keystrokes` | `_flush_paste_buffer_as_keystrokes` (line 1059) |
| `process_simple_paste` | `_process_simple_paste` (line 1063) |
| `start_new_paste` | NEW (helper) |
| `append_to_current_paste` | NEW (helper) |
| `should_merge_paste` | NEW (helper) |

### DisplayController (display_controller.py) - 128 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `update_display` | `_update_display` (line 641) |
| `_force_render` | NEW (extracted from update_display) |
| `pause_rendering` | `pause_rendering` (line 688) |
| `resume_rendering` | `resume_rendering` (line 693) |
| `last_cursor_pos` (property) | NEW |

### KeyPressHandler (key_press_handler.py) - 498 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `set_callbacks` | NEW |
| `command_mode` (property) | NEW |
| `process_character` | `_process_character` (line 385) |
| `is_escape_sequence` (nested) | `is_escape_sequence` (line 197) |
| `delayed_escape_check` (nested) | `delayed_escape_check` (line 427) |
| `_check_prevent_default` | `_check_prevent_default` (line 482) |
| `_handle_key_press` | `_handle_key_press` (line 499) |
| `_handle_enter` | `_handle_enter` (line 698) |
| `_handle_escape` | `_handle_escape` (line 760) |

### CommandModeHandler (command_mode_handler.py) - 596 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `set_update_display_callback` | NEW |
| `set_exit_modal_callback` | NEW |
| `enter_command_mode` | `_enter_command_mode` (line 1520) |
| `exit_command_mode` | `_exit_command_mode` (line 1553) |
| `handle_command_mode_keypress` | `_handle_command_mode_keypress` (line 1588) |
| `handle_command_mode_input` | `_handle_command_mode_input` (line 1618) |
| `handle_menu_popup_input` | `_handle_menu_popup_input` (line 1646) |
| `handle_menu_popup_keypress` | `_handle_menu_popup_keypress` (line 1682) |
| `handle_status_takeover_input` | `_handle_status_takeover_input` (line 1732) |
| `handle_status_takeover_keypress` | `_handle_status_takeover_keypress` (line 1749) |
| `handle_status_view_previous` | `_handle_status_view_previous` (line 784) |
| `handle_status_view_next` | `_handle_status_view_next` (line 828) |
| `_navigate_menu` | `_navigate_menu` (line 2128) |
| `_update_command_filter` | `_update_command_filter` (line 2166) |
| `_execute_selected_command` | `_execute_selected_command` (line 2204) |
| `_get_available_commands` | `_get_available_commands` (line 2254) |
| `_filter_commands` | `_filter_commands` (line 2277) |

### ModalController (modal_controller.py) - 870 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `_handle_modal_trigger` | `_handle_modal_trigger` (line 1444) |
| `_handle_modal_hide` | `_handle_modal_hide` (line 1350) |
| `_handle_modal_keypress` | `_handle_modal_keypress` (line 1766) |
| `_handle_live_modal_trigger` | `_handle_live_modal_trigger` (line 1185) |
| `_handle_live_modal_keypress` | `_handle_live_modal_keypress` (line 2485) |
| `_handle_live_modal_input` | `_handle_live_modal_input` (line 2518) |
| `enter_live_modal_mode` | `enter_live_modal_mode` (line 2427) |
| `_exit_live_modal_mode` | `_exit_live_modal_mode` (line 2538) |
| `_handle_status_modal_trigger` | `_handle_status_modal_trigger` (line 2309) |
| `_enter_status_modal_mode` | `_enter_status_modal_mode` (line 2335) |
| `_handle_status_modal_keypress` | `_handle_status_modal_keypress` (line 2355) |
| `_handle_status_modal_input` | `_handle_status_modal_input` (line 2390) |
| `_exit_status_modal_mode` | `_exit_status_modal_mode` (line 2408) |
| `_handle_status_modal_render` | `_handle_status_modal_render` (line 2563) |
| `_generate_status_modal_lines` | DELEGATES to StatusModalRenderer |
| `_show_modal_from_result` | `_show_modal_from_result` (line 1909) |
| `_enter_modal_mode` | `_enter_modal_mode` (line 1918) |
| `_refresh_modal_display` | `_refresh_modal_display` (line 1953) |
| `_has_pending_modal_changes` | `_has_pending_modal_changes` (line 1991) |
| `_show_save_confirmation` | `_show_save_confirmation` (line 2003) |
| `_handle_save_confirmation` | `_handle_save_confirmation` (line 2010) |
| `_save_and_exit_modal` | `_save_and_exit_modal` (line 2036) |
| `_exit_modal_mode` | `_exit_modal_mode` (line 2058) |
| `_exit_modal_mode_minimal` | `_exit_modal_mode_minimal` (line 2082) |

### HookRegistrar (hook_registrar.py) - 286 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `register_all_hooks` | NEW (orchestrates all registrations) |
| `unregister_all_hooks` | NEW |
| `_register_command_menu_render_hook` | `_register_command_menu_render_hook` (line 1070) |
| `_register_modal_trigger_hook` | `_register_modal_trigger_hook` (line 1122) |
| `_register_status_modal_trigger_hook` | `_register_status_modal_trigger_hook` (line 1143) |
| `_register_live_modal_trigger_hook` | `_register_live_modal_trigger_hook` (line 1164) |
| `_register_status_modal_render_hook` | `_register_status_modal_render_hook` (line 1218) |
| `_register_command_output_display_hook` | `_register_command_output_display_hook` (line 1239) |
| `_register_pause_rendering_hook` | `_register_pause_rendering_hook` (line 1269) |
| `_register_resume_rendering_hook` | `_register_resume_rendering_hook` (line 1290) |
| `_register_modal_hide_hook` | `_register_modal_hide_hook` (line 1329) |

### InputLoopManager (input_loop_manager.py) - 397 lines
| Method | Maps to Original |
|--------|------------------|
| `__init__` | NEW |
| `set_callbacks` | NEW |
| `set_buffer_manager` | NEW |
| `start` | `start` (line 123) |
| `stop` | `stop` (line 171) |
| `_input_loop` | `_input_loop` (line 181) |
| `cleanup` | `cleanup` (line 880) |
| `_check_input_available` | `_check_input_available` (line 296) |
| `_read_input_chunk` | `_read_input_chunk` (line 309) |
| `_read_windows_input` | NEW (extracted from _read_input_chunk) |
| `_read_unix_input` | NEW (extracted from _read_input_chunk) |
| `_is_escape_sequence` | `is_escape_sequence` (line 197, nested) |
| `_route_escape_key` | NEW (extracted from _input_loop) |
| `_handle_paste_chunk` | NEW (extracted from _input_loop) |

---

## Coverage Analysis

### Extracted (have component equivalent): 69 methods
- KeyPressHandler: 7 methods
- DisplayController: 3 methods
- PasteProcessor: 8 methods
- CommandModeHandler: 15 methods
- ModalController: 22 methods
- HookRegistrar: 9 registration methods
- StatusModalRenderer: 2 methods
- InputLoopManager: 6 methods (NEW)

### Remain in InputHandler (facade): 2 methods
| Method | Reason |
|--------|--------|
| `__init__` | Facade - stays in InputHandler |
| `get_status` | Facade - stays in InputHandler |

### Hook Handlers Using Callbacks: 3 methods
These exist in original but HookRegistrar uses callbacks instead:
| Original Method | HookRegistrar Pattern |
|-----------------|----------------------|
| `_handle_command_menu_render` | Callback injection |
| `_handle_pause_rendering` | Callback injection |
| `_handle_resume_rendering` | Callback injection |
| `_handle_command_output_display` | Callback injection |

---

## Final Tally

| Category | Count |
|----------|-------|
| Original methods | 79 |
| Mapped to components | 69 |
| Remain in facade | 2 (__init__, get_status) |
| Handled via callbacks | 4 |
| New helper methods in components | ~20 |

## InputLoopManager (CREATED 2025-12-27)

The following methods are now in `input_loop_manager.py` (397 lines):

| Method | Description |
|--------|-------------|
| `start` | Enter raw mode, register hooks, start loop |
| `stop` | Stop loop, cleanup, exit raw mode |
| `_input_loop` | Main loop with paste detection and routing |
| `cleanup` | Clear errors, reset parser state |
| `_check_input_available` | Cross-platform input checking |
| `_read_input_chunk` | Cross-platform chunk reading |
| `_read_windows_input` | Windows-specific input (NEW) |
| `_read_unix_input` | Unix-specific input (NEW) |
| `_is_escape_sequence` | Escape sequence detection (extracted) |
| `_route_escape_key` | Route ESC to correct handler (NEW) |
| `_handle_paste_chunk` | Paste chunk processing (NEW) |

Includes `WIN_KEY_MAP` constant for Windows extended key mapping.

Unit tests: 15 tests in `tests/unit/test_input_loop_manager.py`

---

## Recommendations

1. **Verify callback handlers** - Ensure HookRegistrar callbacks match original behavior
2. **Integration testing** - Wire components to InputHandler and test
3. **Remove duplicates** - After integration, delete code from InputHandler

## Files Reference

```
core/io/input_handler.py          2,752 lines (original, unchanged)
core/io/input/
  __init__.py                        26 lines
  status_modal_renderer.py          184 lines
  paste_processor.py                320 lines
  display_controller.py             128 lines
  key_press_handler.py              498 lines
  command_mode_handler.py           596 lines
  modal_controller.py               870 lines
  hook_registrar.py                 286 lines
  input_loop_manager.py             397 lines (NEW)
  ----------------------------------------
  Total extracted:                3,305 lines
```

---

## Bugs Fixed (2025-12-27)

### KeyPressHandler - CRITICAL FIX

**Issue:** `_handle_enter` was missing renderer cleanup calls that exist in original

**Original (input_handler.py lines 732-734):**
```python
self.renderer.input_buffer = ""
self.renderer.clear_active_area()
```

**Fix Applied:**
1. Added `renderer` parameter to KeyPressHandler.__init__
2. Added missing lines in `_handle_enter` after adding to history
3. Now properly clears input box after Enter is pressed

**Impact:** Without this fix, the input box would NOT be cleared after pressing Enter

### CommandModeHandler - CRITICAL FIX

**Issue:** `handle_command_mode_keypress` was missing branches for MODAL, STATUS_MODAL, LIVE_MODAL modes

**Original (input_handler.py lines 1598-1611):**
- MENU_POPUP -> _handle_menu_popup_keypress
- STATUS_TAKEOVER -> _handle_status_takeover_keypress
- MODAL -> _handle_modal_keypress
- STATUS_MODAL -> _handle_status_modal_keypress
- LIVE_MODAL -> _handle_live_modal_keypress

**Fix Applied:**
1. Added `set_modal_callbacks()` method for modal handler delegation
2. Added MODAL, STATUS_MODAL, LIVE_MODAL branches to `handle_command_mode_keypress`
3. Added STATUS_MODAL, LIVE_MODAL branches to `handle_command_mode_input`
4. Modal handling now delegates to ModalController via callbacks

**Impact:** Without this fix, modal modes would be treated as "unknown" and exit immediately

### Verification

All 59 component unit tests pass:
- test_input_loop_manager.py: 15 tests PASSED
- test_display_controller.py: 15 tests PASSED
- test_paste_processor.py: 22 tests PASSED
- test_status_modal_renderer.py: 7 tests PASSED
