"""Fullscreen plugin command integration system.

This module handles automatic discovery and registration of slash commands
for fullscreen plugins, enabling dynamic plugin-to-command mapping.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type
import importlib.util
import sys

from ..events.models import CommandDefinition, CommandMode, CommandCategory
from ..commands.registry import SlashCommandRegistry
from .plugin import FullScreenPlugin

logger = logging.getLogger(__name__)


class FullScreenCommandIntegrator:
    """Integrates fullscreen plugins with the slash command system.

    This class:
    - Discovers fullscreen plugins in plugins/fullscreen/
    - Auto-registers slash commands based on plugin metadata
    - Handles dynamic plugin loading/unloading
    - Maps commands to plugin execution
    """

    def __init__(self, command_registry: SlashCommandRegistry, event_bus):
        """Initialize the fullscreen command integrator.

        Args:
            command_registry: Slash command registry for registration
            event_bus: Event bus for communication
        """
        self.command_registry = command_registry
        self.event_bus = event_bus
        self.registered_plugins: Dict[str, Type[FullScreenPlugin]] = {}
        self.plugin_instances: Dict[str, FullScreenPlugin] = {}
        self._fullscreen_manager = None

        logger.info("FullScreen command integrator initialized")

    def discover_and_register_plugins(self, plugins_dir: Path) -> int:
        """Discover and register all fullscreen plugins.

        Args:
            plugins_dir: Base plugins directory

        Returns:
            Number of plugins registered
        """
        fullscreen_dir = plugins_dir / "fullscreen"
        if not fullscreen_dir.exists():
            logger.info("No fullscreen plugins directory found")
            return 0

        registered_count = 0

        # Scan for Python files in fullscreen directory
        for plugin_file in fullscreen_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue

            try:
                plugin_class = self._load_plugin_class(plugin_file)
                if plugin_class:
                    if self._register_plugin_commands(plugin_class):
                        registered_count += 1
                        logger.info(f"Registered commands for plugin: {plugin_class.__name__}")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file.name}: {e}")

        logger.info(f"Discovered and registered {registered_count} fullscreen plugins")
        return registered_count

    def _load_plugin_class(self, plugin_file: Path) -> Optional[Type[FullScreenPlugin]]:
        """Load a plugin class from a Python file.

        Args:
            plugin_file: Path to the plugin Python file

        Returns:
            Plugin class or None if not found/invalid
        """
        try:
            # Create module spec and load
            module_name = f"plugins.fullscreen.{plugin_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if not spec or not spec.loader:
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find FullScreenPlugin subclass
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, FullScreenPlugin) and
                    attr != FullScreenPlugin):
                    return attr

            logger.warning(f"No FullScreenPlugin subclass found in {plugin_file.name}")
            return None

        except Exception as e:
            logger.error(f"Error loading plugin class from {plugin_file}: {e}")
            return None

    def _register_plugin_commands(self, plugin_class: Type[FullScreenPlugin]) -> bool:
        """Register slash commands for a plugin class.

        Args:
            plugin_class: The plugin class to register commands for

        Returns:
            True if registration successful
        """
        try:
            # Create temporary instance to get metadata
            temp_instance = plugin_class()
            metadata = temp_instance.metadata

            if not metadata:
                logger.warning(f"Plugin {plugin_class.__name__} has no metadata")
                return False

            # Store plugin class for later instantiation
            self.registered_plugins[metadata.name] = plugin_class

            # Register primary command (plugin name)
            primary_command = CommandDefinition(
                name=metadata.name,
                aliases=metadata.aliases or [],
                description=metadata.description,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.INSTANT,
                handler=self._create_plugin_handler(metadata.name),
                icon=metadata.icon,
                plugin_name="fullscreen_integrator"
            )

            success = self.command_registry.register_command(primary_command)
            if not success:
                logger.error(f"Failed to register primary command for {metadata.name}")
                return False

            # Register alias commands if any
            for alias in (metadata.aliases or []):
                alias_command = CommandDefinition(
                    name=alias,
                    aliases=[],
                    description=f"{metadata.description} (alias)",
                    category=CommandCategory.SYSTEM,
                    mode=CommandMode.INSTANT,
                    handler=self._create_plugin_handler(metadata.name),
                    icon=metadata.icon,
                    plugin_name="fullscreen_integrator"
                )

                alias_success = self.command_registry.register_command(alias_command)
                if alias_success:
                    logger.debug(f"Registered alias command: {alias} -> {metadata.name}")
                else:
                    logger.warning(f"Failed to register alias command: {alias}")

            return True

        except Exception as e:
            logger.error(f"Error registering commands for {plugin_class.__name__}: {e}")
            return False

    def _create_plugin_handler(self, plugin_name: str):
        """Create a command handler for a specific plugin.

        Args:
            plugin_name: Name of the plugin to handle

        Returns:
            Async command handler function
        """
        async def handler(command):
            """Handle command execution for fullscreen plugin."""
            try:
                # Get or create fullscreen manager
                if not self._fullscreen_manager:
                    from . import FullScreenManager
                    self._fullscreen_manager = FullScreenManager(self.event_bus, None)

                # Get or create plugin instance
                if plugin_name not in self.plugin_instances:
                    plugin_class = self.registered_plugins.get(plugin_name)
                    if not plugin_class:
                        raise ValueError(f"Plugin class not found: {plugin_name}")

                    plugin_instance = plugin_class()
                    self.plugin_instances[plugin_name] = plugin_instance
                    self._fullscreen_manager.register_plugin(plugin_instance)
                    logger.debug(f"Created and registered plugin instance: {plugin_name}")

                # Launch the plugin
                success = await self._fullscreen_manager.launch_plugin(plugin_name)

                if success:
                    from ..events.models import CommandResult
                    return CommandResult(
                        success=True,
                        message="",  # No message to avoid display artifacts
                        display_type="success"
                    )
                else:
                    from ..events.models import CommandResult
                    return CommandResult(
                        success=False,
                        message=f"Failed to launch {plugin_name} plugin",
                        display_type="error"
                    )

            except Exception as e:
                logger.error(f"Error executing plugin {plugin_name}: {e}")
                from ..events.models import CommandResult
                return CommandResult(
                    success=False,
                    message=f"Plugin error: {str(e)}",
                    display_type="error"
                )

        return handler

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin and its commands.

        Args:
            plugin_name: Name of plugin to unregister

        Returns:
            True if successful
        """
        try:
            # Remove from our tracking
            if plugin_name in self.registered_plugins:
                plugin_class = self.registered_plugins[plugin_name]
                temp_instance = plugin_class()
                metadata = temp_instance.metadata

                # Unregister all commands for this plugin
                self.command_registry.unregister_command(metadata.name)
                for alias in (metadata.aliases or []):
                    self.command_registry.unregister_command(alias)

                del self.registered_plugins[plugin_name]

                if plugin_name in self.plugin_instances:
                    del self.plugin_instances[plugin_name]

                logger.info(f"Unregistered plugin: {plugin_name}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error unregistering plugin {plugin_name}: {e}")
            return False

    def get_registered_plugins(self) -> List[str]:
        """Get list of registered plugin names.

        Returns:
            List of plugin names
        """
        return list(self.registered_plugins.keys())

    def reload_plugins(self, plugins_dir: Path) -> int:
        """Reload all fullscreen plugins from directory.

        Args:
            plugins_dir: Base plugins directory

        Returns:
            Number of plugins reloaded
        """
        # Unregister all current plugins
        for plugin_name in list(self.registered_plugins.keys()):
            self.unregister_plugin(plugin_name)

        # Re-discover and register
        return self.discover_and_register_plugins(plugins_dir)