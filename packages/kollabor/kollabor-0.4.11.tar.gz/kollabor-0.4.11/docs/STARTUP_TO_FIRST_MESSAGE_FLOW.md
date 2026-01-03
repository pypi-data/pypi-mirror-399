# 🚀 Kollabor CLI: Complete Startup to First Message Data Flow

**Purpose**: Trace the complete execution path from application startup through sending the first message and receiving a response, highlighting where streaming changes interfere with rendering.

**Status**: Current as of 2025-11-05 (includes recent streaming implementation)

---

## 📋 **PHASE 1: Application Startup**

### **Step 1.1: Entry Point** (`main.py`)

```python
# main.py:32
asyncio.run(main())
└── TerminalLLMChat.__init__()
```

**What Happens:**
1. Bootstrap logging initialized
2. Creates `.kollabor-cli/` directory structure
3. Initializes core application components

### **Step 1.2: Plugin System Initialization** (`core/application.py:34-35`)

```python
plugins_dir = Path.cwd() / "plugins"
self.plugin_registry = PluginRegistry(plugins_dir)
self.plugin_registry.load_all_plugins()
```

**Discovered Plugins:**
- `enhanced_input_plugin.py` ← **Input box rendering**
- `hook_monitoring_plugin.py`
- Other plugins (may fail to load)

**Critical**: Enhanced input plugin registers hooks for input rendering

### **Step 1.3: Configuration Service** (`core/application.py:38-41`)

```python
self.config = ConfigService(self.config_dir / "config.json", self.plugin_registry)
self.config.update_from_plugins()
```

**Loads Config:**
```json
{
  "plugins": {
    "enhanced_input": {
      "enabled": true,
      "style": "lines_only",  ← Controls input box lines
      "show_placeholder": true
    }
  }
}
```

### **Step 1.4: Core Components** (`core/application.py:46-64`)

```python
self.state_manager = StateManager(...)
self.event_bus = EventBus()
self.status_registry = StatusViewRegistry(self.event_bus)
self.renderer = TerminalRenderer(...)
self.input_handler = InputHandler(...)
```

**Event Bus**: Central nervous system for all plugin hooks

### **Step 1.5: LLM Core Initialization** (`core/application.py:166`)

```python
self._initialize_llm_core()
├── KollaborConversationLogger
├── LLMHookSystem
├── MCPIntegration
├── KollaborPluginSDK
└── LLMService
    ├── APICommunicationService  ← HTTP session management
    ├── MessageDisplayService    ← **STREAMING ADDED HERE** ⚠️
    ├── ResponseParser
    └── ToolExecutor
```

**Critical Hooks Registered:**
```python
# In llm_service.py:143-149
Hook(
    name="process_user_input",
    event_type=EventType.USER_INPUT,
    callback=self._handle_user_input  ← Processes user messages
)
```

### **Step 1.6: Plugin Instantiation** (`core/application.py:188`)

```python
self._initialize_plugins()
```

**Enhanced Input Plugin Initializes:**
```python
# plugins/enhanced_input_plugin.py:69-94
def __init__(self, name, state_manager, event_bus, renderer, config):
    self.config = InputConfig.from_config_manager(config)  # "lines_only"
    self.box_renderer = BoxRenderer(...)
    # Registers hooks for input rendering
```

### **Step 1.7: Main Loop Starts** (`core/application.py:106`)

```python
await Application.start()
├── Parallel Task 1: _render_loop() @ 20fps
└── Parallel Task 2: input_handler.start() ← User input processing
```

**Rendering Loop:**
```python
# core/application.py:241
while self.running:
    self.renderer.render()  # Updates display 20x per second
    await asyncio.sleep(1 / render_fps)
```

---

## 🎯 **PHASE 2: User Types First Message**

### **Step 2.1: Input Detection** (`core/io/input_handler.py:141`)

```python
async def _input_loop(self):
    while self.running:
        # Poll stdin with 10ms timeout
        readable, _, _ = select.select([sys.stdin], [], [], self.polling_delay)

        if readable:
            # Read raw bytes (8KB chunks)
            data = os.read(sys.stdin.fileno(), 8192)
```

**Input Flow:**
```
User Keyboard → Raw Bytes → Character Parser → Buffer Manager → Display
```

### **Step 2.2: Character Processing** (`core/io/input_handler.py:215`)

```python
for byte in data:
    char = chr(byte)
    key_press = self.key_parser.parse_char(char)  # Converts to KeyPress

    # Fire KEY_PRESS event for plugins
    await self.event_bus.emit_async(
        Event(type=EventType.KEY_PRESS, data={'key': key_press})
    )

    # Handle the key (insert into buffer, handle backspace, etc.)
    self._handle_key(key_press)
```

**Enhanced Input Plugin Hooks In:**
- Renders box around input area
- Shows placeholder text if empty
- Updates cursor position
- **Draws horizontal separator lines** ←  🚨 THIS IS WHAT'S BROKEN

### **Step 2.3: Display Update** (`core/io/input_handler.py:451`)

