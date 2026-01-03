# /resume Command Implementation Specification

**Document Version:** 1.0
**Date:** 2025-12-11
**Status:** Implementation Review
**Author:** Code Review Analysis

---

## 1. Executive Summary

The `/resume` command enables users to restore previous conversation sessions with full context preservation. This document captures the current implementation state based on code review analysis.

### Implementation Status: Phase 1 Complete (Core Functionality)

| Component | Status | Location |
|-----------|--------|----------|
| ConversationManager extensions | Complete | `core/llm/conversation_manager.py` |
| ConversationLogger extensions | Complete | `core/llm/conversation_logger.py` |
| SystemCommandsPlugin handler | Complete | `core/commands/system_commands.py` |
| ResumeConversationPlugin | Complete | `plugins/resume_conversation_plugin.py` |
| Modal UI (sessions format) | Complete | `core/ui/modal_renderer.py` |
| Input handler integration | Complete | `core/io/input_handler.py` |
| Data models | Complete | `core/models/resume.py` |
| Unit tests | Partial | `tests/test_resume_command.py` |

---

## 2. Architecture

### 2.1 Component Diagram

```
+------------------+     +------------------------+
|   User Input     |     |    /resume [args]      |
+--------+---------+     +-----------+------------+
         |                           |
         v                           v
+------------------+     +------------------------+
| CommandParser    |---->| SlashCommand           |
+------------------+     | {name, args, raw}      |
                         +-----------+------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
     +------------------------------+  +------------------------------+
     | SystemCommandsPlugin         |  | ResumeConversationPlugin     |
     | core/commands/system_commands|  | plugins/resume_conversation_ |
     | .py:409-447                  |  | plugin.py:116-153            |
     +-------------+----------------+  +-------------+----------------+
                   |                                 |
                   +----------------+----------------+
                                    |
                                    v
                   +--------------------------------+
                   | ConversationManager            |
                   | core/llm/conversation_manager  |
                   +--------------------------------+
                   | - save_session()    :324-357   |
                   | - load_session()    :359-413   |
                   | - validate_session():461-549   |
                   | - get_available_sessions()     |
                   |                     :415-459   |
                   +----------------+---------------+
                                    |
                                    v
                   +--------------------------------+
                   | KollaborConversationLogger     |
                   | core/llm/conversation_logger   |
                   +--------------------------------+
                   | - list_sessions()   :476-503   |
                   | - search_sessions() :661-706   |
                   | - get_session_summary()        |
                   |                     :619-659   |
                   +----------------+---------------+
                                    |
                                    v
                   +--------------------------------+
                   | ModalRenderer                  |
                   | core/ui/modal_renderer.py      |
                   +--------------------------------+
                   | - "sessions" format :265-311   |
                   | - Navigation        :524-569   |
                   | - Selection         :612-631   |
                   +----------------+---------------+
                                    |
                                    v
                   +--------------------------------+
                   | InputHandler                   |
                   | core/io/input_handler.py       |
                   +--------------------------------+
                   | - resume_session action        |
                   |                     :1827-1850 |
                   +--------------------------------+
```

### 2.2 Data Flow

#### Flow 1: Session Discovery (`/resume` with no arguments)

```
1. User types: /resume
2. CommandParser creates SlashCommand{name="resume", args=[]}
3. handle_resume() called with empty args
4. _show_session_selector() invoked
5. conversation_manager.get_available_sessions() OR
   conversation_logger.list_sessions()
6. _get_resume_modal_definition(sessions) builds modal config
7. Returns CommandResult with UIConfig{type="modal"}
8. ModalRenderer displays session list with navigation
```

#### Flow 2: Session Selection (User selects from modal)

```
1. User navigates with arrow keys (modal_renderer.py:536-539)
2. selected_command_index updated
3. User presses Enter
4. _handle_widget_input() detects Enter (modal_renderer.py:626-630)
5. _command_selected = True
6. input_handler detects was_command_selected() (input_handler.py:1821)
7. get_selected_command() returns session data
8. Detects action="resume_session" (input_handler.py:1827)
9. Extracts session_id from command/metadata
10. Creates SlashCommand{name="resume", args=[session_id]}
11. Calls resume handler with session_id
```

