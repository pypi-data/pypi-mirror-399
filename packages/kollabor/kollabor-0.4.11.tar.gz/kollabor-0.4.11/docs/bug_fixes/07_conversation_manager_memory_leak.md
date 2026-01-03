# Bug Fix #7: Memory Leak in Conversation Manager

## ⚠️ **HIGH SEVERITY BUG** - DATA LOSS & MEMORY LEAK

**Location:** `core/llm/conversation_manager.py:115-116`
**Severity:** High
**Impact:** Data loss on crashes, inefficient saves

## 📋 **Bug Description**

The conversation manager saves conversations based solely on message count, which can lead to data loss if the application crashes before reaching the save threshold, and inefficient memory usage from holding too many conversations in memory.

### Current Problematic Code
```python
# core/llm/conversation_manager.py:115-116 (approximate)
class ConversationManager:
    def __init__(self):
        self.conversations = {}
        self.save_threshold = 100  # Save every 100 messages
        self.message_count = 0

    async def add_message(self, conversation_id, message):
        """Add message to conversation."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []

        self.conversations[conversation_id].append(message)
        self.message_count += 1

        # ← PROBLEM: Only saves on count, no time-based saving
        if self.message_count >= self.save_threshold:
            await self.save_conversations()
            self.message_count = 0
```

### The Issue
- **Count-based saving only** - can lose data on crashes
- **No time-based persistence** - conversations can be lost
- **Unbounded memory growth** - all conversations kept in memory
- **Inefficient save strategy** - can miss important saves
- **No memory pressure handling** - can exhaust RAM

## 🔧 **Fix Strategy**

### 1. Implement Hybrid Save Strategy (Count + Time)
```python
import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, List[dict]] = {}
        self.save_threshold = 50  # Reduced threshold
        self.time_save_interval = 300  # Save every 5 minutes
        self.max_conversations_in_memory = 1000
        self.max_messages_per_conversation = 1000

        # Save tracking
        self.message_count = 0
        self.last_save_time = time.time()
        self.pending_saves = set()
        self.save_in_progress = False

        # Memory management
        self.conversation_access_times = {}
        self.memory_cleanup_interval = 600  # 10 minutes

    async def add_message(self, conversation_id: str, message: dict) -> bool:
        """Add message with hybrid save strategy."""
        try:
            # Ensure conversation exists
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []

            # Add message
            self.conversations[conversation_id].append(message)
            self.message_count += 1

            # Update access time for memory management
            self.conversation_access_times[conversation_id] = time.time()

            # Mark for saving
            self.pending_saves.add(conversation_id)

            # Check save conditions
            await self._check_save_conditions()

            # Check memory pressure
            await self._check_memory_pressure()

            return True

        except Exception as e:
            logger.error(f"Error adding message to {conversation_id}: {e}")
            return False

    async def _check_save_conditions(self):
        """Check if conversations should be saved."""
        current_time = time.time()
        save_reason = None

        # Condition 1: Message count threshold
        if self.message_count >= self.save_threshold:
            save_reason = "message_count_threshold"

        # Condition 2: Time-based saving
        elif current_time - self.last_save_time >= self.time_save_interval:
            save_reason = "time_interval"

        # Condition 3: Critical data (important messages)
        elif self._has_critical_messages():
            save_reason = "critical_messages"

        # Condition 4: Memory pressure
        elif len(self.conversations) > self.max_conversations_in_memory * 0.8:
            save_reason = "memory_pressure"

        if save_reason:
            logger.info(f"Triggering save due to: {save_reason}")
            await self.save_pending_conversations()

    async def _has_critical_messages(self) -> bool:
        """Check if there are critical messages that need immediate saving."""
        for conversation_id, messages in self.conversations.items():
            for message in messages[-10:]:  # Check last 10 messages
                # Look for important content
                if (message.get('important') or
                    'error' in message.get('content', '').lower() or
                    'critical' in message.get('content', '').lower()):
                    return True
        return False

    async def save_pending_conversations(self):
        """Save all pending conversations."""
        if self.save_in_progress or not self.pending_saves:
            return

        self.save_in_progress = True

        try:
            # Create copy of pending saves to avoid modification during save
            conversations_to_save = list(self.pending_saves)
            self.pending_saves.clear()

            # Save each conversation
            saved_count = 0
            for conversation_id in conversations_to_save:
                if await self._save_conversation(conversation_id):
                    saved_count += 1

            # Update save tracking
            self.message_count = 0
            self.last_save_time = time.time()

            logger.info(f"Saved {saved_count} conversations")

        except Exception as e:
            logger.error(f"Error during conversation save: {e}")
            # Re-add failed saves to pending set
            self.pending_saves.update(conversations_to_save)
        finally:
            self.save_in_progress = False

    async def _save_conversation(self, conversation_id: str) -> bool:
        """Save a single conversation to storage."""
        try:
            if conversation_id not in self.conversations:
                return True  # Nothing to save

            messages = self.conversations[conversation_id]
            if not messages:
                return True

            # Use your storage service to save
            save_data = {
                'conversation_id': conversation_id,
                'messages': messages,
                'timestamp': datetime.now().isoformat(),
                'message_count': len(messages)
            }

            # Save to your storage system
            # await self.storage_service.save_conversation(save_data)
            logger.debug(f"Saved conversation {conversation_id} with {len(messages)} messages")

            return True

        except Exception as e:
            logger.error(f"Error saving conversation {conversation_id}: {e}")
            return False
```