```python
# Update display after each character
display_info = self.buffer_manager.get_display_info()
self.renderer.update_input_text(display_info['text'])
self.renderer.update_cursor_position(display_info['cursor_column'])
```

**What Should Happen:**
```
Ready! Type your message and press Enter.
──────────────────────────────────────────────────────────────
> Hello, can you help me?▌
──────────────────────────────────────────────────────────────
```

**What Actually Happens:**
```
Ready! Type your message and press Enter.
> Hello, can you help me?▌

```
*(No separator lines!)*

---

## ⚡ **PHASE 3: User Presses Enter**

### **Step 3.1: Enter Key Detected** (`core/io/input_handler.py:363`)

```python
elif key.key == KeyType.ENTER:
    message = self.buffer_manager.get_text()

    # Expand paste placeholders if any
    message = self._expand_paste_placeholders(message)

    # Clear input buffer
    self.buffer_manager.clear()
```

### **Step 3.2: USER_INPUT Event Fired** (`core/io/input_handler.py:533`)

```python
await self.event_bus.emit_async(
    Event(
        type=EventType.USER_INPUT,
        data={
            'message': message,
            'timestamp': datetime.now()
        }
    )
)
```

**Event Bus Propagation:**
```
EventBus
├── EventProcessor.process_event()
├── HookRegistry.get_hooks_for_event(USER_INPUT)
├── HookExecutor.execute_hooks()
└── Calls all registered USER_INPUT hooks in priority order
```

---

## 🤖 **PHASE 4: LLM Processing**

### **Step 4.1: LLM Hook Triggered** (`core/llm/llm_service.py:148`)

```python
async def _handle_user_input(self, event: Event) -> None:
    """Main hook that processes user messages."""
    message = event.data.get('message', '')

    # Display user message
    self.message_display.display_user_message(message)

    # Process with LLM
    await self.send_message(message)
```

### **Step 4.2: Message Preparation** (`core/llm/llm_service.py:437`)

```python
async def send_message(self, message: str) -> None:
    # Build conversation history
    self.conversation_manager.add_user_message(message)
    messages = self.conversation_manager.get_messages()

    # Create API request payload
    request_data = {
        "model": self.model,
        "messages": messages,
        "temperature": self.temperature,
        "stream": False  ← NOT using streaming API (yet)
    }
```

### **Step 4.3: API Call** (`core/llm/llm_service.py:1071`)

```python
async def _call_llm(self) -> str:
    """Make API call using APICommunicationService."""

    # Reset streaming state ← **MY CHANGE**
    self._response_started = False
    self._streaming_buffer = ""
    self._in_thinking = False

    # Show thinking animation
    self.renderer.update_thinking(True, "Thinking...")
    start_time = time.time()

    # Make API request
    response_data = await self.api_service.send_request(
        method="post",
        request_data=request_data
    )
```

### **Step 4.4: HTTP Request** (`core/llm/api_communication_service.py:344`)

```python
async def _execute_request(self, method, request_data):
    """Execute HTTP request with session management."""

    # Ensure valid session
    await self._ensure_session()

    # Make request
    async with self.session.post(url, json=payload, headers=headers) as response:
        return await response.json()
```

---

## 📨 **PHASE 5: Response Processing**

### **Step 5.1: Response Received** (`core/llm/llm_service.py:1095`)

```python
# API response received
response_data = await self.api_service.send_request(...)

# Stop thinking animation
thinking_duration = time.time() - start_time
self.renderer.update_thinking(False)

# Extract response content
choices = response_data.get("choices", [])
content = choices[0]["message"]["content"]
```

### **Step 5.2: Response Parsing** (`core/llm/response_parser.py`)

```python
parsed_content, tool_calls = self.response_parser.parse_response(content)
```

**Response Structure:**
```
Raw API Response
├── Thinking tags: <think>...</think>  ← Removed from display
├── Plain text response
└── Tool calls (if any)
```

### **Step 5.3: Thinking Tag Processing** (`core/llm/llm_service.py:900-950`)

```python
def _handle_streaming_chunk(self, chunk: str):
    """Process streaming chunks (for thinking tags)."""

    # Add to buffer
    self._streaming_buffer += chunk

    # Check for thinking tags
    if '</think>' in self._streaming_buffer:
        # Extract thinking content
        # Display thinking sentences
        # **PROBLEM**: Calls _stream_response_chunk() here! ⚠️
        self._stream_response_chunk(parts[0])  # 🚨 THIS BREAKS INPUT RENDERING
```

### **Step 5.4: MY STREAMING CODE (THE PROBLEM!)** (`core/llm/llm_service.py:1053`)

```python
def _stream_response_chunk(self, chunk: str):
    """Stream response chunk to display."""

    # Initialize streaming response 🚨 PROBLEM!
    if not self._response_started:
        # THIS ACTIVATES STREAMING MODE GLOBALLY
        self.message_display.message_coordinator.message_renderer.start_streaming_response()
        self._response_started = True  ← State persists!

    # Write chunk
    self.message_display.message_coordinator.message_renderer.write_streaming_chunk(chunk)
```

