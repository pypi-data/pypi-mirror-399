# Kollabor CLI - Complete Application Dataflow Architecture

## Overview

This document provides a comprehensive analysis of the dataflow architecture for the Kollabor CLI application. The architecture is built around an event-driven system with modular components that communicate through hooks and events.

## 1. Application Startup Flow

```
main.py
├── setup_bootstrap_logging()  # Initial logging setup
└── asyncio.run(main())
    └── TerminalLLMChat.__init__()
        ├── Create .kollabor directory
        ├── Initialize PluginRegistry (with discovery, factory, collector)
        ├── ConfigService with plugin configurations
        ├── StateManager (SQLite persistence)
        ├── EventBus (hook system)
        ├── TerminalRenderer (visual effects, layout, status)
        └── InputHandler (raw mode, key parsing, command system)
            ├── KeyParser
            ├── BufferManager
            ├── SlashCommandParser
            ├── SlashCommandRegistry
            └── SlashCommandExecutor
```

## 2. Core Component Initialization

```
TerminalLLMChat.start()
├── _initialize_llm_core()  # LLM services initialization
│   ├── KollaborConversationLogger
│   ├── LLMHookSystem
│   ├── MCPIntegration
│   ├── KollaborPluginSDK
│   └── LLMService
│       ├── APICommunicationService
│       ├── ConversationLogger
│       ├── MessageDisplayService
│       ├── ResponseParser
│       └── ToolExecutor
├── _initialize_plugins()  # Dynamic plugin loading
├── _register_core_status_views()
└── Start parallel tasks:
    ├── _render_loop()  # 20fps status updates
    └── input_handler.start()  # User input processing
```

## 3. Main Event Loop Architecture

```
┌─ Application.start()
│
├─ Event Bus Coordination:
│   ├─ Hook Registration (plugins → EventBus)
│   ├─ Event Emission (components → EventBus)
│   └─ Hook Execution (EventBus → plugins)
│
├─ Input Processing Flow:
│   └── User Input → InputHandler._input_loop()
│       ├── select.select() polling (10ms delay)
│       ├── Raw data capture (os.read() - 8KB chunks)
│       ├── Multi-character paste detection
│       ├── Character-by-character processing
│       ├── KeyParser.parse_char() → KeyPress objects
│       ├── Event Bus processing (EventType.KEY_PRESS)
│       ├── Command mode detection ('/' triggers MENU_POPUP)
│       ├── Slash command processing (if detected)
│       └── Display updates
│
└─ Rendering Pipeline:
    └── StatusViewRegistry → TerminalRenderer
        ├── StatusRenderer (A, B, C areas)
        ├── MessageRenderer
        └── VisualEffects
```

## 4. Plugin System Dataflow

```
PluginRegistry
├── PluginDiscovery (file system scanning)
│   ├── Scan plugins/ directory
│   ├── Load plugin modules
│   └── Identify plugin classes
├── PluginFactory (instantiation)
│   ├── Dependency injection
│   ├── Plugin initialization
│   └── Error handling
└── PluginStatusCollector (status aggregation)
    ├── Collect plugin status lines
    └── Format for display
```

## 5. Full-Screen Plugin Framework

```
FullScreenManager
├── Plugin Registration:
│   ├── FullScreenPlugin base class
│   ├── Plugin metadata management
│   └── Lifecycle methods (initialize, on_start, render_frame, on_stop)
├── Modal Integration:
│   ├── MODAL_TRIGGER event emission
│   ├── Input routing (normal → modal)
│   └── Terminal state management
└── Session Management:
    ├── FullScreenSession creation
    ├── Plugin lifecycle coordination
    └── Cleanup and restoration
```

## 6. LLM Service Architecture

