# LLM Core Migration Plan & Conversation Logging

**Date**: 2025-09-10  
**Purpose**: Migrate LLM functionality from plugin to core architecture + implement conversation logging  
**Implementation**: Will be handled by separate agent/developer  

## Current State Analysis

### What We Have Now
- **LLM Plugin**: `plugins/llm_plugin.py` (55k lines)
- **Plugin Architecture**: LLM is optional, discoverable plugin
- **Basic Conversation Logging**: Simple JSON logging in `.kollabor-cli/conversations/`
- **Hook System**: Event bus with plugin registration

### What We Need
- **LLM as Core Service**: Essential system component, not optional plugin
- **Conversation Intelligence**: Memory, context awareness, learning
- **JSONL Logging**: Structured conversation export with intelligence

## Migration Objectives

### 1. LLM Plugin → Core Architecture

**FROM**: `plugins/llm_plugin.py`
**TO**: `core/llm/` directory structure

**Key Requirements**:
- LLM becomes **essential system service** 
- Still uses hook system for customization
- Cannot be disabled or removed
- Other core components can depend on it
- Maintains plugin-like extensibility

### 2. Conversation System

**Goal**: Implement conversation logging with intelligence features

**Features**:
- **Conversation Memory**: Learns user patterns, remembers project context
- **Contextual Intelligence**: File relevance scoring, conversation momentum
- **Learning Optimization**: Response effectiveness tracking, knowledge refinement

## Detailed Implementation Plan

### Phase 1: Core LLM Migration

#### Directory Structure
```
core/
├── llm/
│   ├── __init__.py
│   ├── llm_service.py          # Main LLM service (migrated from plugin)
│   ├── conversation_manager.py # Conversation handling
│   ├── model_router.py         # Multi-model routing
│   ├── response_processor.py   # Thinking tags, terminal commands
│   ├── hook_system.py          # Comprehensive LLM hook system
│   ├── mcp_integration.py      # MCP server/tool integration
│   └── plugin_sdk.py           # Custom plugin creation framework
```

#### Comprehensive Hook System
```python
# core/llm/hook_system.py - Complete hook coverage like Claude Code
class LLMHookSystem:
    def register_hooks(self):
        # Pre-processing hooks
        self.register_hook("pre_user_input", HookType.PRE_USER_INPUT)
        self.register_hook("pre_llm_request", HookType.PRE_LLM_REQUEST)
        self.register_hook("pre_tool_call", HookType.PRE_TOOL_CALL)
        
        # Processing hooks  
        self.register_hook("llm_request", HookType.LLM_REQUEST)
        self.register_hook("tool_call", HookType.TOOL_CALL)
        
        # Post-processing hooks
        self.register_hook("post_llm_response", HookType.POST_LLM_RESPONSE)
        self.register_hook("post_tool_call", HookType.POST_TOOL_CALL) 
        self.register_hook("post_user_response", HookType.POST_USER_RESPONSE)
        
        # System hooks
        self.register_hook("conversation_start", HookType.CONVERSATION_START)
        self.register_hook("conversation_end", HookType.CONVERSATION_END)
        self.register_hook("error_handling", HookType.ERROR_HANDLING)
        
        # Intelligence hooks
        self.register_hook("context_analysis", HookType.CONTEXT_ANALYSIS)
        self.register_hook("memory_update", HookType.MEMORY_UPDATE)
```

#### MCP Integration
```python
# core/llm/mcp_integration.py - Model Context Protocol support
class MCPIntegration:
    def __init__(self):
        self.mcp_servers = {}
        self.tool_registry = {}
        
    async def discover_mcp_servers(self):
        """Auto-discover MCP servers and tools"""
        
    async def register_mcp_tool(self, tool_name: str, server: str):
        """Register MCP tool for LLM use"""
        
    async def call_mcp_tool(self, tool_name: str, params: dict):
        """Execute MCP tool call"""
```

#### Custom Plugin SDK
```python
# core/llm/plugin_sdk.py - Create custom plugins separate from MCP
class KollaborPluginSDK:
    def create_plugin_template(self, plugin_name: str):
        """Generate plugin boilerplate"""
        
    def register_custom_tool(self, tool_definition: dict):
        """Register custom tool for LLM use"""
        
    def validate_plugin(self, plugin_path: str):
        """Validate plugin structure and security"""
```

