# Resume Conversation Plugin Specification

## Overview

A comprehensive plugin for managing conversation sessions in Kollabor CLI, providing
functionality to resume previous conversations, browse session history, search conversations,
and create conversation branches from any point in time.

## Core Features

### 1. Session Management
- Resume previous conversations by session ID
- Browse available sessions with rich metadata display
- Search conversations by content
- Filter conversations by date/time criteria
- Display session metadata (messages count, duration, project, git branch)

### 2. Conversation Branching
- Branch conversations from any message point
- Branch from current active conversation
- Branch from saved sessions
- Preserve original conversation while creating new branch
- Display branch lineage and metadata

### 3. Interactive UI
- Modal-based session selection with keyboard navigation
- Rich session previews with first user message
- Metadata display (timestamp, message count, duration, project, git branch)
- Search results with relevance scoring
- Multi-step branching workflow (session -> message -> execute)

## Architecture

### Plugin Class Structure

```python
class ResumeConversationPlugin:
    """Plugin for resuming previous conversations."""

    # Core attributes
    name: str = "resume_conversation"
    version: str = "1.0.0"
    description: str = "Resume previous conversation sessions"
    enabled: bool = True

    # Dependencies (injected during initialization)
    conversation_manager: ConversationManager
    conversation_logger: KollaborConversationLogger
    state_manager: StateManager
    event_bus: EventBus
    config: ConfigManager
    llm_service: LLMService
    renderer: TerminalRenderer
```

### Lifecycle Methods

1. **`__init__(**kwargs)`**
   - Initialize plugin metadata
   - Set dependencies to None (will be injected)
   - Initialize logger

2. **`async initialize(event_bus, config, **kwargs)`**
   - Store event bus and config references
   - Extract dependencies from kwargs
   - Register slash commands via command_registry
   - Log successful initialization

3. **`async register_hooks()`**
   - Register MODAL_COMMAND_SELECTED event hook
   - Priority: 10
   - Callback: `_handle_modal_command`

4. **`async shutdown()`**
   - Cleanup resources
   - Log shutdown completion

### Dependencies

Required services injected via kwargs:
- **conversation_manager**: Session loading, branching, message retrieval
- **conversation_logger**: Session discovery, listing, searching
- **state_manager**: State persistence
- **llm_service**: Active conversation access, history management
- **renderer**: Display coordination via message_coordinator
- **command_registry**: Slash command registration

## Slash Commands

### /resume Command

**Aliases:** /restore, /continue

**Icon:** [⏯]

**Category:** CONVERSATION

**Mode:** STATUS_TAKEOVER

**UI:** Modal (80x20)

**Usage Patterns:**

```bash
/resume                           # Show session selection modal
/resume <session_id>              # Resume specific session
/resume <session_id> --force      # Resume without confirmation
/resume search <query>            # Search sessions
/resume --today                   # Filter today's sessions
/resume --week                    # Filter last week's sessions
/resume --limit 10                # Limit results to 10
```

**Implementation:**
- `handle_resume(command: SlashCommand) -> CommandResult`
- Delegates to:
  - `_show_conversation_menu()` - no args
  - `_load_conversation(session_id, force)` - with session_id
  - `_search_conversations(query)` - with search keyword
  - `_handle_resume_options(args)` - with filters

### /sessions Command

**Aliases:** /history, /conversations

**Icon:** [📚]

**Category:** CONVERSATION

**Mode:** STATUS_TAKEOVER

**UI:** Modal (80x20)

**Usage Patterns:**

```bash
/sessions                         # Show all sessions
/sessions search <query>          # Search sessions
```

**Implementation:**
- `handle_sessions(command: SlashCommand) -> CommandResult`
- Delegates to:
  - `_show_conversation_menu()` - no args
  - `_search_conversations(query)` - with search

### /branch Command

**Aliases:** /fork

**Icon:** [⑂]

**Category:** CONVERSATION

**Mode:** STATUS_TAKEOVER

**UI:** Modal (80x20)

**Usage Patterns:**

```bash
/branch                           # Show sessions to branch from
/branch <session_id>              # Show messages in session
/branch <session_id> <index>      # Create branch at message index
```