```
LLMService (core orchestrator)
├── APICommunicationService (HTTP client)
│   ├── Rate limiting
│   ├── Request/response handling
│   └── Error management
├── ConversationLogger (persistence)
│   ├── SQLite storage
│   ├── History management
│   └── Session tracking
├── MessageDisplayService (formatting)
│   ├── Response parsing
│   ├── Visual formatting
│   └── Display coordination
├── ToolExecutor (function calling)
│   ├── Terminal command execution
│   ├── MCP integration
│   └── Result processing
├── MCPIntegration (Model Context Protocol)
│   ├── Protocol implementation
│   ├── Tool registration
│   └── Session management
├── KollaborPluginSDK (plugin interface)
│   ├── Hook registration
│   ├── Tool registration
│   └── Event emission
└── LLMHookSystem (LLM-specific hooks)
    ├── Pre-processing hooks
    ├── Post-processing hooks
    └── Error handling hooks
```

## 7. Command System Dataflow

```
User Input → SlashCommandParser
├── Parse command format ("/command [args]")
├── Create SlashCommand object
└── Pass to SlashCommandExecutor

SlashCommandExecutor
├── Look up command in SlashCommandRegistry
├── Execute command handler
├── Emit SLASH_COMMAND_DETECTED event
└── Handle CommandResult

System Commands (examples):
├── /config → UIConfig modal (ModalRenderer)
├── /matrix → FullScreenPlugin (alternate buffer)
├── /help → CommandMenuRenderer
└── /status → Status display
```

## 8. Event System Architecture

```
EventBus (central coordinator)
├── HookRegistry (hook management)
│   ├── Hook registration by priority
│   ├── Hook lookup by event type
│   └── Hook lifecycle management
├── HookExecutor (hook execution)
│   ├── Sequential hook execution
│   ├── Error handling and recovery
│   └── Result aggregation
└── EventProcessor (event processing)
    ├── Event emission with hooks
    ├── Event filtering and routing
    └── Event lifecycle management
```

## 9. Input Processing Pipeline

```
Raw Terminal Input → InputHandler
├── Raw mode activation
├── Key sequence parsing (KeyParser)
│   ├── Character keys
│   ├── Control keys (Ctrl+C, Enter, etc.)
│   ├── Arrow keys and function keys
│   └── Escape sequences
├── Buffer management (BufferManager)
│   ├── Character insertion (100KB limit)
│   ├── Command history (100 commands)
│   └── Cursor tracking
├── Command detection and execution
├── Event emission (EventType.USER_INPUT)
└── Display updates (TerminalRenderer)
```

## 10. Configuration System

```
ConfigService (central configuration)
├── Configuration loading (.kollabor/config.json)
├── Dot notation access (config.get("core.llm.enabled"))
├── Configuration validation
├── Runtime configuration updates
└── Plugin configuration propagation

Configuration Persistence:
├── JSON file storage (.kollabor/config.json)
├── Atomic writes with backup
├── In-memory caching
└── Change notification system
```

## 11. State Management

```
StateManager (SQLite persistence)
├── Application state storage
├── Plugin state management
├── Statistics tracking
└── State restoration

State Persistence:
├── SQLite database (.kollabor/state.db)
├── Transaction management
├── State serialization
└── Error recovery
```

## 12. Key Integration Points

```
1. Event Bus Integration:
   - All components communicate via events
   - Hooks enable cross-component functionality
   - Event-driven architecture ensures loose coupling

2. Plugin Integration:
   - Plugins register hooks for event processing
   - Full-screen plugins have special integration
   - Plugin status affects display rendering

3. LLM Integration:
   - LLM services integrate via hooks
   - Tool execution extends LLM capabilities
   - MCP protocol enables external tools

4. UI Integration:
   - Modal system for configuration
   - Full-screen system for immersive experiences
   - Status system for real-time feedback
```

## 13. Primary and Secondary Data Flow Patterns

```
Primary Data Flows:
1. Input → Processing → Output (user interaction)
2. Events → Hooks → Actions (plugin system)
3. Configuration → Services → State (configuration system)
4. LLM → Tools → Results (AI functionality)
5. Plugins → Events → Display (UI integration)

Secondary Data Flows:
1. State → Persistence → Restoration
2. Commands → Handlers → Results
3. Messages → Formatting → Display
4. Errors → Handling → Recovery
```