#### Flow 3: Session Loading (`/resume {session_id}`)

```
1. handle_resume() receives args=[session_id]
2. _resume_session(session_id) called
3. conversation_manager.validate_session(session_id)
   - Checks file exists
   - Validates structure
   - Checks working directory
   - Returns {valid, issues, warnings, compatibility_score}
4. If warnings and not --force: return warning message
5. conversation_manager.load_session(session_id)
   - Finds session file (JSON or JSONL)
   - Parses messages
   - Restores state
6. Load into LLM service:
   - Convert dict messages to ConversationMessage objects
   - Set llm_service.conversation_history = converted_messages
7. Return success CommandResult
```

---

## 3. File Formats

### 3.1 JSON Session Format (Preferred for full state)

**Location:** `.kollabor-cli/conversations/session_{id}_{timestamp}.json`

```json
{
  "session_id": "test_session",
  "metadata": {
    "started_at": "2025-12-11T10:00:00",
    "message_count": 5,
    "turn_count": 3,
    "topics": ["debugging", "feature"],
    "model_used": "qwen/qwen3-4b"
  },
  "summary": {
    "session_id": "test_session",
    "total_messages": 5,
    "user_messages": 3,
    "assistant_messages": 2,
    "duration": "15m",
    "topics": ["debugging"]
  },
  "messages": [
    {
      "uuid": "msg-uuid-1",
      "role": "user",
      "content": "Help me debug this",
      "timestamp": "2025-12-11T10:00:00",
      "parent_uuid": null,
      "metadata": {},
      "session_id": "test_session"
    }
  ],
  "message_index": {
    "msg-uuid-1": { /* message object */ }
  },
  "context_window": [ /* recent messages */ ],
  "current_parent_uuid": "msg-uuid-5",
  "saved_at": "2025-12-11T10:15:00"
}
```

### 3.2 JSONL Session Format (Streaming log format)

**Location:** `.kollabor-cli/conversations/session_{timestamp}.jsonl`

```jsonl
{"type": "conversation_metadata", "sessionId": "session_2025-12-11_100000", "startTime": "2025-12-11T10:00:00Z", "cwd": "/path/to/project", "gitBranch": "main", "uuid": "root-uuid"}
{"type": "user", "message": {"role": "user", "content": "Help me debug"}, "uuid": "msg-1", "timestamp": "2025-12-11T10:01:00Z"}
{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "I'll help you"}]}, "uuid": "msg-2", "timestamp": "2025-12-11T10:01:30Z"}
{"type": "conversation_end", "sessionId": "session_2025-12-11_100000", "endTime": "2025-12-11T10:15:00Z", "summary": {"total_messages": 2, "themes": ["debugging"]}}
```

### 3.3 Format Detection Logic

```python
# conversation_manager.py:371-377
if session_file.suffix == ".jsonl":
    data = self._load_from_jsonl(session_file)
else:
    with open(session_file, 'r') as f:
        data = json.load(f)
```

---

## 4. Command Interface

### 4.1 Command Syntax

```
/resume                          # Show session selection modal
/resume <session_id>             # Resume specific session
/resume <session_id> --force     # Resume ignoring warnings
/resume search <query>           # Search sessions by content
/resume --today                  # Filter today's sessions
/resume --week                   # Filter this week's sessions
/resume --limit <n>              # Limit results
```

### 4.2 Command Definition

```python
# core/commands/system_commands.py:112-129
CommandDefinition(
    name="resume",
    description="Resume a previous conversation session",
    handler=self.handle_resume,
    plugin_name=self.name,
    category=CommandCategory.CONVERSATION,
    mode=CommandMode.STATUS_TAKEOVER,
    aliases=["restore", "continue"],
    icon="[RESUME]",
    ui_config=UIConfig(
        type="modal",
        width=80,
        height=20,
        title="Resume Conversation",
        footer="... navigate ... Enter select ... Esc exit"
    )
)
```

