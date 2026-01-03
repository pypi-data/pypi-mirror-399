# Bug Fix #2: Memory Leak in Queue Processing

## 🚨 **CRITICAL BUG** - MEMORY EXHAUSTION

**Location:** `core/llm/llm_service.py:388-430`
**Severity:** Critical
**Impact:** Infinite memory growth from unbounded queue

## 📋 **Bug Description**

The LLM service processes messages from an unbounded queue without any size limits or overflow handling. This can cause infinite memory growth during long chat sessions or when message processing falls behind.

### Current Problematic Code
```python
# core/llm/llm_service.py:388-430 (approximate)
class LLMService:
    def __init__(self):
        self.message_queue = asyncio.Queue()  # Unbounded queue!
        self.processing = False

    async def add_message(self, message):
        """Add message to processing queue."""
        await self.message_queue.put(message)  # No size limit!

    async def process_messages(self):
        """Process messages from queue."""
        while self.processing:
            message = await self.message_queue.get()
            # Process message...
```

### The Issue
- **Unbounded queue** can grow infinitely large
- **No backpressure** when processing falls behind
- **Memory exhaustion** during long sessions
- **No overflow handling** for high-volume message streams

## 🔧 **Fix Strategy**

### 1. Add Bounded Queue with Overflow Handling
```python
class LLMService:
    def __init__(self, max_queue_size=1000):
        self.max_queue_size = max_queue_size
        self.message_queue = asyncio.Queue(maxsize=max_queue_size)
        self.processing = False
        self.dropped_messages = 0

    async def add_message(self, message):
        """Add message to queue with overflow handling."""
        try:
            # Try to add message without blocking
            self.message_queue.put_nowait(message)
        except asyncio.QueueFull:
            # Queue is full - handle overflow
            self.dropped_messages += 1
            logger.warning(f"Queue full, dropping message (total dropped: {self.dropped_messages})")

            # Option 1: Drop oldest message
            try:
                self.message_queue.get_nowait()
                self.message_queue.put_nowait(message)
                logger.info("Dropped oldest message to make room")
            except asyncio.QueueEmpty:
                pass  # Queue is actually empty, this shouldn't happen
```

### 2. Add Queue Monitoring and Metrics
```python
class LLMService:
    def __init__(self, max_queue_size=1000):
        # ... existing code ...
        self.queue_size_history = []
        self.max_queue_usage = 0

    def get_queue_metrics(self):
        """Get current queue metrics."""
        current_size = self.message_queue.qsize()
        self.max_queue_usage = max(self.max_queue_usage, current_size)

        return {
            'current_size': current_size,
            'max_size': self.max_queue_size,
            'max_usage': self.max_queue_usage,
            'dropped_messages': self.dropped_messages,
            'utilization_percent': (current_size / self.max_queue_size) * 100
        }

    async def monitor_queue(self):
        """Monitor queue health and log warnings."""
        while self.processing:
            metrics = self.get_queue_metrics()

            if metrics['utilization_percent'] > 80:
                logger.warning(f"Queue utilization high: {metrics['utilization_percent']:.1f}%")

            if metrics['dropped_messages'] > 0:
                logger.warning(f"Messages dropped: {metrics['dropped_messages']}")

            await asyncio.sleep(5)  # Check every 5 seconds
```

### 3. Add Configurable Queue Sizes
```python
# core/config/llm_config.py
LLMConfig:
    queue:
        max_size: 1000
        overflow_strategy: "drop_oldest"  # drop_oldest, drop_newest, block
        monitoring_interval: 5  # seconds
```

### 4. Implement Different Overflow Strategies
```python
async def add_message(self, message, strategy="drop_oldest"):
    """Add message with configurable overflow strategy."""
    try:
        self.message_queue.put_nowait(message)
    except asyncio.QueueFull:
        self.dropped_messages += 1

        if strategy == "drop_oldest":
            # Remove oldest and add new
            try:
                self.message_queue.get_nowait()
                self.message_queue.put_nowait(message)
            except asyncio.QueueEmpty:
                pass

        elif strategy == "block":
            # Wait for space (with timeout)
            try:
                await asyncio.wait_for(
                    self.message_queue.put(message),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                logger.warning("Queue full and timeout reached, dropping message")

        elif strategy == "drop_newest":
            # Don't add the new message
            logger.warning("Queue full, dropping new message")
```

## ✅ **Implementation Steps**

1. **Replace unbounded queue** with bounded Queue(maxsize=N)
2. **Add overflow handling** with configurable strategies
3. **Implement queue monitoring** and metrics
4. **Add configuration options** for queue behavior
5. **Create queue health checks** and warnings
6. **Add tests** for overflow scenarios

## 🧪 **Testing Strategy**

1. **Test queue overflow behavior** - verify proper dropping
2. **Test different overflow strategies** - drop_oldest, drop_newest, block
3. **Test memory usage** - monitor with high-volume messages
4. **Test queue metrics** - verify monitoring works
5. **Test configuration** - ensure queue size is configurable

## 🚀 **Files to Modify**

- `core/llm/llm_service.py` - Main fix location
- `core/config/llm_config.py` - Add queue configuration
- `tests/test_llm_service.py` - Add queue overflow tests

## 📊 **Success Criteria**

- ✅ Queue has configurable maximum size
- ✅ Graceful handling of queue overflow
- ✅ No infinite memory growth
- ✅ Queue metrics and monitoring
- ✅ Configurable overflow strategies
- ✅ Proper logging of queue events

## 💡 **Why This Fixes the Issue**

This fix prevents memory exhaustion by:
- **Bounding the queue size** to prevent infinite growth
- **Implementing overflow strategies** when queue is full
- **Monitoring queue health** to detect issues early
- **Providing metrics** for performance tuning
- **Configuring behavior** based on use case needs

The memory leak is eliminated because the queue can't grow beyond the configured limit, and excess messages are handled gracefully instead of accumulating indefinitely.