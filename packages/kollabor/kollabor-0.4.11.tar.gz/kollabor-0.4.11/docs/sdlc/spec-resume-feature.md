# /resume Command Feature Specification

## Overview

The `/resume` command allows users to browse and restore previously saved conversations from their conversation history. This feature addresses the common need to return to previous conversations, reference past discussions, or continue interrupted sessions.

## User Experience

### Command Invocation

1. **Basic Command**: `/resume` - Shows interactive menu of recent conversations
2. **With Search**: `/resume search <query>` - Shows conversations matching search terms
3. **With Filter**: `/resume --today` - Shows today's conversations, `--week` for this week
4. **With Limit**: `/resume --limit 10` - Shows only last 10 conversations
5. **Direct Load**: `/resume <session-id>` - Directly loads specific conversation by ID

### Interactive Menu

When invoked without arguments, `/resume` displays an interactive menu:

```
┌─ Resume Conversation ─────────────────────────────────────────┐
│                                                                │
│  Recent Conversations (showing 20 of 47)                       │
│                                                                │
│  📄 Python asyncio debugging - 2 hours ago                    │
│      Session: 1fbca703...  Messages: 15  ID: #12345           │
│      "Help debug async context manager issue..."               │
│                                                                │
│  📄 WebGPU implementation planning - Yesterday                │
│      Session: 8d4e2f1a...  Messages: 23  ID: #12346           │
│      "Plan WebGPU texture management system..."                │
│                                                                │
│  📄 Code review practices - 3 days ago                        │
│      Session: 2b7c9f3d...  Messages: 8   ID: #12347           │
│      "Review pull request for authentication..."               │
│                                                                │
│                                                                │
│  [↑↓ Navigate] [Enter] Select  [/] Search  [ESC] Cancel       │
└────────────────────────────────────────────────────────────────┘
```

### Keyboard Navigation