### 4.3 Aliases

- `/restore` - Alias for /resume
- `/continue` - Alias for /resume
- `/sessions` - Browse sessions (ResumeConversationPlugin only)
- `/history` - Alias for /sessions
- `/conversations` - Alias for /sessions

---

## 5. Data Models

### 5.1 SessionMetadata (core/models/resume.py:8-23)

```python
@dataclass
class SessionMetadata:
    session_id: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    message_count: int
    turn_count: int
    working_directory: str
    git_branch: str
    themes: List[str]
    files_mentioned: List[str]
    last_activity: Optional[datetime]
    size_bytes: int
    is_valid: bool
    validation_issues: List[str]
```

### 5.2 SessionSummary (core/models/resume.py:26-34)

```python
@dataclass
class SessionSummary:
    metadata: SessionMetadata
    preview_messages: List[Dict]
    key_topics: List[str]
    user_patterns: List[str]
    project_context: Dict[str, Any]
    compatibility_score: float
```

### 5.3 ConversationMetadata (core/models/resume.py:37-54)

```python
@dataclass
class ConversationMetadata:
    file_path: str
    session_id: str
    title: str
    message_count: int
    created_time: Optional[datetime]
    modified_time: Optional[datetime]
    last_message_preview: str
    topics: List[str]
    file_id: str              # Short ID like #12345
    working_directory: str
    git_branch: str
    duration: Optional[str]
    size_bytes: int
    preview_messages: List[Dict]
    search_relevance: Optional[float] = None
```

---

## 6. Modal UI Specification

### 6.1 Sessions Section Format

The modal renderer supports a `sessions` section type for displaying conversation sessions:

```python
# modal_renderer.py:265-311
section_sessions = section.get("sessions", [])
if section_sessions:
    for sess_idx, sess in enumerate(section_sessions):
        cmd_item = {
            "name": sess.get("title", sess.get("id", "Unknown")),
            "description": sess.get("subtitle", ""),
            "session_id": sess.get("id") or sess.get("metadata", {}).get("session_id", ""),
            "action": "resume_session",
            "metadata": sess.get("metadata", {})
        }
        self.command_items.append(cmd_item)
```

### 6.2 Session Item Structure

```python
{
    "id": "session_2025-12-11_100000",
    "title": "Debugging Issue - chat_app",
    "subtitle": "5 messages ... 15m ... /Users/malmazan/dev/chat_app",
    "preview": "Help me debug this issue...",
    "metadata": {
        "session_id": "session_2025-12-11_100000",
        "file_id": "#12345",
        "working_directory": "/Users/malmazan/dev/chat_app",
        "git_branch": "main",
        "topics": ["debugging"]
    }
}
```

### 6.3 Visual Layout

```
+------------------- Resume Conversation -------------------+
|                                                           |
|   Recent Conversations (5 available)                      |
|                                                           |
|   > [abc12345] 2025-12-11 10:00                          |
|       5 messages ... /Users/malmazan/dev/chat_app         |
|                                                           |
|     [def67890] 2025-12-10 15:30                          |
|       3 messages ... /Users/malmazan/dev/other_project    |
|                                                           |
|     [ghi11111] 2025-12-09 09:15                          |
|       8 messages ... /Users/malmazan/dev/chat_app         |
|                                                           |
+-----------------------------------------------------------+
  ... navigate ... Enter select ... Tab search ... Esc exit
```

---

## 7. Validation System

### 7.1 Validation Checks (conversation_manager.py:461-549)

| Check | Condition | Result |
|-------|-----------|--------|
| File exists | Session file found | Issue if missing |
| Structure valid | Required fields present | Issue if missing |
| Working directory | Path still exists | Warning if missing |
| File references | Referenced files exist | Warning if missing |

### 7.2 Validation Result Structure

