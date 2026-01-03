# Hook System SDK Documentation

The Kollabor CLI application provides a comprehensive hook system that allows plugins to intercept, modify, and respond to every aspect of the application's operation. This SDK documentation covers everything you need to build powerful plugins using the hook system.

## Table of Contents

- [Overview](#overview)
- [Core Concepts](#core-concepts)
- [Hook Architecture](#hook-architecture)
- [Event Types](#event-types)
- [Hook Priorities](#hook-priorities)
- [Creating Hooks](#creating-hooks)
- [Plugin Integration](#plugin-integration)
- [Plugin Communication & Service Discovery](#plugin-communication--service-discovery)
- [Advanced Patterns](#advanced-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The hook system is built on the principle **"everything has a hook"**. Every significant operation in the application triggers events that plugins can intercept:

- **User input processing**
- **LLM request/response cycles**
- **Terminal rendering**
- **Tool execution**
- **System lifecycle events**

This provides maximum customization - even core LLM behavior can be completely replaced or enhanced through plugins.

## Core Concepts

### Event-Driven Architecture

The system uses a **three-phase processing model**:

```
PRE Phase → MAIN Phase → POST Phase
```

1. **PRE Phase**: Preprocessing, validation, data transformation
2. **MAIN Phase**: Core event processing
3. **POST Phase**: Post-processing, cleanup, logging, display updates

### Hook Lifecycle

```
Plugin Registration → Hook Creation → Event Bus Registration → Event Triggered → Hook Execution
```

### Error Handling & Cancellation

- **Event Cancellation**: Any hook can cancel the entire event chain
- **Error Actions**: `"continue"` (default) or `"stop"` on hook failure
- **Timeouts**: Configurable per-hook execution timeouts
- **Status Tracking**: Real-time monitoring of hook execution status

## Hook Architecture

### Core Components

The hook system consists of specialized components in `core/events/`:

- **`EventBus`**: Central coordinator for hook registration and event processing
- **`HookRegistry`**: Manages hook organization by event type and priority
- **`HookExecutor`**: Executes individual hooks with timeout/error handling
- **`EventProcessor`**: Handles pre/main/post event processing phases

### Data Models

```python
@dataclass
class Hook:
    name: str                    # Unique hook name
    plugin_name: str            # Owning plugin name
    event_type: EventType       # Event type to listen for
    priority: int               # Execution order (higher = earlier)
    callback: Callable          # Async function to execute
    enabled: bool = True        # Can be toggled on/off
    timeout: int = 30           # Max execution time in seconds
    error_action: str = "continue"  # "continue" or "stop" on error
    status: HookStatus = HookStatus.PENDING
```

## Event Types

### User Interaction Events

```python
# User input processing
USER_INPUT_PRE      # Before input processing
USER_INPUT          # Main input processing
USER_INPUT_POST     # After input processing

# Keyboard events
KEY_PRESS_PRE       # Before key processing
KEY_PRESS           # Main key processing
KEY_PRESS_POST      # After key processing

# Paste detection
PASTE_DETECTED      # When paste operation detected
```

### LLM Operation Events

```python
# Request lifecycle
LLM_REQUEST_PRE     # Before LLM request
LLM_REQUEST         # Main LLM request processing
LLM_REQUEST_POST    # After LLM request

# Response lifecycle
LLM_RESPONSE_PRE    # Before LLM response processing
LLM_RESPONSE        # Main LLM response processing
LLM_RESPONSE_POST   # After LLM response processing

# Special LLM events
LLM_THINKING        # During LLM thinking/processing
CANCEL_REQUEST      # When LLM request cancelled
```

### Tool & System Events

```python
# Tool execution
TOOL_CALL_PRE       # Before tool execution
TOOL_CALL           # Main tool execution
TOOL_CALL_POST      # After tool execution

# System lifecycle
SYSTEM_STARTUP      # Application startup
SYSTEM_SHUTDOWN     # Application shutdown
RENDER_FRAME        # Terminal render frame

# UI Events
INPUT_RENDER_PRE    # Before input rendering
INPUT_RENDER        # Main input rendering
INPUT_RENDER_POST   # After input rendering

# Command menu
COMMAND_MENU_SHOW   # Menu display
COMMAND_MENU_NAVIGATE # Menu navigation
COMMAND_MENU_SELECT # Menu selection
COMMAND_MENU_HIDE   # Menu hiding
```

## Hook Priorities

The system uses a structured priority system to ensure proper execution order:

```python
class HookPriority(Enum):
    SYSTEM = 1000          # Core system operations
    SECURITY = 900         # Security validation, authorization
    PREPROCESSING = 500    # Data transformation, validation
    LLM = 100             # LLM model inference
    POSTPROCESSING = 50   # Response formatting, logging
    DISPLAY = 10          # UI updates, rendering
```

**Higher numbers execute first**. Use appropriate priorities for your hook's purpose.

## Creating Hooks

### Basic Hook Creation

```python
from core.events import Hook, EventType, HookPriority

# Create a hook
my_hook = Hook(
    name="my_custom_hook",
    plugin_name="my_plugin",
    event_type=EventType.USER_INPUT,
    priority=HookPriority.PREPROCESSING.value,
    callback=self._handle_user_input,
    timeout=10,
    error_action="continue"
)

# Hook callback function
async def _handle_user_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    """Process user input."""
    logger.info(f"Processing user input: {data.get('message', '')}")

    # Modify event data if needed
    if "urgent" in data.get('message', '').lower():
        event.data['priority'] = 'high'

    return {
        "status": "processed",
        "modifications": ["priority_check"]
    }
```

### Data Transformation Hook

```python
async def _transform_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    """Transform input data."""

    # Transform the data
    if isinstance(data.get('message'), str):
        # Add timestamp
        data['timestamp'] = datetime.now().isoformat()

        # Transform message format
        data['message'] = f"[{self.plugin_name}] {data['message']}"

    # Return modified data to pass to next hooks
    return {
        "data": data,  # This updates the event data
        "status": "transformed"
    }
```

### Event Cancellation Hook

```python
async def _validate_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    """Validate input and potentially cancel event."""

    message = data.get('message', '')

    # Check for spam or inappropriate content
    if self._is_spam(message):
        event.cancelled = True  # Cancel the entire event chain
        logger.warning(f"Cancelled event due to spam detection: {message[:50]}")

        return {
            "status": "cancelled",
            "reason": "spam_detected"
        }

    return {"status": "validated"}
```

## Plugin Integration

### Complete Plugin Example

```python
"""Example plugin demonstrating comprehensive hook usage."""

import datetime
import logging
from typing import Any, Dict, List
from core.events import Event, EventType, Hook, HookPriority

logger = logging.getLogger(__name__)

class ExamplePlugin:
    """Example plugin with comprehensive hook integration."""

    def __init__(self, name: str, state_manager, event_bus, renderer, config):
        self.name = name
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.config = config

        # Plugin state
        self.message_count = 0
        self.processed_messages = []

        # Create hooks
        self.hooks = self._create_hooks()

    def _create_hooks(self) -> List[Hook]:
        """Create all plugin hooks."""
        timeout = self.config.get('plugins.example.hook_timeout', 30)

        return [
            # Input processing hooks
            Hook(
                name="validate_input",
                plugin_name=self.name,
                event_type=EventType.USER_INPUT_PRE,
                priority=HookPriority.PREPROCESSING.value,
                callback=self._validate_input,
                timeout=timeout
            ),
            Hook(
                name="enhance_input",
                plugin_name=self.name,
                event_type=EventType.USER_INPUT,
                priority=HookPriority.PREPROCESSING.value,
                callback=self._enhance_input,
                timeout=timeout
            ),
            Hook(
                name="log_input",
                plugin_name=self.name,
                event_type=EventType.USER_INPUT_POST,
                priority=HookPriority.POSTPROCESSING.value,
                callback=self._log_input,
                timeout=timeout
            ),

            # LLM hooks
            Hook(
                name="prepare_llm_request",
                plugin_name=self.name,
                event_type=EventType.LLM_REQUEST_PRE,
                priority=HookPriority.PREPROCESSING.value,
                callback=self._prepare_llm_request,
                timeout=timeout
            ),
            Hook(
                name="process_llm_response",
                plugin_name=self.name,
                event_type=EventType.LLM_RESPONSE_POST,
                priority=HookPriority.POSTPROCESSING.value,
                callback=self._process_llm_response,
                timeout=timeout
            )
        ]

    async def _validate_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Validate user input."""
        message = data.get('message', '')

        if len(message.strip()) == 0:
            event.cancelled = True
            return {"status": "cancelled", "reason": "empty_message"}

        if len(message) > 10000:  # Arbitrary limit
            event.cancelled = True
            return {"status": "cancelled", "reason": "message_too_long"}

        return {"status": "validated"}

    async def _enhance_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Enhance user input with additional context."""
        message = data.get('message', '')

        # Add message metadata
        enhanced_data = data.copy()
        enhanced_data.update({
            'message_id': self.message_count,
            'plugin_processed': True,
            'enhancement_timestamp': datetime.now().isoformat()
        })

        self.message_count += 1

        return {
            "data": enhanced_data,
            "status": "enhanced"
        }

    async def _log_input(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Log processed input."""
        message = data.get('message', '')
        message_id = data.get('message_id', 'unknown')

        log_entry = {
            'id': message_id,
            'message': message[:100],  # Truncate for logging
            'timestamp': datetime.now().isoformat()
        }

        self.processed_messages.append(log_entry)

        # Keep only recent messages
        if len(self.processed_messages) > 100:
            self.processed_messages = self.processed_messages[-100:]

        logger.info(f"Logged input message {message_id}")
        return {"status": "logged"}

    async def _prepare_llm_request(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Prepare LLM request with plugin context."""
        # Add plugin context to LLM request
        if 'context' not in data:
            data['context'] = {}

        data['context']['plugin_name'] = self.name
        data['context']['message_count'] = self.message_count

        return {
            "data": data,
            "status": "prepared"
        }

    async def _process_llm_response(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
        """Process LLM response."""
        response = data.get('response', '')

        # Log response statistics
        word_count = len(response.split())
        logger.info(f"LLM response processed: {word_count} words")

        return {
            "status": "processed",
            "word_count": word_count
        }

    # Required plugin methods
    async def initialize(self):
        """Initialize the plugin."""
        logger.info(f"Initializing {self.name} plugin")

    async def register_hooks(self):
        """Register all plugin hooks."""
        for hook in self.hooks:
            await self.event_bus.register_hook(hook)
        logger.info(f"Registered {len(self.hooks)} hooks for {self.name}")

    async def shutdown(self):
        """Shutdown the plugin."""
        logger.info(f"Shutting down {self.name} - processed {self.message_count} messages")

    def get_status_lines(self) -> Dict[str, List[str]]:
        """Get plugin status for display organized by area."""
        return {
            "A": [],  # Core system status
            "B": [    # Plugin-specific metrics
                f"Messages: {self.message_count}",
                f"Recent: {len(self.processed_messages)}"
            ],
            "C": []   # Detailed information
        }

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default plugin configuration."""
        return {
            "plugins": {
                "example": {
                    "enabled": True,
                    "hook_timeout": 30,
                    "log_level": "INFO"
                }
            }
        }
```

## Plugin Communication & Service Discovery

The Kollabor CLI system provides a sophisticated plugin ecosystem where plugins can discover, communicate with, and call services from other plugins. This enables powerful cross-plugin integration like JavaScript extension plugins working with coding aid plugins.

### Core Components for Plugin Communication

#### 1. Plugin Factory Methods

The `PluginFactory` provides essential methods for plugin discovery:

```python
# Access the plugin factory from your plugin
factory = self.get_factory()  # Available in plugin context

# Get a specific plugin instance
js_plugin = factory.get_instance("JavaScriptExtensionPlugin")

# Get all plugin instances for discovery
all_plugins = factory.get_all_instances()
# Returns: {"PluginName": plugin_instance, ...}

# Check instantiation status
errors = factory.get_instantiation_errors()
```

#### 2. KollaborPluginSDK Service Registration

Plugins can register services that other plugins can discover and use:

```python
from core.llm.plugin_sdk import KollaborPluginSDK

class JavaScriptExtensionPlugin:
    def __init__(self, name: str, state_manager, event_bus, renderer, config):
        self.name = name
        self.sdk = KollaborPluginSDK()
        # ... other initialization

    async def initialize(self):
        """Register this plugin's services."""
        # Register analysis service
        self.sdk.register_custom_tool({
            "name": "analyze_javascript",
            "description": "Analyze JavaScript code for syntax errors and suggestions",
            "handler": self.analyze_code,
            "parameters": {
                "code": {"type": "string", "description": "JavaScript code to analyze"}
            },
            "plugin": self.name,
            "enabled": True
        })

        # Register formatting service
        self.sdk.register_custom_tool({
            "name": "format_javascript",
            "description": "Format JavaScript code with proper styling",
            "handler": self.format_code,
            "parameters": {
                "code": {"type": "string", "description": "JavaScript code to format"},
                "style": {"type": "string", "description": "Formatting style (default: 'standard')"}
            },
            "plugin": self.name
        })

    async def analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze JavaScript code."""
        code = params.get("code", "")

        # Perform analysis (example implementation)
        issues = []
        suggestions = []

        if "var " in code:
            issues.append("Use 'let' or 'const' instead of 'var'")

        if code.count(";") < code.count("\n"):
            suggestions.append("Add semicolons for clarity")

        return {
            "syntax_valid": True,
            "issues": issues,
            "suggestions": suggestions,
            "complexity_score": len(code.split("\n"))
        }

    async def format_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Format JavaScript code."""
        code = params.get("code", "")
        style = params.get("style", "standard")

        # Format code (example implementation)
        formatted = code.replace("\t", "  ").strip()

        return {
            "formatted_code": formatted,
            "style_applied": style,
            "changes_made": ["normalized indentation"]
        }
```

#### 3. Service Discovery and Usage

Other plugins can discover and use these services:

```python
class CodingAidPlugin:
    async def initialize(self):
        """Discover available coding services."""
        # Method 1: Direct plugin instance access
        factory = self.get_factory()
        self.js_plugin = factory.get_instance("JavaScriptExtensionPlugin")

        # Method 2: SDK service discovery
        self.sdk = KollaborPluginSDK()
        self.available_tools = self.sdk.list_custom_tools()

        # Log discovered services
        js_tools = [tool for tool in self.available_tools if tool["plugin"] == "JavaScriptExtensionPlugin"]
        logger.info(f"Discovered {len(js_tools)} JavaScript services")

    async def process_code_request(self, code: str, language: str) -> str:
        """Process code analysis request."""

        if language.lower() == "javascript":
            # Method 1: Direct plugin method call
            if self.js_plugin:
                result = await self.js_plugin.analyze_code({"code": code})
                return f"Analysis: {len(result['issues'])} issues found"

            # Method 2: SDK service execution
            result = await self.sdk.execute_custom_tool("analyze_javascript", {"code": code})
            if result.get("status") == "success":
                analysis = result["result"]
                return f"Issues: {analysis['issues']}, Suggestions: {analysis['suggestions']}"

        return f"No analyzer available for {language}"

    async def format_code_request(self, code: str, language: str, style: str = "standard") -> str:
        """Format code using appropriate service."""

        if language.lower() == "javascript":
            result = await self.sdk.execute_custom_tool("format_javascript", {
                "code": code,
                "style": style
            })

            if result.get("status") == "success":
                return result["result"]["formatted_code"]

        return code  # Return unchanged if no formatter available
```

### 4. Event Bus Direct Messaging

Plugins can send direct messages to each other via the event bus:

```python
class SecurityPlugin:
    async def scan_complete_handler(self, scan_results: Dict[str, Any]):
        """Send scan results to other interested plugins."""

        # Send direct message to LLM plugin
        await self.event_bus.send_message(
            target_plugin="llm_plugin",
            data={
                "alert": "security_scan_complete",
                "results": scan_results,
                "priority": "high" if scan_results["threats_found"] > 0 else "normal"
            }
        )

        # Send to monitoring plugin
        await self.event_bus.send_message(
            target_plugin="hook_monitoring_plugin",
            data={
                "metric_update": {
                    "security_scans": scan_results["scan_count"],
                    "threats_detected": scan_results["threats_found"]
                }
            }
        )

class LLMPlugin:
    async def handle_direct_message(self, message: Dict[str, Any], sender: str):
        """Handle direct messages from other plugins."""

        if message.get("alert") == "security_scan_complete":
            priority = message.get("priority", "normal")
            results = message.get("results", {})

            if priority == "high":
                # Inject security context into next LLM request
                self.add_security_context(f"Security scan found {results['threats_found']} threats")

            logger.info(f"Received security update from {sender}")
```

### 5. Dynamic Service Discovery Patterns

For building flexible plugin ecosystems:

```python
class PluginDiscoveryMixin:
    """Mixin for plugins that need to discover services dynamically."""

    def discover_services_by_type(self, service_type: str) -> List[Dict[str, Any]]:
        """Find all plugins providing a specific service type."""
        factory = self.get_factory()
        all_plugins = factory.get_all_instances()

        services = []
        for plugin_name, plugin_instance in all_plugins.items():
            if hasattr(plugin_instance, 'get_services'):
                plugin_services = plugin_instance.get_services()
                for service_name, service_info in plugin_services.items():
                    if service_info.get('type') == service_type:
                        services.append({
                            'plugin': plugin_name,
                            'service': service_name,
                            'info': service_info
                        })

        return services

    async def call_best_service(self, service_type: str, params: Dict[str, Any]) -> Any:
        """Call the best available service for a given type."""
        services = self.discover_services_by_type(service_type)

        if not services:
            raise ServiceNotFoundError(f"No services found for type: {service_type}")

        # Sort by priority or other criteria
        best_service = max(services, key=lambda s: s['info'].get('priority', 0))

        # Call the service
        plugin = self.get_factory().get_instance(best_service['plugin'])
        service_method = getattr(plugin, best_service['service'])

        return await service_method(params)

class AdvancedCodingAidPlugin(PluginDiscoveryMixin):
    async def analyze_any_language(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code in any supported language."""

        try:
            # Try to find a specific analyzer
            result = await self.call_best_service(f"code_analysis_{language.lower()}", {
                "code": code
            })
            return result

        except ServiceNotFoundError:
            # Fall back to generic analysis
            services = self.discover_services_by_type("code_analysis_generic")
            if services:
                return await self.call_best_service("code_analysis_generic", {
                    "code": code,
                    "language": language
                })

            return {"error": f"No analyzer available for {language}"}
```

### Real-World Example: JavaScript Extension Ecosystem

Here's how a complete JavaScript extension would integrate:

```python
# plugins/javascript_extension_plugin.py
class JavaScriptExtensionPlugin:
    """Advanced JavaScript analysis and tooling plugin."""

    @staticmethod
    def get_default_config():
        return {
            "plugins": {
                "javascript_extension": {
                    "enabled": True,
                    "eslint_enabled": True,
                    "prettier_enabled": True,
                    "complexity_analysis": True,
                    "service_priority": 100
                }
            }
        }

    def get_services(self) -> Dict[str, Dict[str, Any]]:
        """Register services this plugin provides."""
        return {
            "analyze_javascript": {
                "type": "code_analysis_javascript",
                "priority": self.config.get("plugins.javascript_extension.service_priority", 100),
                "description": "Advanced JavaScript analysis with ESLint integration",
                "method": self.analyze_javascript
            },
            "format_javascript": {
                "type": "code_formatting_javascript",
                "priority": 100,
                "description": "Format JavaScript with Prettier",
                "method": self.format_javascript
            },
            "suggest_improvements": {
                "type": "code_improvement_javascript",
                "priority": 90,
                "description": "Suggest JavaScript best practices",
                "method": self.suggest_improvements
            }
        }

# plugins/coding_aid_plugin.py
class CodingAidPlugin(PluginDiscoveryMixin):
    """Universal coding assistance plugin."""

    async def handle_code_request(self, code: str, language: str, task: str) -> str:
        """Handle any coding-related request."""

        service_type = f"code_{task}_{language.lower()}"

        try:
            result = await self.call_best_service(service_type, {"code": code})

            return self.format_response(result, task, language)

        except ServiceNotFoundError:
            return f"Sorry, I don't have {task} capabilities for {language} yet. " \
                   f"Available services: {self.list_available_services()}"

    def list_available_services(self) -> str:
        """List all available coding services."""
        all_services = []
        for service_type in ["analysis", "formatting", "improvement"]:
            services = self.discover_services_by_type(f"code_{service_type}")
            for service in services:
                lang = service['service'].split('_')[-1]
                all_services.append(f"{lang} {service_type}")

        return ", ".join(set(all_services))
```

This ecosystem allows:
- **Dynamic service discovery** - coding aid finds all available language extensions
- **Graceful degradation** - falls back gracefully when services aren't available
- **Easy extension** - new language plugins just implement the service interface
- **Cross-plugin communication** - plugins can notify each other of analysis results
- **Priority-based selection** - best available service is automatically chosen

## Advanced Patterns

### Conditional Hook Registration

```python
def _create_hooks(self) -> List[Hook]:
    """Create hooks based on configuration."""
    hooks = []

    # Always include basic hooks
    hooks.append(self._create_basic_hook())

    # Conditional hooks based on config
    if self.config.get('plugins.example.enable_validation', True):
        hooks.append(self._create_validation_hook())

    if self.config.get('plugins.example.enable_enhancement', False):
        hooks.append(self._create_enhancement_hook())

    return hooks
```

### Hook Performance Monitoring

```python
import time

async def _monitored_hook(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    """Hook with performance monitoring."""
    start_time = time.time()

    try:
        # Main hook logic
        result = await self._process_data(data, event)

        # Log performance
        execution_time = (time.time() - start_time) * 1000
        if execution_time > 100:  # Warn on slow hooks
            logger.warning(f"Slow hook execution: {execution_time:.1f}ms")

        return result

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Hook failed after {execution_time:.1f}ms: {e}")
        raise
```

### Dynamic Hook Modification

```python
async def _adaptive_hook(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    """Hook that adapts based on runtime conditions."""

    # Adapt behavior based on system load
    current_load = self._get_system_load()

    if current_load > 0.8:
        # Simplified processing under high load
        return await self._fast_processing(data, event)
    else:
        # Full processing under normal load
        return await self._full_processing(data, event)
```

## Best Practices

### 1. Hook Design

- **Single Responsibility**: Each hook should have one clear purpose
- **Idempotent Operations**: Hooks should be safe to run multiple times
- **Graceful Degradation**: Handle missing data gracefully
- **Resource Management**: Clean up resources properly

### 2. Error Handling

```python
async def _robust_hook(self, data: Dict[str, Any], event: Event) -> Dict[str, Any]:
    """Example of robust error handling."""
    try:
        # Validate input data
        if not isinstance(data, dict):
            logger.warning("Invalid data type received")
            return {"status": "error", "reason": "invalid_data_type"}

        required_fields = ['message']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return {"status": "error", "reason": f"missing_{field}"}

        # Main processing
        result = self._process_safely(data)

        return {"status": "success", "result": result}

    except Exception as e:
        logger.error(f"Hook execution failed: {e}", exc_info=True)
        return {"status": "error", "reason": str(e)}
```

### 3. Performance Considerations

- **Timeout Management**: Set appropriate timeouts for your hooks
- **Resource Limits**: Avoid memory leaks and excessive resource usage
- **Async/Await**: Use proper async patterns for non-blocking execution
- **Caching**: Cache expensive operations when appropriate

### 4. Logging & Debugging

```python
import logging

logger = logging.getLogger(__name__)

# Use structured logging
logger.info("Hook executed", extra={
    'hook_name': self.name,
    'event_type': event.type.value,
    'execution_time_ms': execution_time,
    'data_size': len(str(data))
})

# Include context in error messages
logger.error(f"Hook {self.name} failed for event {event.type.value}: {e}")
```

## Troubleshooting

### Common Issues

1. **Hook Not Executing**
   - Check if hook is properly registered
   - Verify event type matches expected events
   - Check if plugin is enabled in configuration

2. **Event Cancellation**
   - Check if earlier hooks are cancelling events
   - Review hook priorities and execution order
   - Enable debug logging to trace event flow

3. **Performance Issues**
   - Check hook execution times in logs
   - Review hook timeouts and adjust if needed
   - Use the Hook Monitoring Plugin for detailed analysis

4. **Data Not Flowing**
   - Ensure hooks return `{"data": modified_data}` for transformations
   - Check if hooks are modifying event.data directly
   - Verify hook execution order and priorities

5. **Plugin Communication Issues**
   - Verify factory methods are accessible: `factory = self.get_factory()`
   - Check if target plugins are properly instantiated
   - Ensure service registration happens in `initialize()` method
   - Validate service names and plugin names match exactly

### Debug Tools

Use the Hook Monitoring Plugin (`plugins/hook_monitoring_plugin.py`) for comprehensive debugging:

```python
# Enable detailed monitoring
config = {
    "plugins": {
        "hook_monitoring": {
            "enabled": True,
            "log_all_events": True,
            "log_performance": True,
            "performance_threshold_ms": 50,
            "debug_logging": True,
            "show_status": True
        }
    }
}
```

### Log Analysis

Monitor `.kollabor-cli/logs/kollabor.log` for hook execution details:

```bash
# Filter hook-related logs
tail -f .kollabor-cli/logs/kollabor.log | grep "HOOK"

# Monitor performance issues
tail -f .kollabor-cli/logs/kollabor.log | grep "SLOW HOOK"
```

## Conclusion

The hook system provides powerful extensibility for the Kollabor CLI application. By following this SDK documentation and best practices, you can create sophisticated plugins that enhance, modify, or completely replace core application behavior.

For additional examples and implementation details, refer to:
- `plugins/enhanced_input_plugin.py` - UI enhancement example
- `plugins/hook_monitoring_plugin.py` - Comprehensive monitoring example
- `core/events/` - Core hook system implementation

The hook system's "everything has a hook" philosophy ensures maximum customization while maintaining clean separation of concerns and robust error handling.