- **↑/↓**: Navigate conversation list
- **Enter**: Load selected conversation
- **/**: Search within conversations
- **n/p**: Next/Previous page
- **Home/End**: First/Last conversation
- **ESC**: Cancel and return to chat

## Technical Implementation

### Command Registration

```python
# In new file: plugins/resume_conversation_plugin.py

CommandDefinition(
    name="resume",
    description="Resume a previous conversation",
    handler=self.handle_resume,
    plugin_name="resume_conversation",
    aliases=["r", "load"],
    mode=CommandMode.MODAL,
    category=CommandCategory.CONVERSATION,
    icon="[⏯]",
    ui_config=UIConfig(
        type="modal",
        title="Resume Conversation",
        height=20,
        width=80
    )
)
```

### Plugin Structure

**File**: `plugins/resume_conversation_plugin.py`

```python
class ResumeConversationPlugin(BasePlugin):
    """Plugin for resuming previous conversations"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation_manager: ConversationManager = kwargs.get('conversation_manager')
        self.renderer: TerminalRenderer = kwargs.get('renderer')
        self.state_manager = kwargs.get('state_manager')

    async def handle_resume(self, command: SlashCommand) -> CommandResult:
        """Main resume command handler"""

    async def _show_conversation_menu(self) -> CommandResult:
        """Show interactive conversation selection menu"""

    async def _search_conversations(self, query: str) -> CommandResult:
        """Search conversations by content"""

    async def _load_conversation(self, session_id: str) -> CommandResult:
        """Load specific conversation by session ID"""
```

### Data Flow

1. **Command Detection**: User types `/resume`
2. **Menu Trigger**: Command handler opens modal menu
3. **Conversation Discovery**: Scan `.kollabor-cli/conversations/` directory
4. **Metadata Parsing**: Extract session info from JSON files
5. **Menu Rendering**: Display sorted conversation list
6. **User Selection**: User navigates and selects conversation
7. **Conversation Loading**: Load selected conversation into memory
8. **State Update**: Update current conversation state
9. **UI Notification**: Show confirmation message

## Implementation Details

### Conversation Discovery

```python
async def discover_conversations(self, limit: int = 50) -> List[ConversationMetadata]:
    """Discover available conversations"""
    conversations_dir = Path.home() / ".kollabor-cli/conversations"

    conversations = []
    for file_path in conversations_dir.glob("conversation_*.json"):
        try:
            metadata = await self._parse_conversation_metadata(file_path)
            conversations.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")

    # Sort by modification time (newest first)
    conversations.sort(key=lambda x: x.modified_time, reverse=True)
    return conversations[:limit]
```

### Metadata Structure

```python
@dataclass
class ConversationMetadata:
    file_path: Path
    session_id: str
    title: str
    message_count: int
    created_time: datetime
    modified_time: datetime
    last_message_preview: str
    topics: List[str]
    file_id: str  # Short ID for display (#12345)
```

### Menu Rendering

The menu uses the existing modal system with custom widgets:

- **Conversation List Widget**: Scrollable list with conversation details
- **Search Widget**: Real-time search input (optional)
- **Pagination Widget**: For large conversation lists
- **Status Bar**: Shows navigation hints and current selection

### Conversation Loading

```python
async def load_conversation(self, session_id: str) -> CommandResult:
    """Load conversation and update state"""
    try:
        # Find conversation file
        conversation_file = await self._find_conversation_file(session_id)
        if not conversation_file:
            return CommandResult(
                success=False,
                message=f"Conversation {session_id} not found",
                display_type="error"
            )

        # Load using ConversationManager
        success = await self.conversation_manager.load_conversation(conversation_file)
        if not success:
            raise Exception("Failed to load conversation")

        # Update application state
        await self._update_conversation_state(session_id)

        return CommandResult(
            success=True,
            message=f"Resumed conversation: {session_id[:8]}...",
            display_type="success"
        )

    except Exception as e:
        logger.error(f"Failed to resume conversation: {e}")
        return CommandResult(
            success=False,
            message=f"Failed to resume: {str(e)}",
            display_type="error"
        )
```

## Storage Integration

### Conversation File Formats

The feature supports both storage formats:

1. **JSON Archives** (`conversation_*.json`): Primary source for saved conversations
2. **JSONL Session Logs** (`session_*.jsonl`): Fallback for unsaved sessions

### Search Functionality

Search across conversation metadata and content:

```python
async def search_conversations(self, query: str) -> List[ConversationMetadata]:
    """Search conversations by content"""
    results = []

    for metadata in await self.discover_conversations():
        # Search in title, topics, and content preview
        if (query.lower() in metadata.title.lower() or
            query.lower() in metadata.last_message_preview.lower() or
            any(query.lower() in topic.lower() for topic in metadata.topics)):
            results.append(metadata)

    return results
```

## Error Handling

### Common Error Scenarios

1. **No Conversations Found**: Display helpful message suggesting conversation saving
2. **Corrupted Files**: Skip corrupted files and log warnings
3. **Permission Issues**: Check file accessibility before attempting to load
4. **Session ID Not Found**: Clear error with suggestion to use menu
5. **State Loading Failure**: Graceful fallback with error recovery

### Error Messages

```
No saved conversations found.
Tip: Use /save to save current conversations for future resumption.

Conversation not found.
Tip: Use /resume without arguments to browse available conversations.

Failed to load conversation.
The conversation file may be corrupted. Try selecting a different conversation.
```

## Configuration

### Plugin Configuration

```json
{
  "resume_conversation": {
    "max_conversations": 50,
    "preview_length": 80,
    "date_format": "%Y-%m-%d %H:%M",
    "auto_save_on_resume": true,
    "confirm_load": true
  }
}
```

### User Preferences

- **Maximum conversations to show**: Default 50
- **Message preview length**: Default 80 characters
- **Date format**: Configurable datetime display
- **Auto-save current conversation**: Option to save before loading new one
- **Confirmation prompts**: Option to require confirmation before loading

## Integration Points

### Event System Integration

The plugin registers hooks for:

1. **pre_conversation_load**: Validate conversation before loading
2. **post_conversation_load**: Update UI and state after loading
3. **conversation_load_failed**: Handle load failures gracefully

### Status Line Integration

Update status areas to show current conversation:

```
Area A: 💬 Python asyncio debugging (15 messages)
```

### Slash Command Integration

- **Command registration** in `SlashCommandRegistry`
- **Help integration** with `/help resume`
- **Tab completion** for session IDs
- **Command history** support

## Testing

### Unit Tests

1. **Conversation Discovery**: Test file scanning and metadata parsing
2. **Search Functionality**: Test search algorithms and filtering
3. **Menu Rendering**: Test modal display and navigation
4. **Error Handling**: Test various error scenarios
5. **State Management**: Test conversation loading and state updates

### Integration Tests

1. **End-to-End Flow**: Test complete resume command workflow
2. **Multi-Format Support**: Test both JSON and JSONL file handling
3. **Plugin Integration**: Test interaction with other plugins
4. **UI Integration**: Test modal system integration

### Visual Tests

1. **Menu Display**: Verify proper rendering in different terminal sizes
2. **Navigation**: Test keyboard navigation and responsiveness
3. **Error Display**: Verify error message formatting and clarity

## Performance Considerations

### Conversation Discovery Optimization

- **Lazy Loading**: Load metadata on-demand, not all at once
- **Caching**: Cache conversation metadata for faster subsequent access
- **Indexing**: Maintain an index file for faster conversation lookup
- **Background Scanning**: Scan directories in background threads

### Memory Management

- **Efficient Data Structures**: Use generators for large conversation lists
- **Cleanup**: Properly close file handles and cleanup resources
- **State Size Limits**: Limit in-memory conversation history

## Security and Privacy

### Conversation Privacy

- **Local Storage Only**: No external data transmission
- **User Consent**: Clear confirmation before loading conversations
- **Data Sanitization**: Remove sensitive metadata from display
- **Access Control**: Respect file system permissions

### Input Validation

- **Session ID Validation**: Prevent path traversal attacks
- **Search Query Sanitization**: Prevent injection attacks
- **File Path Validation**: Ensure files are within expected directories

## Future Enhancements

### Advanced Features

1. **Conversation Merging**: Merge multiple conversations
2. **Export Integration**: Combine with /save for conversation export
3. **Conversation Bookmarks**: Allow bookmarking important conversations
4. **Conversation Tags**: Add tagging system for organization
5. **Conversation Analytics**: Usage statistics and insights

### UI Improvements

1. **Conversation Previews**: Show expanded message previews
2. **Visual Indicators**: Icons for different conversation types
3. **Filter Tags**: Visual tag filtering in menu
4. **Keyboard Shortcuts**: Customizable keyboard shortcuts
5. **Dark/Light Theme**: Theme-aware menu styling

## Migration Strategy

### Backward Compatibility

- **File Format Support**: Support existing conversation file formats
- **Graceful Degradation**: Handle missing or incomplete metadata
- **Configuration Migration**: Migrate old configuration formats

### Rollout Plan

1. **Phase 1**: Basic /resume command with menu functionality
2. **Phase 2**: Search and filtering capabilities
3. **Phase 3**: Advanced features and integrations
4. **Phase 4**: Performance optimizations and caching

## Success Metrics

### User Experience

- **Success Rate**: Percentage of successful conversation loads
- **Time to Load**: Average time from command to loaded conversation
- **User Satisfaction**: Qualitative feedback on usability

### Technical Performance

- **Discovery Time**: Time to scan and parse conversation metadata
- **Menu Responsiveness**: Menu navigation and search performance
- **Memory Usage**: Memory footprint during conversation discovery

### Adoption

- **Usage Frequency**: How often users use the /resume command
- **Feature Discovery**: Percentage of users who discover and use the feature
- **Error Rate**: Low error rates in conversation loading

---

*This specification provides a comprehensive foundation for implementing the /resume feature in Kollabor CLI, ensuring robust functionality, excellent user experience, and seamless integration with the existing architecture.*