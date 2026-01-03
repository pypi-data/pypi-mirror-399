"""API Communication Service for LLM requests.

Handles pure API communication with LLM endpoints, eliminating
networking concerns from the main LLM service. Follows KISS principle
with single responsibility for HTTP communication.
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from .api_adapters import get_adapter, BaseAPIAdapter

logger = logging.getLogger(__name__)


class APICommunicationService:
    """Pure API communication service for LLM requests.
    
    Handles HTTP sessions, request formatting, response parsing,
    and error handling for LLM API communication. Follows KISS
    principle with single responsibility for API communication.
    
    Eliminates API concerns from the main LLM service class.
    """
    
    def __init__(self, config, raw_conversations_dir):
        """Initialize API communication service.

        Args:
            config: Configuration manager for API settings
            raw_conversations_dir: Directory for raw interaction logs
        """
        self.config = config
        self.raw_conversations_dir = raw_conversations_dir

        # Load API configuration (environment variables take precedence over config)

        # API endpoint/URL
        self.api_url = os.environ.get("KOLLABOR_API_ENDPOINT") or config.get("core.llm.api_url", "http://localhost:1234")
        if os.environ.get("KOLLABOR_API_ENDPOINT"):
            logger.debug("Using API endpoint from KOLLABOR_API_ENDPOINT environment variable")

        # Model name
        self.model = os.environ.get("KOLLABOR_API_MODEL") or config.get("core.llm.model", "qwen/qwen3-4b")
        if os.environ.get("KOLLABOR_API_MODEL"):
            logger.debug("Using model from KOLLABOR_API_MODEL environment variable")

        # Temperature (with type conversion)
        env_temperature = os.environ.get("KOLLABOR_API_TEMPERATURE")
        if env_temperature:
            try:
                self.temperature = float(env_temperature)
                logger.debug("Using temperature from KOLLABOR_API_TEMPERATURE environment variable")
            except ValueError:
                logger.warning(f"Invalid KOLLABOR_API_TEMPERATURE value: {env_temperature}, using config/default")
                self.temperature = config.get("core.llm.temperature", 0.7)
        else:
            self.temperature = config.get("core.llm.temperature", 0.7)

        # Tool calling format (openai or anthropic)
        self.tool_format = config.get("core.llm.tool_format", "openai")

        # Create API adapter based on tool format
        self._adapter: BaseAPIAdapter = get_adapter(self.tool_format, self.api_url)

        # Timeout (with type conversion)
        env_timeout = os.environ.get("KOLLABOR_API_TIMEOUT")
        if env_timeout:
            try:
                self.timeout = int(env_timeout)
                logger.debug("Using timeout from KOLLABOR_API_TIMEOUT environment variable")
            except ValueError:
                logger.warning(f"Invalid KOLLABOR_API_TIMEOUT value: {env_timeout}, using config/default")
                self.timeout = config.get("core.llm.timeout", 30000)
        else:
            self.timeout = config.get("core.llm.timeout", 30000)

        # Streaming (not typically set via env, kept for completeness)
        self.enable_streaming = config.get("core.llm.enable_streaming", False)

        # Session tracking for raw log linking
        self.current_session_id: Optional[str] = None

        # Max tokens (with type conversion)
        env_max_tokens = os.environ.get("KOLLABOR_API_MAX_TOKENS")
        if env_max_tokens:
            try:
                self.max_tokens = int(env_max_tokens)
                logger.debug("Using max tokens from KOLLABOR_API_MAX_TOKENS environment variable")
            except ValueError:
                logger.warning(f"Invalid KOLLABOR_API_MAX_TOKENS value: {env_max_tokens}, using config/default")
                self.max_tokens = config.get("core.llm.max_tokens", None)
        else:
            self.max_tokens = config.get("core.llm.max_tokens", None)

        # API token (supports both KOLLABOR_API_TOKEN and KOLLABOR_API_KEY)
        self.api_token = (
            os.environ.get("KOLLABOR_API_TOKEN")
            or os.environ.get("KOLLABOR_API_KEY")
            or config.get("core.llm.api_token")
        )
        if os.environ.get("KOLLABOR_API_TOKEN"):
            logger.debug("Using API token from KOLLABOR_API_TOKEN environment variable")
        elif os.environ.get("KOLLABOR_API_KEY"):
            logger.debug("Using API token from KOLLABOR_API_KEY environment variable")

        # HTTP session state with enhanced lifecycle management
        self.session = None
        self.connector = None
        self._session_lock = asyncio.Lock()
        self._initialized = False

        # Request cancellation support
        self.current_request_task = None
        self.cancel_requested = False

        # Token usage tracking
        self.last_token_usage = {}

        # Resource monitoring and statistics
        self._connection_stats = {
            'total_requests': 0,
            'failed_requests': 0,
            'recreated_sessions': 0,
            'last_activity': None,
            'session_creation_time': None,
            'connection_errors': 0
        }

        logger.info(f"API service initialized for {self.api_url}")

    def set_session_id(self, session_id: str) -> None:
        """Set current session ID for raw log linking.

        Args:
            session_id: Session identifier from conversation logger
        """
        self.current_session_id = session_id
        logger.debug(f"API service session ID set to: {session_id}")

    def update_from_profile(
        self,
        api_url: str,
        model: str,
        temperature: float = None,
        tool_format: str = None
    ) -> None:
        """Update API settings from a profile.

        Args:
            api_url: New API endpoint URL
            model: New model identifier
            temperature: Optional new temperature setting
            tool_format: Tool calling format ("openai" or "anthropic")
        """
        old_url = self.api_url
        old_model = self.model
        old_format = getattr(self, 'tool_format', 'openai')

        self.api_url = api_url
        self.model = model
        if temperature is not None:
            self.temperature = temperature
        if tool_format is not None:
            self.tool_format = tool_format
            # Recreate adapter with new format
            self._adapter = get_adapter(tool_format, api_url)
        elif api_url != old_url:
            # URL changed, recreate adapter with same format
            self._adapter = get_adapter(self.tool_format, api_url)

        logger.info(
            f"API service updated: {old_model}@{old_url} ({old_format}) -> "
            f"{model}@{api_url} ({tool_format or old_format})"
        )

    async def initialize(self) -> bool:
        """Initialize HTTP session with proper error handling and resource management."""
        async with self._session_lock:
            if self._initialized:
                return True

            try:
                # Create session with proper configuration and resource limits
                # 0 = no timeout (None in aiohttp), >0 = timeout in seconds
                timeout_val = None if self.timeout == 0 else self.timeout
                timeout = aiohttp.ClientTimeout(
                    total=timeout_val,
                    connect=10,  # Connection timeout
                    sock_read=timeout_val  # Read timeout
                )

                # Enhanced connector with proper resource management
                http_connector_limit = self.config.get("core.llm.http_connector_limit", 100)
                http_limit_per_host = self.config.get("core.llm.http_limit_per_host", 20)
                keepalive_timeout = self.config.get("core.llm.keepalive_timeout", 30)

                self.connector = aiohttp.TCPConnector(
                    limit=http_connector_limit,
                    limit_per_host=http_limit_per_host,
                    keepalive_timeout=keepalive_timeout,
                    enable_cleanup_closed=True,  # Enable automatic cleanup
                    force_close=False,  # Allow connection reuse
                    use_dns_cache=True,
                    ttl_dns_cache=300,  # DNS cache TTL
                    family=0,  # IPv4 and IPv6
                    ssl=False  # For local development, adjust as needed
                )

                self.session = aiohttp.ClientSession(
                    connector=self.connector,
                    timeout=timeout,
                    headers={"User-Agent": "Kollabor-CLI/1.0"}
                )

                self._initialized = True
                self._connection_stats['session_creation_time'] = time.time()
                self._connection_stats['last_activity'] = time.time()

                logger.info(
                    f"HTTP session initialized with {http_connector_limit} total connections, "
                    f"{http_limit_per_host} per host, {keepalive_timeout}s keepalive"
                )

            except Exception as e:
                logger.error(f"Failed to initialize API service: {e}")
                # Ensure cleanup on failure
                await self._cleanup_session()
                raise
    
    async def shutdown(self):
        """Shutdown HTTP session and cleanup resources with comprehensive error handling."""
        async with self._session_lock:
            if not self._initialized:
                return

            try:
                logger.info("Starting API communication service shutdown")

                # Cancel any active requests
                if self.current_request_task and not self.current_request_task.done():
                    logger.info("Cancelling active request during shutdown")
                    self.current_request_task.cancel()
                    try:
                        await self.current_request_task
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"Error cancelling request during shutdown: {e}")

                # Clean up session resources
                await self._cleanup_session()

                self._initialized = False
                logger.info("API communication service shutdown complete")

            except Exception as e:
                logger.error(f"Error during API service shutdown: {e}")
                # Don't raise - we want cleanup to complete even if there are errors

    async def _ensure_session(self):
        """Ensure we have a valid session, recreate if needed."""
        if not self._initialized or not self.session or self.session.closed:
            logger.warning("Session not available or closed, reinitializing...")
            await self._recreate_session()

    async def _recreate_session(self):
        """Recreate the session after errors or timeout."""
        async with self._session_lock:
            try:
                logger.info("Recreating HTTP session")
                await self._cleanup_session()
                self._connection_stats['recreated_sessions'] += 1

                # Reinitialize with fresh session
                await self._create_session()

                logger.info("HTTP session recreated successfully")

            except Exception as e:
                logger.error(f"Failed to recreate session: {e}")
                raise

    async def _create_session(self):
        """Create a fresh HTTP session."""
        timeout_val = None if self.timeout == 0 else self.timeout
        timeout = aiohttp.ClientTimeout(
            total=timeout_val,
            connect=10,
            sock_read=timeout_val
        )

        http_connector_limit = self.config.get("core.llm.http_connector_limit", 100)
        http_limit_per_host = self.config.get("core.llm.http_limit_per_host", 20)
        keepalive_timeout = self.config.get("core.llm.keepalive_timeout", 30)

        self.connector = aiohttp.TCPConnector(
            limit=http_connector_limit,
            limit_per_host=http_limit_per_host,
            keepalive_timeout=keepalive_timeout,
            enable_cleanup_closed=True,
            force_close=False,
            use_dns_cache=True,
            ttl_dns_cache=300,
            family=0,
            ssl=False
        )

        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=timeout,
            headers={"User-Agent": "Kollabor-CLI/1.0"}
        )

        self._initialized = True
        self._connection_stats['session_creation_time'] = time.time()

    async def _cleanup_session(self):
        """Clean up session and connector resources."""
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                # Give connections time to close properly
                await asyncio.sleep(0.1)

            if self.connector:
                await self.connector.close()

            self.session = None
            self.connector = None

        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")

    def get_last_token_usage(self) -> Dict[str, Any]:
        """Get token usage from the last API call.

        Returns:
            Dictionary containing token usage info
        """
        return self.last_token_usage.copy()
    
    def cancel_current_request(self):
        """Cancel any active API request."""
        self.cancel_requested = True
        
        if self.current_request_task and not self.current_request_task.done():
            logger.info("Cancelling active API request")
            self.current_request_task.cancel()
    
    async def call_llm(self, conversation_history: List[Dict[str, str]],
                       max_history: int = None, streaming_callback=None) -> str:
        """Make API call to LLM with conversation history and robust error handling.

        Args:
            conversation_history: List of conversation messages
            max_history: Maximum number of messages to send (optional)
            streaming_callback: Optional callback for streaming content chunks

        Returns:
            LLM response content

        Raises:
            RuntimeError: If session not initialized
            asyncio.CancelledError: If request was cancelled
            Exception: For API communication errors
        """
        # Ensure we have a valid session before proceeding
        await self._ensure_session()

        # Validate session state
        if not self.session or self.session.closed:
            raise RuntimeError("HTTP session is not available - failed to initialize")

        # Reset cancellation flag
        self.cancel_requested = False

        # Store streaming callback for use in handlers
        self.streaming_callback = streaming_callback

        # Update activity tracking
        self._connection_stats['total_requests'] += 1
        self._connection_stats['last_activity'] = time.time()

        # Prepare messages for API
        messages = self._prepare_messages(conversation_history, max_history)

        # Build request payload using adapter
        payload = self._adapter.format_request(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            stream=self.enable_streaming,
            max_tokens=int(self.max_tokens) if self.max_tokens else None
        )

        # Execute request with cancellation support and comprehensive error handling
        self.current_request_task = asyncio.create_task(
            self._execute_request_with_error_handling(payload)
        )

        try:
            return await self._monitor_request()
        except asyncio.CancelledError:
            # Log cancellation to raw logs
            self._log_raw_interaction(payload, cancelled=True)
            raise asyncio.CancelledError("API request cancelled by user")
        except Exception as e:
            self._connection_stats['failed_requests'] += 1
            raise
    
    def _prepare_messages(self, conversation_history: List[Any], 
                         max_history: Optional[int]) -> List[Dict[str, str]]:
        """Prepare conversation messages for API request.
        
        Args:
            conversation_history: Raw conversation history
            max_history: Maximum messages to include
            
        Returns:
            List of formatted messages for API
        """
        # Apply history limit if specified
        if max_history:
            recent_messages = conversation_history[-max_history:]
        else:
            recent_messages = conversation_history
        
        # Format messages for API
        messages = []
        for msg in recent_messages:
            # Handle both ConversationMessage objects and dicts
            if hasattr(msg, 'role'):
                role, content = msg.role, msg.content
            else:
                role, content = msg["role"], msg["content"]
            
            messages.append({
                "role": role,
                "content": content
            })
        
        return messages

    async def _execute_request_with_error_handling(self, payload: Dict[str, Any]) -> str:
        """Execute HTTP request with comprehensive error handling and session recovery.

        Args:
            payload: Request payload

        Returns:
            Response content

        Raises:
            Exception: For various API communication errors
        """
        start_time = time.time()

        try:
            # Log raw request
            self._log_raw_interaction(payload)

            # Build headers using adapter (handles auth format differences)
            headers = self._adapter.get_headers(self.api_token)

            # Determine URL - prefer user's configured URL if it's a full endpoint
            # This handles custom APIs like z.ai that have non-standard paths
            if "/chat/completions" in self.api_url or "/messages" in self.api_url:
                # User provided full endpoint URL, use it directly
                url = self.api_url
            else:
                # User provided base URL, use adapter's endpoint pattern
                url = self._adapter.api_endpoint

            # Execute request with proper timeout and error handling
            timeout_val = None if self.timeout == 0 else self.timeout
            timeout = aiohttp.ClientTimeout(
                total=timeout_val,
                connect=10,
                sock_read=timeout_val
            )

            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            ) as response:

                request_duration = time.time() - start_time

                if response.status == 200:
                    if self.enable_streaming:
                        content = await self._handle_streaming_response(response)
                    else:
                        data = await response.json()
                        # Use adapter to parse response (handles OpenAI vs Anthropic formats)
                        parsed = self._adapter.parse_response(data)
                        content = parsed.content
                        # Extract token usage from unified format
                        self.last_token_usage = parsed.usage

                    # Log successful response
                    self._log_raw_interaction(
                        payload,
                        response_data=data if not self.enable_streaming else {"choices": [{"message": {"content": content}}]}
                    )

                    logger.debug(f"API call completed in {request_duration:.2f}s")
                    return content

                else:
                    # Handle HTTP error responses
                    error_text = await response.text()
                    error_msg = f"LLM API error: {response.status} - {error_text}"

                    # Log error response
                    self._log_raw_interaction(payload, error=error_msg)

                    # For server errors (5xx), session might be broken
                    if 500 <= response.status < 600:
                        logger.warning(f"Server error detected, recreating session: {error_msg}")
                        await self._recreate_session()

                    raise Exception(error_msg)

        except aiohttp.ClientError as e:
            self._connection_stats['connection_errors'] += 1
            logger.error(f"API request failed with client error: {e}")

            # Session might be broken, recreate it
            if isinstance(e, (aiohttp.ClientConnectionError,
                             aiohttp.ServerDisconnectedError,
                             aiohttp.ClientPayloadError)):
                logger.info("Connection error detected, recreating session")
                await self._recreate_session()

            raise Exception(f"API connection error: {e}")

        except asyncio.TimeoutError:
            error_msg = f"LLM API timeout after {self.timeout} seconds"
            self._log_raw_interaction(payload, error=error_msg)
            logger.warning(f"API timeout, session may be stale")
            await self._recreate_session()
            raise Exception(error_msg)

        except Exception as e:
            # Log any other exceptions
            error_msg = f"Unexpected API error: {e}"
            if not str(e).startswith("LLM API error") and not str(e).startswith("API connection error"):
                self._log_raw_interaction(payload, error=error_msg)
            raise

    async def _execute_request(self, payload: Dict[str, Any]) -> str:
        """Execute the actual HTTP request (legacy method - uses adapter for parsing).

        Note: This is a legacy method. Prefer _execute_request_with_error_handling
        which has better error handling and session recovery.

        Args:
            payload: Request payload

        Returns:
            Response content
        """
        start_time = time.time()

        try:
            # Log raw request
            self._log_raw_interaction(payload)

            # Build headers using adapter (handles auth format differences)
            headers = self._adapter.get_headers(self.api_token)

            # Determine URL - prefer user's configured URL if it's a full endpoint
            if "/chat/completions" in self.api_url or "/messages" in self.api_url:
                url = self.api_url
            else:
                url = self._adapter.api_endpoint

            async with self.session.post(
                url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=None if self.timeout == 0 else self.timeout)
            ) as response:

                request_duration = time.time() - start_time

                if response.status == 200:
                    if self.enable_streaming:
                        content = await self._handle_streaming_response(response)
                    else:
                        data = await response.json()
                        # Use adapter to parse response (handles OpenAI vs Anthropic formats)
                        parsed = self._adapter.parse_response(data)
                        content = parsed.content
                        # Extract token usage from unified format
                        self.last_token_usage = parsed.usage

                    # Log successful response with full data
                    self._log_raw_interaction(payload, response_data=data if not self.enable_streaming else {"choices": [{"message": {"content": content}}]})

                    logger.debug(f"API call completed in {request_duration:.2f}s")
                    return content

                else:
                    error_text = await response.text()
                    error_msg = f"LLM API error: {response.status} - {error_text}"

                    # Log error response
                    self._log_raw_interaction(payload, error=error_msg)

                    raise Exception(error_msg)

        except asyncio.TimeoutError:
            error_msg = f"LLM API timeout after {self.timeout} seconds"
            self._log_raw_interaction(payload, error=error_msg)
            raise Exception(error_msg)

        except Exception as e:
            # Log any other exceptions
            if not str(e).startswith("LLM API error"):
                self._log_raw_interaction(payload, error=str(e))
            raise
    
    async def _handle_streaming_response(self, response) -> str:
        """Handle streaming response from API.
        
        Args:
            response: HTTP response object
            
        Returns:
            Complete response content
        """
        content_parts = []
        buffer = ""
        
        async for chunk in response.content.iter_chunked(1024):
            # Check for cancellation
            if self.cancel_requested:
                raise asyncio.CancelledError("Streaming request cancelled")
            
            chunk_text = chunk.decode('utf-8')
            buffer += chunk_text
            
            # Process complete SSE lines
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if line.startswith('data: '):
                    data_text = line[6:]  # Remove 'data: ' prefix
                    if data_text == '[DONE]':
                        break
                    try:
                        chunk_data = json.loads(data_text)
                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                            delta = chunk_data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content_chunk = delta['content']
                                content_parts.append(content_chunk)

                                # Call streaming callback with chunk if provided
                                if self.streaming_callback:
                                    await self.streaming_callback(content_chunk)
                    except json.JSONDecodeError:
                        continue
        
        return ''.join(content_parts)
    
    async def _monitor_request(self) -> str:
        """Monitor request execution with cancellation support.
        
        Returns:
            API response content
        """
        try:
            while not self.current_request_task.done():
                if self.cancel_requested:
                    logger.info("Cancelling API request due to user request")
                    self.current_request_task.cancel()
                    break
                
                # Small delay to avoid busy waiting
                await asyncio.sleep(self.config.get("core.llm.api_poll_delay", 0.01))
            
            # Get result
            return await self.current_request_task
            
        except asyncio.CancelledError:
            logger.info("API request was cancelled")
            raise
    
    def _log_raw_interaction(self, request_payload: Dict[str, Any],
                           response_data: Optional[Dict[str, Any]] = None,
                           error: Optional[str] = None,
                           cancelled: bool = False) -> None:
        """Log raw request and response data to JSONL file.
        
        Args:
            request_payload: The request payload sent to LLM
            response_data: The full response data from LLM (optional)
            error: Error message if request failed (optional)
            cancelled: Whether the request was cancelled (optional)
        """
        try:
            # Create filename with session ID for easy correlation
            # Format: {session_id}_raw_{timestamp}.jsonl or fallback to raw_llm_interactions_{timestamp}.jsonl
            timestamp = datetime.now().strftime("%H%M%S")
            if self.current_session_id:
                # e.g., session_2025-12-11_112522_raw_112635.jsonl
                filename = f"{self.current_session_id}_raw_{timestamp}.jsonl"
            else:
                # Fallback if no session ID set
                date_timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                filename = f"raw_llm_interactions_{date_timestamp}.jsonl"
            filepath = self.raw_conversations_dir / filename
            
            # Create log entry with session linking
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.current_session_id,  # Links to conversations/session_*.jsonl
                "request": {
                    "url": f"{self.api_url}/v1/chat/completions",
                    "method": "POST",
                    "payload": request_payload
                }
            }
            
            if response_data:
                log_entry["response"] = {
                    "status": "success",
                    "data": response_data
                }
            elif error:
                log_entry["response"] = {
                    "status": "error", 
                    "error": error
                }
            elif cancelled:
                log_entry["response"] = {
                    "status": "cancelled",
                    "message": "Request was cancelled by user"
                }
            
            # Append to JSONL file
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log raw interaction: {e}")

    @asynccontextmanager
    async def api_session(self):
        """Context manager for safe API operations with guaranteed cleanup.

        Usage:
            async with api_service.api_session():
                result = await api_service.call_llm(conversation)

        Yields:
            The API service instance with initialized session
        """
        try:
            # Ensure session is initialized
            await self._ensure_session()
            logger.debug("API session context entered")
            yield self
        except Exception as e:
            logger.error(f"Error in API session context: {e}")
            raise
        finally:
            # Note: We don't cleanup here to allow session reuse
            # Session cleanup is handled by explicit shutdown() calls
            logger.debug("API session context exited")

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics and resource usage.

        Returns:
            Dictionary with connection statistics and resource information
        """
        stats = self._connection_stats.copy()

        # Add current session information
        if self.session and hasattr(self.session, '_connector'):
            connector = self.session._connector
            stats.update({
                'active_connections': len(connector._conns),
                'available_connections': len(connector._available),
                'closed_connections': getattr(connector, '_closed', 0),
                'limit': connector.limit,
                'limit_per_host': connector.limit_per_host,
                'keepalive_timeout': connector.keepalive_timeout
            })

        # Add session health information
        stats.update({
            'session_initialized': self._initialized,
            'session_closed': self.session.closed if self.session else True,
            'session_age_seconds': (
                time.time() - self._connection_stats['session_creation_time']
                if self._connection_stats['session_creation_time'] else 0
            ),
            'last_activity_age_seconds': (
                time.time() - self._connection_stats['last_activity']
                if self._connection_stats['last_activity'] else 0
            )
        })

        # Calculate derived metrics
        total_requests = stats['total_requests']
        if total_requests > 0:
            stats['failure_rate_percent'] = round((stats['failed_requests'] / total_requests) * 100, 2)
            stats['connection_error_rate_percent'] = round((stats['connection_errors'] / total_requests) * 100, 2)
        else:
            stats['failure_rate_percent'] = 0.0
            stats['connection_error_rate_percent'] = 0.0

        return stats

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check on the API service.

        Returns:
            Dictionary with health status information
        """
        health_status = {
            'healthy': True,
            'checks': {},
            'timestamp': time.time()
        }

        # Check session status
        session_healthy = (
            self._initialized and
            self.session and
            not self.session.closed
        )
        health_status['checks']['session'] = {
            'healthy': session_healthy,
            'initialized': self._initialized,
            'closed': self.session.closed if self.session else True
        }
        if not session_healthy:
            health_status['healthy'] = False

        # Check connection health by attempting a simple request
        connection_healthy = await self._test_connection()
        health_status['checks']['connection'] = {
            'healthy': connection_healthy,
            'url': self.api_url
        }
        if not connection_healthy:
            health_status['healthy'] = False

        # Check resource usage
        stats = self.get_connection_stats()
        resource_healthy = (
            stats.get('failure_rate_percent', 0) < 50 and  # Less than 50% failure rate
            stats.get('connection_error_rate_percent', 0) < 25  # Less than 25% connection error rate
        )
        health_status['checks']['resources'] = {
            'healthy': resource_healthy,
            'failure_rate': stats.get('failure_rate_percent', 0),
            'connection_error_rate': stats.get('connection_error_rate_percent', 0),
            'recreated_sessions': stats.get('recreated_sessions', 0)
        }
        if not resource_healthy:
            health_status['healthy'] = False

        return health_status

    async def _test_connection(self) -> bool:
        """Test if we can establish a connection to the API.

        Returns:
            True if connection test succeeds, False otherwise
        """
        if not self.session or self.session.closed:
            return False

        try:
            # Try to make a simple health check request
            # Note: Many LLM APIs don't have a health endpoint, so we'll test with a minimal request
            timeout = aiohttp.ClientTimeout(total=5)  # Short timeout for health check

            # Try to connect to the base URL
            if "/chat/completions" in self.api_url:
                health_url = self.api_url.rsplit('/chat/completions', 1)[0]
            else:
                health_url = self.api_url

            async with self.session.get(
                health_url,
                timeout=timeout,
                allow_redirects=True
            ) as response:
                # Any response (even 404) indicates the server is reachable
                return response.status < 500

        except Exception as e:
            logger.debug(f"Connection test failed: {e}")
            return False

    def get_api_stats(self) -> Dict[str, Any]:
        """Get API communication statistics.

        Returns:
            Dictionary with API statistics
        """
        return {
            "api_url": self.api_url,
            "model": self.model,
            "temperature": self.temperature,
            "timeout": self.timeout,
            "streaming_enabled": self.enable_streaming,
            "session_active": self.session is not None,
            "connection_stats": self.get_connection_stats()
        }