```python
{
    "valid": True,           # False if critical issues
    "issues": [],            # Critical issues (block resume)
    "warnings": [],          # Non-critical warnings
    "compatibility_score": 1.0  # 0.0 to 1.0
}
```

### 7.3 Compatibility Score Adjustments

- Original working directory missing: -0.2
- Referenced files missing: -0.1 per file (up to 3)
- Minimum score: 0.0

---

## 8. LLM Service Integration

### 8.1 Message Conversion

```python
# resume_conversation_plugin.py:408-429
from core.models import ConversationMessage

converted_messages = []
for msg in raw_messages:
    converted_messages.append(ConversationMessage(
        role=msg.get("role", "user"),
        content=msg.get("content", "")
    ))

# Replace conversation history
self.llm_service.conversation_history = converted_messages
```

### 8.2 UI Display (Attempted)

```python
# resume_conversation_plugin.py:434-450
if self.renderer and hasattr(self.renderer, 'message_coordinator'):
    # Show header
    self.renderer.message_coordinator.display_message_sequence([
        ("system", f"--- Resumed conversation ({len(display_messages)} messages) ---", {})
    ])

    # Display history
    self.renderer.message_coordinator.display_message_sequence(display_messages)

    # Show separator
    self.renderer.message_coordinator.display_message_sequence([
        ("system", "--- End of history. Continue below ---", {})
    ])
```

---

## 9. Known Issues

### 9.1 Dual Command Registration

**Issue:** Both `SystemCommandsPlugin` and `ResumeConversationPlugin` register `/resume`.

**Location:**
- `core/commands/system_commands.py:112-129`
- `plugins/resume_conversation_plugin.py:76-92`

**Impact:** Plugin loaded last takes precedence. Typically `ResumeConversationPlugin` wins.

**Resolution Options:**
1. Remove from `SystemCommandsPlugin` (delegate to plugin)
2. Remove plugin, keep in `SystemCommandsPlugin`
3. Add conflict detection in command registry

### 9.2 Message Display Not Rendered

**Issue:** Resumed messages load into `llm_service.conversation_history` but don't render in terminal UI.

**Location:** `resume_conversation_plugin.py:434-450`

**Root Cause:** The `message_coordinator.display_message_sequence()` approach may not integrate properly with the terminal rendering pipeline.

**Impact:** User sees success message but not historical conversation.

**Resolution Options:**
1. Integrate with terminal renderer's message buffer
2. Use event bus to trigger message display
3. Add dedicated "replay history" method to terminal renderer

### 9.3 Test Mock Path Mismatch

**Issue:** Tests patch incorrect import path for `get_config_directory`.

**Location:** `tests/test_resume_command.py:45`

```python
# Test uses:
patch('core.llm.conversation_manager.get_config_directory')

# Actual import in conversation_manager.py:46:
from ..utils.config_utils import get_config_directory
```

**Resolution:** Update patch path to `core.utils.config_utils.get_config_directory`

### 9.4 Import Path Fragility

**Issue:** Multiple try/except blocks for imports suggest fragile import paths.

**Location:** `core/commands/system_commands.py:463-471`

```python
try:
    from ...utils.config_utils import get_config_directory
except ImportError:
    try:
        from core.utils.config_utils import get_config_directory
    except ImportError:
        from ..utils.config_utils import get_config_directory
```

**Resolution:** Standardize import paths across codebase.

---

## 10. Test Coverage

### 10.1 Existing Tests

| Test | File | Status |
|------|------|--------|
| `test_handle_resume_no_args` | test_resume_command.py:105 | May fail (mock path) |
| `test_handle_resume_with_session_id` | test_resume_command.py:133 | Working |
| `test_handle_resume_search` | test_resume_command.py:163 | May fail (mock path) |
| `test_handle_resume_with_filters` | test_resume_command.py:191 | Working |
| `test_conversation_manager_save_session` | test_resume_command.py:220 | May fail (mock path) |
| `test_conversation_manager_load_session` | test_resume_command.py:243 | May fail (mock path) |
| `test_conversation_manager_validate_session` | test_resume_command.py:259 | May fail (mock path) |
| `test_conversation_logger_list_sessions` | test_resume_command.py:272 | Working |
| `test_conversation_logger_search_sessions` | test_resume_command.py:285 | Working |
| `test_conversation_logger_get_session_summary` | test_resume_command.py:296 | Working |
| `test_resume_plugin_initialization` | test_resume_command.py:306 | Working |
| `test_resume_plugin_handle_resume` | test_resume_command.py:338 | Working |
| `test_session_metadata_dataclass` | test_resume_command.py:358 | Working |
| `test_conversation_metadata_dataclass` | test_resume_command.py:383 | Working |