## 14. Performance Characteristics

- **Render Loop**: 20fps default (configurable)
- **Input Polling**: 10ms delay (configurable)
- **Buffer Limits**: 100KB input buffer, 100 command history
- **Matrix Animation**: 1.2-3.5 speed range, 5-25 character columns
- **Event Processing**: Asynchronous with priority-based hook execution
- **Memory Management**: SQLite state persistence, rotating logs

## 15. Error Handling and Recovery

```
Error Handling Strategies:
1. Input Errors: Graceful degradation with error messages
2. Command Errors: Command-specific error handling
3. Plugin Errors: Isolated error handling with fallbacks
4. LLM Errors: Retry mechanisms with exponential backoff
5. Rendering Errors: Emergency state restoration

Recovery Mechanisms:
1. Automatic modal exit on critical errors
2. Terminal state emergency restoration
3. Configuration rollback on validation failures
4. CommandMode.NORMAL fallback guarantee
5. Graceful degradation for non-critical components
```

## 16. Debugging and Monitoring

```
Debugging Entry Points:
- Application logs: `.kollabor/logs/kollabor.log`
- Configuration: `.kollabor/config.json`
- State persistence: `.kollabor/state.db`
- Framework activation logs: Search for "🎯 NEW FRAMEWORK" in logs
- Event bus stats: Available via `EventBus.get_registry_stats()`

Performance Monitoring:
- Frame rate tracking in render loop
- Input processing latency
- LLM response times
- Plugin execution statistics
- Memory usage patterns
```

## 17. Component Dependencies

```
Core Dependencies:
- EventBus: Central communication hub
- ConfigService: Configuration management
- StateManager: State persistence
- TerminalRenderer: Display management
- InputHandler: Input processing

Service Dependencies:
- LLMService: Depends on APICommunicationService, MessageDisplayService
- PluginRegistry: Depends on PluginDiscovery, PluginFactory
- FullScreenManager: Depends on EventBus, TerminalRenderer

Plugin Dependencies:
- Plugins depend on EventBus for hook registration
- Full-screen plugins depend on FullScreenManager
- UI plugins depend on TerminalRenderer and ModalRenderer
```

## 18. Extensibility Points

```
Extension Interfaces:
1. Plugin System: Add new functionality through plugins
2. Hook System: Extend behavior through hooks
3. Command System: Add new slash commands
4. Tool System: Extend LLM capabilities
5. UI Components: Add new widgets and modals

Customization Options:
1. Configuration: Runtime configuration changes
2. Theming: Visual customization
3. Key Bindings: Input customization
4. Status Display: Custom status lines
5. Event Handlers: Custom event processing
```

## 19. Security Considerations

```
Security Measures:
1. Input Validation: All user inputs are validated
2. Command Filtering: Only registered commands are executed
3. Resource Limits: Buffer size limits prevent memory exhaustion
4. Safe Execution: Tool execution in controlled environment
5. Configuration Validation: Prevents invalid configuration

Data Protection:
1. State Persistence: Encrypted storage for sensitive data
2. Configuration: Secure file permissions
3. Logs: Sensitive data filtering
4. API Communication: Secure HTTP client
5. Input Sanitization: Protection against injection attacks
```

## 20. Future Enhancements

```
Planned Improvements:
1. Performance Optimization: Async improvements, caching
2. Enhanced UI: More sophisticated widgets and animations
3. Plugin Marketplace: Plugin discovery and installation
4. Advanced Tools: More sophisticated tool execution
5. Multi-Model Support: Multiple LLM model support

Long-term Goals:
1. Distributed Architecture: Multi-node processing
2. Advanced Analytics: Usage statistics and insights
3. Cloud Integration: Cloud-based LLM services
4. Mobile Support: Mobile application companion
5. Enterprise Features: Team management, compliance
```

---

This document provides a comprehensive overview of the Kollabor CLI application dataflow architecture. The architecture is designed to be modular, extensible, and maintainable while providing a rich set of features for terminal-based AI interaction.