**Implementation:**
- `handle_branch(command: SlashCommand) -> CommandResult`
- Three-step workflow:
  1. `_show_branch_session_selector()` - Select source session
  2. `_show_branch_point_selector(session_id)` - Select branch point
  3. `_execute_branch_from_session(session_id, index)` - Execute branch

## Core Methods

### Session Discovery

**`async discover_conversations(limit: int = 50) -> List[ConversationMetadata]`**

Discover available conversations from conversation logger.

**Logic:**
1. Get sessions from conversation_logger.list_sessions()
2. Filter sessions with < 2 messages
3. Strip "session_" prefix from session_id for compatibility
4. Build ConversationMetadata objects with:
   - file_path, session_id, title
   - message_count, created_time, modified_time
   - last_message_preview, topics
   - working_directory, git_branch, duration
   - size_bytes, preview_messages
5. Return up to limit conversations

**Error Handling:**
- Log warnings for session processing failures
- Continue processing remaining sessions
- Return empty list on critical errors

### Session Loading

**`async _load_conversation(session_id: str, force: bool = False) -> CommandResult`**

Load specific conversation by session ID.

**Logic:**
1. Ensure conversation_manager available
2. Load session via conversation_manager.load_session(session_id)
3. Delegate to `_load_and_display_session()` with header/success messages
4. Return CommandResult

**Error Handling:**
- Return error if conversation_manager unavailable
- Return error if load_session fails
- Catch and log exceptions

### Session Display

**`_load_and_display_session(header: str, success_msg: str) -> CommandResult`**

Load session into llm_service and display in UI.

**Logic:**
1. Read messages from conversation_manager.messages
2. Convert to ConversationMessage objects
3. Build display_messages list:
   - Add header as system message
   - Add user/assistant messages for display
   - Add success_msg as system message
4. Update llm_service.conversation_history
5. Update llm_service.session_stats["messages"]
6. Display via renderer.message_coordinator.display_message_sequence()
7. Return success CommandResult with empty message

**Note:** Used by both resume and branch operations after session is loaded.

### Branching Operations

**`async _execute_branch_from_session(session_id: str, branch_index: int) -> CommandResult`**

Execute branch operation - create new session from branch point.

**Current Conversation Handling:**
1. If session_id == "current":
   - Validate llm_service and conversation_history available
   - Validate branch_index in range
   - Truncate conversation_history to [:branch_index + 1]
   - Update session_stats["messages"]
   - Return success with message count

**Saved Session Handling:**
1. Call conversation_manager.branch_session(session_id, branch_index)
2. Check result["success"]
3. Get new_session_id from result
4. Load and display new session with branch metadata
5. Return CommandResult

### Modal Building

**`_build_conversation_modal(conversations: List[ConversationMetadata]) -> Dict[str, Any]`**

Build conversation selection modal definition.

**Session Item Format:**
```python
{
    "id": conv.session_id,
    "title": "[12/11 14:30] First line of user request...",
    "subtitle": "15 msgs | 45m | project-name | main",
    "preview": "Last message preview...",
    "action": "resume_session",
    "exit_mode": "minimal",
    "metadata": {
        "session_id": conv.session_id,
        "file_id": conv.file_id,
        "working_directory": conv.working_directory,
        "git_branch": conv.git_branch,
        "topics": conv.topics
    }
}
```

**Modal Structure:**
```python
{
    "title": "Resume Conversation",
    "footer": "↑↓ navigate • Enter select • Tab search • F filter • Esc exit",
    "width": 80,
    "height": 20,
    "sections": [
        {
            "title": f"Recent Conversations ({count} available)",
            "type": "session_list",
            "sessions": session_items
        }
    ],
    "actions": [
        {"key": "Enter", "label": "Resume", "action": "select"},
        {"key": "Tab", "label": "Search", "action": "search"},
        {"key": "F", "label": "Filter", "action": "filter"},
        {"key": "Escape", "label": "Cancel", "action": "cancel"}
    ]
}
```

**`_build_search_modal(conversations, query) -> Dict[str, Any]`**

Build search results modal.

**Differences from conversation modal:**
- Title includes query: "Search Results: {query}"
- Session titles include relevance score: "[87%]"
- Simplified footer: "↑↓ navigate • Enter select • Esc back"

**`_build_filtered_modal(conversations, filters) -> Dict[str, Any]`**

Build filtered results modal.

