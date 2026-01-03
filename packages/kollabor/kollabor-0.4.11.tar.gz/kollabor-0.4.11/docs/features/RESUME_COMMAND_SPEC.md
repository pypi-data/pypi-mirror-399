
# /resume Command Specification

## Overview

The `/resume` command provides conversation restoration capabilities, allowing users to continue previous chat sessions with full context preservation. This feature integrates with the existing conversation logging and management systems to provide seamless session continuity.

## Purpose

The `/resume` command addresses the need for:
- **Session Continuity**: Users often work on complex tasks across multiple sessions
- **Context Preservation**: Maintain conversation history, threading, and learned patterns
- **Workflow Efficiency**: Avoid re-explaining context when returning to previous work
- **Project State Management**: Resume work in the same project context and environment

## Feature Requirements

### Core Functionality

1. **Session Discovery**
   - List available conversation sessions with metadata
   - Display session information (timestamp, message count, git branch, working directory)
   - Support filtering and searching of sessions

2. **Interactive Selection**
   - Modal interface for browsing and selecting sessions
   - Keyboard navigation (arrow keys, Enter, Escape)
   - Session preview with summary information

3. **Conversation Restoration**
   - Full message history restoration with threading
   - Preserve message UUIDs and parent-child relationships
   - Maintain conversation context and metadata

4. **Context Integration**
   - Restore learned user patterns and project context
   - Re-establish session metadata (git branch, working directory)
   - Maintain conversation themes and intelligence features

5. **Session Management**
   - Save current session before switching (if applicable)
   - Handle session conflicts and validation
   - Provide rollback capabilities for failed resumes

### Advanced Features

1. **Smart Resume**
   - Detect changes in working directory and project state
   - Validate file existence and dependencies
   - Provide diff view of changes since original session

2. **Search Capabilities**
   - Search sessions by content keywords
   - Filter by date range, git branch, or message count
   - Find sessions related to specific files or topics

3. **Resume Validation**
   - Check if referenced files still exist
   - Validate project structure consistency
   - Warn about potential context loss

4. **Partial Resume**
   - Resume specific message threads
   - Selective context restoration
   - Merge multiple sessions

## Technical Architecture

### Integration Points

The `/resume` command integrates with multiple existing systems:

#### Conversation Manager (`core/llm/conversation_manager.py`)
```python
# Extend with resume capabilities
class ConversationManager:
    def save_session(self, session_id: str) -> bool:
        """Save current session state."""
        
    def load_session(self, session_id: str) -> bool:
        """Load session from storage."""
        
    def get_available_sessions(self) -> List[Dict]:
        """Get list of available sessions."""
        
    def validate_session(self, session_id: str) -> Dict:
        """Validate session for resume compatibility."""
```

#### Conversation Logger (`core/llm/conversation_logger.py`)
```python
# Extend for session discovery
class KollaborConversationLogger:
    def list_sessions(self, filters: Dict = None) -> List[Dict]:
        """List available sessions with metadata."""
        
    def get_session_summary(self, session_id: str) -> Dict:
        """Get session summary for preview."""
        
    def search_sessions(self, query: str) -> List[Dict]:
        """Search sessions by content."""
```

#### State Manager (`core/storage/state_manager.py`)
```python
# Extend for session persistence
class StateManager:
    def set_session_state(self, session_id: str, state: Dict):
        """Store session state."""
        
    def get_session_state(self, session_id: str) -> Dict:
        """Retrieve session state."""
```

### Command Implementation

#### Command Registration
```python
# In core/commands/system_commands.py
resume_command = CommandDefinition(
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
        footer="↑↓ navigate • Enter select • Esc exit • /help resume"
    )
)
```

#### Handler Implementation
```python
async def handle_resume(self, command: SlashCommand) -> CommandResult:
    """Handle /resume command."""
    try:
        # Parse arguments
        args = command.args or []
        
        if len(args) == 0:
            # Show session selection modal
            return await self._show_session_selector()
        elif len(args) == 1:
            # Resume specific session by ID
            session_id = args[0]
            return await self._resume_session(session_id)
        else:
            # Handle search/filter arguments
            return await self._search_and_resume(args)
            
    except Exception as e:
        self.logger.error(f"Error in resume command: {e}")
        return CommandResult(
            success=False,
            message=f"Error resuming session: {str(e)}",
            display_type="error"
        )
```

### Data Structures