#### Core Integration Points  
```python
# core/application.py
class TerminalLLMChat:
    def __init__(self):
        # LLM service initialized as core component
        self.llm_service = LLMService(self.config, self.state_manager)
        self.mcp_integration = MCPIntegration()
        self.plugin_sdk = KollaborPluginSDK()
        
    async def start(self):
        # LLM service starts with core application
        await self.llm_service.initialize()
        await self.mcp_integration.discover_mcp_servers()
```

### Phase 2: Kollabor Conversation Logging

#### Kollabor Logging Structure  
**CRITICAL REQUIREMENT**: Implement conversation logging with intelligence features that make every terminal interaction a structured object

#### Kollabor JSONL Structure - Every Terminal Interaction as JSON

```python
# Conversation Root Structure (Session metadata - first object in .jsonl file)
{
    "type": "conversation_metadata",
    "sessionId": "session_2025-09-10_143022",
    "startTime": "2025-09-10T14:30:22.517Z",
    "endTime": null,  # Updated when conversation ends
    "uuid": "conv_root_uuid",
    "timestamp": "2025-09-10T14:30:22.517Z",
    "cwd": "/Users/malmazan/dev/chat_app",
    "gitBranch": "main",
    "version": "1.0.0",
    "conversation_context": {
        "project_type": "python_terminal_app",
        "active_plugins": ["llm_service", "hook_system", "file_monitor"],
        "user_profile": {
            "expertise_level": "advanced",
            "preferred_communication": "direct",
            "coding_style": "pythonic"
        },
        "session_goals": [],  # Populated as conversation progresses
        "conversation_summary": ""  # Updated periodically
    },
    "kollabor_intelligence": {
        "conversation_memory": {
            "related_sessions": ["session_2025-09-09_102030"],
            "recurring_themes": ["plugin_architecture", "hook_system"],
            "user_patterns": ["prefers_detailed_explanations", "asks_followup_questions"]
        }
    }
}

# User Message Structure
{
    "parentUuid": "ac3bb1bb-5179-4e11-b053-cb55d3fa69b6",
    "isSidechain": false,
    "userType": "external", 
    "cwd": "/Users/malmazan/dev/chat_app",
    "sessionId": "8802772c-1304-402a-b484-d0fdc6c55325",
    "version": "1.0.0",
    "gitBranch": "main",
    "type": "user",
    "message": {
        "role": "user",
        "content": "Hello, what can you help me with today?"
    },
    "uuid": "39c120c0-4fed-4705-9811-c813d57a8919",
    "timestamp": "2025-09-10T04:03:38.517Z",
    
    # KOLLABOR INTELLIGENCE
    "kollabor_intelligence": {
        "user_context": {
            "detected_intent": "greeting_and_help_request",
            "expertise_level": "intermediate",
            "communication_style": "direct"
        },
        "session_context": {
            "conversation_phase": "initiation",
            "previous_sessions_count": 5,
            "last_session_topic": "authentication_debugging"
        },
        "project_awareness": {
            "files_in_focus": ["main.py", "config.json"],
            "recent_changes": ["updated LLM plugin yesterday"],
            "architecture_understanding": "hook_based_plugin_system"
        }
    }
}

# Assistant Response Structure  
{
    "parentUuid": "39c120c0-4fed-4705-9811-c813d57a8919",
    "isSidechain": false,
    "userType": "external",
    "cwd": "/Users/malmazan/dev/chat_app", 
    "sessionId": "8802772c-1304-402a-b484-d0fdc6c55325",
    "version": "1.0.0",
    "gitBranch": "main", 
    "message": {
        "id": "msg_kollabor_123456",
        "type": "message",
        "role": "assistant", 
        "model": "qwen/qwen3-4b",  # Our model
        "content": [
            {
                "type": "text",
                "text": "Hello! I'm Kollabor, ready to help you with your development tasks."
            }
        ],
        "stop_reason": null,
        "stop_sequence": null,
        "usage": {
            "input_tokens": 4,
            "output_tokens": 28,
            "service_tier": "standard"
        }
    },
    "requestId": "req_kollabor_123456", 
    "type": "assistant",
    "uuid": "ac3bb1bb-5179-4e11-b053-cb55d3fa69b6",
    "timestamp": "2025-09-10T04:03:41.353Z"
}

# System Messages (Hook outputs, tool calls, etc)
{
    "parentUuid": "ac3bb1bb-5179-4e11-b053-cb55d3fa69b6",
    "isSidechain": false,
    "userType": "external",
    "cwd": "/Users/malmazan/dev/chat_app",
    "sessionId": "8802772c-1304-402a-b484-d0fdc6c55325", 
    "version": "1.0.0",
    "gitBranch": "main",
    "type": "system",
    "subtype": "informational",
    "content": "💡 Consider running: python tests/run_tests.py",
    "isMeta": false,
    "timestamp": "2025-09-10T04:03:41.628Z",
    "uuid": "14b874ae-40e8-4926-a131-d71041e52ed8", 
    "toolUseID": "hook_123456",
    "level": "info"
}
```