**Differences:**
- Title includes filter description
- Parses filters dict to build description
- Shows applied filters in title

### Branch UI Methods

**`async _show_branch_session_selector() -> CommandResult`**

Show modal to select session to branch from.

**Current Session Handling:**
1. Check if llm_service has conversation_history
2. Count messages in current conversation
3. If >= 2 messages, add as first option:
   - id: "current"
   - title: "[*CURRENT*] {first_user_msg}"
   - subtitle: "{count} msgs | this session"

**Saved Sessions:**
1. Get conversations via discover_conversations(limit=20)
2. Format each with timestamp, first user message, metadata
3. Build session_items list

**Modal:**
- Title: "Branch From Session"
- Action: "branch_select_session"
- Footer: "Up/Down navigate | Enter select | Esc cancel"

**`async _show_branch_point_selector(session_id: str) -> CommandResult`**

Show modal to select branch point message.

**Current vs Saved:**
- If session_id == "current": read from llm_service.conversation_history
- Else: get messages via conversation_manager.get_session_messages()

**Message Item Format:**
```python
{
    "id": str(index),
    "title": "[{index}] -> User message preview...",
    "subtitle": "user | 2025-12-13 14:30",
    "metadata": {
        "session_id": session_id,
        "message_index": index
    },
    "action": "branch_execute",
    "exit_mode": "minimal"
}
```

**Role Indicators:**
- User messages: "->"
- Assistant messages: "<-"

### Event Handling

**`async _handle_modal_command(data: Dict[str, Any], event: Event) -> Dict[str, Any]`**

Handle modal command selection events.

**Action Types:**

1. **"resume_session"**
   - Extract session_id from command or metadata
   - Load session via conversation_manager.load_session()
   - Prepare display messages via _prepare_session_display()
   - Add to data["display_messages"]

2. **"branch_select_session"**
   - Extract session_id
   - Show branch point selector modal
   - Add modal config to data["show_modal"]

3. **"branch_execute"**
   - Extract session_id and message_index from metadata
   - Execute branch via conversation_manager.branch_session()
   - Prepare display messages with branch metadata
   - Add to data["display_messages"]

**Return:** Modified data dict

### Helper Methods

**`_generate_session_title(session_data: Dict) -> str`**

Generate descriptive title for session.

**Logic:**
1. Extract topics and working_directory
2. Get project name from directory path
3. If topics exist: "{main_topic} - {project_name}"
4. Else: "Conversation - {project_name}"

**`_generate_file_id(session_id: str) -> str`**

Generate short file ID for display.

**Logic:**
1. Hash session_id
2. Modulo 100000
3. Format as "#12345"

**`_parse_datetime(dt_str: Optional[str]) -> Optional[datetime]`**

Parse datetime string.

**Logic:**
1. Return None if empty
2. Replace 'Z' with '+00:00' for ISO format
3. Parse via datetime.fromisoformat()
4. Return None on error

**`_ensure_conversation_manager() -> bool`**

Ensure conversation_manager is available.

**Logic:**
1. If already exists, return True
2. Try to create one:
   - Import ConversationManager
   - Create BasicConfig with get() method
   - Get conversations directory
   - Instantiate ConversationManager
3. Return True if successful, False otherwise

**`_prepare_session_display(header: str, success_msg: str) -> list`**

Prepare session messages for display.

**Logic:**
1. Read messages from conversation_manager.messages
2. Build ConversationMessage objects
3. Build display_messages list
4. Update llm_service.conversation_history
5. Update session_stats
6. Return display_messages (without displaying)

**Note:** Similar to _load_and_display_session but returns messages instead of displaying.

### Search & Filtering

**`async _search_conversations(query: str) -> CommandResult`**

Search conversations by content.

**Logic:**
1. Call conversation_logger.search_sessions(query)
2. Limit to 20 results
3. Build ConversationMetadata objects with search_relevance
4. Build search modal with query and results
5. Return CommandResult with modal

**`async _handle_resume_options(args: List[str]) -> CommandResult`**

Handle resume filters and options.

**Supported Filters:**
- `--today`: Filter today's conversations
- `--week`: Filter last 7 days
- `--limit N`: Limit results to N

**Logic:**
1. Parse args to extract filters
2. Discover conversations
3. Apply filters to conversations
4. Build filtered modal
5. Return CommandResult

## Data Models

