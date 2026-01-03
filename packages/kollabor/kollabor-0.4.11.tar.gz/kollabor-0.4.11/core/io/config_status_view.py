"""Configuration status view for displaying config errors and status.

This module provides a status view component for monitoring configuration
errors, validation warnings, and overall configuration health status.
"""

import logging
from typing import Dict, Any, Optional, List

from .status_renderer import StatusViewConfig

logger = logging.getLogger(__name__)


class ConfigStatusView:
    """Status view for configuration monitoring and error reporting."""

    def __init__(self, config_service, event_bus):
        """Initialize the configuration status view.

        Args:
            config_service: The configuration service to monitor.
            event_bus: Event bus for receiving notifications.
        """
        self.config_service = config_service
        self.event_bus = event_bus
        self.view_id = "config_status"
        self.priority = 900  # High priority for config errors

        # Register for config reload notifications
        if hasattr(config_service, "register_reload_callback"):
            config_service.register_reload_callback(self._on_config_reload)

        logger.debug("ConfigStatusView initialized")

    def _on_config_reload(self) -> None:
        """Callback when configuration is reloaded."""
        # Trigger status refresh by emitting event
        if self.event_bus and hasattr(self.event_bus, "emit_with_hooks"):
            # Note: This is called from sync context during config reload
            # EventBus doesn't have emit_async method
            # Skip the event emission during sync config reload
            logger.debug("Config reloaded - status refresh skipped (sync context)")

    def get_status_data(self) -> Dict[str, Any]:
        """Get configuration status data.

        Returns:
            Dictionary with config status information.
        """
        if not self.config_service:
            return {"error": "No config service", "status": "ERROR"}

        config_error = self.config_service.get_config_error()
        has_error = self.config_service.has_config_error()

        using_cache = has_error and self.config_service._cached_config is not None
        status_data = {
            "has_error": has_error,
            "error_message": config_error,
            "status": "ERROR" if has_error else "OK",
            "using_cache": using_cache,
        }

        # Add validation info
        try:
            validation_result = self.config_service.validate_config()
            status_data.update(
                {
                    "valid": validation_result.get("valid", True),
                    "warnings": validation_result.get("warnings", []),
                    "errors": validation_result.get("errors", []),
                }
            )
        except Exception as e:
            logger.warning(f"Could not validate config: {e}")
            status_data["validation_error"] = str(e)

        return status_data

    def format_status_line(self, data: Dict[str, Any]) -> Optional[str]:
        """Format the configuration status line.

        Args:
            data: Status data dictionary.

        Returns:
            Formatted status line or None if no status needed.
        """
        if not data:
            return None

        # Show errors prominently
        if data.get("has_error"):
            error_msg = data.get("error_message", "Unknown config error")
            if data.get("using_cache"):
                return f" Config Error (using cache): {error_msg[:40]}..."
            else:
                return f"Config Error: {error_msg[:50]}..."

        # Show validation warnings
        warnings = data.get("warnings", [])
        if warnings:
            warning_count = len(warnings)
            if warning_count == 1:
                return f" Config Warning: {warnings[0][:45]}..."
            else:
                return f" Config: {warning_count} warnings"

        # Show validation errors (different from load errors)
        errors = data.get("errors", [])
        if errors:
            error_count = len(errors)
            if error_count == 1:
                return f"Config Validation: {errors[0][:40]}..."
            else:
                return f"Config: {error_count} validation errors"

        # Normal status - only show if explicitly requested
        if data.get("show_normal_status", False):
            return "[ok] Config: OK"

        # No status line needed for normal operation
        return None

    def should_display(self, data: Dict[str, Any]) -> bool:
        """Determine if this status view should be displayed.

        Args:
            data: Status data dictionary.

        Returns:
            True if status should be shown, False otherwise.
        """
        if not data:
            return False

        # Always show errors and warnings
        return (
            data.get("has_error", False)
            or data.get("warnings", [])
            or data.get("errors", [])
            or data.get("show_normal_status", False)
        )

    def get_color_scheme(self, data: Dict[str, Any]) -> str:
        """Get color scheme based on config status.

        Args:
            data: Status data dictionary.

        Returns:
            Color scheme name.
        """
        if data.get("has_error"):
            return "error"
        elif data.get("warnings") or data.get("errors"):
            return "warning"
        else:
            return "success"

    def get_priority(self) -> int:
        """Get display priority for this status view.

        Returns:
            Priority value (higher = more important).
        """
        # High priority for config issues
        return self.priority

    async def handle_status_event(
        self, event_type: str, event_data: Dict[str, Any]
    ) -> None:
        """Handle status-related events.

        Args:
            event_type: Type of the event.
            event_data: Event data dictionary.
        """
        if event_type in ["config_reloaded", "config_error", "config_changed"]:
            # Refresh status display
            await self.refresh_status()

    async def refresh_status(self) -> None:
        """Refresh the status display."""
        if self.event_bus and hasattr(self.event_bus, "emit_with_hooks"):
            from ..events.models import EventType

            await self.event_bus.emit_with_hooks(
                EventType.STATUS_CONTENT_UPDATE,
                {"view_id": self.view_id, "source": "config_status"},
                "config_status_view",
            )

    def get_status_view_config(self) -> StatusViewConfig:
        """Get StatusViewConfig for registry registration.

        Returns:
            StatusViewConfig that can be registered with StatusViewRegistry.
        """
        from .status_renderer import BlockConfig

        return StatusViewConfig(
            name="Configuration Status",
            plugin_source="core",
            priority=self.priority,
            blocks=[
                BlockConfig(
                    width_fraction=1.0,
                    content_provider=self._get_config_status_content,
                    title="Configuration Status",
                    priority=100
                )
            ],
        )

    def _get_config_status_content(self) -> List[str]:
        """Get configuration status content for status view.

        Returns:
            List of status content lines.
        """
        status_data = self.get_status_data()

        # Show errors prominently
        if status_data.get("has_error"):
            error_msg = status_data.get("error_message", "Unknown config error")
            if status_data.get("using_cache"):
                return [f"Config: ERROR (using cache)", f"Error: {error_msg[:60]}"]
            else:
                return [f"Config: ERROR", f"Error: {error_msg[:60]}"]

        # Show validation warnings
        warnings = status_data.get("warnings", [])
        if warnings:
            lines = [f"Config: {len(warnings)} warning(s)"]
            for warning in warnings[:3]:  # Show first 3 warnings
                lines.append(f"- {warning[:60]}")
            return lines

        # Show validation errors
        errors = status_data.get("errors", [])
        if errors:
            lines = [f"Config: {len(errors)} validation error(s)"]
            for error in errors[:3]:  # Show first 3 errors
                lines.append(f"- {error[:60]}")
            return lines

        # Normal status - show healthy config
        return ["Config: OK", "No errors or warnings"]