#### Session Metadata
```python
@dataclass
class SessionMetadata:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    message_count: int
    turn_count: int
    working_directory: str
    git_branch: str
    themes: List[str]
    files_mentioned: List[str]
    last_activity: datetime
    size_bytes: int
    is_valid: bool
    validation_issues: List[str]
```

#### Session Summary
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

### Modal Interface Design

#### Session Selection Modal
```python
def _get_resume_modal_definition(self) -> Dict[str, Any]:
    """Get modal definition for session selection."""
    return {
        "title": "Resume Conversation",
        "footer": "↑↓ navigate • Enter select • Esc exit • Tab search • F filter",
        "width": 80,
        "height": 20,
        "sections": [
            {
                "title": "Recent Sessions",
                "type": "session_list",
                "sessions": self._get_recent_sessions()
            },
            {
                "title": "Search",
                "type": "search_box",
                "placeholder": "Search sessions by content..."
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

#### Session Preview Modal
```python
def _get_session_preview_definition(self, session_id: str) -> Dict[str, Any]:
    """Get modal definition for session preview."""
    summary = self.conversation_logger.get_session_summary(session_id)
    
    return {
        "title": f"Session: {session_id}",
        "footer": "Enter resume • Esc back • Tab details",
        "width": 80,
        "height": 20,
        "sections": [
            {
                "title": "Session Information",
                "type": "info",
                "data": {
                    "Started": summary.metadata.start_time.strftime("%Y-%m-%d %H:%M"),
                    "Duration": self._format_duration(summary.metadata),
                    "Messages": summary.metadata.message_count,
                    "Directory": summary.metadata.working_directory,
                    "Git Branch": summary.metadata.git_branch
                }
            },
            {
                "title": "Key Topics",
                "type": "tags",
                "tags": summary.key_topics
            },
            {
                "title": "Preview",
                "type": "message_preview",
                "messages": summary.preview_messages
            }
        ]
    }
```

## Implementation Plan

### Phase 1: Core Resume Functionality

1. **Extend Conversation Manager**
   - Add `save_session()` and `load_session()` methods
   - Implement session state serialization
   - Add session validation logic

2. **Extend Conversation Logger**
   - Add `list_sessions()` method
   - Implement `get_session_summary()` method
   - Add session metadata extraction

3. **Implement Basic Command**
   - Add `/resume` command to SystemCommandsPlugin
   - Implement session listing and selection
   - Add basic resume functionality

4. **Create Modal Interface**
   - Design session selection modal
   - Implement keyboard navigation
   - Add session preview functionality

### Phase 2: Advanced Features

1. **Search and Filter**
   - Implement content search across sessions
   - Add filtering by date, branch, directory
   - Add search result ranking

2. **Smart Resume**
   - Add environment validation
   - Implement change detection
   - Add compatibility scoring

3. **Enhanced UI**
   - Add session diff view
   - Implement advanced filtering
   - Add batch operations

### Phase 3: Integration and Polish

1. **Error Handling**
   - Comprehensive error scenarios
   - Graceful degradation
   - User-friendly error messages

2. **Performance Optimization**
   - Efficient session loading
   - Lazy loading for large sessions
   - Caching strategies

3. **Testing**
   - Unit tests for all components
   - Integration tests for end-to-end flow
   - Performance tests for large datasets

## Configuration

### Default Configuration
```python
# In plugins/system_commands_plugin.py
@staticmethod
def get_default_config() -> Dict[str, Any]:
    return {
        "plugins": {
            "system_commands": {
                "resume": {
                    "enabled": True,
                    "max_sessions_shown": 20,
                    "preview_message_count": 3,
                    "auto_save_current": True,
                    "validate_environment": True,
                    "cache_session_summaries": True,
                    "default_sort": "last_activity",  # last_activity, start_time, message_count
                    "search_indexing": True
                }
            }
        }
    }