### ConversationMetadata

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
    file_id: str
    working_directory: str
    git_branch: str
    duration: Optional[str]
    size_bytes: int
    preview_messages: List[Dict]
    search_relevance: Optional[float] = None
```

### CommandDefinition

```python
@dataclass
class CommandDefinition:
    name: str
    description: str
    handler: Callable
    plugin_name: str
    category: CommandCategory
    mode: CommandMode
    aliases: List[str]
    icon: str
    ui_config: UIConfig
```

### UIConfig

```python
@dataclass
class UIConfig:
    type: str  # "modal"
    title: str
    width: int = 80
    height: int = 20
    modal_config: Optional[Dict] = None
```

### CommandResult

```python
@dataclass
class CommandResult:
    success: bool
    message: str
    display_type: str  # "success", "error", "info", "modal"
    ui_config: Optional[UIConfig] = None
```

## Configuration

**Default Config:**

```python
{
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

## Event System Integration

### Registered Hooks

**Event:** MODAL_COMMAND_SELECTED

**Priority:** 10

**Handler:** `_handle_modal_command`

**Purpose:** Handle modal command selections for resume and branch operations

### Event Data Flow

1. User selects item in modal
2. Modal system fires MODAL_COMMAND_SELECTED event
3. Plugin receives event with command data
4. Plugin extracts action and metadata
5. Plugin performs action (load session, show branch modal, execute branch)
6. Plugin modifies event data with display_messages or show_modal
7. Modal system processes modified data
8. UI updates accordingly

## UI Workflow Diagrams

### Resume Workflow

```
/resume
   |
   v
[Show Conversation Modal]
   |
   |-- User presses Enter on session
   |      |
   |      v
   |   MODAL_COMMAND_SELECTED event
   |      |
   |      v
   |   _handle_modal_command (action: resume_session)
   |      |
   |      v
   |   Load session into conversation_manager
   |      |
   |      v
   |   Load messages into llm_service
   |      |
   |      v
   |   Display messages via message_coordinator
   |      |
   |      v
   |   [Conversation Resumed]
```

### Branch Workflow

```
/branch
   |
   v
[Show Session Selector]
   |
   |-- User selects session
   |      |
   |      v
   |   MODAL_COMMAND_SELECTED event (action: branch_select_session)
   |      |
   |      v
   |   [Show Message Selector for chosen session]
   |      |
   |      |-- User selects message
   |      |      |
   |      |      v
   |      |   MODAL_COMMAND_SELECTED event (action: branch_execute)
   |      |      |
   |      |      v
   |      |   Create branch via conversation_manager
   |      |      |
   |      |      v
   |      |   Load branched session
   |      |      |
   |      |      v
   |      |   Display messages
   |      |      |
   |      |      v
   |      |   [Branch Created and Loaded]
```

### Search Workflow

```
/sessions search <query>
   |
   v
Search via conversation_logger
   |
   v
[Show Search Results Modal]
   |
   |-- User selects session
   |      |
   |      v
   |   MODAL_COMMAND_SELECTED event (action: resume_session)
   |      |
   |      v
   |   Load and display session
   |      |
   |      v
   |   [Conversation Resumed]
```

## Error Handling

### Strategy

1. **Graceful Degradation**: Return error CommandResult instead of crashing
2. **Informative Messages**: Provide clear error messages to user
3. **Logging**: Log all errors for debugging
4. **Fallbacks**: Create conversation_manager if not injected

### Error Types

**Missing Dependencies:**
```python
if not self.conversation_manager:
    return CommandResult(
        success=False,
        message="Conversation manager not available",
        display_type="error"
    )
```

**Invalid Input:**
```python
if branch_index < 0 or branch_index >= len(messages):
    return CommandResult(
        success=False,
        message=f"Invalid index. Must be 0-{len(messages)-1}.",
        display_type="error"
    )
```

**Operation Failures:**
```python
if not result.get("success"):
    return CommandResult(
        success=False,
        message=f"Branch failed: {result.get('error', 'Unknown error')}",
        display_type="error"
    )
```

## Testing Strategy

### Unit Tests

1. **Command Handlers**
   - Test /resume with various args
   - Test /sessions with search
   - Test /branch multi-step workflow

2. **Session Discovery**
   - Test discover_conversations with limit
   - Test session filtering
   - Test metadata generation

3. **Modal Building**
   - Test conversation modal structure
   - Test search modal structure
   - Test filtered modal structure

4. **Event Handling**
   - Test resume_session action
   - Test branch_select_session action
   - Test branch_execute action

### Integration Tests

1. **Full Resume Flow**
   - Discover → Select → Load → Display

2. **Full Branch Flow**
   - Select Session → Select Message → Execute → Display

3. **Search Flow**
   - Search → Select → Load → Display

### Mock Dependencies

```python
class MockConversationManager:
    def load_session(self, session_id: str) -> bool:
        return True

    def branch_session(self, session_id: str, index: int) -> Dict:
        return {
            "success": True,
            "session_id": "new_session_123",
            "branch_point": index,
            "message_count": 10
        }

    def get_session_messages(self, session_id: str) -> List[Dict]:
        return [
            {"index": 0, "role": "user", "preview": "Test", "timestamp": None}
        ]

class MockConversationLogger:
    def list_sessions(self) -> List[Dict]:
        return [
            {
                "session_id": "test_123",
                "message_count": 5,
                "start_time": "2025-12-13T10:00:00",
                "preview_messages": [{"role": "user", "content": "Test"}]
            }
        ]

    def search_sessions(self, query: str) -> List[Dict]:
        return self.list_sessions()
```

## Implementation Checklist

- [ ] Create plugin class with metadata
- [ ] Implement __init__ with dependency placeholders
- [ ] Implement async initialize() with dependency injection
- [ ] Implement _register_resume_commands() for /resume, /sessions, /branch
- [ ] Implement handle_resume() with all usage patterns
- [ ] Implement handle_sessions() with search
- [ ] Implement handle_branch() with three-step workflow
- [ ] Implement async discover_conversations()
- [ ] Implement _show_conversation_menu()
- [ ] Implement _search_conversations()
- [ ] Implement _load_conversation()
- [ ] Implement _load_and_display_session()
- [ ] Implement _prepare_session_display()
- [ ] Implement _execute_branch_from_session()
- [ ] Implement _show_branch_session_selector()
- [ ] Implement _show_branch_point_selector()
- [ ] Implement _build_conversation_modal()
- [ ] Implement _build_search_modal()
- [ ] Implement _build_filtered_modal()
- [ ] Implement _handle_resume_options() with filters
- [ ] Implement async register_hooks()
- [ ] Implement async _handle_modal_command()
- [ ] Implement _generate_session_title()
- [ ] Implement _generate_file_id()
- [ ] Implement _parse_datetime()
- [ ] Implement _ensure_conversation_manager()
- [ ] Implement get_default_config()
- [ ] Implement get_status_line()
- [ ] Implement async shutdown()
- [ ] Add comprehensive docstrings
- [ ] Add type hints
- [ ] Add error handling
- [ ] Add logging
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Test with mock dependencies
- [ ] Test with real conversation data
- [ ] Validate modal UI rendering
- [ ] Validate keyboard navigation
- [ ] Validate event handling
- [ ] Test edge cases (empty sessions, invalid IDs, etc.)

## Future Enhancements

1. **Export/Import**: Export sessions to markdown, import from other formats
2. **Merge Sessions**: Combine multiple sessions into one
3. **Session Tags**: Tag sessions for better organization
4. **Advanced Search**: Full-text search with regex support
5. **Session Templates**: Create new sessions from templates
6. **Collaboration**: Share sessions with team members
7. **Analytics**: Session statistics and insights
8. **Backup/Restore**: Backup sessions to cloud storage

## Dependencies Required

```
# Core imports
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

# Kollabor core
from core.events.models import (
    CommandDefinition, CommandMode, CommandCategory,
    CommandResult, SlashCommand, UIConfig, Event,
    EventType, Hook
)
from core.models.resume import (
    SessionMetadata, SessionSummary, ConversationMetadata
)
from core.models import ConversationMessage
from core.llm.conversation_manager import ConversationManager
from core.utils.config_utils import get_config_directory
```

## File Structure

```
plugins/
└── resume_conversation_plugin.py    # 1294 lines

core/
├── models/
│   └── resume.py                     # ConversationMetadata, SessionMetadata, etc.
└── llm/
    └── conversation_manager.py       # Session loading and branching
```
