# Duplicate Input Box Issue - Structured Problem Analysis

## Executive Summary

After resuming a session via `/resume` command, users experience duplicate input boxes
when typing the first character. This creates a degraded user experience and indicates
a fundamental issue in the terminal render state management system.

---

## Problem Statement

**What:** Two input boxes appear on screen instead of one after resume
**When:** Upon typing the first character after session resume
**Where:** Terminal UI render pipeline
**Impact:** Poor UX, visual confusion, potential data entry issues

---

## Issue Tree

```
Why does duplicate input box appear after resume?
│
├─ 1. Two separate renders are occurring
│   ├─ 1.1 Render loop (application.py) renders input box
│   ├─ 1.2 Force render (input_handler.py) renders input box
│   └─ 1.3 Both happen before clearing occurs
│
├─ 2. Single render occurs but clearing fails
│   ├─ 2.1 input_line_written flag is incorrect
│   ├─ 2.2 last_line_count has wrong value
│   ├─ 2.3 Cursor position is wrong when clearing
│   └─ 2.4 ANSI escape sequences not working
│
├─ 3. State is corrupted between renders
│   ├─ 3.1 Race condition between async components
│   ├─ 3.2 State reset happens at wrong time
│   └─ 3.3 Multiple components modifying same state
│
└─ 4. Something else is writing to terminal
    ├─ 4.1 Message display writes after render
    ├─ 4.2 Plugin writes to stdout directly
    └─ 4.3 Logging writes to terminal
```

---

## Hypothesis Matrix

| # | Hypothesis | Test Method | Status |
|---|------------|-------------|--------|
| H1 | Both render loop AND force_render are creating input boxes | Add logging to both paths | NOT TESTED |
| H2 | input_line_written is True when it should be False | Log value at render time | NOT TESTED |
| H3 | last_line_count has stale value causing wrong clearing | Log value at render time | NOT TESTED |
| H4 | Cursor position shifted during message display | Log cursor position | NOT TESTED |
| H5 | Cache comparison failing, causing extra renders | Log cache hits/misses | NOT TESTED |
| H6 | Race condition: render loop runs during force_render | Add mutex/lock logging | NOT TESTED |

---

## Data Gathering Requirements

### Critical Questions to Answer

1. **How many times is _render_lines() called** between resume and first keypress?
   - Expected: 1 (from force_render)
   - If > 1: Multiple render sources problem

2. **What are the state values at each _render_lines() call?**
   - input_line_written: ?
   - last_line_count: ?
   - _last_render_content length: ?

3. **Is clearing code executed?**
   - Does `if self.input_line_written and hasattr(self, "last_line_count")` evaluate True?
   - How many lines are cleared?

4. **What is cursor position** at each stage?
   - After message display
   - Before first render
   - Before second render (if any)

---

## Proposed Diagnostic Instrumentation

Add targeted logging to capture state at critical points:

```python
# In terminal_renderer._render_lines() at start:
logger.info(f"[RENDER] _render_lines called: "
            f"input_line_written={self.input_line_written}, "
            f"last_line_count={getattr(self, 'last_line_count', 'N/A')}, "
            f"cache_len={len(self._last_render_content)}, "
            f"new_lines_len={len(lines)}")

# In terminal_renderer._render_lines() at clearing section:
logger.info(f"[RENDER] Clearing: will_clear={self.input_line_written and hasattr(self, 'last_line_count')}")

# In application.py render loop:
logger.info(f"[RENDER_LOOP] About to call render_active_area")

# In input_handler._update_display():
logger.info(f"[INPUT] _update_display called, force_render={force_render}")
```

---

## Component Flow Analysis

### Current Flow (Expected)

```
1. User selects session in modal
2. _exit_modal_mode_minimal() called
3. display_message_sequence() displays messages
4. display_message_sequence() resets state:
   - input_line_written = False
   - last_line_count = 0
   - invalidate_render_cache()
5. force_render=True triggers render_active_area()
6. _render_lines() called:
   - input_line_written=False → NO clearing
   - Writes input box at cursor
   - Sets input_line_written=True, last_line_count=X
7. User types 'd'
8. Buffer updated
9. Render (loop or keypress) calls _render_lines():
   - input_line_written=True → CLEARS X lines
   - Writes input box with 'd'
10. Single input box displayed ✓
```

### Actual Flow (Broken)

```
1-4. Same as above
5. force_render=True triggers render_active_area()
6. _render_lines() renders input box (placeholder)
7. ??? SOMETHING ELSE renders ANOTHER input box ???
8. User types 'd'
9. Second input box rendered with 'd'
10. Two input boxes displayed ✗

KEY QUESTION: What is step 7?
```

---

## Prioritized Investigation Plan

### Phase 1: Instrument & Observe (30 min)

1. Add logging to _render_lines() entry point
2. Add logging to render_active_area() entry point
3. Add logging to _update_display()
4. Run /resume, type one character
5. Analyze logs to count render calls

### Phase 2: Isolate the Source (30 min)

Based on Phase 1 findings:
- If 2+ renders: Identify which paths are calling
- If 1 render: Check clearing logic execution
- If clearing fails: Check state values

### Phase 3: Root Cause & Fix (1 hr)

Once source identified:
- Design targeted fix
- Implement
- Test
- Verify no regressions

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Fix breaks other render scenarios | Medium | High | Test all modal/command flows |
| Fix introduces new race conditions | Medium | Medium | Add state assertions |
| Root cause is deeper architectural issue | Low | High | May need larger refactor |

---

## Success Criteria

1. Single input box after resume + first keypress
2. No visual glitches during session resume
3. All other modal commands (/branch, /save, etc.) still work
4. Render performance not degraded

---

## Next Actions

1. [ ] Add diagnostic logging per instrumentation plan
2. [ ] Reproduce issue and capture logs
3. [ ] Analyze logs to identify duplicate render source
4. [ ] Update hypothesis matrix with findings
5. [ ] Design targeted fix based on root cause
6. [ ] Implement and test fix
