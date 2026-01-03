"""Core LLM Service for Kollabor CLI.

This is the essential LLM service that provides core language model
functionality as a critical part of the application infrastructure.
"""

import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Optional
from datetime import datetime

from ..models import ConversationMessage
from ..events import EventType, Hook, HookPriority
from ..config.llm_task_config import LLMTaskConfig
from .api_communication_service import APICommunicationService
from .conversation_logger import KollaborConversationLogger
from .conversation_manager import ConversationManager
from .hook_system import LLMHookSystem
from .mcp_integration import MCPIntegration
from .message_display_service import MessageDisplayService
from .response_parser import ResponseParser
from .tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


class LLMService:
    """Core LLM service providing essential language model functionality.
    
    This service is initialized as a core component and cannot be disabled.
    It manages conversation history, model communication, and intelligent
    conversation logging with memory features.
    """

    def _add_conversation_message(self, message_or_role, content=None, parent_uuid=None) -> str:
        """Add a message to both conversation manager and legacy history.

        This wrapper method ensures that messages are added to both the
        ConversationManager and the legacy conversation_history for compatibility.

        Args:
            message_or_role: Either a ConversationMessage object or a role string
            content: Message content (required if first arg is role string)
            parent_uuid: Optional parent UUID for message threading

        Returns:
            UUID of the added message
        """
        from ..models import ConversationMessage

        # Handle both signatures: ConversationMessage object or separate role/content
        if isinstance(message_or_role, ConversationMessage):
            message = message_or_role
            role = message.role
            content = message.content
        else:
            role = message_or_role
            if content is None:
                raise TypeError("Content is required when role is provided as string")
            message = ConversationMessage(role=role, content=content)

        # Add to conversation manager if available
        if hasattr(self, "conversation_manager") and self.conversation_manager:
            message_uuid = self.conversation_manager.add_message(
                role=role,
                content=content,
                parent_uuid=parent_uuid
            )
        else:
            # Fallback - create a UUID if conversation manager not available
            import uuid
            message_uuid = str(uuid.uuid4())

        # Add to legacy history for compatibility
        self.conversation_history.append(message)

        return message_uuid

    
    def __init__(
        self,
        config,
        state_manager,
        event_bus,
        renderer,
        profile_manager=None,
        agent_manager=None,
        default_timeout: Optional[float] = None,
        enable_metrics: bool = False,
    ):
        """Initialize the core LLM service.

        Args:
            config: Configuration manager instance
            state_manager: State management system
            event_bus: Event bus for hook registration
            renderer: Terminal renderer for output
            profile_manager: Profile manager for LLM endpoint profiles
            agent_manager: Agent manager for agent/skill system
            default_timeout: Default timeout for background tasks in seconds
            enable_metrics: Whether to enable detailed task metrics tracking
        """
        self.config = config
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.profile_manager = profile_manager
        self.agent_manager = agent_manager

        # Timeout and metrics configuration
        self.default_timeout = default_timeout
        self.enable_metrics = enable_metrics

        # Load LLM configuration from core.llm section (API details handled by API service)
        self.max_history = config.get("core.llm.max_history", 90)

        # Load task management configuration using structured dataclass
        task_config_dict = config.get("core.llm.task_management", {})
        self.task_config = LLMTaskConfig.from_dict(task_config_dict)

        # Conversation state
        self.conversation_history: List[ConversationMessage] = []
          # Queue management with memory leak prevention
        self.max_queue_size = self.task_config.queue.max_size
        self.processing_queue = asyncio.Queue(maxsize=self.max_queue_size)
        self.dropped_messages = 0
        self.is_processing = False
        self.turn_completed = False
        self.cancel_processing = False
        self.cancellation_message_shown = False
        
        # Initialize conversation logger with intelligence features
        from ..utils.config_utils import get_config_directory
        config_dir = get_config_directory()
        conversations_dir = config_dir / "conversations"
        conversations_dir.mkdir(parents=True, exist_ok=True)

        # Initialize raw conversation logging directory
        self.raw_conversations_dir = config_dir / "conversations_raw"
        self.raw_conversations_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_logger = KollaborConversationLogger(conversations_dir)

        # Initialize conversation manager for advanced features
        self.conversation_manager = ConversationManager(
            config=self.config,
            conversation_logger=self.conversation_logger
        )

        # Initialize hook system
        self.hook_system = LLMHookSystem(event_bus)
        
        # Initialize MCP integration and tool components
        self.mcp_integration = MCPIntegration()
        self.response_parser = ResponseParser()
        self.tool_executor = ToolExecutor(
            mcp_integration=self.mcp_integration,
            event_bus=event_bus,
            terminal_timeout=config.get("core.llm.terminal_timeout", 30),
            mcp_timeout=config.get("core.llm.mcp_timeout", 60)
        )
        
        # Initialize message display service (KISS/DRY: eliminates duplicated display code)
        self.message_display = MessageDisplayService(renderer)
        
        # Initialize API communication service (KISS: pure API communication separation)
        self.api_service = APICommunicationService(config, self.raw_conversations_dir)

        # Link session ID for raw log correlation
        self.api_service.set_session_id(self.conversation_logger.session_id)

        # Track current message threading
        self.current_parent_uuid = None
        
        # Create hooks for LLM service
        self.hooks = [
            Hook(
                name="process_user_input",
                plugin_name="llm_core",
                event_type=EventType.USER_INPUT,
                priority=HookPriority.LLM.value,
                callback=self._handle_user_input
            ),
            Hook(
                name="cancel_request",
                plugin_name="llm_core",
                event_type=EventType.CANCEL_REQUEST,
                priority=HookPriority.SYSTEM.value,
                callback=self._handle_cancel_request
            ),
            Hook(
                name="add_message_handler",
                plugin_name="llm_core",
                event_type=EventType.ADD_MESSAGE,
                priority=HookPriority.LLM.value,
                callback=self._handle_add_message
            )
        ]
        
        # Session statistics
        self.stats = {
            "total_messages": 0,
            "total_thinking_time": 0.0,
            "sessions_count": 0,
            "last_session": None,
            "total_input_tokens": 0,
            "total_output_tokens": 0
        }
        
        self.session_stats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "messages": 0
        }
        
        # Current processing state
        self.current_processing_tokens = 0
        self.processing_start_time = None

        # Background task tracking system
        self._background_tasks: Set[asyncio.Task] = set()
        self._task_metadata: Dict[str, Any] = {}
        self._max_concurrent_tasks = self.task_config.background_tasks.max_concurrent
        self._task_error_count = 0
        self._monitoring_task: Optional[asyncio.Task] = None

        # Circuit breaker state variables
        self._circuit_breaker_state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

        # Queue overflow metrics counters
        self._queue_metrics = {
            'drop_oldest_count': 0,
            'drop_newest_count': 0,
            'block_count': 0,
            'block_timeout_count': 0,
            'total_enqueue_attempts': 0,
            'total_enqueue_successes': 0
        }
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure_time = None
        self._circuit_breaker_test_task_running = False

        # Metrics tracking system
        if self.enable_metrics:
            self._task_metrics: Dict[str, Dict[str, Any]] = {}

        logger.info("Core LLM Service initialized")
    
    async def initialize(self) -> bool:
        """Initialize the LLM service components."""
        # Initialize API communication service (KISS refactoring)
        await self.api_service.initialize()

        # Register hooks
        await self.hook_system.register_hooks()
        
        # Discover and register MCP servers and tools
        try:
            discovered_servers = await self.mcp_integration.discover_mcp_servers()
            logger.info(f"Discovered {len(discovered_servers)} MCP servers")
        except Exception as e:
            logger.warning(f"MCP discovery failed: {e}")
        
        # Initialize conversation with context
        await self._initialize_conversation()
        
        # Log conversation start
        await self.conversation_logger.log_conversation_start()

        # Start task monitoring
        if self.task_config.background_tasks.enable_monitoring:
            await self.start_task_monitor()

        logger.info("Core LLM Service initialized and ready")
        return True
    
    async def _initialize_conversation(self):
        """Initialize conversation with project context."""
        try:
            # Clear any existing history
            self.conversation_history = []
            self.state_manager.set("llm.conversation_history", [])
            
            # Build system prompt from configuration
            initial_message = self._build_system_prompt()

            self._add_conversation_message(ConversationMessage(
                role="system",
                content=initial_message
            ))
            
            # Log initial context message
            self.current_parent_uuid = await self.conversation_logger.log_user_message(
                initial_message,
                user_context={
                    "type": "system_initialization",
                    "project_context_loaded": True
                }
            )
            
            logger.info("Conversation initialized with project context")

        except Exception as e:
            logger.error(f"Failed to initialize conversation: {e}")

    async def _enqueue_with_overflow_strategy(self, message: str) -> None:
        """Enqueue message with configurable overflow strategy.

        Args:
            message: Message to enqueue

        Raises:
            RuntimeError: If overflow_strategy is 'drop_newest' and queue is full
        """
        self._queue_metrics['total_enqueue_attempts'] += 1

        # Log queue events if enabled
        if self.task_config.queue.log_queue_events:
            logger.debug(f"Attempting to enqueue message (queue size: {self.processing_queue.qsize()}/{self.max_queue_size})")

        # Try to enqueue immediately
        try:
            self.processing_queue.put_nowait(message)
            self._queue_metrics['total_enqueue_successes'] += 1
            if self.task_config.queue.log_queue_events:
                logger.debug(f"Message enqueued successfully")
            return
        except asyncio.QueueFull:
            pass  # Queue is full, apply overflow strategy

        # Apply configured overflow strategy
        strategy = self.task_config.queue.overflow_strategy

        if strategy == "drop_oldest":
            # Cancel oldest task by start_time and drop it
            if self.task_config.queue.log_queue_events:
                logger.debug("Applying drop_oldest strategy")

            # Find oldest task by start_time
            oldest_task = None
            oldest_start_time = None

            for task in self._background_tasks:
                task_name = task.get_name()
                if task_name in self._task_metadata:
                    start_time = self._task_metadata[task_name].get('created_at')
                    if start_time and (oldest_start_time is None or start_time < oldest_start_time):
                        oldest_task = task
                        oldest_start_time = start_time

            if oldest_task:
                oldest_task.cancel()
                self._queue_metrics['drop_oldest_count'] += 1
                if self.task_config.queue.log_queue_events:
                    logger.info(f"Cancelled oldest task {oldest_task.get_name()} to make room")

                # Wait a moment for cancellation to take effect
                await asyncio.sleep(0.01)

            # Try to enqueue again
            try:
                self.processing_queue.put_nowait(message)
                self._queue_metrics['total_enqueue_successes'] += 1
                if self.task_config.queue.log_queue_events:
                    logger.info("Message enqueued after dropping oldest task")
            except asyncio.QueueFull:
                # Still full, drop the message
                self.dropped_messages += 1
                if self.task_config.queue.log_queue_events:
                    logger.warning("Queue still full after dropping oldest task, dropping message")

        elif strategy == "drop_newest":
            # Raise RuntimeError when queue is full
            self._queue_metrics['drop_newest_count'] += 1
            if self.task_config.queue.log_queue_events:
                logger.debug("Applying drop_newest strategy - raising RuntimeError")
            raise RuntimeError(f"Queue is full (max size: {self.max_queue_size}) and overflow strategy is 'drop_newest'")

        elif strategy == "block":
            # Wait with asyncio.sleep polling until space or block_timeout
            self._queue_metrics['block_count'] += 1
            if self.task_config.queue.log_queue_events:
                logger.debug(f"Applying block strategy (timeout: {self.task_config.queue.block_timeout}s)")

            start_time = time.time()
            poll_interval = 0.01  # 10ms polling

            while True:
                # Check if queue has space
                if self.processing_queue.qsize() < self.max_queue_size:
                    try:
                        self.processing_queue.put_nowait(message)
                        self._queue_metrics['total_enqueue_successes'] += 1
                        if self.task_config.queue.log_queue_events:
                            logger.info("Message enqueued after blocking")
                        return
                    except asyncio.QueueFull:
                        pass  # Still full, continue blocking

                # Check timeout
                elapsed = time.time() - start_time
                if self.task_config.queue.block_timeout is not None and elapsed >= self.task_config.queue.block_timeout:
                    self._queue_metrics['block_timeout_count'] += 1
                    if self.task_config.queue.log_queue_events:
                        logger.warning(f"Block timeout after {elapsed:.2f}s, dropping message")
                    self.dropped_messages += 1
                    return

                # Brief sleep before next poll
                await asyncio.sleep(poll_interval)

        else:
            # Unknown strategy, default to dropping oldest
            logger.warning(f"Unknown overflow strategy '{strategy}', defaulting to drop_oldest")
            try:
                self.processing_queue.get_nowait()  # Drop oldest
                self.processing_queue.put_nowait(message)
                self._queue_metrics['total_enqueue_successes'] += 1
            except asyncio.QueueEmpty:
                self.dropped_messages += 1

    def create_background_task(self, coro, name: str = None) -> asyncio.Task:
        """Create and track a background task with proper error handling and circuit breaker."""
        # Check circuit breaker state
        if self.task_config.background_tasks.enable_task_circuit_breaker:
            # Reject tasks if circuit is OPEN
            if self._circuit_breaker_state == "OPEN":
                # Check if timeout has passed to transition to HALF_OPEN
                if self._circuit_breaker_last_failure_time:
                    time_since_failure = time.time() - self._circuit_breaker_last_failure_time
                    timeout = self.task_config.background_tasks.circuit_breaker_timeout
                    if time_since_failure >= timeout:
                        logger.info(f"Circuit breaker timeout elapsed, transitioning to HALF_OPEN")
                        self._circuit_breaker_state = "HALF_OPEN"
                        self._circuit_breaker_test_task_running = False
                    else:
                        logger.warning(f"Circuit breaker OPEN - rejecting task '{name or 'unnamed'}'")
                        raise Exception(f"Circuit breaker OPEN - tasks rejected for {timeout - time_since_failure:.1f}s more")
                else:
                    logger.warning(f"Circuit breaker OPEN - rejecting task '{name or 'unnamed'}'")
                    raise Exception("Circuit breaker OPEN - tasks rejected")

            # Allow only one test task in HALF_OPEN state
            elif self._circuit_breaker_state == "HALF_OPEN" and self._circuit_breaker_test_task_running:
                logger.warning(f"Circuit breaker HALF_OPEN - test task already running, rejecting '{name or 'unnamed'}'")
                raise Exception("Circuit breaker HALF_OPEN - test task already running")

        # Handle task overflow using configured queue strategy
        if len(self._background_tasks) >= self._max_concurrent_tasks:
            strategy = self.task_config.queue.overflow_strategy

            if self.task_config.queue.log_queue_events:
                logger.debug(f"Background task queue full ({len(self._background_tasks)}/{self._max_concurrent_tasks}), applying strategy: {strategy}")

            if strategy == "drop_newest":
                # Raise RuntimeError when task queue is full
                self._queue_metrics['drop_newest_count'] += 1
                if self.task_config.queue.log_queue_events:
                    logger.debug("Background task queue full - raising RuntimeError")
                raise RuntimeError(f"Maximum concurrent tasks ({self._max_concurrent_tasks}) reached and overflow strategy is 'drop_newest'")

            elif strategy == "drop_oldest":
                # Cancel oldest task by start_time to make room
                oldest_task = None
                oldest_start_time = None

                for task in self._background_tasks:
                    task_name = task.get_name()
                    if task_name in self._task_metadata:
                        start_time = self._task_metadata[task_name].get('created_at')
                        if start_time and (oldest_start_time is None or start_time < oldest_start_time):
                            oldest_task = task
                            oldest_start_time = start_time

                if oldest_task:
                    oldest_task.cancel()
                    self._queue_metrics['drop_oldest_count'] += 1
                    if self.task_config.queue.log_queue_events:
                        logger.info(f"Cancelled oldest background task {oldest_task.get_name()} to make room")
                else:
                    # No suitable task found, raise error
                    raise RuntimeError(f"Maximum concurrent tasks ({self._max_concurrent_tasks}) reached and no cancellable tasks found")

            elif strategy == "block":
                # For block strategy, create a background task that handles the blocking
                self._queue_metrics['block_count'] += 1
                if self.task_config.queue.log_queue_events:
                    logger.debug(f"Creating background task to handle blocking strategy (timeout: {self.task_config.queue.block_timeout}s)")

                # Create a task that will wait for space and then run the actual task
                blocking_task = asyncio.create_task(
                    self._create_task_with_blocking(coro, name),
                    name=f"blocking_wrapper_{name or 'unnamed'}"
                )
                return blocking_task

            else:
                # Unknown strategy, default to drop_oldest
                logger.warning(f"Unknown overflow strategy '{strategy}', defaulting to drop_oldest")
                raise RuntimeError(f"Maximum concurrent tasks ({self._max_concurrent_tasks}) reached")

        task_name = name or f"bg_task_{datetime.now().timestamp()}"
        start_time = time.time()

        # Store original coroutine before timeout wrapping for retry purposes
        original_coro = coro

        # Add timeout wrapping if default_timeout is set (0 = disabled for autonomous LLM work)
        default_timeout = getattr(self.task_config.background_tasks, 'default_timeout', 0)
        if default_timeout is not None and default_timeout > 0:
            wrapped_coro = asyncio.wait_for(coro, timeout=default_timeout)
        else:
            wrapped_coro = coro

        # Mark test task running in HALF_OPEN state
        if self.task_config.background_tasks.enable_task_circuit_breaker and self._circuit_breaker_state == "HALF_OPEN":
            self._circuit_breaker_test_task_running = True
            logger.info(f"Circuit breaker HALF_OPEN - allowing test task '{task_name}'")

        task = asyncio.create_task(
            self._safe_task_wrapper(wrapped_coro, task_name),
            name=task_name
        )

        # Track the task with retry information
        self._background_tasks.add(task)
        self._task_metadata[task_name] = {
            'created_at': datetime.now(),
            'coro_name': coro.__name__ if hasattr(coro, '__name__') else str(coro),
            'start_time': start_time,
            'retry_count': 0,
            'original_coro': original_coro  # Store original coroutine for retries
        }

        # Add cleanup callback
        task.add_done_callback(self._task_done_callback)

        return task

    async def _create_task_with_blocking(self, coro, name: str = None) -> Any:
        """Handle blocking strategy by waiting for available task slot."""
        start_time = time.time()
        poll_interval = 0.01  # 10ms polling

        while len(self._background_tasks) >= self._max_concurrent_tasks:
            # Check timeout
            elapsed = time.time() - start_time
            if self.task_config.queue.block_timeout is not None and elapsed >= self.task_config.queue.block_timeout:
                self._queue_metrics['block_timeout_count'] += 1
                if self.task_config.queue.log_queue_events:
                    logger.warning(f"Background task block timeout after {elapsed:.2f}s")
                raise RuntimeError(f"Timeout waiting for available task slot (timeout: {self.task_config.queue.block_timeout}s)")

            # Brief sleep before next poll
            await asyncio.sleep(poll_interval)

        # Space is available, create the actual task using the normal path
        # We can call the synchronous version since we now have space
        return self.create_background_task(coro, name)

    async def _safe_task_wrapper(self, coro, task_name: str):
        """Wrapper that safely executes task and handles exceptions."""
        try:
            if self.task_config.background_tasks.log_task_events:
                logger.debug(f"Starting background task: {task_name}")
            result = await coro
            if self.task_config.background_tasks.log_task_events:
                logger.debug(f"Background task completed successfully: {task_name}")
            return result

        except asyncio.CancelledError:
            logger.info(f"Background task cancelled: {task_name}")
            raise

        except Exception as e:
            if self.task_config.background_tasks.log_task_errors:
                logger.error(f"Background task failed: {task_name} - {type(e).__name__}: {e}")
            self._task_error_count += 1
            await self._handle_task_error(task_name, e)
            raise

    def _task_done_callback(self, task: asyncio.Task):
        """Called when a task completes."""
        self._background_tasks.discard(task)

        task_name = task.get_name()

        # Track duration and metrics if enabled - capture metadata before deletion
        metadata = None
        if task_name in self._task_metadata:
            metadata = self._task_metadata[task_name]

            # Store metrics if enabled and we have start_time
            if self.enable_metrics and hasattr(self, '_task_metrics') and metadata:
                start_time = metadata.get('start_time')

                if start_time:
                    duration = time.time() - start_time

                    # Store metrics
                    self._task_metrics[task_name] = {
                        'duration': duration,
                        'status': 'cancelled' if task.cancelled() else 'failed' if task.exception() else 'completed',
                        'cancelled': task.cancelled(),
                        'exception': str(task.exception()) if task.exception() else None,
                        'completed_at': datetime.now(),
                        'coro_name': metadata.get('coro_name', 'unknown')
                    }

            # Clean up metadata
            del self._task_metadata[task_name]

        if task.cancelled():
            if self.task_config.background_tasks.log_task_events:
                logger.debug(f"Task cancelled: {task_name}")
        elif task.exception():
            if self.task_config.background_tasks.log_task_errors:
                logger.error(f"Task failed with exception: {task_name} - {task.exception()}")
        else:
            # Task completed successfully - check circuit breaker state
            if (self.task_config.background_tasks.enable_task_circuit_breaker and
                self._circuit_breaker_state == "HALF_OPEN"):
                logger.info(f"Circuit breaker HALF_OPEN - test task '{task_name}' completed successfully, transitioning to CLOSED")
                self._circuit_breaker_state = "CLOSED"
                self._circuit_breaker_failures = 0
                self._circuit_breaker_last_failure_time = None
                self._circuit_breaker_test_task_running = False

            if self.task_config.background_tasks.log_task_events:
                logger.debug(f"Task completed: {task_name}")

    async def _handle_task_error(self, task_name: str, error: Exception):
        """Handle errors from background tasks."""
        # Circuit breaker pattern implementation
        if self.task_config.background_tasks.enable_task_circuit_breaker:
            self._circuit_breaker_failures += 1
            self._circuit_breaker_last_failure_time = time.time()

            # Check if failure threshold reached
            threshold = self.task_config.background_tasks.circuit_breaker_threshold
            if self._circuit_breaker_failures >= threshold:
                if self._circuit_breaker_state != "OPEN":
                    logger.warning(f"Circuit breaker threshold ({threshold}) reached, opening circuit due to task failure: {task_name}")
                    self._circuit_breaker_state = "OPEN"
                    self._circuit_breaker_test_task_running = False
                else:
                    logger.debug(f"Circuit breaker already OPEN, failure count: {self._circuit_breaker_failures}")
            else:
                logger.warning(f"Task failure ({self._circuit_breaker_failures}/{threshold}) - circuit breaker {self._circuit_breaker_state}")

        # Retry logic implementation
        task_metadata = self._task_metadata.get(task_name, {})
        retry_count = task_metadata.get('retry_count', 0)
        original_coro = task_metadata.get('original_coro')

        # Check if we should retry this task
        max_retries = self.task_config.background_tasks.task_retry_attempts
        retry_delay = self.task_config.background_tasks.task_retry_delay

        if retry_count < max_retries and original_coro is not None:
            # Increment retry count
            self._task_metadata[task_name]['retry_count'] = retry_count + 1

            logger.warning(
                f"Retrying task {task_name} (attempt {retry_count + 1}/{max_retries}) "
                f"after {retry_delay}s delay due to {type(error).__name__}: {error}"
            )

            # Wait for retry delay
            await asyncio.sleep(retry_delay)

            # Create new task with original coroutine
            new_task_name = f"{task_name}_retry_{retry_count + 1}"
            self.create_background_task(original_coro, new_task_name)

            logger.info(f"Created retry task: {new_task_name}")
        else:
            # No more retries or no original coroutine available
            if retry_count >= max_retries:
                logger.error(
                    f"Task {task_name} failed after {max_retries} retry attempts. "
                    f"Final error: {type(error).__name__}: {error}"
                )
            else:
                logger.error(f"Task {task_name} failed (no retry possible): {error}")

            # Could implement additional error handling:
            # - Error reporting to monitoring service
            # - Error notifications

    async def start_task_monitor(self):
        """Start background task monitoring and cleanup."""
        self._monitoring_task = asyncio.create_task(self._monitor_tasks())
        logger.info("Task monitoring started")

    async def _monitor_tasks(self):
        """Monitor and cleanup completed tasks."""
        cleanup_interval = self.task_config.background_tasks.cleanup_interval

        while True:
            try:
                # Remove completed tasks
                completed_tasks = [t for t in self._background_tasks if t.done()]
                for task in completed_tasks:
                    self._background_tasks.discard(task)

                if completed_tasks:
                    logger.debug(f"Cleaned up {len(completed_tasks)} completed tasks")

                # Log status
                if len(self._background_tasks) > 0:
                    logger.debug(f"Active background tasks: {len(self._background_tasks)}")

                # Monitor queue health
                queue_size = self.processing_queue.qsize()
                queue_utilization = (queue_size / self.max_queue_size * 100) if self.max_queue_size > 0 else 0

                if queue_utilization > 80:
                    logger.warning(f"Queue utilization high: {queue_utilization:.1f}% ({queue_size}/{self.max_queue_size})")

                if self.dropped_messages > 0:
                    logger.warning(f"Messages dropped: {self.dropped_messages}")

                await asyncio.sleep(cleanup_interval)

            except Exception as e:
                logger.error(f"Error in task monitoring: {e}")
                await asyncio.sleep(cleanup_interval)

    async def get_task_status(self):
        """Get status of all background tasks."""
        status = {
            'active_tasks': len(self._background_tasks),
            'max_concurrent': self._max_concurrent_tasks,
            'error_count': self._task_error_count,
            'tasks': []
        }

        for task in self._background_tasks:
            task_info = {
                'name': task.get_name(),
                'done': task.done(),
                'cancelled': task.cancelled(),
                'exception': str(task.exception()) if task.exception() else None
            }
            status['tasks'].append(task_info)

        return status

    async def cancel_all_tasks(self):
        """Cancel all background tasks and wait for cleanup."""
        logger.info(f"Cancelling {len(self._background_tasks)} background tasks")

        for task in self._background_tasks:
            if not task.done():
                task.cancel()

        # Wait for all tasks to complete (with timeout)
        if self._background_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._background_tasks, return_exceptions=True),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning("Some tasks didn't finish gracefully")

        self._background_tasks.clear()
        self._task_metadata.clear()

    async def wait_for_tasks(self, timeout: float = 30.0):
        """Wait for all background tasks to complete."""
        if not self._background_tasks:
            return

        try:
            await asyncio.wait_for(
                asyncio.gather(*self._background_tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for tasks to complete")
            # Cancel remaining tasks
            await self.cancel_all_tasks()
    
    def _get_tree_output(self) -> str:
        """Get project directory tree output."""
        try:
            result = subprocess.run(
                ["tree", "-I", "__pycache__|*.pyc|.git|.venv|venv|node_modules", "-L", "3"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=Path.cwd()
            )
            if result.returncode == 0:
                return result.stdout
            else:
                # Fallback to basic ls if tree is not available
                result = subprocess.run(
                    ["ls", "-la"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=Path.cwd()
                )
                return result.stdout if result.returncode == 0 else "Could not get directory listing"
        except Exception as e:
            logger.warning(f"Failed to get tree output: {e}")
            return "Could not get directory listing"

    def _finalize_system_prompt(self, prompt_parts: List[str]) -> str:
        """Finalize system prompt by adding common sections.

        Args:
            prompt_parts: List of prompt parts (base prompt should be first)

        Returns:
            Complete system prompt string
        """
        # Add project structure if enabled
        include_structure = self.config.get("core.llm.system_prompt.include_project_structure", True)
        if include_structure:
            tree_output = self._get_tree_output()
            prompt_parts.append(f"## Project Structure\n```\n{tree_output}\n```")

        # Add attachment files
        attachment_files = self.config.get("core.llm.system_prompt.attachment_files", [])
        for filename in attachment_files:
            file_path = Path.cwd() / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    prompt_parts.append(f"## {filename}\n```markdown\n{content}\n```")
                    logger.debug(f"Attached file: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to read {filename}: {e}")

        # Add custom prompt files
        custom_files = self.config.get("core.llm.system_prompt.custom_prompt_files", [])
        for filename in custom_files:
            file_path = Path.cwd() / filename
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8')
                    prompt_parts.append(f"## Custom Instructions ({filename})\n{content}")
                    logger.debug(f"Added custom prompt: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to read custom prompt {filename}: {e}")

        # Add closing statement
        prompt_parts.append("This is the codebase and context for our session. You now have full project awareness.")

        return "\n\n".join(prompt_parts)

    def _build_system_prompt(self) -> str:
        """Build system prompt from file or agent.

        Priority:
        0. Active agent's system prompt (if agent is active)
        1. KOLLABOR_SYSTEM_PROMPT environment variable (direct string)
        2. KOLLABOR_SYSTEM_PROMPT_FILE environment variable (custom file path)
        3. Local .kollabor-cli/system_prompt/default.md (project override)
        4. Global ~/.kollabor-cli/system_prompt/default.md
        5. Fallback to minimal default

        Returns:
            Fully rendered system prompt with all <trender> tags executed.
        """
        from ..utils.config_utils import get_system_prompt_content, initialize_system_prompt
        from ..utils.prompt_renderer import render_system_prompt

        # Check if we have an active agent with a system prompt
        if self.agent_manager:
            agent_prompt = self.agent_manager.get_system_prompt()
            if agent_prompt:
                # Render <trender> tags in agent prompt
                base_prompt = render_system_prompt(agent_prompt, timeout=5)
                logger.info(f"Using agent system prompt from: {self.agent_manager.active_agent_name}")
                # Continue with the rest of the build process using agent prompt
                prompt_parts = [base_prompt]
                return self._finalize_system_prompt(prompt_parts)

        # Ensure system prompts are initialized (copies global to local if needed)
        initialize_system_prompt()

        # Load base prompt (checks env vars and files in priority order)
        base_prompt = get_system_prompt_content()

        # Render <trender> tags BEFORE building the full prompt
        base_prompt = render_system_prompt(base_prompt, timeout=5)

        prompt_parts = [base_prompt]
        return self._finalize_system_prompt(prompt_parts)

    def rebuild_system_prompt(self) -> bool:
        """Rebuild the system prompt and update conversation history.

        Call this after skills are loaded/unloaded to update the system message
        with the new prompt content including active skills.

        Returns:
            True if system prompt was rebuilt successfully.
        """
        try:
            new_prompt = self._build_system_prompt()

            # Update the first message in conversation history (system message)
            if self.conversation_history:
                first_msg = self.conversation_history[0]
                if first_msg.role == "system":
                    # Create new message with updated content
                    self.conversation_history[0] = ConversationMessage(
                        role="system",
                        content=new_prompt
                    )
                    logger.info("System prompt rebuilt with updated skills")
                    return True

            logger.warning("No system message found to update")
            return False

        except Exception as e:
            logger.error(f"Failed to rebuild system prompt: {e}")
            return False

    async def process_user_input(self, message: str) -> Dict[str, Any]:
        """Process user input through the LLM.
        
        This is the main entry point for user messages.
        
        Args:
            message: User's input message
            
        Returns:
            Status information about processing
        """
        # Display user message using MessageDisplayService (DRY refactoring)
        logger.debug(f"DISPLAY DEBUG: About to display user message: '{message[:100]}...' ({len(message)} chars)")
        self.message_display.display_user_message(message)
        
        # Reset turn_completed flag
        self.turn_completed = False
        self.cancel_processing = False
        self.cancellation_message_shown = False
        
        # Log user message
        self.current_parent_uuid = await self.conversation_logger.log_user_message(
            message,
            parent_uuid=self.current_parent_uuid
        )
        
        # Add to processing queue with overflow handling
        await self._enqueue_with_overflow_strategy(message)
        
        # Start processing if not already running
        if not self.is_processing:
            self.create_background_task(self._process_queue(), name="process_queue")

        return {"status": "queued"}
    
    async def _handle_user_input(self, data: Dict[str, Any], event) -> Dict[str, Any]:
        """Handle user input hook callback.
        
        This is called by the event bus when user input occurs.
        
        Args:
            data: Event data containing user message
            event: The event object
            
        Returns:
            Result of processing
        """
        message = data.get("message", "")
        if message.strip():
            result = await self.process_user_input(message)
            return result
        return {"status": "empty_message"}
    
    async def _handle_cancel_request(self, data: Dict[str, Any], event) -> Dict[str, Any]:
        """Handle cancel request hook callback.

        This is called by the event bus when a cancellation request occurs.

        Args:
            data: Event data containing cancellation reason
            event: The event object

        Returns:
            Result of cancellation
        """
        reason = data.get("reason", "unknown")
        source = data.get("source", "unknown")

        # Check if we're in pipe mode - ignore cancel requests from stdin
        if hasattr(self.renderer, 'pipe_mode') and getattr(self.renderer, 'pipe_mode', False):
            logger.info(f"LLM SERVICE: Ignoring cancel request in pipe mode (from {source}: {reason})")
            return {"status": "ignored", "reason": "pipe_mode"}

        logger.info(f"LLM SERVICE: Cancel request hook called! From {source}: {reason}")
        logger.info(f"LLM SERVICE: Currently processing: {self.is_processing}")

        # Cancel current request
        self.cancel_current_request()

        logger.info(f"LLM SERVICE: Cancellation flag set: {self.cancel_processing}")
        return {"status": "cancelled", "reason": reason}

    async def _handle_add_message(self, data: Dict[str, Any], event) -> Dict[str, Any]:
        """Handle ADD_MESSAGE event - inject messages into conversation.

        This allows plugins to inject messages into the conversation that:
        - Get added to AI-visible history
        - Get logged to conversation logger
        - Get displayed to user with loading indicator
        - Optionally trigger LLM response

        Args:
            data: Event data with messages array and options
            event: The event object

        Returns:
            Result dict with status and message count
        """
        messages = data.get("messages", [])
        options = data.get("options", {})

        if not messages:
            return {"success": False, "error": "No messages provided"}

        show_loading = options.get("show_loading", True)
        loading_message = options.get("loading_message", "Loading...")
        log_messages = options.get("log_messages", True)
        add_to_history = options.get("add_to_history", True)
        display_messages = options.get("display_messages", True)
        trigger_llm = options.get("trigger_llm", False)
        parent_uuid = options.get("parent_uuid", self.current_parent_uuid)

        try:
            # Show loading indicator
            if show_loading:
                self.message_display.show_loading(loading_message)

            display_sequence = []

            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                # Add to conversation history
                if add_to_history:
                    from ..models import ConversationMessage
                    self._add_conversation_message(
                        ConversationMessage(role=role, content=content),
                        parent_uuid=parent_uuid
                    )

                # Log message
                if log_messages:
                    if role == "user":
                        parent_uuid = await self.conversation_logger.log_user_message(
                            content, parent_uuid=parent_uuid
                        )
                    elif role == "assistant":
                        parent_uuid = await self.conversation_logger.log_assistant_message(
                            content, parent_uuid=parent_uuid
                        )
                    elif role == "system":
                        await self.conversation_logger.log_system_message(
                            content, parent_uuid=parent_uuid
                        )

                # Build display sequence
                if display_messages and role in ("user", "assistant", "system"):
                    display_sequence.append((role, content, {}))


            # Display messages atomically
            if display_messages and display_sequence:
                self.message_display.message_coordinator.display_message_sequence(
                    display_sequence
                )

            # Hide loading before display
            if show_loading:
                await asyncio.sleep(0.5)
                self.message_display.hide_loading()
                
            # Update session stats
            if hasattr(self, 'session_stats'):
                self.session_stats["messages"] += len(messages)

            # Optionally trigger LLM response
            if trigger_llm:
                # Find the last user message to process
                last_user_msg = None
                for msg in reversed(messages):
                    if msg.get("role") == "user":
                        last_user_msg = msg.get("content", "")
                        break

                if last_user_msg:
                    await self._enqueue_with_overflow_strategy(last_user_msg)
                    if not self.is_processing:
                        self.create_background_task(self._process_queue(), name="process_queue")

            logger.info(f"ADD_MESSAGE: Processed {len(messages)} messages, trigger_llm={trigger_llm}")
            return {
                "success": True,
                "message_count": len(messages),
                "parent_uuid": parent_uuid,
                "llm_triggered": trigger_llm
            }

        except Exception as e:
            # Ensure loading is hidden on error
            if show_loading:
                self.message_display.hide_loading()
            logger.error(f"Error in ADD_MESSAGE handler: {e}")
            return {"success": False, "error": str(e)}

    async def register_hooks(self) -> None:
        """Register LLM service hooks with the event bus."""
        for hook in self.hooks:
            await self.event_bus.register_hook(hook)
        logger.info(f"Registered {len(self.hooks)} hooks for LLM core service")
    
    def cancel_current_request(self):
        """Cancel the current processing request."""
        if self.is_processing:
            self.cancel_processing = True
            # Cancel API request through API service (KISS refactoring)
            self.api_service.cancel_current_request()
            logger.info("Processing cancellation requested")
    
    async def _process_queue(self):
        """Process queued messages."""
        self.is_processing = True
        self.current_processing_tokens = 0  # Reset token counter
        self.processing_start_time = time.time()  # Track elapsed time
        logger.info("Started processing queue")
        
        while not self.processing_queue.empty() and not self.cancel_processing:
            try:
                # Collect all queued messages
                messages = []
                while not self.processing_queue.empty():
                    message = await self.processing_queue.get()
                    messages.append(message)
                
                if messages and not self.cancel_processing:
                    await self._process_message_batch(messages)
                    
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                # Provide user-friendly error messages
                error_msg = str(e)
                if "'str' object has no attribute 'get'" in error_msg:
                    error_msg = ("API format mismatch. Your profile's tool_format setting may be wrong.\n"
                                "Run /profile, press 'e' to edit, and check Tool Format matches your API.")
                self.message_display.display_error_message(error_msg)
                break
        
        # Continue conversation until completed (unlimited agentic turns)
        turn_count = 0
        while not self.turn_completed and not self.cancel_processing:
            try:
                turn_count += 1
                logger.info(f"Turn not completed - continuing conversation (turn {turn_count})")
                await self._continue_conversation()
            except Exception as e:
                logger.error(f"Continued conversation error (turn {turn_count}): {e}")
                # On error, mark turn as completed to prevent infinite error loops
                self.turn_completed = True
                break
        
        self.is_processing = False
        self.current_processing_tokens = 0  # Reset token counter when done
        self.processing_start_time = None  # Clear elapsed time tracking
        if self.cancel_processing:
            logger.info("Processing cancelled by user")
            # Show cancellation message (only once)
            if not self.cancellation_message_shown:
                self.cancellation_message_shown = True
                # Display cancellation using MessageDisplayService (DRY refactoring)
                self.message_display.display_cancellation_message()
        else:
            logger.info("Finished processing queue")
    
    async def _process_message_batch(self, messages: List[str]):
        """Process a batch of messages."""
        # Combine messages
        combined_message = "\n".join(messages)
        
        # Add to conversation history
        self._add_conversation_message(ConversationMessage(
            role="user",
            content=combined_message
        ))
        
        # Start thinking animation
        self.renderer.update_thinking(True, "Processing...")
        thinking_start = time.time()
        
        # Estimate input tokens for status display
        total_input_chars = sum(len(msg.content) for msg in self.conversation_history[-3:])  # Last 3 messages
        estimated_input_tokens = total_input_chars // 4  # Rough approximation
        self.current_processing_tokens = estimated_input_tokens
        
        try:
            # Call LLM API (streaming handled by API service)
            response = await self._call_llm()

            # Update session stats with actual token usage from API response
            token_usage = self.api_service.get_last_token_usage()
            if token_usage:
                prompt_tokens = token_usage.get("prompt_tokens", 0)
                completion_tokens = token_usage.get("completion_tokens", 0)
                self.session_stats["input_tokens"] += prompt_tokens
                self.session_stats["output_tokens"] += completion_tokens
                logger.debug(f"Token usage: {prompt_tokens} input, {completion_tokens} output")
            
            # Stop thinking animation and show completion message
            thinking_duration = time.time() - thinking_start
            self.renderer.update_thinking(False)
            
            # Brief pause to ensure clean transition from thinking to completion message
            await asyncio.sleep(self.config.get("core.llm.processing_delay", 0.1))
            
            # Parse response using new ResponseParser
            parsed_response = self.response_parser.parse_response(response)
            clean_response = parsed_response["content"]
            all_tools = self.response_parser.get_all_tools(parsed_response)
            
            # Update turn completion state
            self.turn_completed = parsed_response["turn_completed"]
            
            # Update statistics
            self.stats["total_thinking_time"] += thinking_duration
            self.session_stats["messages"] += 1
            
            # Show "Generating..." briefly before displaying messages
            if clean_response.strip() or all_tools:
                # Estimate token count (rough approximation: ~4 chars per token)
                estimated_tokens = len(clean_response) // 4 if clean_response else 0
                self.current_processing_tokens = estimated_tokens  # Update current processing tokens
                self.renderer.update_thinking(True, f"Generating... ({estimated_tokens} tokens)")
                
                # Brief pause to show generating state
                await asyncio.sleep(self.config.get("core.llm.thinking_delay", 0.3))
                
                # Stop generating animation before message display
                self.renderer.update_thinking(False)
            
            # Execute all tools (terminal commands and MCP tools) if any
            tool_results = None
            if all_tools:
                tool_results = await self.tool_executor.execute_all_tools(all_tools)

            # Display thinking duration, response, and tool results atomically using unified method
            self.message_display.display_complete_response(
                thinking_duration=thinking_duration,
                response=clean_response,
                tool_results=tool_results,
                original_tools=all_tools
            )

            # Log assistant response
            self.current_parent_uuid = await self.conversation_logger.log_assistant_message(
                clean_response or response,
                parent_uuid=self.current_parent_uuid,
                usage_stats={
                    "input_tokens": self.session_stats.get("input_tokens", 0),
                    "output_tokens": self.session_stats.get("output_tokens", 0),
                    "thinking_duration": thinking_duration
                }
            )

            # Add to conversation history
            self._add_conversation_message(ConversationMessage(
                role="assistant",
                content=response
            ))

            # Log tool execution results and batch them for conversation history (if tools were executed)
            if tool_results:
                batched_tool_results = []
                for result in tool_results:
                    await self.conversation_logger.log_system_message(
                        f"Executed {result.tool_type} ({result.tool_id}): {result.output if result.success else result.error}",
                        parent_uuid=self.current_parent_uuid,
                        subtype="tool_call"
                    )

                    # Collect tool results for batching
                    tool_context = self.tool_executor.format_result_for_conversation(result)
                    batched_tool_results.append(f"Tool result: {tool_context}")

                # Add all tool results as single conversation message
                if batched_tool_results:
                    self._add_conversation_message(ConversationMessage(
                        role="user",
                        content="\n".join(batched_tool_results)
                    ))
            
        except asyncio.CancelledError:
            logger.info("Message processing cancelled by user")
            thinking_duration = time.time() - thinking_start
            self.renderer.update_thinking(False)
            
            # Clear any display artifacts
            self.renderer.clear_active_area()
            
            # Remove the user message that was just added since processing was cancelled
            if self.conversation_history and self.conversation_history[-1].role == "user":
                self.conversation_history.pop()
                logger.info("Removed cancelled user message from conversation history")
            
            # Show cancellation message (only once)
            if not self.cancellation_message_shown:
                self.cancellation_message_shown = True
                # Display cancellation using MessageDisplayService (DRY refactoring)
                self.message_display.display_cancellation_message()
            
            # Complete turn to reset state
            self.turn_completed = True
            
            # Update stats
            self.stats["total_thinking_time"] += thinking_duration
            
        except Exception as e:
            logger.error(f"Error processing message batch: {e}")
            self.renderer.update_thinking(False)
            # Provide user-friendly error messages
            error_msg = str(e)
            if "'str' object has no attribute 'get'" in error_msg:
                error_msg = ("API format mismatch. Your profile's tool_format setting may be wrong.\n"
                            "Run /profile, press 'e' to edit, and check Tool Format matches your API.")
            self.message_display.display_error_message(error_msg)
            # Complete turn on error to prevent infinite loops
            self.turn_completed = True
    
    async def _continue_conversation(self):
        """Continue an ongoing conversation."""
        # Similar to _process_message_batch but without adding user message
        self.renderer.update_thinking(True, "Continuing...")
        thinking_start = time.time()
        
        # Estimate input tokens for status display
        total_input_chars = sum(len(msg.content) for msg in self.conversation_history[-3:])  # Last 3 messages
        estimated_input_tokens = total_input_chars // 4  # Rough approximation
        self.current_processing_tokens = estimated_input_tokens
        
        try:
            response = await self._call_llm()

            # Update session stats with actual token usage from API response
            token_usage = self.api_service.get_last_token_usage()
            if token_usage:
                prompt_tokens = token_usage.get("prompt_tokens", 0)
                completion_tokens = token_usage.get("completion_tokens", 0)
                self.session_stats["input_tokens"] += prompt_tokens
                self.session_stats["output_tokens"] += completion_tokens
                logger.debug(f"Token usage: {prompt_tokens} input, {completion_tokens} output")
            
            # Parse response using new ResponseParser
            parsed_response = self.response_parser.parse_response(response)
            clean_response = parsed_response["content"]
            all_tools = self.response_parser.get_all_tools(parsed_response)
            
            # Update turn completion state
            self.turn_completed = parsed_response["turn_completed"]
            
            thinking_duration = time.time() - thinking_start
            self.renderer.update_thinking(False)
            
            # Brief pause to ensure clean transition
            await asyncio.sleep(self.config.get("core.llm.processing_delay", 0.1))
            
            # Show "Generating..." briefly before displaying messages
            if clean_response.strip() or all_tools:
                # Estimate token count (rough approximation: ~4 chars per token)
                estimated_tokens = len(clean_response) // 4 if clean_response else 0
                self.current_processing_tokens = estimated_tokens  # Update current processing tokens
                self.renderer.update_thinking(True, f"Generating... ({estimated_tokens} tokens)")
                
                # Brief pause to show generating state
                await asyncio.sleep(self.config.get("core.llm.thinking_delay", 0.3))
                
                # Stop generating animation before message display
                self.renderer.update_thinking(False)
            
            # Execute all tools (terminal commands and MCP tools) if any
            tool_results = None
            if all_tools:
                tool_results = await self.tool_executor.execute_all_tools(all_tools)

            # Display thinking duration, response, and tool results atomically using unified method
            self.message_display.display_complete_response(
                thinking_duration=thinking_duration,
                response=clean_response,
                tool_results=tool_results,
                original_tools=all_tools
            )

            # Log continuation
            self.current_parent_uuid = await self.conversation_logger.log_assistant_message(
                clean_response or response,
                parent_uuid=self.current_parent_uuid,
                usage_stats={
                    "thinking_duration": thinking_duration
                }
            )

            self._add_conversation_message(ConversationMessage(
                role="assistant",
                content=response
            ))

            # Log tool execution results and batch them for conversation history (if tools were executed)
            if tool_results:
                batched_tool_results = []
                for result in tool_results:
                    await self.conversation_logger.log_system_message(
                        f"Executed {result.tool_type} ({result.tool_id}): {result.output if result.success else result.error}",
                        parent_uuid=self.current_parent_uuid,
                        subtype="tool_call"
                    )

                    # Collect tool results for batching
                    tool_context = self.tool_executor.format_result_for_conversation(result)
                    batched_tool_results.append(f"Tool result: {tool_context}")

                # Add all tool results as single conversation message
                if batched_tool_results:
                    self._add_conversation_message(ConversationMessage(
                        role="user",
                        content="\n".join(batched_tool_results)
                    ))
            
        except asyncio.CancelledError:
            logger.info("Conversation continuation cancelled by user")
            thinking_duration = time.time() - thinking_start
            self.renderer.update_thinking(False)
            
            # Clear any display artifacts
            self.renderer.clear_active_area()
            
            # Show cancellation message (only once)
            if not self.cancellation_message_shown:
                self.cancellation_message_shown = True
                # Display cancellation using MessageDisplayService (DRY refactoring)
                self.message_display.display_cancellation_message()
            
            # Complete turn to reset state
            self.turn_completed = True
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            self.renderer.update_thinking(False)
    

    def _stream_thinking_content(self, thinking_content: str) -> None:
        """Process complete thinking content block.
        
        Args:
            thinking_content: Complete thinking content from <think> tags
        """
        logger.debug(f"Processing complete thinking block: {thinking_content[:50]}...")
        
    def _stream_thinking_sentences(self, thinking_buffer: str, final: bool = False) -> str:
        """Stream thinking content with terminal width-based truncation (legacy method).
        
        Args:
            thinking_buffer: Current thinking content buffer
            final: Whether this is the final processing (show remaining content)
            
        Returns:
            Empty string (no remaining content processing needed)
        """
        return self._stream_thinking_width_based(thinking_buffer, final)
    
    def _stream_thinking_width_based(self, thinking_buffer: str, final: bool = False) -> str:
        """Stream thinking content in 70% terminal width chunks.
        
        Args:
            thinking_buffer: Current thinking content buffer
            final: Whether this is the final processing (show remaining content)
            
        Returns:
            Remaining buffer after displaying complete chunks
        """
        # Initialize tracking if not exists
        if not hasattr(self, '_last_chunk_position'):
            self._last_chunk_position = 0
            
        # Get terminal width and calculate thinking display width (70% of terminal width)
        try:
            import os
            terminal_width = os.get_terminal_size().columns
            chunk_width = int(terminal_width * 0.7)
        except:
            chunk_width = 80  # Fallback width
            
        # Normalize whitespace in thinking buffer (convert line breaks to spaces)
        # REASON: LLM generates thinking content with line breaks which breaks our chunk logic
        # Example: "scanning directory.\n\nuser wants..." becomes "scanning directory. user wants..."
        # This prevents line breaks from creating artificial chunk boundaries that cause repetition
        normalized_buffer = ' '.join(thinking_buffer.split())
        
        # Filter out confusing thinking content that shouldn't be displayed
        # REASON: Sometimes LLM outputs "Generating..." or similar terms during thinking
        # which confuses users as it looks like our UI state, not actual thinking content
        if normalized_buffer.strip().lower() in ['generating...', 'generating', 'processing...', 'processing']:
            # Don't display confusing meta-content, show a generic thinking message instead
            normalized_buffer = "Analyzing your request..."
        
        # Get content from where we left off
        remaining_content = normalized_buffer[self._last_chunk_position:]
        
        if final:
            # Final processing - show whatever remains
            if remaining_content.strip():
                display_text = remaining_content.strip()
                if len(display_text) > chunk_width:
                    # Truncate with word boundary
                    truncated = display_text[:chunk_width - 3]
                    last_space = truncated.rfind(' ')
                    if last_space > chunk_width * 0.8:
                        truncated = truncated[:last_space]
                    display_text = truncated + "..."
                self.renderer.update_thinking(True, display_text)
            return ""
            
        # Check if we have enough content for a full chunk
        if len(remaining_content) >= chunk_width:
            # Extract a chunk of chunk_width characters
            chunk = remaining_content[:chunk_width]
            
            # Try to break at word boundary to avoid cutting words
            last_space = chunk.rfind(' ')
            if last_space > chunk_width * 0.8:  # Only break at space if it's not too short
                chunk = chunk[:last_space]
            
            chunk = chunk.strip()
            if chunk:
                self.renderer.update_thinking(True, chunk + "...")
                # Update position to after this chunk
                self._last_chunk_position += len(chunk)
                # Add space to position if we broke at a space
                if chunk != remaining_content[:len(chunk)].strip():
                    self._last_chunk_position += 1
        
        # Return the original buffer (we track position internally)
        return thinking_buffer

    async def _handle_streaming_chunk(self, chunk: str) -> None:
        """Handle streaming content chunk from API.

        Args:
            chunk: Content chunk from streaming API response
        """
        # Initialize streaming state if not exists
        if not hasattr(self, '_streaming_buffer'):
            self._streaming_buffer = ""
            self._in_thinking = False
            self._thinking_buffer = ""
            self._response_started = False

        # Add chunk to buffer
        self._streaming_buffer += chunk

        # Process thinking content in real-time
        while True:
            if not self._in_thinking:
                # Look for start of thinking
                if '<think>' in self._streaming_buffer:
                    parts = self._streaming_buffer.split('<think>', 1)
                    if len(parts) == 2:
                        # Stream any content before thinking tag
                        if parts[0].strip():
                            self._stream_response_chunk(parts[0])
                        self._streaming_buffer = parts[1]
                        self._in_thinking = True
                        self._thinking_buffer = ""
                    else:
                        break
                else:
                    # No thinking tags found, stream the content as response
                    if self._streaming_buffer.strip():
                        self._stream_response_chunk(self._streaming_buffer)
                        self._streaming_buffer = ""
                    break
            else:
                # We're in thinking mode, look for end or accumulate content
                if '</think>' in self._streaming_buffer:
                    parts = self._streaming_buffer.split('</think>', 1)
                    self._thinking_buffer += parts[0]
                    self._streaming_buffer = parts[1]

                    # Process complete thinking content
                    if self._thinking_buffer.strip():
                        self._stream_thinking_sentences(self._thinking_buffer, final=True)

                    # Switch to generating mode after thinking is complete
                    self.renderer.update_thinking(True, "Generating...")

                    # Reset thinking state
                    self._in_thinking = False
                    self._thinking_buffer = ""
                else:
                    # Still in thinking, accumulate and stream chunks
                    if self._streaming_buffer:
                        self._thinking_buffer += self._streaming_buffer
                        # Stream thinking content as we get it
                        self._stream_thinking_sentences(self._thinking_buffer)
                        self._streaming_buffer = ""
                    break

    def _stream_response_chunk(self, chunk: str) -> None:
        """Stream a response chunk in real-time to the message renderer.

        Args:
            chunk: Response content chunk to stream immediately
        """
        # Handle empty chunks gracefully
        if not chunk or not chunk.strip():
            return

        # Initialize streaming response if this is the first chunk
        if not self._response_started:
            self.message_display.message_coordinator.start_streaming_response()
            self._response_started = True

        # Stream the chunk through the message coordinator (proper architecture)
        self.message_display.message_coordinator.write_streaming_chunk(chunk)

    async def _call_llm(self) -> str:
        """Make API call to LLM using APICommunicationService (KISS refactoring)."""
        # Reset streaming state for new request
        self._streaming_buffer = ""
        self._in_thinking = False
        self._thinking_buffer = ""
        self._last_chunk_position = 0
        self._response_started = False

        # Check for cancellation before starting
        if self.cancel_processing:
            logger.info("API call cancelled before starting")
            raise asyncio.CancelledError("Request cancelled by user")
        
        # Delegate to API communication service (eliminates ~160 lines of duplicated API code)
        try:
            return await self.api_service.call_llm(
                conversation_history=self.conversation_history,
                max_history=self.max_history,
                streaming_callback=self._handle_streaming_chunk
            )
        except asyncio.CancelledError:
            logger.info("LLM API call was cancelled")
            # Clean up streaming state on cancellation
            self._cleanup_streaming_state()
            raise
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            # Clean up streaming state on error
            self._cleanup_streaming_state()
            raise

    def _cleanup_streaming_state(self) -> None:
        """Clean up streaming state after request completion or failure.

        This ensures streaming state is properly reset even if errors occur.
        """
        self._streaming_buffer = ""
        self._in_thinking = False
        self._thinking_buffer = ""
        self._response_started = False
        self._last_chunk_position = 0

        # End streaming session in message display service if active
        if hasattr(self, 'message_display_service') and self.message_display_service.is_streaming_active():
            self.message_display_service.end_streaming_response()

        logger.debug("Cleaned up streaming state")


    def get_status_line(self) -> Dict[str, List[str]]:
        """Get status information for display."""
        status = {
            "A": [],
            "B": [],
            "C": []
        }
        
        # Area B - LLM status
        if self.is_processing:
            # Show elapsed time and tokens
            elapsed = ""
            if self.processing_start_time:
                elapsed_secs = time.time() - self.processing_start_time
                elapsed = f" ({elapsed_secs:.1f}s)"

            if self.current_processing_tokens > 0:
                status["A"].append(f"Processing: {self.current_processing_tokens} tokens{elapsed}")
            else:
                status["A"].append(f"Processing: Yes{elapsed}")
        else:
            status["A"].append(f"Processing: No")
        
          # Enhanced queue metrics with memory leak monitoring
        queue_size = self.processing_queue.qsize()
        queue_utilization = (queue_size / self.max_queue_size * 100) if self.max_queue_size > 0 else 0
        dropped_indicator = f" ({self.dropped_messages} dropped)" if self.dropped_messages > 0 else ""
        
        status["C"].append(f"Queue: {queue_size}/{self.max_queue_size} ({queue_utilization:.0f}%){dropped_indicator}")
        
        # Add warning if queue utilization is high
        if queue_utilization > 80:
            status["C"].append(f"⚠️ Queue usage high!")
        status["C"].append(f"History: {len(self.conversation_history)}")
        status["C"].append(f"Tasks: {len(self._background_tasks)}")
        if self._task_error_count > 0:
            status["C"].append(f"Task Errors: {self._task_error_count}")

        # Circuit breaker status if enabled
        if self.task_config.background_tasks.enable_task_circuit_breaker:
            cb_state = self._circuit_breaker_state
            cb_failures = self._circuit_breaker_failures
            cb_threshold = self.task_config.background_tasks.circuit_breaker_threshold

            if cb_state == "OPEN":
                status["C"].append(f"⚠️ Circuit: OPEN ({cb_failures}/{cb_threshold})")
            elif cb_state == "HALF_OPEN":
                status["C"].append(f"🔧 Circuit: HALF_OPEN ({cb_failures}/{cb_threshold})")
            else:  # CLOSED
                if cb_failures > 0:
                    status["C"].append(f"✓ Circuit: CLOSED ({cb_failures}/{cb_threshold})")

        # Area C - Session stats
        if self.session_stats["messages"] > 0:
            status["C"].append(f"Messages: {self.session_stats['messages']}")
            status["C"].append(f"Tokens In: {self.session_stats.get('input_tokens', 0)}")
            status["C"].append(f"Tokens Out: {self.session_stats.get('output_tokens', 0)}")
        
        # Area A - Tool execution stats
        tool_stats = self.tool_executor.get_execution_stats()
        if tool_stats["total_executions"] > 0:
            status["A"].append(f"Tools: {tool_stats['total_executions']}")
            status["A"].append(f"Terminal: {tool_stats['terminal_executions']}")
            status["A"].append(f"MCP: {tool_stats['mcp_executions']}")
            status["A"].append(f"Success: {tool_stats['success_rate']:.1%}")
        
        return status


    def get_queue_metrics(self) -> dict:
        """Get comprehensive queue metrics for monitoring."""
        queue_size = self.processing_queue.qsize()
        queue_utilization = (queue_size / self.max_queue_size * 100) if self.max_queue_size > 0 else 0

        base_metrics = {
            'current_size': queue_size,
            'max_size': self.max_queue_size,
            'utilization_percent': round(queue_utilization, 1),
            'dropped_messages': self.dropped_messages,
            'status': 'healthy' if queue_utilization < 80 else 'warning' if queue_utilization < 95 else 'critical',
            'memory_safe': queue_utilization < 90,
            'overflow_strategy': self.task_config.queue.overflow_strategy
        }

        # Add overflow strategy metrics if enabled
        if self.task_config.queue.enable_queue_metrics:
            base_metrics.update({
                'overflow_metrics': {
                    'drop_oldest_count': self._queue_metrics['drop_oldest_count'],
                    'drop_newest_count': self._queue_metrics['drop_newest_count'],
                    'block_count': self._queue_metrics['block_count'],
                    'block_timeout_count': self._queue_metrics['block_timeout_count'],
                    'total_enqueue_attempts': self._queue_metrics['total_enqueue_attempts'],
                    'total_enqueue_successes': self._queue_metrics['total_enqueue_successes'],
                    'success_rate': (
                        (self._queue_metrics['total_enqueue_successes'] /
                         self._queue_metrics['total_enqueue_attempts'] * 100)
                        if self._queue_metrics['total_enqueue_attempts'] > 0 else 100.0
                    )
                }
            })

        return base_metrics

    def reset_queue_metrics(self):
        """Reset queue metrics (for testing or maintenance)."""
        self.dropped_messages = 0

        # Reset overflow strategy metrics
        for key in self._queue_metrics:
            self._queue_metrics[key] = 0

        logger.info("Queue metrics reset")

    async def shutdown(self):
        """Shutdown the LLM service."""
        # Log conversation end
        await self.conversation_logger.log_conversation_end()

        # Cancel all background tasks
        await self.cancel_all_tasks()

        # Stop task monitoring
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        # Shutdown API communication service (KISS refactoring)
        await self.api_service.shutdown()

        # Shutdown MCP integration
        try:
            await self.mcp_integration.shutdown()
            logger.info("MCP integration shutdown complete")
        except Exception as e:
            logger.warning(f"MCP shutdown error: {e}")

        # Save statistics
        self.state_manager.set("llm.stats", self.stats)


    
        logger.info("Core LLM Service shutdown complete")