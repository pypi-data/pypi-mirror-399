"""Hook executor for individual hook execution with error handling."""

import asyncio
import logging
import time
from typing import Any, Dict, List

from .models import Event, Hook, HookStatus
from ..utils.error_utils import log_and_continue

logger = logging.getLogger(__name__)


class HookExecutor:
    """Executes individual hooks with timeout and error handling.
    
    This class is responsible for the safe execution of a single hook,
    including timeout management, error handling, and status tracking.
    """
    
    def __init__(self):
        """Initialize the hook executor."""
        logger.debug("HookExecutor initialized")
    
    async def execute_hook(self, hook: Hook, event: Event) -> Dict[str, Any]:
        """Execute a single hook with error handling and timeout.
        
        Args:
            hook: The hook to execute.
            event: The event being processed.
            
        Returns:
            Dictionary with execution result and metadata.
        """
        hook_key = f"{hook.plugin_name}.{hook.name}"
        result_metadata = {
            "hook_key": hook_key,
            "success": False,
            "result": None,
            "error": None,
            "duration_ms": 0
        }
        
        if not hook.enabled:
            result_metadata["error"] = "hook_disabled"
            logger.debug(f"Skipping disabled hook: {hook_key}")
            return result_metadata
        
        if event.cancelled:
            result_metadata["error"] = "event_cancelled"
            logger.debug(f"Skipping hook due to cancelled event: {hook_key}")
            return result_metadata
        
        # Track execution time
        start_time = time.time()
        
        try:
            # Update hook status to working
            hook.status = HookStatus.WORKING
            
            # Execute hook with timeout
            result = await asyncio.wait_for(
                hook.callback(event.data, event),
                timeout=hook.timeout
            )
            
            # Calculate execution time
            end_time = time.time()
            result_metadata["duration_ms"] = max(1, int((end_time - start_time) * 1000))
            
            # Mark as successful
            hook.status = HookStatus.COMPLETED
            result_metadata["success"] = True
            result_metadata["result"] = result
            # Handle data transformation if hook returns modified data
            if isinstance(result, dict) and "data" in result:
                self._apply_data_transformation(event, result["data"])
                logger.debug(f"Hook {hook_key} modified event data")
                
        except asyncio.TimeoutError:
            end_time = time.time()
            result_metadata["duration_ms"] = max(1, int((end_time - start_time) * 1000))
            result_metadata["error"] = "timeout"
            
            hook.status = HookStatus.TIMEOUT
            logger.warning(f"Hook {hook_key} timed out after {hook.timeout}s")
            
            # Handle timeout based on error action
            if hook.error_action == "stop":
                event.cancelled = True
                logger.info(f"Event cancelled due to hook timeout: {hook_key}")
                
        except Exception as e:
            end_time = time.time()
            result_metadata["duration_ms"] = max(1, int((end_time - start_time) * 1000))
            result_metadata["error"] = str(e)
            
            hook.status = HookStatus.FAILED
            log_and_continue(logger, f"executing hook {hook_key}", e)
            
            # Handle error based on error action
            if hook.error_action == "stop":
                event.cancelled = True
                logger.info(f"Event cancelled due to hook error: {hook_key}")
        
        return result_metadata
    
    def _apply_data_transformation(self, event: Event, hook_data: Dict[str, Any]) -> None:
        """Apply data transformation from hook result to event.
        
        Args:
            event: The event to modify.
            hook_data: Data transformation from hook.
        """
        try:
            if isinstance(hook_data, dict):
                event.data.update(hook_data)
            else:
                logger.warning(f"Hook returned non-dict data transformation: {type(hook_data)}")
        except Exception as e:
            log_and_continue(logger, "applying hook data transformation", e)
    
    def get_execution_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get execution statistics from a list of hook results.
        
        Args:
            results: List of hook execution results.
            
        Returns:
            Dictionary with execution statistics.
        """
        if not results:
            return {
                "total_hooks": 0,
                "successful": 0,
                "failed": 0,
                "timed_out": 0,
                "total_duration_ms": 0,
                "avg_duration_ms": 0
            }
        
        successful = sum(1 for r in results if r.get("success", False))
        failed = sum(1 for r in results if r.get("error") and r["error"] not in ["timeout", "hook_disabled", "event_cancelled"])
        timed_out = sum(1 for r in results if r.get("error") == "timeout")
        total_duration = sum(r.get("duration_ms", 0) for r in results)
        
        return {
            "total_hooks": len(results),
            "successful": successful,
            "failed": failed,
            "timed_out": timed_out,
            "total_duration_ms": total_duration,
            "avg_duration_ms": int(total_duration / len(results)) if results else 0
        }