**WHY THIS BREAKS INPUT LINES:**

1. `start_streaming_response()` gets called during thinking tag processing
2. This sets global streaming state in message renderer
3. Streaming state **never gets cleared** properly
4. Enhanced input plugin checks streaming state
5. If streaming active → **suppresses input box lines**
6. Result: Missing separator lines!

---

## 🎨 **PHASE 6: Display to User**

### **Step 6.1: Message Display** (`core/llm/message_display_service.py:37`)

```python
def display_complete_response(
    self,
    thinking_duration,
    response,
    tool_results=None
):
    """Display response atomically."""

    message_sequence = []

    # Add thinking duration
    if thinking_duration > 0.1:
        message_sequence.append(("system", f"Thought for {thinking_duration:.1f}s", {}))

    # Add assistant response (but skip if streaming already showed it!)
    if response.strip() and not skip_response_content:  ← MY CHANGE
        message_sequence.append(("assistant", response, {}))

    # Display everything
    self.message_coordinator.display_message_sequence(message_sequence)
```

### **Step 6.2: Back to Input Prompt** (`core/io/input_handler.py`)

```python
# Input handler still running
# User can type next message
# BUT: Streaming state still active! ← 🚨 PROBLEM
# Enhanced input plugin sees streaming = True
# Suppresses separator lines!
```

---

## 🚨 **ROOT CAUSE IDENTIFIED**

### **The Bug:**

```python
# In llm_service.py:1065
def _stream_response_chunk(self, chunk: str):
    if not self._response_started:
        self.message_display.message_coordinator.message_renderer.start_streaming_response()
        # ↑ This activates streaming mode GLOBALLY
        # ↑ It NEVER gets deactivated!
        # ↑ Enhanced input plugin sees this and suppresses lines!
```

### **The Flow:**

```
1. User sends message
2. LLM processes response
3. Thinking tags detected
4. _handle_streaming_chunk() called
5. Calls _stream_response_chunk()
6. Activates streaming mode
7. Response displays
8. Back to input prompt
9. ❌ Streaming mode STILL ACTIVE
10. ❌ Enhanced input plugin suppresses separator lines
11. ❌ User sees broken input box!
```

---

## 🔧 **THE FIX STRATEGY**

### **Option 1: Proper Streaming State Cleanup** (RECOMMENDED)

```python
# In llm_service.py
async def _call_llm(self):
    try:
        # Reset streaming state BEFORE request
        self._response_started = False

        # Make API call
        response = await self.api_service.send_request(...)

        # Process response
        content = self._process_response(response)

        return content
    finally:
        # ALWAYS cleanup streaming state after request completes
        self._cleanup_streaming_state()

def _cleanup_streaming_state(self):
    """Clean up streaming state completely."""
    self._response_started = False
    self._streaming_buffer = ""

    # CRITICAL: End streaming session in message display
    if self.message_display._streaming_active:
        self.message_display.end_streaming_response()
```

### **Option 2: Isolate Streaming from Input Rendering**

```python
# Don't activate streaming mode during thinking tag processing
# Only activate during ACTUAL API streaming responses
def _stream_response_chunk(self, chunk: str):
    # Add check: Only stream if API is actually streaming
    if not self.api_service.is_streaming:
        return  # Don't interfere with normal flow

    # Rest of streaming logic...
```

### **Option 3: Complete Revert** (FALLBACK)

```bash
# Revert streaming changes entirely
git checkout HEAD -- core/llm/llm_service.py
git checkout HEAD -- core/llm/message_display_service.py
```

---

## 📊 **MISSING STATUS PANES ISSUE**

**Separate Problem:** 7 panes → 5 panes

**Investigation Needed:**
1. Check `status_registry.register_status_view()` calls
2. Verify all plugins register their status views
3. Check if plugins are failing to load
4. Review `core/application.py:_register_core_status_views()`

**Config shows:** `"status_lines": 4` but user expects 7 panes

**Likely causes:**
- Plugins not loading correctly
- Status views not registered
- Configuration mismatch

---

## ✅ **NEXT STEPS**

1. **Implement Option 1** - Proper streaming cleanup
2. **Test input box lines restored**
3. **If fails** → Implement Option 2 or revert
4. **Separately investigate** status panes issue
5. **Create plugin management UI** for toggling plugins

---

## 📝 **SUMMARY**

**What Breaks:**
- Streaming state activates during thinking tag processing
- Never gets deactivated
- Enhanced input plugin suppresses lines when streaming active
- User sees broken input box

**The Fix:**
- Add proper `_cleanup_streaming_state()` method
- Call it in `finally` block after every LLM request
- Ensure `message_display.end_streaming_response()` is called

**Impact:**
- Zero changes to existing flow
- Just adds proper cleanup
- Streaming infrastructure stays in place for future use

---

**Document Status:** Ready for implementation
**Next Action:** Implement Option 1 fix with user approval