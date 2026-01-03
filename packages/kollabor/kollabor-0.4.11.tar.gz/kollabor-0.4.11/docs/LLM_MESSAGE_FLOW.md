# LLM Service Message Display Flow

This document traces the complete code path from when a user sends a message through the LLM service to the actual terminal output.

## Comparison with Resume Flow

Both flows use the **same final display mechanism**: `message_coordinator.display_message_sequence()`. The difference is in how messages are sourced:

| Aspect | Resume Flow | LLM Flow |
|--------|-------------|----------|
| Source | File storage (.jsonl) | API response |
| Trigger | /resume command | User input + Enter |
| Messages | Historical (all at once) | Real-time (as generated) |
| Display | Batch display | Atomic display after processing |

## Overview

```
User Input -> Event Bus -> LLM Service -> API Call -> Response -> Display
```

## Detailed Flow

### 1. User Submits Input (Enter Key)

**File:** `core/io/input/key_press_handler.py:410-468`

```python
_handle_enter()
    |
    +-- message = buffer_manager.get_content_and_clear()
    +-- renderer.clear_active_area()
    +-- event_bus.emit_with_hooks(EventType.USER_INPUT, {"message": message})
```

### 2. LLM Service Receives Input

**File:** `core/llm/llm_service.py:890-906`

```python
_handle_user_input(data, event)  # Registered hook for USER_INPUT
    |
    +-- message = data.get("message")
    +-- process_user_input(message)
```

### 3. Process User Input

**File:** `core/llm/llm_service.py:855-888`

```python
process_user_input(message)
    |
    +-- message_display.display_user_message(message)  # Show user input
    +-- conversation_logger.log_user_message(message)  # Persist
    +-- _enqueue_with_overflow_strategy(message)       # Queue for processing
    +-- create_background_task(_process_queue())       # Start processing
```

### 4. Display User Message

**File:** `core/llm/message_display_service.py:98-111`

```python
display_user_message(message)
    |
    +-- message_sequence = [("user", message, {})]
    +-- message_coordinator.display_message_sequence(message_sequence)
```

### 5. Process Message Batch

**File:** `core/llm/llm_service.py:1001-1077`

```python
_process_message_batch(messages)
    |
    +-- _add_conversation_message(user_message)
    +-- renderer.update_thinking(True, "Processing...")  # Start animation
    +-- response = await _call_llm()                     # API call
    +-- renderer.update_thinking(False)                  # Stop animation
    +-- parsed_response = response_parser.parse_response(response)
    +-- tool_results = await tool_executor.execute_all_tools(tools)
    +-- message_display.display_complete_response(...)   # Display all
```

### 6. Display Complete Response (Atomic)

**File:** `core/llm/message_display_service.py:376-441`

```python
display_complete_response(thinking_duration, response, tool_results)
    |
    +-- message_sequence = []
    +-- if thinking_duration > threshold:
    |       message_sequence.append(("system", "Thought for X seconds", {}))
    +-- if response.strip():
    |       message_sequence.append(("assistant", response, {}))
    +-- for each tool_result:
    |       message_sequence.append(("system", formatted_tool_output, {}))
    +-- message_coordinator.display_message_sequence(message_sequence)
```

### 7. Message Coordinator (Same as Resume)

**File:** `core/io/message_coordinator.py:74-137`

```python
display_message_sequence(messages)
    |
    +-- queue_message() for each
    +-- display_queued_messages()
         |
         +-- writing_messages = True
         +-- clear_active_area()
         +-- for each: _display_single_message()
         +-- writing_messages = False
         +-- reset render state
```

### 8. Single Message Display (Same as Resume)

**File:** `core/io/message_coordinator.py:139-173`

```python
_display_single_message(message_type, content, kwargs)
    |
    +-- system    -> write_message(SYSTEM, DIMMED)
    +-- user      -> write_user_message()
    +-- assistant -> write_message(ASSISTANT, GRADIENT)
    +-- error     -> write_message(ERROR, HIGHLIGHTED)
```

### 9. Terminal Output (Same as Resume)

**File:** `core/io/message_renderer.py:342-408`

```python
_display_message_immediately(content, message_type, format_style)
    |
    +-- Add symbol: ">" for user, "∴" for assistant
    +-- format_message() with gradient colors
    +-- exit_raw_mode() temporarily
    +-- print(formatted_content, flush=True)  # <-- ACTUAL OUTPUT
    +-- print("")  # blank line
    +-- enter_raw_mode() restore
```

## Key Files Summary

| File | Responsibility |
|------|----------------|
| `core/io/input/key_press_handler.py` | Captures Enter, emits USER_INPUT event |
| `core/llm/llm_service.py` | Orchestrates LLM processing |
| `core/llm/message_display_service.py` | Formats and coordinates display |
| `core/io/message_coordinator.py` | Atomic message sequencing |
| `core/io/message_renderer.py` | Formatting, symbols, terminal output |

## Message Assembly

The LLM response is assembled into a message sequence like this:

```python
message_sequence = [
    ("system", "Thought for 2.3 seconds", {}),     # If thinking > 0.1s
    ("assistant", "Here's my response...", {}),    # LLM response
    ("system", "⏺ terminal(ls -la)\n✓ Done", {}),  # Tool result 1
    ("system", "⏺ file_read(README.md)\n...", {}), # Tool result 2
]
```

## Thinking Animation

During API processing, a thinking animation runs:

```python
renderer.update_thinking(True, "Processing...")   # Start
# ... API call happens ...
renderer.update_thinking(False)                   # Stop
```

This is separate from message display and uses the status area.

## Differences from Resume

| Step | Resume | LLM Service |
|------|--------|-------------|
| Source | `conversation_manager.load_session()` | `api_service.call_llm()` |
| User msg | Already in history | Displayed before processing |
| Thinking | Not applicable | Animated during API call |
| Tools | Not applicable | Executed and results displayed |
| Display | All messages at once | After each processing cycle |

## Shared Infrastructure

Both flows converge at the same point:

```
message_coordinator.display_message_sequence()
         |
         v
    Same code path from here
         |
         v
    print(formatted_content)
```

This ensures consistent formatting, symbols, and terminal state management regardless of message source.
