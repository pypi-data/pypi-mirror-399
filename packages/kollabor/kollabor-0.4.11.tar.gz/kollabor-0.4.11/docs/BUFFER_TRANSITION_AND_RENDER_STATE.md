
# Buffer Transition and Render State Documentation

## Overview

The buffer transition and render state system provides comprehensive management of terminal input buffers, message display coordination, and rendering state transitions. This system prevents race conditions, manages buffer state during mode transitions (modal, fullscreen, etc.), and ensures clean rendering without visual artifacts.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
   - BufferManager, Message Rendering System, TerminalState
   - MessageDisplayCoordinator, InputHandler Facade, TerminalRenderer
   - LayoutManager, ModalState, Plugin Render Integration
3. [Conversation Persistence System](#conversation-persistence-system)
   - KollaborConversationLogger (real-time JSONL)
   - ConversationManager (session JSON)
   - Persistence Flow Diagram
4. [State Transitions](#state-transitions)
   - Normal Conversation Flow
   - Modal Open/Close Flow
   - Fullscreen Plugin Flow
   - Resize Flow
   - Message Display Flow
5. [Buffer Management](#buffer-management)
6. [Render State Management](#render-state-management)
7. [Coordination Patterns](#coordination-patterns)
8. [Streaming and Coordinator Interaction](#streaming-and-coordinator-interaction)
   - Architecture Overview (Dual Pathways)
   - Why Streaming Bypasses the Coordinator
   - How the Pathways Coexist
   - Potential Conflicts and Mitigations
9. [Plugin Render Resolution](#plugin-render-resolution)
   - Resolution Mechanism (First-Match-Wins)
   - Priority Values
   - Yielding to Another Plugin
   - Debugging Plugin Conflicts
   - Cooperative Plugin Patterns
10. [Testing Strategies](#testing-strategies)
    - Mocking Terminal State
    - Testing BufferManager
    - Testing MessageDisplayCoordinator
    - Testing Resize Handling
    - Integration Testing
11. [API Reference](#api-reference)
12. [Best Practices](#best-practices)
13. [Error Handling and Recovery](#error-handling-and-recovery)
14. [Future Enhancements](#future-enhancements)
15. [References](#references)

---

## Architecture Overview

The buffer transition and render state system consists of two main subsystems that work together:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              RENDERING SUBSYSTEM                            │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        TerminalRenderer                                │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌────────────────┐  │ │
│  │  │MessageDisplayCoord. │  │    TerminalState    │  │  LayoutManager │  │ │
│  │  │ - Atomic sequences  │  │ - Mode (RAW/NORMAL) │  │ - Areas        │  │ │
│  │  │ - State management  │  │ - Resize handling   │  │ - Layout       │  │ │
│  │  └─────────────────────┘  └─────────────────────┘  └────────────────┘  │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                      │ │
│  │  │   MessageRenderer   │  │  ThinkingAnimation  │                      │ │
│  │  │ - ConversationBuffer│  │ - Spinner frames    │                      │ │
│  │  │ - MessageFormatter  │  │ - Elapsed time      │                      │ │
│  │  └─────────────────────┘  └─────────────────────┘                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                               INPUT SUBSYSTEM                               │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                     InputHandler (Facade)                              │ │
│  │                                                                        │ │
│  │  ┌─────────────────────┐    ┌─────────────────────────────────────┐    │ │
│  │  │    BufferManager    │    │     core/io/input/ components       │    │ │
│  │  │  - Input buffer     │    │  ┌───────────┐  ┌───────────────┐   │    │ │
│  │  │  - Cursor position  │    │  │DisplayCtrl│  │KeyPressHandler│   │    │ │
│  │  │  - Command history  │    │  │ModalCtrl  │  │CommandModeHdlr│   │    │ │
│  │  └─────────────────────┘    │  │PasteProc  │  │InputLoopMgr   │   │    │ │
│  │                             │  └───────────┘  └───────────────┘   │    │ │
│  │                             └─────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘

Interaction:
  InputHandler.DisplayController ──update_display()──► TerminalRenderer
  InputHandler.BufferManager ◄──get input_buffer──── TerminalRenderer
```

### Key Design Principles

1. **Atomic Operations**: Message displays happen atomically to prevent interference
2. **State Preservation**: Buffer state is preserved during transitions
3. **Render Optimization**: Caching prevents unnecessary terminal writes
4. **Debounced Resize**: Terminal resize events are debounced to prevent flickering
5. **Unified Coordination**: All terminal state changes go through the coordinator

---

## Core Components

### 1. BufferManager

**Location**: `core/io/buffer_manager.py`

**Purpose**: Manages the user input buffer with comprehensive editing capabilities.

**Key Features**:
- Character insertion/deletion with cursor tracking
- Command history navigation (up/down arrows)
- Input validation (dangerous pattern detection)
- Buffer size limits
- Paste handling with line break normalization

**State Variables**:
```python
_buffer: str                    # Current buffer content
_cursor_pos: int                 # Cursor position (0 to len(_buffer))
_history: List[str]              # Command history
_history_index: int              # Current history navigation position
_temp_buffer: str                # Temporary buffer for history nav
_buffer_limit: int               # Maximum characters (default: 1000)
_history_limit: int              # Max history entries (default: 100)
```

**Key Methods**:
- `insert_char(char)` - Insert character at cursor position
- `delete_char()` - Delete character before cursor (backspace)
- `delete_forward()` - Delete character after cursor (delete key)
- `move_cursor(direction)` - Move cursor left/right
- `navigate_history(direction)` - Navigate command history
- `get_display_info()` - Get (buffer_content, cursor_position) tuple
- `validate_content()` - Validate buffer content for dangerous patterns
- `handle_paste(content)` - Handle pasted content with proper line break handling

**Example Usage**:
```python
from core.io.buffer_manager import BufferManager

buffer_mgr = BufferManager(buffer_limit=1000, history_limit=100)

# Insert characters
buffer_mgr.insert_char('H')
buffer_mgr.insert_char('e')
buffer_mgr.insert_char('l')
buffer_mgr.insert_char('l')
buffer_mgr.insert_char('o')

# Get display info
content, cursor_pos = buffer_mgr.get_display_info()
# content = "Hello", cursor_pos = 5

# Add to history
buffer_mgr.add_to_history("Hello")

# Navigate history
buffer_mgr.navigate_history("up")  # Go to previous command
buffer_mgr.navigate_history("down")  # Go to next command
```

---

### 2. Message Rendering System

**Location**: `core/io/message_renderer.py`

**Purpose**: Provides conversation message storage, formatting, and display through a layered architecture.

**Class Hierarchy**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         message_renderer.py                             │
│                                                                         │
│  ┌──────────────────────┐                                               │
│  │  ConversationMessage │  ← Pure data model (dataclass)                │
│  │  - content           │                                               │
│  │  - message_type      │                                               │
│  │  - format_style      │                                               │
│  │  - timestamp         │                                               │
│  │  - metadata          │                                               │
│  └──────────────────────┘                                               │
│            ↑ creates                                                    │
│  ┌──────────────────────┐     ┌──────────────────────┐                  │
│  │  ConversationBuffer  │     │   MessageFormatter   │                  │
│  │  (Data Store)        │     │   (Formatting Logic) │                  │
│  │  - messages: deque   │     │   - format_message() │                  │
│  │  - add_message()     │     │   - _format_gradient │                  │
│  │  - get_recent()      │     │   - _format_dimmed   │                  │
│  └──────────────────────┘     └──────────────────────┘                  │
│            ↑ owns                      ↑ owns                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    ConversationRenderer                         │    │
│  │  (Storage + Display - tightly coupled)                          │    │
│  │  - buffer: ConversationBuffer                                   │    │
│  │  - formatter: MessageFormatter                                  │    │
│  │  - terminal_state: TerminalState                                │    │
│  │  - write_message() → stores AND displays                        │    │
│  │  - render_conversation_history() → reads from buffer            │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│            ↑ owns                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      MessageRenderer                            │    │
│  │  (Facade for backward compatibility)                            │    │
│  │  - conversation_renderer: ConversationRenderer                  │    │
│  │  - write_message() → delegates                                  │    │
│  │  - write_streaming_chunk() → manages streaming state            │    │
│  │  - get_conversation_buffer() → exposes inner buffer             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Design Pattern**: The architecture follows a modified **Model-View pattern** where:
- **Model**: `ConversationBuffer` (data store) + `ConversationMessage` (data model)
- **View**: `MessageFormatter` (formatting) + display methods in `ConversationRenderer`
- **Coupling**: `ConversationRenderer` violates single responsibility by combining storage and display in `write_message()`

**Why This Matters**: When you call `write_message()`, it performs TWO operations:
1. Adds the message to the buffer (storage)
2. Displays the message immediately to terminal (display)

This means the buffer always contains what was displayed, but you cannot store without displaying (unless using `ConversationBuffer.add_message()` directly).

#### 2a. ConversationBuffer (Data Store)

**Role**: Pure data storage - a bounded deque of `ConversationMessage` objects.

**IMPORTANT: No Disk Persistence**: `ConversationBuffer` is purely in-memory. It does NOT save to disk. For disk persistence, see [Conversation Persistence System](#conversation-persistence-system) below.

**State Variables**:
```python
messages: deque[ConversationMessage]  # Message history (maxlen=1000)
_message_counter: int                   # Total messages added
max_messages: int                       # Maximum messages to keep
```

**Pruning Strategy**: FIFO (First In, First Out)

Python's `deque(maxlen=N)` automatically discards the **oldest** elements when new items are appended to a full deque. There is no LRU, priority-based, or "important message" preservation in this buffer.

```python
# Internal behavior when buffer is full:
self.messages.append(new_message)  # Oldest message silently dropped
```

**No Important Message Preservation**: All messages are treated equally. System prompts, errors, and user messages all follow the same FIFO eviction. If you need to preserve certain messages, you must manage this externally.

**Message Types**:
```python
MessageType.USER       # User input messages
MessageType.ASSISTANT  # AI assistant responses
MessageType.SYSTEM     # System messages (thoughts, status)
MessageType.ERROR      # Error messages
MessageType.INFO       # Informational messages
MessageType.DEBUG      # Debug messages
```

**Key Methods**:
- `add_message(content, message_type, format_style, **metadata)` - Add message (storage only)
- `get_recent_messages(count)` - Get N most recent messages
- `get_messages_by_type(message_type)` - Get all messages of specific type
- `clear()` - Clear all messages
- `get_stats()` - Get buffer statistics

#### 2b. MessageFormatter (Formatting Logic)

**Role**: Pure formatting - transforms `ConversationMessage` into display strings.

**Format Styles**:
```python
MessageFormat.PLAIN       # No formatting
MessageFormat.GRADIENT    # Color gradient via VisualEffects
MessageFormat.HIGHLIGHTED # ANSI colors based on message type
MessageFormat.DIMMED      # Dim gray text
```

**Key Method**:
- `format_message(message: ConversationMessage) -> str` - Apply format style

#### 2c. ConversationRenderer (Storage + Display)

**Role**: Combines storage and display operations. This is the main working class.

**Key Methods**:
- `write_message(content, message_type, format_style, immediate_display=True)` - Store AND display
- `write_user_message(content)` - Convenience for user messages
- `write_system_message(content)` - Convenience for system messages
- `render_conversation_history(count)` - Get formatted lines from buffer

**Important**: `immediate_display=True` by default, so every `write_message()` call displays to terminal.

#### 2d. MessageRenderer (Facade)

**Role**: Backward-compatible facade that wraps `ConversationRenderer` and adds streaming support.

**Key Methods**:
- `write_message(content, apply_gradient)` - Simplified API
- `write_streaming_chunk(chunk)` - Real-time streaming display
- `finish_streaming_message()` - End streaming mode
- `get_conversation_buffer()` - Access underlying buffer

**Example Usage**:
```python
from core.io.message_renderer import (
    ConversationBuffer, ConversationRenderer, MessageRenderer,
    MessageType, MessageFormat
)

# Direct buffer access (storage only, no display)
buffer = ConversationBuffer(max_messages=1000)
buffer.add_message("Hello", MessageType.USER, MessageFormat.PLAIN)

# ConversationRenderer (storage + display)
renderer = ConversationRenderer(terminal_state, visual_effects)
renderer.write_message("Hello", MessageType.USER)  # Stores AND displays

# MessageRenderer facade (recommended for most uses)
msg_renderer = MessageRenderer(terminal_state, visual_effects)
msg_renderer.write_message("Hello", apply_gradient=True)

# Access buffer through facade
buffer = msg_renderer.get_conversation_buffer()
recent = buffer.get_recent_messages(5)
```

---

### 3. TerminalState

**Location**: `core/io/terminal_state.py`

**Purpose**: Manages terminal state, mode switching, capability detection, and cross-platform terminal control.

**Key Features**:
- Terminal mode management (NORMAL, RAW, COOKED)
- Cursor visibility and position tracking
- Terminal capability detection (color, size, mouse support)
- Resize handling with debouncing
- Cross-platform support (Unix/Windows)

**State Variables**:
```python
current_mode: TerminalMode           # Current terminal mode
is_terminal: bool                     # Is this a TTY terminal?
capabilities: TerminalCapabilities    # Detected terminal capabilities
_cursor_hidden: bool                  # Is cursor currently hidden?
_last_size: tuple[int, int]          # Last known terminal size
_resize_occurred: bool                # Resize flag (debounced)
_last_resize_time: float             # Last resize signal timestamp
_resize_debounce_delay: float         # Wait time for resize to settle (0.9s)
```

**Terminal Modes**:
```python
TerminalMode.NORMAL   # Normal cooked mode (line-buffered input)
TerminalMode.RAW      # Raw mode (character-by-character input)
TerminalMode.COOKED   # Cooked mode (same as NORMAL, alternate naming)
```

**Key Methods**:
- `enter_raw_mode()` - Enter raw terminal mode
- `exit_raw_mode()` - Exit raw mode, restore normal settings
- `write_raw(text)` - Write text directly to terminal
- `hide_cursor()` / `show_cursor()` - Cursor visibility control
- `clear_line()` - Clear current line
- `move_cursor_up/down/lines(n)` - Cursor movement
- `save_cursor_position()` / `restore_cursor_position()` - Cursor position save/restore
- `check_and_clear_resize_flag()` - Check if resize occurred and settled (debounced)
- `update_size()` - Update terminal size information
- `get_size()` - Get current terminal size (width, height)
- `supports_color(color_type)` - Check color support
- `get_status()` - Get terminal state status dictionary
- `cleanup()` - Cleanup and restore all terminal settings

**Resize Handling**:
The system uses a debounced approach to handle terminal resize:

1. **Signal Reception**: SIGWINCH signal is caught (Unix) or size is polled (Windows)
2. **Debouncing**: 0.9 second wait period allows multiple resize events to settle
3. **Settlement Detection**: `check_and_clear_resize_flag()` returns True only after debounce period
4. **Size Update**: Terminal size is polled and updated after resize settles

**Example Usage**:
```python
from core.io.terminal_state import TerminalState, TerminalMode

term_state = TerminalState()

# Enter raw mode for character-by-character input
term_state.enter_raw_mode()

# Check terminal capabilities
caps = term_state.capabilities
print(f"Color level: {caps.color_level}")  # "truecolor", "256color", "basic", "monochrome"
print(f"Size: {caps.width}x{caps.height}")

# Handle resize
if term_state.check_and_clear_resize_flag():
    # Resize has settled - update layout
    term_state.update_size()
    width, height = term_state.get_size()

# Cleanup
term_state.cleanup()  # Restore original terminal settings
```

---

### 4. MessageDisplayCoordinator

**Location**: `core/io/message_coordinator.py`

**Purpose**: Coordinates message display AND render state to prevent interference between different message writing systems.

**Key Features**:
- Atomic message sequences (all messages display together)
- Unified state management (prevents clearing conflicts)
- Proper ordering (system messages before responses)
- Protection from interference (no race conditions)
- Buffer transition management (modal open/close state preservation)

**State Variables**:
```python
message_queue: List[Tuple[str, str, Dict]]  # Queued messages
is_displaying: bool                         # Atomic display flag
_saved_main_buffer_state: Optional[Dict[str, Any]]  # Captured render state during buffer transitions
_in_alternate_buffer: bool                   # Alternate buffer mode flag
```

**State Management**: The coordinator uses a **hybrid** approach:
1. **Flag-based blocking**: `writing_messages = True` blocks the render loop during transitions
2. **State capture**: `_saved_main_buffer_state` captures render state when entering alternate buffer
3. **Flexible restoration**: `exit_alternate_buffer(restore_state=True)` restores captured state, or `exit_alternate_buffer()` (default) resets to clean state

This is distinct from `ModalOverlayRenderer.ModalState` (see [ModalState](#8-modalstate)) which captures terminal-level state (cursor position, visibility, terminal size).

**Key Methods**:
- `queue_message(message_type, content, **kwargs)` - Queue message for display
- `display_single_message(message_type, content, **kwargs)` - Display single message immediately
- `display_queued_messages()` - Display all queued messages atomically
- `display_message_sequence(messages)` - Display sequence of messages atomically
- `clear_queue()` - Clear queued messages without displaying
- `enter_alternate_buffer()` - Enter alternate buffer mode, capture state
- `exit_alternate_buffer(restore_state=False)` - Exit alternate buffer mode
- `get_saved_state()` - Get captured state (for debugging)
- `get_queue_status()` - Get queue status for debugging

**Message Display Flow**:

```
queue_message() → queue_message() → display_queued_messages()
     ↓                 ↓                     ↓
  [Queue A]        [Queue B]           [Atomic Display]
                                         ↓
                              Enter atomic mode
                                         ↓
                           Clear active area once
                                         ↓
                      Display all messages in sequence
                                         ↓
                           Exit atomic mode
                                         ↓
                      Reset render state flags
```

**Buffer Transition Management**:

When entering modal or fullscreen mode:
1. Call `enter_alternate_buffer()` to mark mode transition
2. System sets `writing_messages = True` to prevent render loop interference
3. Modal/fullscreen code manages its own display lifecycle
4. On exit, use one of two patterns (see "Modal Exit Patterns" below)

**Modal Exit Patterns**:

There are TWO exit patterns depending on what happens after the modal closes:

| Pattern | Method | Use When |
|---------|--------|----------|
| **Normal Exit** | `_exit_modal_mode()` | Modal closes and render loop resumes normally |
| **Minimal Exit** | `_exit_modal_mode_minimal()` | Command will display messages after modal closes |

**Normal Exit** (`_exit_modal_mode()`):
- Resets `writing_messages = False` immediately
- Calls `_update_display()` to render input box
- Use for simple modals with no follow-up display

**Minimal Exit** (`_exit_modal_mode_minimal()`):
- KEEPS `writing_messages = True` (blocks render loop)
- Sets `input_line_written = True` for proper clearing
- Does NOT call `_update_display()`
- The command's `display_message_sequence()` will reset flags when done

```python
# In modal_controller.py, these actions use minimal exit:
minimal_actions = ["resume_session", "branch_select_session", "branch_execute"]

# Why minimal exit exists:
# When a command (like /branch) displays messages after modal closes,
# the normal exit causes a race condition:
#   1. _exit_modal_mode() sets writing_messages=False
#   2. Render loop immediately runs, draws input box
#   3. Command's display_message_sequence() runs, draws input box again
#   4. Result: DUPLICATE INPUT BOX
#
# Minimal exit prevents this by keeping writing_messages=True until
# display_message_sequence() completes.
```

**Adding Minimal Exit to New Commands**:

If your slash command displays messages after modal selection:

```python
# In your command definition:
command = {
    "action": "my_custom_action",
    "exit_mode": "minimal",  # <-- Add this
    # ... other fields
}

# OR add your action to minimal_actions list in modal_controller.py:
minimal_actions = ["resume_session", "branch_select_session", "branch_execute", "my_custom_action"]
```

**State Capture and Restoration**:

The coordinator captures render state when entering alternate buffer mode:
```python
_saved_main_buffer_state = {
    "writing_messages": bool,      # Was render loop blocked?
    "input_line_written": bool,    # Was input line rendered?
    "last_line_count": int,        # Line count for clearing
    "conversation_active": bool,   # Was conversation in progress?
    "thinking_active": bool,       # Was thinking animation running?
}
```

**Exiting Alternate Buffer Mode**:

Use `exit_alternate_buffer()` to cleanly exit alternate buffer mode:

**Pattern 1: Reset to clean state** (default - recommended for most cases):
```python
# After modal closes, reset to clean state for fresh input rendering
coordinator.exit_alternate_buffer()
# Equivalent to: writing_messages=False, input_line_written=False, last_line_count=0
# This prevents duplicate input boxes when render loop resumes
```

**Pattern 2: Restore previous state** (for nested transitions):
```python
# Restore the exact state captured when entering alternate buffer
coordinator.exit_alternate_buffer(restore_state=True)
# Useful when you want to resume exactly where you left off
```

**Pattern 3: Let display_queued_messages() handle it** (for message display flows):
```python
# display_queued_messages() automatically resets flags in its finally block
coordinator.display_message_sequence([
    ("system", "Modal closed"),
    ("assistant", "Here's the result...")
])
# Flags are now reset: writing_messages=False, input_line_written=False, last_line_count=0
```

**Pattern 4: Minimal exit** (for commands displaying their own content):
```python
# See "Modal Exit Patterns" above - use _exit_modal_mode_minimal()
await self._exit_modal_mode_minimal()
# Then your command displays messages (this will reset flags when done)
self.renderer.message_coordinator.display_message_sequence(messages)
```

**Debugging saved state**:
```python
# Check what state was captured (for debugging)
saved = coordinator.get_saved_state()
if saved:
    print(f"Captured state: {saved}")
```

**Example Usage**:
```python
from core.io.message_coordinator import MessageDisplayCoordinator

coordinator = MessageDisplayCoordinator(terminal_renderer)

# Queue multiple messages
coordinator.queue_message("system", "Thought for 2.1 seconds")
coordinator.queue_message("assistant", "Here's your answer...")

# Display them atomically
coordinator.display_queued_messages()

# Or display a sequence directly
coordinator.display_message_sequence([
    ("system", "Thought for 2.1 seconds", {}),
    ("assistant", "Here's your answer...", {})
])

# Display single message
coordinator.display_single_message("error", "Something went wrong")

# Get queue status
status = coordinator.get_queue_status()
# status = {
#     "queue_length": 0,
#     "is_displaying": False,
#     "queued_types": []
# }
```

---

### 5. InputHandler Facade and Components

**Location**: `core/io/input_handler.py` (facade) + `core/io/input/*.py` (components)

**Purpose**: The InputHandler is a **facade** that coordinates 8 modular components for input handling. This was refactored from a monolithic class into specialized components.

**Architecture**:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        InputHandler (Facade)                            │
│                      core/io/input_handler.py                           │
│                                                                         │
│  Coordinates:                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   core/io/input/ components                     │    │
│  │                                                                 │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │    │
│  │  │ InputLoopManager │  │ KeyPressHandler  │  │ PasteProcessor│  │    │
│  │  │ - Main I/O loop  │  │ - Key processing │  │ - Paste detect│  │    │
│  │  │ - Platform I/O   │  │ - Enter/Escape   │  │ - Placeholders│  │    │
│  │  └──────────────────┘  └──────────────────┘  └───────────────┘  │    │
│  │                                                                 │    │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │    │
│  │  │CommandModeHandler│  │ ModalController  │  │ HookRegistrar │  │    │
│  │  │ - Slash commands │  │ - All modal types│  │ - Event hooks │  │    │
│  │  │ - Menu handling  │  │ - Modal lifecycle│  │ - Registration│  │    │
│  │  └──────────────────┘  └──────────────────┘  └───────────────┘  │    │
│  │                                                                 │    │
│  │  ┌──────────────────┐  ┌──────────────────┐                     │    │
│  │  │DisplayController │  │StatusModalRender │                     │    │
│  │  │ - Display update │  │ - Status modal   │                     │    │
│  │  │ - Pause/resume   │  │ - Line generation│                     │    │
│  │  └──────────────────┘  └──────────────────┘                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  Also owns:                                                             │
│  - BufferManager (core/io/buffer_manager.py)                            │
│  - KeyParser (core/io/key_parser.py)                                    │
│  - SlashCommandParser, Registry, Executor (core/commands/)              │
│  - InputErrorHandler (core/io/input_errors.py)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Component Creation Order** (from `_create_components()`):

```python
# Phase 1: Foundation components
self._status_modal_renderer = StatusModalRenderer(renderer)
self._display_controller = DisplayController(renderer, buffer_manager, error_handler)
self._paste_processor = PasteProcessor(buffer_manager, display_controller.update_display)

# Phase 2: Core processing
self._input_loop_manager = InputLoopManager(renderer, key_parser, error_handler, paste_processor, config)

# Phase 3: Command/Modal components
self._key_press_handler = KeyPressHandler(buffer_manager, key_parser, event_bus, ...)
self._command_mode_handler = CommandModeHandler(buffer_manager, renderer, event_bus, ...)
self._modal_controller = ModalController(renderer, event_bus, config, ...)

# Phase 4: Hook system
self._hook_registrar = HookRegistrar(event_bus, ...)
```

#### 5a. DisplayController

**Location**: `core/io/input/display_controller.py`

**Role**: Thin wrapper that manages rendering state and delegates to TerminalRenderer.

**Key Features**:
- Display updates from buffer changes
- Rendering pause/resume for special effects (Matrix, etc.)
- Cursor position tracking

**State Variables**:
```python
rendering_paused: bool     # Is rendering paused?
_last_cursor_pos: int      # Last cursor position
```

**Key Methods**:
- `update_display(force_render=False)` - Update terminal display with current buffer state
- `pause_rendering()` - Pause all UI rendering for special effects
- `resume_rendering()` - Resume normal UI rendering
- `last_cursor_pos` property - Get/set last cursor position

**How It's Used**:

DisplayController is injected into other components that need to trigger display updates:

```python
# PasteProcessor uses it for display after paste
self._paste_processor = PasteProcessor(
    self.buffer_manager,
    self._display_controller.update_display  # Callback injection
)

# CommandModeHandler uses it for menu updates
self._command_mode_handler.set_update_display_callback(
    self._display_controller.update_display
)

# ModalController uses it after modal close
self._modal_controller = ModalController(
    ...,
    self._display_controller.update_display,  # Callback injection
    ...
)
```

**Example Usage**:
```python
from core.io.input.display_controller import DisplayController

display_controller = DisplayController(
    renderer=terminal_renderer,
    buffer_manager=buffer_manager,
    error_handler=error_handler
)

# Update display
await display_controller.update_display()

# Force immediate render (e.g., after paste)
await display_controller.update_display(force_render=True)

# Pause for special effect
display_controller.pause_rendering()
# ... perform special effect ...
display_controller.resume_rendering()
```

---

### 6. TerminalRenderer

**Location**: `core/io/terminal_renderer.py`

**Purpose**: Advanced terminal renderer with modular architecture.

**Key Features**:
- Modular visual effects system
- Advanced layout management
- Comprehensive status rendering
- Message formatting and display
- Render caching optimization
- Resize handling with aggressive clearing

**State Variables**:
```python
terminal_state: TerminalState                # Terminal state manager
visual_effects: VisualEffects                # Visual effects system
layout_manager: LayoutManager                # Layout manager
message_renderer: MessageRenderer            # Message renderer
thinking_animation: ThinkingAnimationManager # Thinking animation
message_coordinator: MessageDisplayCoordinator  # Message coordinator

# Interface properties
input_buffer: str                            # Current input buffer content
cursor_position: int                         # Cursor position
status_areas: Dict[str, List[str]]           # Status area contents (A, B, C)
thinking_active: bool                        # Thinking animation state

# State management
conversation_active: bool                     # Is conversation active?
writing_messages: bool                       # Are we writing messages?
input_line_written: bool                     # Has input line been written?
last_line_count: int                         # Number of lines last rendered
active_area_start_position: bool             # Track active area start

# Render optimization
_last_render_content: List[str]              # Cache of last rendered content
_render_cache_enabled: bool                  # Enable/disable render caching
```

**Key Methods**:
- `enter_raw_mode()` / `exit_raw_mode()` - Terminal mode management
- `write_message(message, apply_gradient)` - Write message to conversation
- `write_streaming_chunk(chunk)` - Write streaming chunk immediately
- `write_user_message(message)` - Write user message
- `write_hook_message(content, **metadata)` - Write hook message via coordinator
- `update_thinking(active, message)` - Update thinking animation
- `set_thinking_effect(effect)` - Set thinking text effect
- `configure_shimmer(speed, wave_width)` - Configure shimmer effect
- `configure_thinking_limit(limit)` - Configure thinking message limit
- `render_active_area()` - Render active input/status area
- `clear_active_area()` - Clear active area before writing messages
- `invalidate_render_cache()` - Invalidate cache to force re-render
- `set_render_cache_enabled(enabled)` - Enable/disable render caching
- `get_render_cache_status()` - Get render cache status for debugging

**Render Flow**:

```
render_active_area()
    ↓
Check modal state (skip if modal active)
    ↓
Check writing_messages flag (skip unless enhanced input)
    ↓
Update terminal size (check resize with debouncing)
    ↓
Generate render lines:
    - Safety buffer line
    - Thinking animation (if active)
    - Input area (or enhanced input from plugins)
    - Status area (or command menu, or status modal)
    ↓
_render_lines(lines, size_changed)
    ↓
Check render cache (skip if unchanged)
    ↓
Clear previous active area
    ↓
Write new lines (buffered to reduce flicker)
    ↓
Hide cursor
    ↓
Flush buffered writes
```

**Resize Handling**:

When terminal resize occurs:

1. **Size Change Detection**: `check_and_clear_resize_flag()` returns True after debounce
2. **Aggressive Clearing**: If width reduced by 10%+, use aggressive clearing
3. **Cursor Restoration**: Restore to saved cursor position (`\033[u`)
4. **Clear to End**: Clear from cursor to end of screen (`\033[J`)
5. **Small Reduction**: If width reduced less than 10%, just invalidate cache
6. **Size Increase**: Invalidate cache, no clearing needed

**Example Usage**:
```python
from core.io.terminal_renderer import TerminalRenderer

renderer = TerminalRenderer(event_bus=event_bus, config=config)

# Enter raw mode
renderer.enter_raw_mode()

# Write messages
renderer.write_message("Hello, world!", apply_gradient=True)
renderer.write_user_message("User input here")

# Update thinking animation
renderer.update_thinking(True, "Processing your request...")
# ... do work ...
renderer.update_thinking(False)

# Configure effects
renderer.set_thinking_effect("shimmer")
renderer.configure_shimmer(speed=2, wave_width=10)
renderer.configure_thinking_limit(5)

# Render active area
await renderer.render_active_area()

# Clear active area before writing messages
renderer.clear_active_area()

# Force cache invalidation
renderer.invalidate_render_cache()

# Configure render caching
renderer.set_render_cache_enabled(True)
cache_status = renderer.get_render_cache_status()

# Exit raw mode
renderer.exit_raw_mode()
```

---

### 7. LayoutManager

**Location**: `core/io/layout.py`

**Purpose**: Manages terminal layout with multiple areas and adaptive sizing.

**Key Features**:
- Multiple layout areas (status_a, status_b, status_c, input, thinking)
- Adaptive layout based on terminal size
- Area visibility control
- Priority-based layout
- Alignment options (LEFT, CENTER, RIGHT, JUSTIFY)

**State Variables**:
```python
_areas: Dict[str, LayoutArea]  # All layout areas
terminal_width: int             # Terminal width
terminal_height: int            # Terminal height
_dirty: bool                    # Layout dirty flag
_last_render_lines: int         # Last number of lines rendered
```

**Layout Areas**:
- `status_a`: Status area A (left column in horizontal layout)
- `status_b`: Status area B (center column in horizontal layout)
- `status_c`: Status area C (right column in horizontal layout)
- `input`: Input area
- `thinking`: Thinking animation area

**Layout Modes**:
```python
LayoutMode.HORIZONTAL    # Side-by-side areas
LayoutMode.VERTICAL      # Stacked areas
LayoutMode.STACKED       # Overlapping areas
LayoutMode.ADAPTIVE      # Adaptive based on content (default)
```

**Key Methods**:
- `set_terminal_size(width, height)` - Update terminal dimensions
- `add_area(name, area)` - Add a layout area
- `get_area(name)` - Get layout area by name
- `update_area_content(name, content)` - Update content for area
- `set_area_visibility(name, visible)` - Set area visibility
- `calculate_layout(mode)` - Calculate layout regions
- `render_areas(regions)` - Render areas into display lines
- `get_render_info()` - Get layout rendering information

**Example Usage**:
```python
from core.io.layout import LayoutManager, LayoutArea, AreaAlignment

layout_mgr = LayoutManager(terminal_width=80, terminal_height=24)

# Update area content
layout_mgr.update_area_content("status_a", ["Status A: OK"])
layout_mgr.update_area_content("input", ["> Hello, world"])

# Set area visibility
layout_mgr.set_area_visibility("thinking", False)

# Calculate layout
regions = layout_mgr.calculate_layout(mode=LayoutMode.ADAPTIVE)

# Render areas
lines = layout_mgr.render_areas(regions)

# Get render info
info = layout_mgr.get_render_info()
```

---

### 8. ModalState

**Location**: `core/ui/modal_overlay_renderer.py`

**Purpose**: A `@dataclass` that captures terminal state for `ModalOverlayRenderer` modal operations. This is a **snapshot-based** approach, distinct from `MessageDisplayCoordinator`'s flag-based approach.

**State Variables**:
```python
@dataclass
class ModalState:
    cursor_position: Tuple[int, int]    # Saved cursor position (row, col)
    screen_lines: List[str]             # Saved screen content (currently not captured)
    cursor_visible: bool                 # Saved cursor visibility state
    terminal_size: Tuple[int, int]      # Saved terminal size (width, height)
```

**Used By**: `ModalOverlayRenderer` to save/restore terminal state when displaying modals.

**What Gets Captured** (current implementation):
- `cursor_visible`: Captured from `terminal_state._cursor_hidden`
- `terminal_size`: Captured from `terminal_state.get_size()`
- `cursor_position`: Placeholder `(0, 0)` - actual query not implemented
- `screen_lines`: Empty list - screen capture not implemented

**Note**: This is separate from `MessageDisplayCoordinator._saved_main_buffer_state`. The two serve different purposes:
- `ModalState`: For `ModalOverlayRenderer`'s overlay modals - captures terminal state
- `MessageDisplayCoordinator`: Uses flag-based coordination, no snapshot capture

---

### 9. Plugin Render Integration

**Location**: Plugin hooks registered for `EventType.INPUT_RENDER`

**Purpose**: Allows plugins to override or enhance the default input rendering with custom UI components (e.g., bordered input boxes, command menus).

**How It Works**:

The terminal renderer uses an event-driven architecture to allow plugins to inject custom rendering into the active area. During each render cycle, the renderer emits an `INPUT_RENDER` event and checks if any plugin provides enhanced input lines.

**Integration Flow**:

```
render_active_area()
    ↓
_render_input_area(lines)
    ↓
event_bus.emit_with_hooks(EventType.INPUT_RENDER, {...})
    ↓
[Plugin hooks execute in priority order]
    ↓
Check result["main"] for "fancy_input_lines"
    ↓ Found
    lines.extend(hook_result["fancy_input_lines"])
    return (skip default rendering)
    ↓ Not Found
    [Default input rendering with cursor]
```

**Plugin Hook Contract**:

Plugins that want to provide enhanced input rendering must:

1. **Register a hook** for `EventType.INPUT_RENDER`:
```python
from core.events import EventType, Hook, HookPriority

Hook(
    name="render_fancy_input",
    plugin_name=self.name,
    event_type=EventType.INPUT_RENDER,
    priority=HookPriority.DISPLAY.value,  # Priority 10
    callback=self._render_fancy_input
)
```

2. **Return `fancy_input_lines`** in the hook result:
```python
async def _render_fancy_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    # Access renderer state
    input_text = getattr(self.renderer, 'input_buffer', '')
    cursor_position = getattr(self.renderer, 'cursor_position', len(input_text))

    # Generate custom input lines (e.g., bordered box)
    fancy_lines = [
        "┌─────────────────────────────────┐",
        f"│ > {input_text}▌                │",
        "└─────────────────────────────────┘"
    ]

    # Return the lines in the expected format
    return {
        "status": "rendered",
        "fancy_input_lines": fancy_lines
    }
```

**Data Available to Plugins**:

| Source | Property | Description |
|--------|----------|-------------|
| `data` parameter | `input_buffer` | Current input text |
| `self.renderer` | `input_buffer` | Current input text |
| `self.renderer` | `cursor_position` | Cursor position in buffer |
| `self.renderer` | `thinking_active` | Whether thinking animation is active |
| `self.renderer` | `terminal_state.get_size()` | Terminal dimensions |

**Example: EnhancedInputPlugin**:

The `EnhancedInputPlugin` (`plugins/enhanced_input_plugin.py`) demonstrates the full pattern:

```python
class EnhancedInputPlugin:
    def __init__(self, name, state_manager, event_bus, renderer, config):
        self.renderer = renderer
        self.event_bus = event_bus

        # Initialize modular components
        self.box_renderer = BoxRenderer(...)
        self.cursor_manager = CursorManager(...)

        # Register the hook
        self.hooks = [
            Hook(
                name="render_fancy_input",
                plugin_name=self.name,
                event_type=EventType.INPUT_RENDER,
                priority=HookPriority.DISPLAY.value,
                callback=self._render_fancy_input
            )
        ]

    async def _render_fancy_input(self, data, event):
        if not self.config.enabled:
            return {"status": "disabled"}

        # Get input state from renderer
        input_text = getattr(self.renderer, 'input_buffer', '')
        cursor_position = getattr(self.renderer, 'cursor_position', len(input_text))

        # Insert cursor character at position
        text_with_cursor = self.cursor_manager.insert_cursor(
            input_text, cursor_position, cursor_char
        )

        # Render bordered box
        fancy_lines = self.box_renderer.render_box(
            content_lines=[f"> {text_with_cursor}"],
            box_width=calculated_width,
            style_name=current_style
        )

        # Return in expected format
        return {
            "status": "rendered",
            "fancy_input_lines": fancy_lines
        }
```

**Priority and Conflict Resolution**:

- Hooks execute in priority order (higher values first)
- `HookPriority.DISPLAY` (value=10) is the standard priority for UI rendering
- The **first** plugin to return `fancy_input_lines` wins - subsequent hooks are still called but their output is ignored for input rendering
- If no plugin provides `fancy_input_lines`, default rendering is used

**Writing Messages During Plugin Rendering**:

When `writing_messages = True`, the render loop normally skips rendering to prevent interference. However, the renderer makes an exception if a plugin provides enhanced input (like a command menu):

```python
# In render_active_area():
if self.writing_messages:
    # Check if any plugin wants to provide enhanced input
    has_enhanced_input = False
    result = await self.event_bus.emit_with_hooks(EventType.INPUT_RENDER, ...)
    if "fancy_input_lines" in result:
        has_enhanced_input = True

    # Only skip if no enhanced input available
    if not has_enhanced_input:
        return
```

This allows command menus and other interactive UI elements to render even during message processing.

---

## Conversation Persistence System

**IMPORTANT**: The `ConversationBuffer` in `core/io/message_renderer.py` is **purely in-memory** for display purposes. It does NOT persist to disk.

Actual conversation persistence is handled by two separate systems in `core/llm/`:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PERSISTENCE ARCHITECTURE                             │
│                                                                             │
│  ConversationBuffer (message_renderer.py)     ← IN-MEMORY ONLY (display)    │
│  └── NOT persisted to disk                                                  │
│                                                                             │
│  ════════════════════════════════════════════════════════════════════════   │
│                                                                             │
│  KollaborConversationLogger (conversation_logger.py)  ← REAL-TIME LOGGING   │
│  └── Writes JSONL immediately after each message                            │
│  └── Location: .kollabor-cli/conversations/{session_name}.jsonl             │
│  └── Also stores: conversation_memory/ (patterns, context, solutions)       │
│                                                                             │
│  ConversationManager (conversation_manager.py)        ← SESSION MANAGEMENT  │
│  └── Auto-saves every 10 messages (if save_conversations=True)              │
│  └── Manual save via save_conversation() or save_session()                  │
│  └── Location: .kollabor-cli/conversations/conversation_*.json              │
│  └── Used for: resume, branch, session switching                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### KollaborConversationLogger (Real-time Logging)

**Location**: `core/llm/conversation_logger.py`

**Purpose**: Logs every terminal interaction as structured JSON Lines (JSONL) for conversation history, intelligence features, and resume functionality.

**When Messages Are Saved**:
- **Immediately** after each message via `_append_to_jsonl()`
- No batching or delay - every message is written to disk as it occurs

**File Format**: JSONL (one JSON object per line)

**File Naming**: `{session_name}.jsonl`
- Old format: `session_{timestamp}.jsonl`
- New format: `{YYMMDDHHMM}-{memorable-name}.jsonl` (e.g., `2512111701-frost-blade.jsonl`)

**File Location**: `.kollabor-cli/conversations/`

**JSONL Structure**:

```jsonl
{"type": "conversation_metadata", "sessionId": "...", "startTime": "2025-12-11T17:01:00Z", ...}
{"type": "user", "message": {"role": "user", "content": "Hello"}, "uuid": "...", ...}
{"type": "assistant", "message": {"role": "assistant", "content": [...]}, "uuid": "...", ...}
{"type": "conversation_end", "sessionId": "...", "summary": {"total_messages": 10, ...}}
```

**Message Types in JSONL**:

| Type | Description | Key Fields |
|------|-------------|------------|
| `conversation_metadata` | Session start marker | sessionId, startTime, cwd, gitBranch |
| `user` | User input message | message.content, uuid, kollabor_intelligence |
| `assistant` | LLM response | message.content (array), usage stats |
| `system` | System messages | subtype, content, level |
| `conversation_end` | Session end marker | endTime, summary |

**Intelligence Features** (stored in `.kollabor-cli/conversation_memory/`):

```
conversation_memory/
├── user_patterns.json      # Learned user behavior patterns
├── project_context.json    # Files mentioned, technologies used
└── solution_history.json   # Successful solution patterns
```

### ConversationManager (Session Management)

**Location**: `core/llm/conversation_manager.py`

**Purpose**: Manages in-memory conversation state for LLM context windows, with periodic saves for session management.

**When Messages Are Saved**:
- **Auto-save**: Every 10 messages (if `save_conversations=True` in config)
- **Manual save**: `save_conversation()` or `save_session()`
- **On clear**: Before clearing conversation (if it has messages)

**File Format**: JSON (pretty-printed)

**File Naming**: `conversation_{session_id}_{timestamp}.json` or `session_{id}_{timestamp}.json`

**JSON Structure**:

```json
{
  "metadata": {
    "started_at": "2025-12-11T17:01:00",
    "message_count": 42,
    "turn_count": 21,
    "topics": ["debugging", "feature_development"]
  },
  "summary": {...},
  "messages": [
    {"uuid": "...", "role": "user", "content": "Hello", "timestamp": "...", ...}
  ]
}
```

**Key Configuration**:

```python
"core.llm.save_conversations": True   # Enable auto-save (default)
"core.llm.max_history": 50            # Context window size
```

**Context Window Pruning Strategy**: FIFO with System Message Preservation

Unlike `ConversationBuffer`, the `ConversationManager` has special logic to preserve the first system message:

```python
def _update_context_window(self):
    """Update the context window with recent messages."""
    # Simple sliding window - keep most recent N messages
    self.context_window = self.messages[-self.max_history:]

    # IMPORTANT: Ensure system message is preserved
    system_messages = [m for m in self.messages if m["role"] == "system"]
    if system_messages and system_messages[0] not in self.context_window:
        # Prepend system message even if it's older than the window
        self.context_window = [system_messages[0]] + self.context_window
```

**What This Means**:
- Regular user/assistant messages follow FIFO eviction
- The **first system message** (typically the system prompt) is always preserved
- Context window can exceed `max_history` by 1 when system message is prepended
- Only the FIRST system message gets this treatment - subsequent system messages are evicted normally

### Persistence Flow Diagram

```
[User sends message]
    │
    ├──► ConversationManager.add_message()
    │        │
    │        ├── Add to in-memory messages list
    │        ├── Update context window
    │        │
    │        ├── Log to KollaborConversationLogger (if available)
    │        │        │
    │        │        └── _append_to_jsonl() ──► IMMEDIATE DISK WRITE
    │        │                                   (.kollabor-cli/conversations/{session}.jsonl)
    │        │
    │        └── Every 10 messages: save_conversation()
    │                                   └── PERIODIC DISK WRITE
    │                                       (.kollabor-cli/conversations/conversation_*.json)
    │
    └──► ConversationRenderer.write_message() (separate system)
             │
             └── ConversationBuffer.add_message()
                      │
                      └── IN-MEMORY ONLY (for display)
```

### Resume and Session Management

The persistence system enables:

1. **Resume Conversation** (`/resume`): Lists and restores sessions from disk
2. **Branch Session**: Creates new session from a point in existing session
3. **Save Conversation** (`/save`): Exports to JSON, Markdown, or clipboard

---

## State Transitions

### Normal Conversation Flow

```
[Start]
    ↓
Enter RAW mode
    ↓
[Input Buffer Active]
    ↓
User types input (BufferManager updates)
    ↓
User presses Enter
    ↓
Enter Alternate Buffer Mode
    ↓
Queue system message ("Thinking...")
    ↓
Queue assistant message
    ↓
Display queued messages (atomic)
    ↓
Exit Alternate Buffer Mode
    ↓
[Return to Input]
```

### Modal Open/Close Flow

```
[Normal Input Mode]
    ↓
Trigger modal (e.g., slash command)
    ↓
Enter Alternate Buffer Mode
    ↓
Save terminal state (cursor, screen content)
    ↓
Clear active area
    ↓
Display modal overlay
    ↓
[Modal Active - Input routed to modal]
    ↓
User closes modal (Escape or action)
    ↓
Hide modal overlay
    ↓
Restore terminal state
    ↓
Exit Alternate Buffer Mode
    ↓
[Return to Normal Input Mode]
```

### Fullscreen Plugin Flow

Fullscreen plugins (e.g., Matrix rain effect) use a more complex flow that involves the fullscreen subsystem (`core/fullscreen/`):

```
                              FULLSCREEN PLUGIN ARCHITECTURE
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│  FullScreenManager                   FullScreenSession                    │
│  (core/fullscreen/manager.py)        (core/fullscreen/session.py)         │
│  ┌──────────────────────────┐        ┌──────────────────────────┐         │
│  │ - Plugin registry        │        │ - Session lifecycle      │         │
│  │ - launch_plugin()        │───────►│ - Render loop (60 fps)   │         │
│  │ - _enter_modal_mode()    │        │ - Input handling         │         │
│  │ - _exit_modal_mode()     │        │ - Stats tracking         │         │
│  └──────────────────────────┘        └──────────────────────────┘         │
│                                                     │                     │
│                                                     ▼                     │
│                                      FullScreenRenderer                   │
│                                      (core/fullscreen/renderer.py)        │
│                                      ┌───────────────────────────┐        │
│                                      │ - Alternate buffer mgmt   │        │
│                                      │ - Direct terminal output  │        │
│                                      │ - Terminal state snapshot │        │
│                                      └───────────────────────────┘        │
└───────────────────────────────────────────────────────────────────────────┘
```

**Entry Flow**:

```
[User triggers fullscreen plugin (e.g., /matrix)]
    ↓
FullScreenManager.launch_plugin(name)
    ↓
Check: Is another session already active?
    ↓ No (Yes = reject)
    ↓
_enter_modal_mode(plugin)
    ↓
Emit MODAL_TRIGGER event with {fullscreen_plugin: True}
    ↓
ModalController._handle_modal_trigger()
    ↓
    ├── Set terminal_renderer.writing_messages = True
    ├── message_coordinator.enter_alternate_buffer()  ← SET FLAGS (no state snapshot)
    ├── Set _fullscreen_session_active = True
    └── input_handler.pause_rendering()
    ↓
Create FullScreenSession(plugin, event_bus)
    ↓
session._initialize()
    ├── Register FULLSCREEN_INPUT hook (for input routing)
    ├── FullScreenRenderer.setup_terminal()
    │       ├── Save termios/console settings (TerminalSnapshot)
    │       ├── Write "\033[?1049h" (ENTER alternate screen buffer)
    │       ├── Hide cursor
    │       └── Clear screen
    ├── plugin.initialize(renderer)
    └── plugin.on_start()
    ↓
session._session_loop() at 60 FPS
    ├── _handle_input() → plugin.handle_input(key_press)
    ├── plugin.render_frame(delta_time)
    └── Frame rate limiting
    ↓
[Fullscreen Session Running]
```

**Exit Flow**:

```
[User presses Escape OR plugin requests exit]
    ↓
plugin.handle_input() returns True (exit requested)
    OR
plugin.render_frame() returns False (plugin done)
    ↓
session._session_loop() breaks
    ↓
session._cleanup()
    ├── plugin.on_stop()
    ├── FullScreenRenderer.restore_terminal()
    │       ├── Clear alternate screen
    │       ├── Write "\033[?1049l" (EXIT alternate screen buffer)
    │       │       └── This AUTOMATICALLY restores main screen content
    │       └── Restore termios/console settings
    ├── Unregister FULLSCREEN_INPUT hook
    └── plugin.cleanup()
    ↓
FullScreenManager._exit_modal_mode(plugin)
    ↓
Emit MODAL_HIDE event
    ↓
ModalController._handle_modal_hide()
    ├── Set writing_messages = False
    ├── Set input_line_written = False
    ├── Invalidate render cache
    ├── Set _fullscreen_session_active = False
    └── resume_rendering()
    ↓
[Return to Normal Input Mode - Main screen restored]
```

**Key Points**:

1. **Double Buffer Management**: Fullscreen uses BOTH the modal system's alternate buffer AND its own FullScreenRenderer alternate buffer
   - Modal system: Saves/restores `MessageDisplayCoordinator` state
   - FullScreenRenderer: Uses terminal's alternate screen buffer (`\033[?1049h/l`)

2. **Input Routing**: During fullscreen, input is routed via:
   - `_fullscreen_session_active` flag in ModalController
   - `FULLSCREEN_INPUT` event type for hook-based routing
   - Direct stdin reading as fallback

3. **State Preservation**:
   - `TerminalSnapshot` saves termios settings (Unix) or console mode (Windows)
   - Alternate screen buffer automatically preserves main screen
   - No need to manually save/restore screen content

4. **Integration with Modal System**: Fullscreen plugins emit `MODAL_TRIGGER`/`MODAL_HIDE` events to leverage the existing modal infrastructure for:
   - Pausing the main render loop
   - Coordinating with `MessageDisplayCoordinator`
   - Proper state restoration

### Resize Flow

```
[Normal Rendering]
    ↓
Terminal resize detected (SIGWINCH or poll)
    ↓
Set _last_resize_time (signal received)
    ↓
Check_and_clear_resize_flag() called
    ↓
Is resize settled? (debounce delay passed?)
    ↓ No
    ↓
Return False (still debouncing)
    ↓
[Continue normal rendering with old size]
    ↓
[Wait...]
    ↓
Check_and_clear_resize_flag() called again
    ↓
Is resize settled? (debounce delay passed?)
    ↓ Yes
    ↓
Update terminal size
    ↓
Invalidate render cache
    ↓
Did width reduce by 10%+?
    ↓ Yes → Use aggressive clearing (restore cursor, clear to end)
    ↓ No  → Just invalidate cache
    ↓
[Continue normal rendering with new size]
```

### Resize with Active Input

When the terminal width is reduced while the user is actively typing, the system prioritizes **data integrity over visual presentation**. The input buffer content is never truncated or lost.

**Key Principle**: `BufferManager` has no width awareness - it stores raw text up to `buffer_limit` (default: 1000 chars) regardless of terminal dimensions.

**What Happens on Width Reduction**:

```
[User typing in input box]
    ↓
Terminal width reduced (e.g., user drags window smaller)
    ↓
SIGWINCH signal received
    ↓
0.9s debounce period (multiple resize events settle)
    ↓
render_active_area() detects settled resize
    ↓
┌─────────────────────────────────────────────────────────────────┐
│ FRESH terminal width query: shutil.get_terminal_size().columns  │
│ GeometryCalculator.calculate_box_width() uses new width         │
│ TextProcessor.wrap_text(content, new_content_width)             │
└─────────────────────────────────────────────────────────────────┘
    ↓
Display adapts to new width
    ↓
[Buffer content PRESERVED, display WRAPPED/ADAPTED]
```

**Display Behavior by Renderer**:

| Renderer | Behavior | Data Loss |
|----------|----------|-----------|
| Enhanced Input Plugin (`wrap_text=True`) | Text wraps at word boundaries, box grows vertically | None |
| Enhanced Input Plugin (`wrap_text=False`) | Single line, extends beyond visible area | None |
| Default Renderer (no plugin) | Line `> {buffer}` extends past terminal edge | None |

**What is Preserved**:
- ✓ Full buffer content (all typed characters)
- ✓ Cursor position (character index in buffer)
- ✓ Command history
- ✓ Undo state (if applicable)

**What Adapts**:
- Box width recalculated each render cycle
- Text wrapping recomputed for new width
- Line count may change (wrapped text = more lines)

**Aggressive Clearing** (width reduced ≥10%):

When significant width reduction occurs, the renderer uses aggressive clearing to prevent visual artifacts:

```python
# From terminal_renderer.py:_render_lines()
if size_changed:
    self._write("\033[u")   # Restore cursor to saved position
    self._write("\033[6A")  # Move up into safety buffer zone
    self._write("\033[J")   # Clear from cursor to end of screen
    await asyncio.sleep(0.1)  # Let terminal process escape sequences
    # ... render new content ...
    await asyncio.sleep(0.4)  # Additional settling time
```

**Configuration** (Enhanced Input Plugin):

```python
# .kollabor-cli/config.json
{
  "plugins.enhanced_input.wrap_text": true,      # Enable word wrapping (default)
  "plugins.enhanced_input.dynamic_sizing": true, # Box height adapts to content
  "plugins.enhanced_input.width_mode": "auto",   # Auto-fit to terminal width
  "plugins.enhanced_input.min_width": 40,        # Minimum box width
  "plugins.enhanced_input.max_width": 120        # Maximum box width
}
```

### Message Display Flow

```
[Queue messages]
    ↓
display_queued_messages()
    ↓
Set is_displaying = True
    ↓
Set writing_messages = True
    ↓
Clear active area once
    ↓
For each message:
    - Format message
    - Display message
    ↓
Write blank line for separation
    ↓
Set writing_messages = False
    ↓
Set is_displaying = False
    ↓
Reset render state flags:
    - input_line_written = False
    - last_line_count = 0
    ↓
Invalidate render cache
    ↓
[Display Complete]
```

---

## Buffer Management

### Input Buffer Lifecycle

```
1. Initialization
   ├─ Create BufferManager
   ├─ Set buffer_limit (default: 1000)
   └─ Set history_limit (default: 100)

2. Active Input
   ├─ User types characters
   │   ├─ insert_char() adds to buffer
   │   └─ Cursor position updated
   ├─ User navigates cursor
   │   ├─ move_cursor(left/right)
   │   └─ Cursor position updated
   └─ User edits
       ├─ delete_char() (backspace)
       ├─ delete_forward() (delete key)
       └─ Content adjusted

3. Paste Handling
   ├─ Paste detected
   ├─ handle_paste(content) called
   ├─ Content processed (line breaks → spaces)
   ├─ Inserted at cursor position
   └─ History navigation reset

4. History Navigation
   ├─ User presses up/down
   ├─ First up: Save temp_buffer = current content
   ├─ Navigate through history
   │   ├─ Up: Load older command
   │   └─ Down: Load newer command
   └─ New input: Reset history navigation

5. Validation
   ├─ validate_content() called
   ├─ Check dangerous patterns (rm -rf, etc.)
   ├─ Check buffer limit (90% warning)
   └─ Return error list

6. Submission
   ├─ User presses Enter
   ├─ get_content_and_clear() called
   ├─ Content saved to history
   ├─ Buffer cleared
   └─ Cursor reset to 0
```

### Conversation Buffer Lifecycle

```
1. Initialization
   ├─ Create ConversationBuffer
   ├─ Set max_messages (default: 1000)
   └─ Initialize deque with maxlen

2. Message Addition
   ├─ add_message() called
   ├─ Create ConversationMessage object
   │   ├─ content: Message text
   │   ├─ message_type: USER/ASSISTANT/SYSTEM/ERROR/INFO/DEBUG
   │   ├─ format_style: PLAIN/GRADIENT/HIGHLIGHTED/DIMMED
   │   ├─ timestamp: Current time
   │   └─ metadata: Additional data dict
   ├─ Append to deque (auto-trim if exceeding maxlen)
   └─ Increment message_counter

3. Message Retrieval
   ├─ get_recent_messages(count) - Get N most recent
   ├─ get_messages_by_type(type) - Get all of specific type
   └─ Direct access via buffer.messages deque

4. Formatting
   ├─ MessageFormatter formats each message
   ├─ Applies format_style
   │   ├─ PLAIN: No formatting
   │   ├─ GRADIENT: Color gradient (via VisualEffects)
   │   ├─ HIGHLIGHTED: ANSI highlighting (colors by type)
   │   └─ DIMMED: Dimmed appearance
   └─ Returns formatted string

5. Clearing
   ├─ clear() called
   ├─ messages.clear() - Clear deque
   ├─ message_counter = 0
   └─ All messages removed

6. Statistics
   ├─ get_stats() called
   ├─ Count total messages
   ├─ Count messages by type
   └─ Return stats dictionary
```

---

## Render State Management

### Render States

The system manages multiple render states:

```
Render States:
├─ Normal Mode
│   ├─ input_line_written: False/True
│   ├─ writing_messages: False
│   └─ _in_alternate_buffer: False
│
├─ Writing Messages (during display_message_sequence)
│   ├─ input_line_written: True
│   ├─ writing_messages: True
│   └─ _in_alternate_buffer: True
│
├─ Modal Mode (DURING modal - while overlay is visible)
│   ├─ input_line_written: True (from before modal)
│   ├─ writing_messages: True (blocks render loop)
│   └─ _in_alternate_buffer: True
│
├─ Modal Mode EXIT (after modal closes)
│   ├─ input_line_written: False (RESET by display_queued_messages)
│   ├─ writing_messages: False (RESET - render loop resumes)
│   ├─ last_line_count: 0 (RESET)
│   └─ _in_alternate_buffer: True (NOT reset - stays True)
│
└─ Fullscreen Mode (DURING - while fullscreen is active)
    ├─ input_line_written: True (from before fullscreen)
    ├─ writing_messages: True (blocks render loop)
    └─ _in_alternate_buffer: True
```

**Note**: The states above show flag values at specific moments. On modal/fullscreen EXIT,
`display_queued_messages()` resets `input_line_written=False`, `writing_messages=False`,
and `last_line_count=0`. The `_in_alternate_buffer` flag is NOT reset (intentionally).

### Render Cache

The render cache optimizes terminal writes by skipping unchanged content:

```python
# Cache structure
_last_render_content: List[str]  # Last rendered lines
_render_cache_enabled: bool      # Cache enabled flag

# Cache check before rendering
if cache_enabled and _last_render_content == lines:
    # Content unchanged - skip rendering
    return

# Content changed - update cache and render
_last_render_content = lines.copy()
# ... perform render ...
```

**How Formatted Content is Compared**:

The cache comparison uses Python's list equality (`==`), which performs element-by-element string comparison. Strings include ANSI escape codes, so:

| Scenario | Cache Result | Reason |
|----------|--------------|--------|
| Same text, same colors | HIT (skip render) | Byte-identical strings including ANSI codes |
| Same text, different colors | MISS (re-render) | ANSI escape sequences differ |
| Different text, same colors | MISS (re-render) | Text content differs |
| Shimmer/animation frame | MISS (re-render) | Color codes change each frame |

**Example**:

```python
# These are DIFFERENT strings (cache miss):
line_red   = "\033[38;2;255;0;0mHello\033[0m"    # Red "Hello"
line_blue  = "\033[38;2;0;0;255mHello\033[0m"    # Blue "Hello"

# These are IDENTICAL strings (cache hit):
line1 = "\033[38;2;255;0;0mHello\033[0m"
line2 = "\033[38;2;255;0;0mHello\033[0m"
```

**Implications**:

1. **Animations always re-render**: Shimmer effects change ANSI codes each frame, causing cache misses
2. **Static colored content caches well**: If colors don't change, formatted content caches efficiently
3. **No stripping**: ANSI codes are NOT stripped before comparison - full formatted strings are compared
4. **Color mode changes**: If `ColorSupport` changes (e.g., from TRUE_COLOR to 256), all colors regenerate and cache misses

**Debugging Cache Behavior**:

```python
# Get cache status
status = terminal_renderer.get_render_cache_status()
# Returns: {"enabled": True, "cached_lines": 5, "last_cached_content": [...]}

# Force re-render
terminal_renderer.invalidate_render_cache()
```

### Render Cache Invalidation

Cache is invalidated when:
1. `invalidate_render_cache()` is explicitly called
2. Terminal size changes
3. Configuration changes that affect rendering
4. Manual refresh requested

### Terminal State Flags

```python
# Mode state
current_mode: TerminalMode  # NORMAL, RAW, COOKED

# Cursor state
_cursor_hidden: bool        # Is cursor hidden?

# Resize state
_resize_occurred: bool       # Resize signal received
_last_resize_time: float    # Last resize timestamp
_resize_debounce_delay: float  # Wait time for settlement

# Size state
_last_size: tuple           # Last known terminal size
```

---

## Coordination Patterns

### Pattern 1: Atomic Message Display

**Problem**: Multiple systems writing messages interfere with each other, causing messages to be overwritten or cleared.

**Solution**: `MessageDisplayCoordinator` provides atomic message sequences.

```python
# BAD: Direct writes can interfere
print("System message")  # System A writes
print("Thinking...")     # System B writes (overwrites System A)
print("Response")        # System C writes (overwrites Thinking)

# GOOD: Atomic display
coordinator = MessageDisplayCoordinator(renderer)
coordinator.display_message_sequence([
    ("system", "System message", {}),
    ("system", "Thinking...", {}),
    ("assistant", "Response", {})
])
# All three messages display together atomically
```

### Pattern 2: Buffer State Preservation During Transitions

**Problem**: Opening a modal can lose input buffer content or cursor position.

**Solution**: Save state before transition, restore after.

```python
# Before modal
saved_buffer = buffer_manager.content
saved_cursor = buffer_manager.cursor_position

# Open modal
enter_alternate_buffer()
show_modal()
# ... modal interaction ...
hide_modal()

# After modal
buffer_manager.content = saved_buffer
buffer_manager.cursor_position = saved_cursor
```

### Pattern 3: Debounced Resize Handling

**Problem**: Rapid resize events cause excessive re-rendering and flickering.

**Solution**: Debounce resize events with a settlement period.

```python
# Resize signal received
_last_resize_time = current_time

# Check if settled
if current_time - _last_resize_time >= debounce_delay:
    # Resize has settled - update layout
    update_size()
    invalidate_cache()
else:
    # Still settling - wait
    pass
```

### Pattern 4: Render Cache Optimization

**Problem**: Unnecessary terminal writes cause performance issues and flickering.

**Solution**: Cache last render and skip if unchanged.

```python
# Before rendering
if cache_enabled and last_render == new_render:
    return  # Skip rendering

# After rendering
last_render = new_render.copy()
```

### Pattern 5: Pause/Resume for Special Effects

**Problem**: Special effects (Matrix, etc.) conflict with normal input rendering.

**Solution**: Pause rendering during effects, resume after.

```python
# Before effect
display_controller.pause_rendering()

# Run effect
run_matrix_effect()

# After effect
display_controller.resume_rendering()
```

---

## Streaming and Coordinator Interaction

The system has two distinct message output pathways that operate independently:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MESSAGE OUTPUT PATHWAYS                              │
│                                                                             │
│  PATHWAY 1: Coordinated Display (Atomic)                                    │
│  ═══════════════════════════════════════                                    │
│  MessageDisplayCoordinator                                                  │
│       │                                                                     │
│       ├── queue_message() → accumulates messages                            │
│       ├── display_queued_messages() → atomic batch display                  │
│       │       │                                                             │
│       │       ├── Sets writing_messages = True (blocks render loop)         │
│       │       ├── Clears active area once                                   │
│       │       ├── Displays all messages in sequence                         │
│       │       └── Resets state flags on completion                          │
│       │                                                                     │
│       └── Uses: print() with terminal mode switching                        │
│                                                                             │
│  PATHWAY 2: Streaming Display (Real-time)                                   │
│  ═════════════════════════════════════════                                  │
│  MessageRenderer.write_streaming_chunk()                                    │
│       │                                                                     │
│       └── ConversationRenderer._display_chunk_immediately()                 │
│               │                                                             │
│               └── print(chunk, end="", flush=True)  ← Direct terminal write │
│                                                                             │
│  INDEPENDENCE: Streaming BYPASSES the coordinator entirely                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Streaming Bypasses the Coordinator

Streaming has fundamentally different requirements than coordinated display:

| Aspect | Coordinated Display | Streaming Display |
|--------|--------------------|--------------------|
| Timing | Batch (all at once) | Real-time (as received) |
| Buffering | Queues until ready | No buffering |
| Active area | Clears before display | Appends inline |
| State management | Full state transition | Minimal (just writes) |
| Use case | Complete messages | LLM response chunks |

### How the Pathways Coexist

The two pathways operate in different phases of the conversation:

```
[User submits message]
    │
    ├── MessageDisplayService.display_user_message()
    │       └── Uses coordinator → atomic display with ">" prefix
    │
    ├── LLM starts processing
    │       └── renderer.update_thinking(True, "Processing...")
    │
    ├── [Streaming phase begins]
    │       │
    │       ├── _handle_streaming_chunk() receives chunk
    │       │       │
    │       │       └── _stream_response_chunk()
    │       │               │
    │       │               ├── First chunk: start_streaming_response()
    │       │               │       └── Writes "∴ " prefix
    │       │               │
    │       │               └── write_streaming_chunk(chunk)
    │       │                       └── Direct print() to terminal
    │       │
    │       └── [Chunks continue until complete]
    │
    ├── [Streaming phase ends]
    │       └── finish_streaming_message()
    │               └── Writes newlines, clears streaming state
    │
    └── [Post-response display]
            └── display_complete_response() via coordinator
                    └── Thinking duration, tool results (atomic)
```

### Potential Conflicts and Mitigations

**Conflict 1: Coordinator display during active streaming**

If `display_queued_messages()` is called while streaming is active, the coordinator clears the active area, potentially erasing streamed content that hasn't been committed to the conversation buffer.

**Current mitigation**: The LLM service doesn't trigger coordinator display during streaming. Streaming completes first via `finish_streaming_message()`, then coordinator handles post-response messages.

**Conflict 2: Render loop interference during streaming**

The render loop could potentially overwrite streamed content if it runs during streaming.

**Current mitigation**: Streaming writes directly to stdout with `flush=True`, which immediately commits to the terminal. The render loop operates on the active area (input box, status), not the conversation area where streaming occurs.

**Conflict 3: Render cache and streaming**

Streaming doesn't interact with `_last_render_content` cache because it writes to a different area (conversation vs. active area).

**Best Practice**: Never mix coordinator and streaming calls for the same logical message. Use streaming for real-time LLM responses, coordinator for complete system messages.

```python
# CORRECT: Streaming for LLM response, coordinator for completion notice
for chunk in llm_stream:
    message_renderer.write_streaming_chunk(chunk)
message_renderer.finish_streaming_message()
coordinator.display_single_message("system", f"Thought for {duration}s")

# INCORRECT: Don't queue while streaming
for chunk in llm_stream:
    coordinator.queue_message("assistant", chunk)  # Don't do this!
```

---

## Plugin Render Resolution

When multiple plugins want to provide enhanced input rendering, a priority-based resolution system determines which plugin's output is used.

### Resolution Mechanism

```
render_active_area()
    │
    └── _render_input_area(lines)
            │
            └── event_bus.emit_with_hooks(EventType.INPUT_RENDER, {...})
                    │
                    ├── Hook 1: EnhancedInputPlugin (priority=10)
                    │       └── Returns: {"fancy_input_lines": [...], "status": "rendered"}
                    │
                    ├── Hook 2: AnotherPlugin (priority=5)
                    │       └── Returns: {"fancy_input_lines": [...], "status": "rendered"}
                    │       └── ⚠️ IGNORED - first match already found
                    │
                    └── Hook 3: DisabledPlugin (priority=10)
                            └── Returns: {"status": "disabled"}
                            └── ⚠️ No fancy_input_lines, not counted as match

    Result: EnhancedInputPlugin's lines are used
```

### Priority Values

Hook priority determines execution order (higher values execute first):

```python
class HookPriority(Enum):
    CRITICAL = 100    # System-critical operations
    HIGH = 50         # Important processing
    NORMAL = 25       # Standard operations
    LOW = 10          # Display/UI operations
    LLM = 75          # LLM-specific operations
    DISPLAY = 10      # Display rendering
    SYSTEM = 90       # System-level operations
```

The `EnhancedInputPlugin` uses `HookPriority.DISPLAY` (value=10), meaning plugins with higher priority values execute first but don't typically provide `fancy_input_lines`.

### First-Match-Wins Behavior

The terminal renderer uses the **first** hook result that contains `fancy_input_lines`:

```python
# From terminal_renderer.py:_render_input_area()
if "main" in result:
    for hook_result in result["main"].values():
        if isinstance(hook_result, dict) and "fancy_input_lines" in hook_result:
            lines.extend(hook_result["fancy_input_lines"])
            return  # STOPS HERE - first match wins
```

This means:
1. Plugins are called in priority order
2. The first plugin to return `fancy_input_lines` wins
3. Subsequent plugins' `fancy_input_lines` are ignored
4. Plugins can "yield" by not returning `fancy_input_lines`

### Yielding to Another Plugin

A plugin can choose not to provide enhanced input, allowing the next plugin (or default rendering) to handle it:

```python
async def _render_fancy_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    # Yield if disabled
    if not self.config.enabled:
        return {"status": "disabled"}  # No fancy_input_lines = yield

    # Yield to another plugin under certain conditions
    if self._should_yield_to_command_menu():
        return {"status": "yielding", "reason": "command_menu_active"}

    # Provide enhanced input
    return {
        "status": "rendered",
        "fancy_input_lines": self._generate_input_box()
    }
```

### Debugging Plugin Conflicts

When unexpected plugin behavior occurs:

**1. Check hook registration order:**
```python
# In your plugin's register_hooks():
logger.info(f"Registering {self.name} hook with priority {HookPriority.DISPLAY.value}")
```

**2. Log when yielding:**
```python
async def _render_fancy_input(self, data, event):
    result = self._compute_result()
    logger.debug(f"{self.name}: returning {result.get('status')} "
                 f"(has fancy_input_lines: {'fancy_input_lines' in result})")
    return result
```

**3. Check which plugin won:**
The terminal renderer logs at debug level which plugin's input is used.

### Cooperative Plugin Patterns

**Pattern 1: Priority-based exclusion**
```python
# CommandMenuPlugin (high priority) yields when menu is closed
if not self.menu_active:
    return {"status": "inactive"}

# EnhancedInputPlugin (lower priority) only runs when menu is closed
```

**Pattern 2: Plugin composition**
```python
# One plugin can delegate to another's renderer
async def _render_fancy_input(self, data, event):
    if self.should_use_partner_plugin:
        return await self.partner_plugin._render_fancy_input(data, event)
    return self._own_render()
```

**Pattern 3: Configuration-based selection**
```python
# User configures which plugin handles input rendering
active_input_plugin = config.get("plugins.active_input_renderer", "enhanced_input")
if self.name != active_input_plugin:
    return {"status": "not_selected"}
```

### No Built-in Negotiation

The current system does **not** support:
- Plugin negotiation protocols
- Merged output from multiple plugins
- Runtime priority changes
- Plugin capability discovery

If you need these features, implement them at the plugin level using the yielding and composition patterns above.

---

## Testing Strategies

The buffer transition and render state system can be tested effectively through a combination of unit tests with mocking and integration tests.

### Mocking Terminal State

Since `TerminalState` interacts with system terminal settings, tests should mock the terminal:

```python
import unittest
from unittest.mock import MagicMock, patch
from core.io.terminal_state import TerminalState, TerminalMode

class TestTerminalState(unittest.TestCase):
    def setUp(self):
        # Mock sys.stdin.fileno() and termios
        self.stdin_patch = patch('sys.stdin')
        self.mock_stdin = self.stdin_patch.start()
        self.mock_stdin.isatty.return_value = True
        self.mock_stdin.fileno.return_value = 0

    def tearDown(self):
        self.stdin_patch.stop()

    @patch('core.io.terminal_state.termios')
    @patch('core.io.terminal_state.tty')
    def test_enter_raw_mode(self, mock_tty, mock_termios):
        """Test entering raw mode saves settings and calls setraw."""
        mock_termios.tcgetattr.return_value = [0, 1, 2, 3, 4, 5, 6]

        state = TerminalState()
        result = state.enter_raw_mode()

        self.assertTrue(result)
        mock_tty.setraw.assert_called_once()
        self.assertEqual(state.current_mode, TerminalMode.RAW)

    @patch('shutil.get_terminal_size')
    def test_get_size_returns_dimensions(self, mock_size):
        """Test terminal size retrieval."""
        mock_size.return_value = MagicMock(columns=120, lines=40)

        state = TerminalState()
        width, height = state.get_size()

        self.assertEqual(width, 120)
        self.assertEqual(height, 40)
```

### Testing BufferManager

`BufferManager` is stateful but doesn't require terminal mocking:

```python
from core.io.buffer_manager import BufferManager

class TestBufferManager(unittest.TestCase):
    def setUp(self):
        self.buffer = BufferManager(buffer_limit=100, history_limit=10)

    def test_insert_char_at_cursor(self):
        """Test character insertion at cursor position."""
        self.buffer.insert_char('H')
        self.buffer.insert_char('i')

        content, cursor = self.buffer.get_display_info()
        self.assertEqual(content, "Hi")
        self.assertEqual(cursor, 2)

    def test_cursor_movement(self):
        """Test cursor moves correctly."""
        self.buffer.insert_char('A')
        self.buffer.insert_char('B')
        self.buffer.insert_char('C')
        self.buffer.move_cursor('left')
        self.buffer.move_cursor('left')

        _, cursor = self.buffer.get_display_info()
        self.assertEqual(cursor, 1)

    def test_history_navigation_preserves_current(self):
        """Test that history navigation preserves current input."""
        self.buffer.add_to_history("previous command")
        self.buffer.insert_char('X')

        self.buffer.navigate_history('up')
        content, _ = self.buffer.get_display_info()
        self.assertEqual(content, "previous command")

        self.buffer.navigate_history('down')
        content, _ = self.buffer.get_display_info()
        self.assertEqual(content, "X")  # Original preserved
```

### Testing MessageDisplayCoordinator

The coordinator requires mocking the terminal renderer:

```python
from unittest.mock import MagicMock, AsyncMock
from core.io.message_coordinator import MessageDisplayCoordinator

class TestMessageDisplayCoordinator(unittest.TestCase):
    def setUp(self):
        # Create mock terminal renderer
        self.mock_renderer = MagicMock()
        self.mock_renderer.writing_messages = False
        self.mock_renderer.input_line_written = False
        self.mock_renderer.last_line_count = 0
        self.mock_renderer.clear_active_area = MagicMock()
        self.mock_renderer.invalidate_render_cache = MagicMock()
        self.mock_renderer.message_renderer = MagicMock()

        self.coordinator = MessageDisplayCoordinator(self.mock_renderer)

    def test_queue_message_accumulates(self):
        """Test messages accumulate in queue."""
        self.coordinator.queue_message("system", "Message 1")
        self.coordinator.queue_message("assistant", "Message 2")

        status = self.coordinator.get_queue_status()
        self.assertEqual(status["queue_length"], 2)
        self.assertEqual(status["queued_types"], ["system", "assistant"])

    def test_display_queued_sets_writing_flag(self):
        """Test display sets and clears writing_messages flag."""
        self.coordinator.queue_message("system", "Test")

        self.coordinator.display_queued_messages()

        # Flag should be reset after display
        self.assertFalse(self.mock_renderer.writing_messages)
        self.assertFalse(self.mock_renderer.input_line_written)

    def test_display_clears_queue(self):
        """Test display empties the queue."""
        self.coordinator.queue_message("system", "Test")
        self.coordinator.display_queued_messages()

        status = self.coordinator.get_queue_status()
        self.assertEqual(status["queue_length"], 0)
```

### Testing Resize Handling

Resize behavior requires simulating the debounce mechanism:

```python
import time
from unittest.mock import patch

class TestResizeHandling(unittest.TestCase):
    @patch('shutil.get_terminal_size')
    def test_resize_debounce(self, mock_size):
        """Test resize events are debounced."""
        mock_size.return_value = MagicMock(columns=80, lines=24)
        state = TerminalState()

        # Simulate resize signal
        state._resize_occurred = True
        state._last_resize_time = time.time()

        # Immediately after resize, should return False (still debouncing)
        self.assertFalse(state.check_and_clear_resize_flag())

        # After debounce delay, should return True
        state._last_resize_time = time.time() - 1.0  # 1 second ago
        self.assertTrue(state.check_and_clear_resize_flag())
```

### Integration Testing with Mock Terminal

For integration tests that span multiple components:

```python
class TestRenderIntegration(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create mock event bus
        self.mock_event_bus = MagicMock()
        self.mock_event_bus.emit_with_hooks = AsyncMock(return_value={"main": {}})

        # Create renderer with mocked dependencies
        with patch('core.io.terminal_state.TerminalState') as MockState:
            mock_state_instance = MagicMock()
            mock_state_instance.get_size.return_value = (80, 24)
            mock_state_instance.check_and_clear_resize_flag.return_value = False
            MockState.return_value = mock_state_instance

            from core.io.terminal_renderer import TerminalRenderer
            self.renderer = TerminalRenderer(event_bus=self.mock_event_bus)

    async def test_render_active_area_with_input(self):
        """Test rendering includes input buffer content."""
        self.renderer.input_buffer = "Hello"
        self.renderer.cursor_position = 5

        await self.renderer.render_active_area()

        # Verify render occurred (check cache was updated)
        self.assertTrue(len(self.renderer._last_render_content) > 0)
```

### Testing Plugin Render Hooks

To test plugin render hook behavior:

```python
class TestPluginRenderIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_first_plugin_wins(self):
        """Test first plugin returning fancy_input_lines is used."""
        mock_bus = MagicMock()

        # Simulate two plugins returning fancy_input_lines
        mock_bus.emit_with_hooks = AsyncMock(return_value={
            "main": {
                "plugin_a": {"fancy_input_lines": ["Box A"], "status": "rendered"},
                "plugin_b": {"fancy_input_lines": ["Box B"], "status": "rendered"}
            }
        })

        # The renderer should use the first one found
        # (dict iteration order is insertion order in Python 3.7+)
```

### Test File Organization

Recommended test structure:

```
tests/
├── unit/
│   ├── io/
│   │   ├── test_buffer_manager.py
│   │   ├── test_terminal_state.py
│   │   ├── test_message_coordinator.py
│   │   └── test_message_renderer.py
│   └── ...
├── integration/
│   ├── test_render_flow.py
│   └── test_modal_transitions.py
└── fixtures/
    └── mock_terminal.py  # Reusable terminal mocking utilities
```

---

## API Reference

### BufferManager

```python
class BufferManager:
    def __init__(self, buffer_limit: int = 1000, history_limit: int = 100):
        """Initialize buffer manager."""
    
    @property
    def content(self) -> str:
        """Get current buffer content."""
    
    @property
    def cursor_position(self) -> int:
        """Get current cursor position."""
    
    @property
    def is_empty(self) -> bool:
        """Check if buffer is empty or whitespace."""
    
    @property
    def length(self) -> int:
        """Get current buffer length."""
    
    def insert_char(self, char: str) -> bool:
        """Insert character at cursor position."""
    
    def delete_char(self) -> bool:
        """Delete character before cursor (backspace)."""
    
    def delete_forward(self) -> bool:
        """Delete character after cursor (delete key)."""
    
    def move_cursor(self, direction: str) -> bool:
        """Move cursor left or right."""
    
    def move_to_start(self) -> None:
        """Move cursor to start of buffer."""
    
    def move_to_end(self) -> None:
        """Move cursor to end of buffer."""
    
    def clear(self) -> None:
        """Clear buffer and reset cursor."""
    
    def get_content_and_clear(self) -> str:
        """Get buffer content and clear it."""
    
    def add_to_history(self, command: str) -> None:
        """Add command to history."""
    
    def navigate_history(self, direction: str) -> bool:
        """Navigate command history (up/down)."""
    
    def get_display_info(self) -> Tuple[str, int]:
        """Get (buffer_content, cursor_position) tuple."""
    
    def validate_content(self) -> List[str]:
        """Validate buffer content. Returns error list."""
    
    async def handle_paste(self, paste_content: str) -> bool:
        """Handle pasted content."""
    
    def get_stats(self) -> dict:
        """Get buffer statistics."""
```

### TerminalState

```python
class TerminalState:
    def __init__(self):
        """Initialize terminal state manager."""
    
    @property
    def current_mode(self) -> TerminalMode:
        """Get current terminal mode."""
    
    @property
    def capabilities(self) -> TerminalCapabilities:
        """Get terminal capabilities."""
    
    def enter_raw_mode(self) -> bool:
        """Enter raw terminal mode."""
    
    def exit_raw_mode(self) -> bool:
        """Exit raw terminal mode."""
    
    def write_raw(self, text: str) -> bool:
        """Write text directly to terminal."""
    
    def hide_cursor(self) -> bool:
        """Hide terminal cursor."""
    
    def show_cursor(self) -> bool:
        """Show terminal cursor."""
    
    def clear_line(self) -> bool:
        """Clear current line."""
    
    def move_cursor_up(self, lines: int = 1) -> bool:
        """Move cursor up."""
    
    def move_cursor_down(self, lines: int = 1) -> bool:
        """Move cursor down."""
    
    def move_cursor_to_column(self, column: int) -> bool:
        """Move cursor to specified column."""
    
    def save_cursor_position(self) -> bool:
        """Save cursor position."""
    
    def restore_cursor_position(self) -> bool:
        """Restore cursor position."""
    
    def clear_screen_from_cursor(self) -> bool:
        """Clear screen from cursor to end."""
    
    def update_size(self) -> bool:
        """Update terminal size. Returns True if changed."""
    
    def get_size(self) -> Tuple[int, int]:
        """Get terminal size (width, height)."""
    
    def supports_color(self, color_type: str = "basic") -> bool:
        """Check color support."""
    
    def check_and_clear_resize_flag(self) -> bool:
        """Check if resize occurred and settled (debounced)."""
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """Query cursor position from terminal."""
    
    def get_status(self) -> Dict[str, Any]:
        """Get terminal state status."""
    
    def cleanup(self) -> None:
        """Cleanup and restore terminal settings."""
```

### MessageDisplayCoordinator

```python
class MessageDisplayCoordinator:
    def __init__(self, terminal_renderer):
        """Initialize coordinator."""
    
    def queue_message(self, message_type: str, content: str, **kwargs) -> None:
        """Queue message for display."""
    
    def display_single_message(self, message_type: str, content: str, **kwargs) -> None:
        """Display single message immediately."""
    
    def display_queued_messages(self) -> None:
        """Display all queued messages atomically."""
    
    def display_message_sequence(self, messages: List[Tuple]) -> None:
        """Display sequence of messages atomically."""
    
    def clear_queue(self) -> None:
        """Clear queued messages without displaying."""
    
    def enter_alternate_buffer(self) -> None:
        """Set flags for alternate buffer mode.

        Sets _in_alternate_buffer=True and writing_messages=True.
        Does NOT capture state - uses flag-based coordination.
        Caller is responsible for resetting flags on exit.
        """

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status for debugging."""
```

### TerminalRenderer

```python
class TerminalRenderer:
    def __init__(self, event_bus=None, config=None):
        """Initialize renderer."""
    
    def enter_raw_mode(self) -> None:
        """Enter raw terminal mode."""
    
    def exit_raw_mode(self) -> None:
        """Exit raw terminal mode."""
    
    def write_message(self, message: str, apply_gradient: bool = True) -> None:
        """Write message to conversation."""
    
    def write_streaming_chunk(self, chunk: str) -> None:
        """Write streaming chunk immediately."""
    
    def write_user_message(self, message: str) -> None:
        """Write user message."""
    
    def write_hook_message(self, content: str, **metadata) -> None:
        """Write hook message via coordinator."""
    
    def update_thinking(self, active: bool, message: str = "") -> None:
        """Update thinking animation."""
    
    def set_thinking_effect(self, effect: str) -> None:
        """Set thinking effect (dim, shimmer, normal)."""
    
    def configure_shimmer(self, speed: int, wave_width: int) -> None:
        """Configure shimmer effect."""
    
    def configure_thinking_limit(self, limit: int) -> None:
        """Configure thinking message limit."""
    
    async def render_active_area(self) -> None:
        """Render active input/status area."""
    
    def clear_active_area(self) -> None:
        """Clear active area."""
    
    def invalidate_render_cache(self) -> None:
        """Invalidate render cache."""
    
    def set_render_cache_enabled(self, enabled: bool) -> None:
        """Enable/disable render cache."""
    
    def get_render_cache_status(self) -> dict:
        """Get render cache status."""
```

---

## Best Practices

### 1. Always Use the Coordinator for Message Display

**DO**:
```python
# Good: Use coordinator for atomic display
coordinator.display_message_sequence([
    ("system", "Thought for 2.1 seconds", {}),
    ("assistant", "Here's your answer...", {})
])
```

**DON'T**:
```python
# Bad: Direct writes can interfere
print("Thought for 2.1 seconds")
print("Here's your answer...")
```

### 2. Preserve Buffer State During Transitions

**DO**:
```python
# Good: Save and restore state
saved_buffer = buffer_manager.content
saved_cursor = buffer_manager.cursor_position

# ... transition (modal, fullscreen, etc.) ...

buffer_manager.content = saved_buffer
buffer_manager.cursor_position = saved_cursor
```

**DON'T**:
```python
# Bad: Lose state during transition
# ... transition ...
# Buffer state is lost!
```

### 3. Use Debounced Resize Handling

**DO**:
```python
# Good: Check if resize settled
if terminal_state.check_and_clear_resize_flag():
    terminal_state.update_size()
    # Update layout with new size
```

**DON'T**:
```python
# Bad: Update on every resize signal
# Causes excessive re-rendering
terminal_state.update_size()
# Update layout with new size
```

### 4. Invalidate Cache After External Changes

**DO**:
```python
# Good: Invalidate cache after external change
renderer.invalidate_render_cache()
```

**DON'T**:
```python
# Bad: Don't invalidate cache
# Stale content will be displayed
```

### 5. Pause Rendering During Special Effects

**DO**:
```python
# Good: Pause before effect
display_controller.pause_rendering()
run_special_effect()
display_controller.resume_rendering()
```

**DON'T**:
```python
# Bad: Render conflicts with effect
run_special_effect()
# Rendering interferes with effect
```

### 6. Validate Buffer Content Before Submission

**DO**:
```python
# Good: Validate before submission
errors = buffer_manager.validate_content()
if errors:
    for error in errors:
        print(f"Warning: {error}")
    # Don't submit
```

**DON'T**:
```python
# Bad: Submit without validation
# Potentially dangerous command executed
```

### 7. Use Appropriate Message Types

**DO**:
```python
# Good: Use correct message types
coordinator.display_single_message("system", "Thought for 2.1 seconds")
coordinator.display_single_message("assistant", "Here's your answer")
coordinator.display_single_message("error", "Something went wrong")
```

**DON'T**:
```python
# Bad: Use wrong message type
coordinator.display_single_message("assistant", "Something went wrong")
# Should be "error" type
```

### 8. Clean Up Terminal State on Shutdown

**DO**:
```python
# Good: Cleanup on shutdown
try:
    # ... main application loop ...
finally:
    terminal_state.cleanup()
    # Restore original terminal settings
```

**DON'T**:
```python
# Bad: Don't cleanup
# Terminal left in raw mode, broken state
```

---

## Troubleshooting

### Problem: Duplicate input boxes

**Cause**: Render state flags not reset after message display.

**Solution**: Ensure `MessageDisplayCoordinator` resets flags:
```python
self.terminal_renderer.input_line_written = False
self.terminal_renderer.last_line_count = 0
self.terminal_renderer.invalidate_render_cache()
```

### Problem: Messages overwritten by other systems

**Cause**: Direct writes without coordination.

**Solution**: Use `MessageDisplayCoordinator` for all message writes.

### Problem: Flickering on resize

**Cause**: Excessive re-rendering during resize.

**Solution**: Ensure debounced resize handling is used.

### Problem: Cursor lost after modal

**Cause**: Cursor state not saved/restored.

**Solution**: Use `ModalState` to save/restore cursor position.

### Problem: Stale content after resize

**Cause**: Render cache not invalidated.

**Solution**: Call `invalidate_render_cache()` after resize.

---

## Error Handling and Recovery

### Overview

The buffer transition and render state system employs multiple error recovery strategies to maintain terminal integrity. The design philosophy is **graceful degradation** - operations continue with fallbacks rather than crashing, and critical state is always restored via `try/finally` patterns.

### Core Recovery Mechanisms

#### 1. Terminal State Recovery (TerminalState)

**Location**: `core/io/terminal_state.py`

The terminal state manager uses defensive error handling:

```python
def enter_raw_mode(self) -> bool:
    """Returns False on failure, logs error, never throws."""
    try:
        if IS_WINDOWS:
            # Windows-specific raw mode setup
        else:
            tty.setraw(sys.stdin.fileno())
        return True
    except Exception as e:
        logger.error(f"Failed to enter raw mode: {e}")
        return False  # Caller can check and handle
```

**Recovery Patterns**:
- **Fallback defaults**: If terminal detection fails, falls back to 80x24 size, no color
- **Initialization tolerance**: If `_initialize_terminal()` fails, sets `is_terminal = False` and continues
- **Cleanup guarantee**: The `cleanup()` method wraps all restoration in try/except:

```python
def cleanup(self) -> None:
    """Cleanup terminal state and restore settings."""
    try:
        if self._cursor_hidden:
            self.show_cursor()
        if self.current_mode == TerminalMode.RAW:
            self.exit_raw_mode()
    except Exception as e:
        logger.error(f"Error during terminal cleanup: {e}")
        # State may be partially restored, but we don't crash
```

**Resize Error Handling**:
- Resize handler (`_setup_resize_handler()`) catches exceptions silently
- If SIGWINCH setup fails, falls back to polling-based resize detection
- Debouncing (0.9s delay) prevents issues from rapid resize events

#### 2. Message Display Recovery (MessageDisplayCoordinator)

**Location**: `core/io/message_coordinator.py`

Critical state is always reset via `try/finally`:

```python
def display_queued_messages(self) -> None:
    self.is_displaying = True
    self.terminal_renderer.writing_messages = True

    try:
        for message_type, content, kwargs in self.message_queue:
            self._display_single_message(message_type, content, kwargs)
    finally:
        # ALWAYS restore state, even if display fails
        self.terminal_renderer.writing_messages = False
        self.message_queue.clear()
        self.is_displaying = False
        self.terminal_renderer.input_line_written = False
        self.terminal_renderer.last_line_count = 0
        self.terminal_renderer.invalidate_render_cache()
```

**Fallback Display**:

```python
def _display_single_message(self, message_type, content, kwargs):
    try:
        # ... normal display logic ...
    except Exception as e:
        logger.error(f"Error displaying {message_type} message: {e}")
        # Fallback to raw print to ensure message is shown
        try:
            print(f"[{message_type.upper()}] {content}")
        except Exception:
            logger.error("Critical: Failed even with fallback")
```

#### 3. Modal State Recovery (ModalController)

**Location**: `core/io/input/modal_controller.py`

Modal operations use consistent error recovery:

```python
async def _enter_modal_mode(self, ui_config):
    try:
        self.modal_renderer = ModalRenderer(...)
        self.renderer.writing_messages = True
        self.command_mode = CommandMode.MODAL
        await self.modal_renderer.show_modal(ui_config)
    except Exception as e:
        logger.error(f"Error entering modal mode: {e}")
        # Reset to safe state
        self.command_mode = CommandMode.NORMAL
        self.renderer.writing_messages = False
```

**Keypress Error Recovery**:

```python
async def _handle_modal_keypress(self, key_press) -> bool:
    try:
        # ... keypress handling ...
    except Exception as e:
        logger.error(f"Error handling modal keypress: {e}")
        await self._exit_modal_mode()  # Force exit on error
        return False
```

**Exit Guarantees**: All modal exit methods reset `command_mode` in finally/except blocks:

```python
async def _exit_modal_mode(self):
    try:
        if self.modal_renderer:
            self.modal_renderer.close_modal()
        self.command_mode = CommandMode.NORMAL
        self.renderer.writing_messages = False
    except Exception as e:
        logger.error(f"Error exiting modal mode: {e}")
        # Still reset critical state
        self.command_mode = CommandMode.NORMAL
        self.modal_renderer = None
        self.renderer.writing_messages = False
```

#### 4. Fullscreen Session Recovery (FullScreenSession)

**Location**: `core/fullscreen/session.py`

Fullscreen uses the strongest recovery pattern - guaranteed cleanup via `try/finally`:

```python
async def run(self) -> bool:
    try:
        if not await self._initialize():
            return False

        self.running = True
        await self._session_loop()
        return True

    except Exception as e:
        logger.error(f"Session error for {self.plugin.name}: {e}")
        return False

    finally:
        # ALWAYS runs - restores terminal even on crash
        await self._cleanup()
```

**Initialization Tolerance**:

```python
async def _initialize(self) -> bool:
    try:
        # Register input hook (non-critical)
        await self._register_input_hook()
    except Exception as e:
        logger.warning(f"Input hook registration failed: {e}")
        # Continue anyway - input might still work via fallback

    # Terminal setup (critical)
    if not self.renderer.setup_terminal():
        logger.error("Failed to setup terminal")
        return False  # Can't continue without terminal
```

**Cleanup Error Handling**:

```python
async def _cleanup(self):
    try:
        self.running = False
        await self.plugin.on_stop()
        self.renderer.restore_terminal()

        # Unregister hook (best-effort)
        if self.input_hook_registered:
            try:
                await self.event_bus.unregister_hook(hook_id)
            except Exception as e:
                logger.error(f"Error unregistering hook: {e}")

        await self.plugin.cleanup()

    except Exception as e:
        logger.error(f"Error during session cleanup: {e}")
        # Terminal state may be partially restored
```

#### 5. Alternate Buffer Recovery (FullScreenRenderer)

**Location**: `core/fullscreen/renderer.py`

The alternate buffer provides **automatic screen restoration**:

```python
def setup_terminal(self) -> bool:
    try:
        # Save terminal state snapshot
        self.terminal_snapshot = TerminalSnapshot()
        if sys.stdin.isatty():
            if IS_WINDOWS:
                self.terminal_snapshot.console_mode = ...
            else:
                self.terminal_snapshot.termios_settings = termios.tcgetattr(...)

        # Enter alternate buffer - original screen is preserved
        sys.stdout.write("\033[?1049h")
        return True

    except Exception as e:
        logger.error(f"Failed to setup terminal: {e}")
        return False

def restore_terminal(self) -> bool:
    try:
        # Exit alternate buffer - automatically restores original screen
        sys.stdout.write("\033[?1049l")

        # Restore termios/console settings
        if self.terminal_snapshot:
            # ... restore from snapshot ...

        return True

    except Exception as e:
        logger.error(f"Failed to restore terminal: {e}")
        return False  # Best effort - screen might be partially restored
```

### State Transition Error Matrix

| Transition | Failure Mode | Recovery Strategy |
|------------|--------------|-------------------|
| Enter raw mode | `termios` error | Return False, continue in cooked mode |
| Exit raw mode | Settings lost | Use saved `original_termios` |
| Resize | Signal fails | Fall back to polling |
| Modal open | Renderer error | Reset `command_mode`, clear `writing_messages` |
| Modal close | Exit fails | Force state reset regardless |
| Fullscreen enter | Terminal setup | Return False, skip session |
| Fullscreen exit | Cleanup error | Log, continue, best-effort restore |
| Alternate buffer | Write fails | Screen may be corrupted |
| Message display | Format error | Fall back to `print()` |

### Rollback Limitations

The system does **not** implement transactional rollback. Key limitations:

1. **Partial State Changes**: If `enter_raw_mode()` succeeds but a later operation fails, raw mode remains active until explicit cleanup

2. **No Automatic Retry**: Failed operations are logged but not retried

3. **Silent Degradation**: Some failures (resize handler setup) are silent with fallbacks

4. **Cleanup Cascade**: If early cleanup steps fail, later steps may be skipped

### Emergency Recovery

If the terminal is left in a broken state (cursor hidden, raw mode, garbled display), users can:

1. **Reset terminal**: Type `reset` (blindly if needed) or `stty sane`
2. **Force show cursor**: `echo -e "\033[?25h"`
3. **Exit alternate buffer**: `echo -e "\033[?1049l"`
4. **Kill and restart**: The application's `finally` blocks should clean up on exit

### Best Practices for Error Handling

1. **Always use try/finally for state-modifying operations**:
   ```python
   self.renderer.writing_messages = True
   try:
       # ... operations ...
   finally:
       self.renderer.writing_messages = False
   ```

2. **Reset critical state in except blocks**:
   ```python
   except Exception:
       self.command_mode = CommandMode.NORMAL  # Safe state
   ```

3. **Log errors at appropriate levels**:
   - `logger.error()`: Failures affecting functionality
   - `logger.warning()`: Recoverable issues
   - `logger.debug()`: Expected fallbacks

4. **Return success indicators**:
   ```python
   def setup_terminal(self) -> bool:  # Caller can check
   ```

5. **Provide fallback behavior**:
   ```python
   try:
       fancy_render()
   except Exception:
       simple_print()  # Always show something
   ```

---

## Future Enhancements

1. **Screen Capture**: Implement full screen capture for better modal restoration
2. **Scrollback Buffer**: Add scrollback buffer for conversation history
3. **Multiple Buffers**: Support multiple input buffers (multi-line editing)
4. **Diff Rendering**: Show changes between renders for debugging
5. **Performance Metrics**: Add timing metrics for render operations
6. **State Machine**: Formal state machine for render transitions
7. **Snapshot/Restore**: Full terminal snapshot/restore for state transitions

---

## References

- Related Files:
  - `core/io/buffer_manager.py` - Input buffer management
  - `core/io/message_renderer.py` - Message rendering and conversation buffer
  - `core/io/terminal_state.py` - Terminal state management
  - `core/io/message_coordinator.py` - Message display coordination
  - `core/io/terminal_renderer.py` - Terminal renderer
  - `core/io/layout.py` - Layout management
  - `core/ui/modal_overlay_renderer.py` - Modal state management

- Related Documentation:
  - `docs/LLM_MESSAGE_FLOW.md` - LLM message flow
  - `docs/STARTUP_TO_FIRST_MESSAGE_FLOW.md` - Startup flow
  - `docs/reference/slash-commands-guide.md` - Slash commands
  - `docs/reference/hook-system-sdk.md` - Hook system