### 2. Implement Memory Management
```python
async def _check_memory_pressure(self):
    """Check and handle memory pressure."""
    total_conversations = len(self.conversations)

    # Check if we need to free memory
    if total_conversations > self.max_conversations_in_memory:
        logger.warning(f"Memory pressure: {total_conversations} conversations in memory")
        await self._cleanup_old_conversations()

async def _cleanup_old_conversations(self):
    """Remove old conversations from memory to free space."""
    try:
        # Sort conversations by last access time
        sorted_conversations = sorted(
            self.conversation_access_times.items(),
            key=lambda x: x[1]
        )

        # Remove oldest conversations (but keep recent ones)
        conversations_to_remove = sorted_conversations[:len(sorted_conversations) // 4]  # Remove 25%

        removed_count = 0
        for conversation_id, _ in conversations_to_remove:
            # Save before removing if not already saved
            if conversation_id in self.pending_saves:
                await self._save_conversation(conversation_id)
                self.pending_saves.discard(conversation_id)

            # Remove from memory
            del self.conversations[conversation_id]
            del self.conversation_access_times[conversation_id]
            removed_count += 1

        logger.info(f"Cleaned up {removed_count} old conversations from memory")

    except Exception as e:
        logger.error(f"Error during conversation cleanup: {e}")

async def _limit_conversation_size(self, conversation_id: str):
    """Limit the size of individual conversations."""
    if conversation_id not in self.conversations:
        return

    messages = self.conversations[conversation_id]
    if len(messages) <= self.max_messages_per_conversation:
        return

    # Save full conversation before truncating
    await self._save_conversation(conversation_id)

    # Keep only recent messages
    excess_count = len(messages) - self.max_messages_per_conversation
    self.conversations[conversation_id] = messages[-self.max_messages_per_conversation:]

    logger.info(f"Truncated conversation {conversation_id}, removed {excess_count} old messages")
```

### 3. Add Recovery and Resilience
```python
async def startup_recovery(self):
    """Perform recovery procedures on startup."""
    try:
        logger.info("Starting conversation manager recovery...")

        # Check for unsaved conversations from previous session
        # This could involve checking temporary files or recovery logs

        # Validate conversation integrity
        await self._validate_conversations()

        # Save any pending data
        if self.pending_saves:
            logger.info(f"Recovering {len(self.pending_saves)} pending saves")
            await self.save_pending_conversations()

        logger.info("Conversation manager recovery complete")

    except Exception as e:
        logger.error(f"Error during startup recovery: {e}")

async def _validate_conversations(self):
    """Validate conversation data integrity."""
    invalid_conversations = []

    for conversation_id, messages in self.conversations.items():
        try:
            # Basic validation
            if not isinstance(messages, list):
                invalid_conversations.append(conversation_id)
                continue

            for i, message in enumerate(messages):
                if not isinstance(message, dict):
                    logger.warning(f"Invalid message at index {i} in {conversation_id}")
                    # Remove invalid message
                    messages.pop(i)

        except Exception as e:
            logger.error(f"Error validating conversation {conversation_id}: {e}")
            invalid_conversations.append(conversation_id)

    # Remove invalid conversations
    for conv_id in invalid_conversations:
        del self.conversations[conv_id]
        if conv_id in self.conversation_access_times:
            del self.conversation_access_times[conv_id]

    if invalid_conversations:
        logger.warning(f"Removed {len(invalid_conversations)} invalid conversations")

async def shutdown_cleanup(self):
    """Perform cleanup before shutdown."""
    try:
        logger.info("Starting conversation manager shutdown...")

        # Save all pending conversations
        if self.pending_saves:
            logger.info(f"Saving {len(self.pending_saves)} pending conversations")
            await self.save_pending_conversations()

        # Save all conversations
        for conversation_id in self.conversations:
            await self._save_conversation(conversation_id)

        logger.info("Conversation manager shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown cleanup: {e}")
```

