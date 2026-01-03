"""Event system for plugin communication."""

import logging
from typing import Any, Dict

from .models import EventType, Hook
from .registry import HookRegistry
from .executor import HookExecutor
from .processor import EventProcessor

logger = logging.getLogger(__name__)


class EventBus:
    """Simplified event bus system for plugin communication.
    
    Coordinates between specialized components for hook registration
    and event processing with clean separation of concerns.
    """
    
    def __init__(self) -> None:
        """Initialize the event bus with specialized components."""
        self.hook_registry = HookRegistry()
        self.hook_executor = HookExecutor()
        self.event_processor = EventProcessor(self.hook_registry, self.hook_executor)
        logger.info("Event bus initialized with specialized components")
    
    async def register_hook(self, hook: Hook) -> bool:
        """Register a hook with the event bus.
        
        Args:
            hook: The hook to register.
            
        Returns:
            True if registration successful, False otherwise.
        """
        success = self.hook_registry.register_hook(hook)
        if success:
            logger.debug(f"Successfully registered hook: {hook.plugin_name}.{hook.name}")
        else:
            logger.error(f"Failed to register hook: {hook.plugin_name}.{hook.name}")
        return success
    
    async def unregister_hook(self, plugin_name: str, hook_name: str) -> bool:
        """Unregister a hook from the event bus.
        
        Args:
            plugin_name: Name of the plugin that owns the hook.
            hook_name: Name of the hook.
            
        Returns:
            True if unregistration successful, False otherwise.
        """
        return self.hook_registry.unregister_hook(plugin_name, hook_name)
    
    async def emit_with_hooks(self, event_type: EventType, data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """Emit an event with pre/post hook processing.
        
        Args:
            event_type: Type of event to emit.
            data: Event data.
            source: Source of the event.
            
        Returns:
            Results from hook processing.
        """
        return await self.event_processor.process_event_with_phases(event_type, data, source)
    
    def get_hook_status(self) -> Dict[str, Any]:
        """Get current status of all registered hooks.
        
        Returns:
            Dictionary with hook status information.
        """
        return self.hook_registry.get_hook_status_summary()
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics.
        
        Returns:
            Dictionary with detailed registry statistics.
        """
        return self.hook_registry.get_registry_stats()
    
    def enable_hook(self, plugin_name: str, hook_name: str) -> bool:
        """Enable a registered hook.
        
        Args:
            plugin_name: Name of the plugin that owns the hook.
            hook_name: Name of the hook.
            
        Returns:
            True if hook was enabled, False otherwise.
        """
        return self.hook_registry.enable_hook(plugin_name, hook_name)
    
    def disable_hook(self, plugin_name: str, hook_name: str) -> bool:
        """Disable a registered hook.
        
        Args:
            plugin_name: Name of the plugin that owns the hook.
            hook_name: Name of the hook.
            
        Returns:
            True if hook was disabled, False otherwise.
        """
        return self.hook_registry.disable_hook(plugin_name, hook_name)
    
    def get_hooks_for_event(self, event_type: EventType) -> int:
        """Get the number of hooks registered for an event type.
        
        Args:
            event_type: The event type to check.
            
        Returns:
            Number of hooks registered for the event type.
        """
        hooks = self.hook_registry.get_hooks_for_event(event_type)
        return len(hooks)
    
    def add_event_type_mapping(self, main_event: EventType, pre_event: EventType, post_event: EventType) -> None:
        """Add a new event type mapping for pre/post processing.
        
        Args:
            main_event: The main event type.
            pre_event: The pre-processing event type.
            post_event: The post-processing event type.
        """
        self.event_processor.add_event_type_mapping(main_event, pre_event, post_event)