```

### User Preferences
```python
# Runtime configuration options
resume_config = {
    "show_hidden_sessions": False,
    "auto_preview": True,
    "confirm_before_resume": True,
    "save_on_switch": True,
    "session_retention_days": 30,
    "index_content": True
}
```

## Error Handling

### Error Scenarios

1. **Session Not Found**
   ```python
   return CommandResult(
       success=False,
       message=f"Session '{session_id}' not found",
       display_type="error",
       data={"suggestions": self._get_similar_sessions(session_id)}
   )
   ```

2. **Session Corruption**
   ```python
   return CommandResult(
       success=False,
       message="Session file is corrupted or incomplete",
       display_type="error",
       data={"repair_options": self._get_repair_options(session_id)}
   )
   ```

3. **Environment Mismatch**
   ```python
   return CommandResult(
       success=False,
       message="Working directory has changed significantly",
       display_type="warning",
       data={
           "old_directory": session.working_directory,
           "new_directory": str(Path.cwd()),
           "changes": self._detect_environment_changes(session)
       }
   )
   ```

4. **File Dependencies Missing**
   ```python
   return CommandResult(
       success=False,
       message="Some referenced files are no longer available",
       display_type="warning",
       data={
           "missing_files": missing_files,
           "resume_anyway": True
       }
   )
   ```

### Recovery Strategies

1. **Partial Resume**
   - Resume conversation without file-dependent context
   - Mark missing references in conversation
   - Allow manual correction

2. **Session Repair**
   - Attempt to fix corrupted session files
   - Rebuild message threading from available data
   - Preserve as much context as possible

3. **Environment Sync**
   - Offer to change to original working directory
   - Suggest git checkout for original branch
   - Provide manual override options

## Testing Strategy

### Unit Tests

1. **Conversation Manager Tests**
   ```python
   def test_save_session(self):
       """Test session state saving."""
       
   def test_load_session(self):
       """Test session state loading."""
       
   def test_validate_session(self):
       """Test session validation."""
   ```

2. **Command Handler Tests**
   ```python
   def test_resume_command_no_args(self):
       """Test resume command without arguments."""
       
   def test_resume_command_with_session_id(self):
       """Test resume command with specific session ID."""
       
   def test_resume_command_search(self):
       """Test resume command with search."""
   ```

3. **Modal Interface Tests**
   ```python
   def test_session_selection_modal(self):
       """Test session selection modal rendering."""
       
   def test_session_preview_modal(self):
       """Test session preview modal rendering."""
   ```

### Integration Tests

1. **End-to-End Resume Flow**
   ```python
   def test_complete_resume_workflow(self):
       """Test complete resume from command to conversation restoration."""
   ```

2. **Multi-Session Management**
   ```python
   def test_session_switching(self):
       """Test switching between multiple sessions."""
   ```

3. **Error Recovery Tests**
   ```python
   def test_resume_corrupted_session(self):
       """Test handling of corrupted sessions."""
   ```

### Performance Tests

1. **Large Session Handling**
   ```python
   def test_resume_large_session(self):
       """Test resuming sessions with many messages."""
   ```

2. **Search Performance**
   ```python
   def test_session_search_performance(self):
       """Test search performance across many sessions."""
   ```

## Security Considerations

### Data Protection

1. **Sensitive Content**
   - Mask or redact sensitive information in session previews
   - Provide options to exclude sensitive sessions from listings
   - Implement content filtering for shared environments

2. **Path Validation**
   - Validate working directory paths to prevent directory traversal
   - Sanitize file paths in session metadata
   - Check permissions before accessing session files

3. **Access Control**
   - Restrict access to sessions based on file permissions
   - Implement user-based session isolation
   - Provide audit logging for resume operations

### Privacy Features

1. **Session Expiration**
   - Automatic cleanup of old sessions
   - Configurable retention policies
   - Manual session deletion options

2. **Content Filtering**
   - Option to exclude sessions with sensitive patterns
   - Private mode that disables session logging
   - Selective session export/import

## Future Enhancements

### Planned Features

1. **Cloud Sync**
   - Sync sessions across multiple machines
   - Conflict resolution for concurrent access
   - Offline mode support

2. **Collaborative Sessions**
   - Share sessions between users
   - Merge conversation histories
   - Multi-user session management

3. **AI-Powered Features**
   - Automatic session summarization
   - Smart session recommendations
   - Context-aware search suggestions

4. **Advanced Analytics**
   - Session usage patterns
   - Productivity metrics
   - Project progress tracking

### Extension Points

1. **Custom Resume Handlers**
   - Plugin-specific resume logic
   - Custom validation rules
   - Specialized UI components

2. **Session Transformers**
   - Content filtering and transformation
   - Format conversion utilities
   - Migration tools

3. **Integration Hooks**
   - External tool integration
   - Workflow automation
   - Event-driven actions

## Conclusion

The `/resume` command provides a comprehensive solution for conversation continuity in Kollabor. By leveraging the existing conversation management and logging systems, it offers seamless session restoration with full context preservation. The modular design allows for incremental implementation and future extensibility.

The specification balances functionality with performance, ensuring efficient operation even with large conversation histories. Comprehensive error handling and security measures provide a robust foundation for production use.

Through careful integration with the existing slash command system and modal UI framework, `/resume` delivers a consistent user experience that aligns with Kollabor's design principles and interaction patterns.

---

## Implementation Status

### Completed Features (as of 2025-12-11)

#### Core Components Implemented

1. **ConversationManager Extensions** (`core/llm/conversation_manager.py`)
   - [x] `save_session(session_id)` - Saves current session to JSON/JSONL
   - [x] `load_session(session_id)` - Loads session from storage into `self.messages`
   - [x] `get_available_sessions()` - Lists all available sessions with metadata
   - [x] `validate_session(session_id)` - Validates session compatibility

2. **ConversationLogger Extensions** (`core/llm/conversation_logger.py`)
   - [x] `list_sessions(filters)` - Lists sessions with optional filters
   - [x] `search_sessions(query)` - Content search across sessions
   - [x] `get_session_summary(session_id)` - Session preview information

3. **Resume Command Implementation**
   - [x] `/resume` command in `SystemCommandsPlugin` (`core/commands/system_commands.py`)
   - [x] `/resume` command in `ResumeConversationPlugin` (`plugins/resume_conversation_plugin.py`)
   - [x] Session selection modal with "sessions" format support
   - [x] Keyboard navigation (arrow keys, Enter, Escape)
   - [x] LLM service integration - loads messages into `conversation_history`

4. **Modal Renderer Updates** (`core/ui/modal_renderer.py`)
   - [x] Support for "commands" section format
   - [x] Support for "sessions" section format (title/subtitle display)
   - [x] Selection state tracking (`selected_command_index`)
   - [x] Visual selection indicator (`>`)
   - [x] Navigation with arrow keys
   - [x] Enter key selection handling
   - [x] `_command_selected` state reset on modal open

5. **Input Handler Integration** (`core/io/input_handler.py`)
   - [x] Modal command selection handling
   - [x] `resume_session` action detection
   - [x] Session ID extraction from command metadata
   - [x] Resume command execution
   - [x] Result message display to terminal

6. **Data Models** (`core/models/resume.py`)
   - [x] `SessionMetadata` dataclass
   - [x] `SessionSummary` dataclass
   - [x] `ConversationMetadata` dataclass

### Known Issues

1. **Dual Command Registration**: Both `SystemCommandsPlugin` and `ResumeConversationPlugin` register `/resume`. The plugin's version takes precedence (loaded last).

2. **Message Display**: Resumed conversations load into `llm_service.conversation_history` for LLM context, but historical messages are not re-rendered in the terminal UI. User sees confirmation message only.

3. **Test Failures**: Some unit tests fail due to mock patch path issues (`get_config_directory`).

### Files Modified

| File | Changes |
|------|---------|
| `core/application.py` | Added `llm_service` to plugin init kwargs |
| `core/commands/system_commands.py` | Added resume handler with LLM integration |
| `core/ui/modal_renderer.py` | Added sessions format support, selection state |
| `core/io/input_handler.py` | Added resume action handling, result display |
| `plugins/resume_conversation_plugin.py` | Added `llm_service` dependency, LLM integration |

## Implementation Checklist

### Phase 1: Core Functionality
- [x] Extend `ConversationManager` with session save/load methods
- [x] Extend `ConversationLogger` with session discovery capabilities
- [x] Implement basic `/resume` command in `SystemCommandsPlugin`
- [x] Create session selection modal interface
- [x] Add keyboard navigation and session preview
- [x] Implement basic conversation restoration

### Phase 2: Advanced Features
- [x] Add content search across sessions
- [x] Implement filtering by date, branch, directory
- [x] Add environment validation and change detection
- [x] Create compatibility scoring system
- [ ] Implement session diff view
- [ ] Add advanced filtering options

### Phase 3: Integration and Polish
- [x] Implement comprehensive error handling
- [ ] Add performance optimizations and caching
- [x] Create unit tests for all components (partial - some tests failing)
- [ ] Add integration tests for end-to-end flow
- [ ] Implement security measures and data protection
- [ ] Add configuration options and user preferences

### Documentation
- [x] Update slash commands guide with `/resume` documentation
- [ ] Create user guide for session management
- [ ] Add troubleshooting documentation
- [ ] Create API documentation for extension points

### Testing
- [ ] Unit test coverage > 90%
- [ ] Integration test coverage for all workflows
- [ ] Performance tests with large datasets
- [ ] Security audit and penetration testing
- [ ] User acceptance testing

### Release
- [ ] Feature flag implementation for gradual rollout
- [ ] Migration guide for existing users
- [ ] Release notes and changelog
- [ ] Support documentation and training materials