#### Conversation Logger Implementation
```python
# core/llm/conversation_logger.py
class KollaborConversationLogger:
    def __init__(self, conversations_dir: Path):
        self.conversations_dir = conversations_dir
        self.current_session_id = str(uuid4())
        self.current_session_file = conversations_dir / f"{self.current_session_id}.jsonl"
        
    async def log_user_message(self, content: str, parent_uuid: str = None):
        """Log user message in Kollabor format"""
        message = {
            "parentUuid": parent_uuid,
            "isSidechain": False,
            "userType": "external",
            "cwd": str(Path.cwd()),
            "sessionId": self.current_session_id,
            "version": "1.0.0", 
            "gitBranch": self._get_git_branch(),
            "type": "user",
            "message": {
                "role": "user",
                "content": content
            },
            "uuid": str(uuid4()),
            "timestamp": datetime.now().isoformat() + "Z"
        }
        await self._append_to_jsonl(message)
        return message["uuid"]
        
    async def log_assistant_message(self, content: str, parent_uuid: str, usage_stats: dict):
        """Log assistant response in Kollabor format"""  
        message = {
            "parentUuid": parent_uuid,
            "isSidechain": False,
            "userType": "external", 
            "cwd": str(Path.cwd()),
            "sessionId": self.current_session_id,
            "version": "1.0.0",
            "gitBranch": self._get_git_branch(),
            "message": {
                "id": f"msg_kollabor_{int(time.time())}",
                "type": "message",
                "role": "assistant",
                "model": "qwen/qwen3-4b", 
                "content": [{"type": "text", "text": content}],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": usage_stats
            },
            "requestId": f"req_kollabor_{int(time.time())}",
            "type": "assistant", 
            "uuid": str(uuid4()),
            "timestamp": datetime.now().isoformat() + "Z"
        }
        await self._append_to_jsonl(message)
        return message["uuid"]
        
    async def log_system_message(self, content: str, parent_uuid: str, subtype: str = "informational"):
        """Log system messages (hooks, tool outputs) in Kollabor format"""
        message = {
            "parentUuid": parent_uuid,
            "isSidechain": False,
            "userType": "external",
            "cwd": str(Path.cwd()), 
            "sessionId": self.current_session_id,
            "version": "1.0.0",
            "gitBranch": self._get_git_branch(),
            "type": "system",
            "subtype": subtype,
            "content": content,
            "isMeta": False,
            "timestamp": datetime.now().isoformat() + "Z", 
            "uuid": str(uuid4()),
            "level": "info"
        }
        await self._append_to_jsonl(message)
        return message["uuid"]
```

### Phase 3: Integration & Testing

#### Core Service Dependencies
```python
# Other core components can now depend on LLM
class TerminalRenderer:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service  # Safe dependency
```

#### Configuration Updates  
```json
// .kollabor-cli/config.json
{
    "core": {
        "llm": {
            "enabled": true,
            "essential": true,
            "api_url": "http://localhost:1234", 
            "model": "qwen/qwen3-4b",
            "conversation_logging": {
                "enabled": true,
                "format": "kollabor",
                "output_directory": ".kollabor-cli/conversations/",
                "intelligence_features": {
                    "user_context_analysis": true,
                    "session_memory": true,
                    "project_awareness": true,
                    "conversation_learning": true
                }
            }
        }
    }
}
```

