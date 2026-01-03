# API Documentation Reference

## Overview
This document provides comprehensive API documentation for the Chat App project, including internal APIs, external integrations, and AI tool interfaces.

## Internal APIs

### Core Event Bus API

#### Event Publishing
```python
class EventBus:
    async def publish_event(self, event_type: str, data: dict, source: str = None) -> EventResult:
        """
        Publish an event to the event bus
        
        Args:
            event_type: Type of event (USER_INPUT, LLM_REQUEST, etc.)
            data: Event payload data
            source: Source component name
            
        Returns:
            EventResult containing success status and hook results
        """
```

**Event Types**:
- `USER_INPUT`: User interaction events
- `KEY_PRESS`: Keyboard input events  
- `LLM_REQUEST`: LLM API request events
- `LLM_RESPONSE`: LLM API response events
- `TOOL_CALL`: Tool execution events
- `SYSTEM_STATUS`: System status updates

**Example Usage**:
```python
# Publishing a user input event
result = await event_bus.publish_event(
    event_type="USER_INPUT",
    data={
        "message": "Hello, Claude!",
        "timestamp": datetime.now().isoformat(),
        "user_id": "user123"
    },
    source="input_handler"
)
```

#### Hook Registration
```python
class Plugin:
    async def register_hooks(self):
        """Register event hooks with the event bus"""
        await self.event_bus.register_hook(
            event_type="USER_INPUT",
            hook_function=self.handle_user_input,
            priority=500,
            hook_type="pre"
        )
```

**Hook Priorities**:
- System hooks: 1000
- Security hooks: 900
- Preprocessing hooks: 500
- LLM hooks: 100
- Postprocessing hooks: 50
- Display hooks: 10

### Plugin System API

#### Plugin Registration
```python
class PluginRegistry:
    def register_plugin(self, plugin_class: type, config: dict) -> Plugin:
        """
        Register a plugin with the system
        
        Args:
            plugin_class: Plugin class to instantiate
            config: Plugin configuration dictionary
            
        Returns:
            Instantiated plugin instance
        """
```

#### Plugin Lifecycle Methods
```python
class BasePlugin:
    async def initialize(self) -> None:
        """Initialize plugin resources"""
        
    async def register_hooks(self) -> None:
        """Register event hooks"""
        
    def get_status_line(self) -> str:
        """Return status information for display"""
        
    async def shutdown(self) -> None:
        """Cleanup plugin resources"""
```

### Configuration API

#### Configuration Access
```python
class ConfigManager:
    def get(self, key: str, default=None) -> any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., "terminal.render_fps")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
```

**Configuration Structure**:
```json
{
  "terminal": {
    "render_fps": 20,
    "shimmer_speed": 3,
    "thinking_effect": "shimmer"
  },
  "plugins": {
    "llm": {
      "api_endpoint": "http://localhost:1234",
      "model_name": "claude-3-sonnet"
    }
  }
}
```

## External API Integrations

### LLM Provider APIs

#### Claude API Integration
```python
class ClaudeAPIClient:
    async def chat_completion(
        self,
        messages: List[dict],
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> dict:
        """
        Send chat completion request to Claude API
        
        Args:
            messages: List of message dictionaries
            model: Model identifier
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            
        Returns:
            API response dictionary
        """
```

**Message Format**:
```json
{
  "role": "user|assistant|system",
  "content": "Message content"
}
```

**Response Format**:
```json
{
  "id": "msg_123",
  "type": "message",
  "content": [
    {
      "type": "text",
      "text": "Response content"
    }
  ],
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

#### OpenAI API Integration
```python
class OpenAIClient:
    async def create_completion(
        self,
        messages: List[dict],
        model: str = "gpt-4",
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[dict, AsyncIterator[dict]]:
        """Create chat completion with OpenAI API"""
```

### GitHub API Integration

#### Repository Operations
```python
class GitHubClient:
    async def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main"
    ) -> dict:
        """Create a pull request"""
        
    async def get_repository_info(self, repo: str) -> dict:
        """Get repository information"""
```

## AI Tool Integration APIs

### Claude Code Integration

#### Session Management
```python
class ClaudeCodeSession:
    async def start_session(self, context: dict) -> str:
        """
        Start a new Claude Code session
        
        Args:
            context: Project context and preferences
            
        Returns:
            Session ID
        """
        
    async def send_message(
        self,
        session_id: str,
        message: str,
        files: List[str] = None
    ) -> dict:
        """Send message to Claude Code session"""
