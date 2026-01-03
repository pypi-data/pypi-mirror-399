"""System commands plugin for core application functionality."""

import logging
from typing import Dict, Any, List

from core.commands.system_commands import SystemCommandsPlugin as CoreSystemCommandsPlugin
from core.io.visual_effects import AgnosterSegment

logger = logging.getLogger(__name__)


class SystemCommandsPlugin:
    """Plugin wrapper for system commands integration."""

    def __init__(self) -> None:
        """Initialize the system commands plugin wrapper."""
        self.name = "system_commands"
        self.version = "1.0.0"
        self.description = "Core system commands (/help, /config, /status, etc.)"
        self.enabled = True
        self.system_commands = None
        self.renderer = None
        self.logger = logger

    async def initialize(self, event_bus, config, **kwargs) -> None:
        """Initialize the plugin and register system commands."""
        try:
            self.renderer = kwargs.get('renderer')

            command_registry = kwargs.get('command_registry')
            if not command_registry:
                self.logger.warning("No command registry provided, system commands not registered")
                return

            self.system_commands = CoreSystemCommandsPlugin(
                command_registry=command_registry,
                event_bus=event_bus,
                config_manager=config
            )
            self.system_commands.register_commands()

            # Register status view
            await self._register_status_view()

            self.logger.info("System commands plugin initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing system commands plugin: {e}")
            raise

    async def _register_status_view(self) -> None:
        """Register system commands status view."""
        try:
            if (self.renderer and
                hasattr(self.renderer, 'status_renderer') and
                self.renderer.status_renderer and
                hasattr(self.renderer.status_renderer, 'status_registry') and
                self.renderer.status_renderer.status_registry):

                from core.io.status_renderer import StatusViewConfig, BlockConfig

                view = StatusViewConfig(
                    name="System Commands",
                    plugin_source="system_commands",
                    priority=400,
                    blocks=[BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_status_content,
                        title="System Commands",
                        priority=100
                    )],
                )

                registry = self.renderer.status_renderer.status_registry
                registry.register_status_view("system_commands", view)
                self.logger.info("Registered 'System Commands' status view")

        except Exception as e:
            self.logger.error(f"Failed to register status view: {e}")

    def _get_status_content(self) -> List[str]:
        """Get system commands status (agnoster style)."""
        try:
            seg = AgnosterSegment()

            if self.system_commands:
                seg.add_lime("Commands", "dark")
                seg.add_cyan("Active", "dark")
                seg.add_neutral("/help /config /status", "mid")
            else:
                seg.add_neutral("Commands: Inactive", "dark")

            return [seg.render()]

        except Exception as e:
            self.logger.error(f"Error getting status content: {e}")
            seg = AgnosterSegment()
            seg.add_neutral("Commands: Error", "dark")
            return [seg.render()]

    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        try:
            if self.system_commands:
                self.logger.info("System commands plugin shutdown completed")
        except Exception as e:
            self.logger.error(f"Error shutting down system commands plugin: {e}")

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "plugins": {
                "system_commands": {
                    "enabled": True
                }
            }
        }

    async def register_hooks(self) -> None:
        """Register event hooks (none needed)."""
        pass