#### Kollabor Conversation Directory Structure
```
.kollabor-cli/
├── conversations/
│   ├── session_2025-09-10_143022.jsonl     # Readable session names  
│   ├── session_2025-09-10_151545.jsonl     # With timestamps
│   └── session_2025-09-10_163820.jsonl     # Easy to identify
├── conversation_memory/
│   ├── user_patterns.json                  # Learned user preferences
│   ├── project_context.json               # Codebase understanding  
│   └── solution_history.json              # What worked/failed
└── config.json
```

**KOLLABOR BEHAVIOR**: Every terminal interaction becomes a structured JSON object with intelligence features that learn, remember, and improve over time. Local storage in `.kollabor-cli/` for full user control and analysis.

## Implementation Files to Create/Modify

### New Files
- `core/llm/__init__.py` - LLM core module exports
- `core/llm/llm_service.py` - Main service (migrate from plugin)  
- `core/llm/conversation_logger.py` - **CRITICAL**: Kollabor JSONL logging
- `core/llm/message_threading.py` - parentUuid chain management
- `core/llm/session_manager.py` - Session ID and file management
- `core/llm/hook_system.py` - **CRITICAL**: Comprehensive hook system (pre/post tool calls, response hooks)
- `core/llm/mcp_integration.py` - **CRITICAL**: MCP server and tool integration
- `core/llm/plugin_sdk.py` - **CRITICAL**: Custom plugin creation framework

### Modified Files  
- `core/application.py` - Integrate LLM as core service + conversation logging
- `core/config/config_service.py` - LLM core configuration  
- `plugins/llm_plugin.py` - **DELETE** after migration
- `.kollabor-cli/config.json` - Add conversation logging configuration

### Critical Implementation Requirements
1. **Conversation Root Structure** - Session metadata as first JSONL object with conversation context
2. **Comprehensive JSONL Format** - Every terminal interaction as structured JSON
3. **Complete Hook System** - Pre/post hooks for all operations (like Claude Code)
4. **MCP Integration** - Full Model Context Protocol server/tool support
5. **Custom Plugin SDK** - Framework for creating Kollabor-specific plugins
6. **Session File Management** - One `.jsonl` file per conversation session  
7. **Message Threading** - Proper parentUuid chains for conversation flow
8. **Real-time Logging** - Every interaction logged immediately
9. **Git Branch Tracking** - Dynamic git branch detection for context
10. **Working Directory Context** - Current directory tracking per message

## Value Proposition - Why This Matters

### Before (Current State)
```
User: "Fix this authentication bug"
AI: "I can help with that. Can you show me the code?"
```

### After (Kollabor System)  
```
User: "Fix this authentication bug"  
AI: "I see you're working on the auth system we discussed last week. 
     Based on your JWT implementation and the middleware pattern you 
     prefer, this looks similar to the token refresh issue we solved 
     in session abc123. Should I check the token expiration logic first?"
```

**The AI becomes your actual programming partner instead of a helpful stranger.**

## Success Metrics

### Technical Metrics
- ✅ LLM service loads as core component (not plugin)
- ✅ Conversation intelligence captures user patterns  
- ✅ Cross-session memory works between conversations
- ✅ JSONL export includes intelligence data

### User Experience Metrics  
- ✅ AI remembers previous conversations and decisions
- ✅ AI suggests solutions based on past successful patterns
- ✅ AI understands project context without re-explanation
- ✅ Conversation quality improves over time

## Implementation Notes for Developer

1. **Migration Strategy**: Move `plugins/llm_plugin.py` code to `core/llm/` 
2. **Hook Preservation**: Keep all existing hook functionality
3. **Essential Service**: LLM cannot be disabled, loads with core
4. **Intelligence Layer**: Add conversation analysis on top of basic logging
5. **JSONL Enhancement**: Extend current logging with intelligence fields

## Final Result

- **LLM as Core**: Essential service, not optional plugin
- **Intelligence Features**: Memory, learning, context awareness  
- **Learning System**: Conversation system learns and improves over time
- **Maintained Extensibility**: Still uses hooks for customization

---

**Next Steps**: Hand this document to implementation agent to execute the migration and logging features.