```

#### Tool Call Handling
```python
class ToolCallHandler:
    async def execute_tool_call(
        self,
        tool_name: str,
        parameters: dict
    ) -> dict:
        """
        Execute a tool call from Claude Code
        
        Args:
            tool_name: Name of tool to execute
            parameters: Tool parameters dictionary
            
        Returns:
            Tool execution result
        """
```

### Subagent Management

#### Subagent Creation
```python
class SubagentManager:
    async def create_subagent(
        self,
        agent_type: str,
        specialization: str,
        context: dict
    ) -> str:
        """
        Create a specialized subagent
        
        Args:
            agent_type: Type of agent to create
            specialization: Agent specialization area
            context: Initial context for agent
            
        Returns:
            Subagent ID
        """
```

**Available Agent Types**:
- `code_reviewer`: Code review and analysis
- `test_generator`: Test case generation
- `documentation_writer`: Documentation creation
- `architecture_analyst`: System architecture analysis

## Data Models

### Core Data Structures

#### ConversationMessage
```python
@dataclass
class ConversationMessage:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary format"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
```

#### Event Structure
```python
@dataclass
class Event:
    event_type: str
    data: dict
    source: str
    timestamp: datetime
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cancelled: bool = False
    
    def cancel(self):
        """Cancel event processing"""
        self.cancelled = True
```

#### Plugin Status
```python
@dataclass
class PluginStatus:
    name: str
    status: str  # "active", "inactive", "error"
    last_update: datetime
    metrics: dict = field(default_factory=dict)
    error_message: str = None
```

## Error Handling

### Standard Error Responses
```python
class APIError(Exception):
    def __init__(self, message: str, error_code: str, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
```

**Error Codes**:
- `CONFIG_ERROR`: Configuration-related errors
- `PLUGIN_ERROR`: Plugin loading or execution errors
- `EVENT_ERROR`: Event processing errors
- `API_ERROR`: External API errors
- `VALIDATION_ERROR`: Input validation errors

### Error Response Format
```json
{
  "error": {
    "code": "PLUGIN_ERROR",
    "message": "Failed to load plugin",
    "details": {
      "plugin_name": "llm_plugin",
      "reason": "Import error"
    }
  }
}
```

## Authentication and Authorization

### API Key Management
```python
class APIKeyManager:
    def get_api_key(self, service: str) -> str:
        """Retrieve API key for service"""
        
    def validate_api_key(self, service: str, key: str) -> bool:
        """Validate API key format"""
```

### Permission System
```python
class PermissionManager:
    def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str
    ) -> bool:
        """Check if user has permission for action"""
```

## Performance Monitoring

### Metrics Collection API
```python
class MetricsCollector:
    async def record_metric(
        self,
        metric_name: str,
        value: Union[int, float],
        tags: dict = None
    ):
        """Record a performance metric"""
        
    async def get_metrics(
        self,
        metric_name: str,
        time_range: tuple
    ) -> List[dict]:
        """Retrieve metrics for time range"""
```

### Health Check Endpoints
```python
class HealthCheck:
    async def check_system_health(self) -> dict:
        """
        Comprehensive system health check
        
        Returns:
            Health status dictionary with component statuses
        """
```

**Health Check Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z",
  "components": {
    "event_bus": "healthy",
    "plugin_system": "healthy", 
    "ai_tools": "degraded",
    "database": "healthy"
  },
  "metrics": {
    "uptime": 86400,
    "memory_usage": 0.75,
    "cpu_usage": 0.45
  }
}
```

## Testing APIs

### Test Utilities
```python
class TestUtils:
    @staticmethod
    def create_mock_event(event_type: str, data: dict) -> Event:
        """Create a mock event for testing"""
        
    @staticmethod
    async def setup_test_environment() -> dict:
        """Set up test environment with mock services"""
```

### Plugin Testing Framework
```python
class PluginTestCase(unittest.TestCase):
    async def setUp(self):
        """Set up test plugin environment"""
        
    async def tearDown(self):
        """Clean up test environment"""
        
    def assert_hook_called(
        self,
        hook_name: str,
        call_count: int = 1
    ):
        """Assert that a hook was called"""
```

---

*This API documentation provides comprehensive reference information for all Chat App APIs, enabling efficient development and integration of new features and plugins.*