### 10.2 Missing Test Coverage

- [ ] Modal navigation (arrow keys)
- [ ] Modal selection (Enter key)
- [ ] InputHandler resume_session action handling
- [ ] JSONL format parsing edge cases
- [ ] Validation with missing files
- [ ] --force flag behavior
- [ ] Search relevance ranking
- [ ] Filter combinations

---

## 11. Configuration

### 11.1 Plugin Configuration

```python
# plugins/resume_conversation_plugin.py:782-800
@staticmethod
def get_default_config() -> Dict[str, Any]:
    return {
        "plugins": {
            "resume_conversation": {
                "enabled": True,
                "max_conversations": 50,
                "preview_length": 80,
                "auto_save_current": True,
                "confirm_load": True,
                "session_retention_days": 30
            }
        }
    }
```

### 11.2 Configuration Paths

- Session files: `.kollabor-cli/conversations/`
- Memory files: `.kollabor-cli/conversation_memory/`

---

## 12. Future Enhancements (from original spec)

### Phase 2: Advanced Features (Not Yet Implemented)

- [ ] Session diff view
- [ ] Advanced filtering UI
- [ ] Batch session operations
- [ ] Session merging

### Phase 3: Integration and Polish

- [ ] Performance optimizations (lazy loading, caching)
- [ ] Full integration test suite
- [ ] Security audit
- [ ] User documentation

---

## 13. Recommendations

### 13.1 Immediate Fixes

1. **Fix test mock paths** - Update `test_resume_command.py` to use correct import paths
2. **Resolve dual registration** - Choose single registration point for `/resume`
3. **Fix message display** - Implement proper terminal rendering for resumed messages

### 13.2 Short-term Improvements

1. Add integration tests for full modal interaction flow
2. Standardize import paths to eliminate try/except chains
3. Add session file format migration support
4. Implement session deletion command

### 13.3 Long-term Enhancements

1. Session tagging and categorization
2. Smart session recommendations
3. Cross-machine session sync
4. Session analytics dashboard

---

## Appendix A: File Reference

| File | Purpose | Key Lines |
|------|---------|-----------|
| `core/commands/system_commands.py` | SystemCommandsPlugin resume handler | 409-760 |
| `plugins/resume_conversation_plugin.py` | ResumeConversationPlugin | Full file |
| `core/llm/conversation_manager.py` | Session save/load/validate | 324-682 |
| `core/llm/conversation_logger.py` | Session discovery/search | 476-737 |
| `core/ui/modal_renderer.py` | Sessions UI format | 265-311, 524-631 |
| `core/io/input_handler.py` | Resume action handling | 1827-1850 |
| `core/models/resume.py` | Data models | Full file |
| `tests/test_resume_command.py` | Unit tests | Full file |

---

## Appendix B: Event Types

| Event | Purpose | Source |
|-------|---------|--------|
| `STATUS_CONTENT_UPDATE` | Notify UI of conversation change | system_commands.py:581 |
| `RESUME_RENDERING` | Resume terminal rendering | input_handler.py:1299 |

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| Session | A complete conversation with metadata and messages |
| Session ID | Unique identifier for a session (e.g., `session_2025-12-11_100000`) |
| JSONL | JSON Lines format - one JSON object per line |
| Compatibility Score | 0.0-1.0 rating of how well a session matches current environment |
| Turn | One user message (turn_count = number of user messages) |