### 4. Add Monitoring and Metrics
```python
def get_memory_usage_stats(self):
    """Get memory usage statistics."""
    total_messages = sum(len(msgs) for msgs in self.conversations.values())

    return {
        'total_conversations': len(self.conversations),
        'total_messages': total_messages,
        'pending_saves': len(self.pending_saves),
        'memory_usage_estimate': total_messages * 1024,  # Rough estimate
        'oldest_conversation_age': self._get_oldest_conversation_age(),
        'newest_conversation_age': self._get_newest_conversation_age()
    }

def _get_oldest_conversation_age(self) -> Optional[float]:
    """Get age of oldest conversation in seconds."""
    if not self.conversation_access_times:
        return None
    oldest_time = min(self.conversation_access_times.values())
    return time.time() - oldest_time

def _get_newest_conversation_age(self) -> Optional[float]:
    """Get age of newest conversation in seconds."""
    if not self.conversation_access_times:
        return None
    newest_time = max(self.conversation_access_times.values())
    return time.time() - newest_time
```

### 5. Add Configuration Options
```python
# core/config/conversation_config.py
class ConversationConfig:
    save:
        message_count_threshold: int = 50
        time_save_interval: int = 300  # 5 minutes
        critical_message_detection: bool = True

    memory:
        max_conversations_in_memory: int = 1000
        max_messages_per_conversation: int = 1000
        cleanup_interval: int = 600  # 10 minutes
        cleanup_threshold_percent: float = 0.8

    recovery:
        enable_startup_recovery: bool = True
        validate_integrity: bool = True
        auto_save_on_shutdown: bool = True
```

## ✅ **Implementation Steps**

1. **Implement hybrid save strategy** (count + time + critical detection)
2. **Add memory management** with conversation limits and cleanup
3. **Create recovery procedures** for startup and shutdown
4. **Add comprehensive metrics** and monitoring
5. **Implement data validation** and integrity checks
6. **Add configuration options** for all thresholds and behaviors

## 🧪 **Testing Strategy**

1. **Test hybrid save strategy** - verify all save conditions work
2. **Test memory management** - verify cleanup works under pressure
3. **Test crash recovery** - simulate crashes and verify data recovery
4. **Test data integrity** - verify corrupted data is handled
5. **Test memory limits** - verify conversation size limits work
6. **Test concurrent access** - verify thread safety of operations

## 🚀 **Files to Modify**

- `core/llm/conversation_manager.py` - Main fix location
- `core/config/conversation_config.py` - Add configuration
- `tests/test_conversation_manager.py` - Add comprehensive tests
- `core/storage/conversation_storage.py` - Update storage interface

## 📊 **Success Criteria**

- ✅ Conversations saved on multiple triggers (count, time, critical)
- ✅ Memory usage stays bounded under all conditions
- ✅ Data recovery works after crashes
- ✅ No data loss during normal operation
- ✅ Comprehensive monitoring and metrics available
- ✅ Configurable thresholds and behaviors

## 💡 **Why This Fixes the Issue**

This fix eliminates data loss and memory leaks by:
- **Hybrid save strategy** ensures data is saved frequently for different reasons
- **Time-based saving** prevents data loss during crashes
- **Memory management** prevents unbounded growth
- **Recovery procedures** handle crash scenarios gracefully
- **Data validation** ensures corrupted data is handled properly
- **Comprehensive monitoring** provides visibility into system health

The memory leak and data loss issues are eliminated because conversations are saved frequently for multiple reasons, memory usage is actively managed, and recovery procedures ensure data integrity even after crashes.