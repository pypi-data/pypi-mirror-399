# Resume/Branch Message Display Flow

This document traces the complete code path from when a user selects a session to resume (or branch) in the modal, through to the actual terminal output.

## Overview

```
Modal Selection -> Plugin Handler -> Message Coordinator -> Terminal Output
```

## Detailed Flow

### 1. Modal Selection (Enter Key)

**File:** `core/io/input/modal_controller.py:260-289`

```python
_handle_modal_keypress()
    |
    +-- was_command_selected() -> True
    +-- get_selected_command() -> {"action": "resume_session", "session_id": "xxx"}
    +-- _exit_modal_mode_minimal()  # clears modal without rendering input
    +-- emit_with_hooks(MODAL_COMMAND_SELECTED, context)
```

The modal controller detects Enter key, gets the selected command, exits the modal, and emits an event for plugins to handle.

### 2. Plugin Handles Selection

**File:** `plugins/resume_conversation_plugin.py:1252-1262`

```python
handle_modal_command_selected()
    |
    +-- action == "resume_session"
    +-- conversation_manager.load_session(session_id)  # loads from .jsonl
    +-- _prepare_session_display() -> returns display_messages list
    +-- data["display_messages"] = display_messages
```

The plugin loads the session from storage and prepares a list of messages to display:

```python
display_messages = [
    ("system", "--- Resumed session: xxx ---", {}),
    ("user", "first user message", {}),
    ("assistant", "first assistant reply", {}),
    ("user", "second user message", {}),
    # ... more messages ...
    ("system", "[ok] Resumed: xxx. Continue below.", {})
]
```

### 3. Modal Controller Displays Messages

**File:** `core/io/input/modal_controller.py:284-288`

```python
if final_data.get("display_messages"):
    renderer.message_coordinator.display_message_sequence(display_messages)
```

### 4. Message Coordinator Queues and Displays

**File:** `core/io/message_coordinator.py:114-137`

```python
display_message_sequence(messages)
    |
    +-- queue_message() for each message
    +-- display_queued_messages()
```

**File:** `core/io/message_coordinator.py:74-112`

```python
display_queued_messages()
    |
    +-- writing_messages = True        # block render loop
    +-- clear_active_area()            # clear input box area
    +-- for each message:
    |       _display_single_message()
    +-- finally:
            writing_messages = False   # unblock render loop
            input_line_written = False # reset render state
            last_line_count = 0
            invalidate_render_cache()
```

### 5. Single Message Display

**File:** `core/io/message_coordinator.py:139-173`

```python
_display_single_message(message_type, content, kwargs)
    |
    +-- if "system":
    |       conversation_renderer.write_message(SYSTEM, DIMMED)
    +-- if "user":
    |       conversation_renderer.write_message(USER, GRADIENT)
    +-- if "assistant":
            conversation_renderer.write_message(ASSISTANT, GRADIENT)
```

### 6. Conversation Renderer Formats

**File:** `core/io/message_renderer.py:272-294`

```python
ConversationRenderer.write_message(content, message_type, format_style)
    |
    +-- buffer.add_message()           # store in buffer
    +-- _display_message_immediately() # render to terminal
```

### 7. Terminal Output

**File:** `core/io/message_renderer.py:342-408`

```python
_display_message_immediately(content, message_type, format_style)
    |
    +-- Determine symbol:
    |       user     -> ">"  (dim yellow)
    |       assistant -> "∴" (cyan)
    |       system   -> none
    +-- format_message() -> apply gradient colors
    +-- exit_raw_mode() temporarily
    +-- print(formatted_content, flush=True)  # <-- ACTUAL OUTPUT
    +-- print("")  # blank line separator
    +-- enter_raw_mode() restore
```

## Key Files Summary

| File | Responsibility |
|------|----------------|
| `core/io/input/modal_controller.py` | Handles modal Enter key, emits event |
| `plugins/resume_conversation_plugin.py` | Loads session, prepares display_messages |
| `core/io/message_coordinator.py` | Atomic message sequencing, render state |
| `core/io/message_renderer.py` | Formatting, symbols, terminal output |
| `core/llm/conversation_manager.py` | Session storage loading |

## Message Types and Formatting

| Type | Symbol | Format | Use |
|------|--------|--------|-----|
| system | none | DIMMED | Headers, status messages |
| user | `>` | GRADIENT | User input from history |
| assistant | `∴` | GRADIENT | LLM responses from history |

## Branch Flow Differences

The branch flow is nearly identical, with these differences:

1. **Action:** `branch_execute` instead of `resume_session`
2. **Load Method:** `conversation_manager.branch_session(session_id, index)` instead of `load_session()`
3. **Header:** `"--- Branched from {session_id} at message {index} ---"`

Branch creates a new session with copied messages up to the branch point, assigns new UUIDs, and saves as a new session file.

## Render State Management

The message coordinator carefully manages render state to prevent duplicate input boxes:

```python
# Before display
writing_messages = True      # Blocks render loop from drawing input

# After display (in finally block)
writing_messages = False     # Unblocks render loop
input_line_written = False   # Forces fresh input render
last_line_count = 0          # Resets line tracking
invalidate_render_cache()    # Clears stale content
```

This ensures clean handoff back to the normal render loop after displaying resumed messages.
