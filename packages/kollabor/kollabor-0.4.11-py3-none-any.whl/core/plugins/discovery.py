"""Plugin discovery for file system scanning and module loading."""

import importlib
import inspect
import logging
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Type, Optional

from ..utils.plugin_utils import has_method, get_plugin_config_safely
from ..utils.error_utils import safe_execute

logger = logging.getLogger(__name__)

# Platform check
IS_WINDOWS = sys.platform == "win32"


class PluginDiscovery:
    """Handles plugin discovery and module loading from the file system.

    This class is responsible for scanning directories for plugin files,
    loading Python modules, and extracting plugin classes and configurations.
    """

    def __init__(self, plugins_dir: Path):
        """Initialize plugin discovery.

        Args:
            plugins_dir: Directory containing plugin modules.
        """
        self.plugins_dir = plugins_dir
        self.discovered_modules: List[str] = []
        self.loaded_classes: Dict[str, Type] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

        # Security validation patterns
        self.valid_plugin_name_pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')
        self.max_plugin_name_length = 50
        self.blocked_names = {
            '__init__', '__pycache__', 'system', 'os', 'sys', 'subprocess',
            'eval', 'exec', 'compile', 'open', 'file', 'input', 'raw_input'
        }

        logger.info(f"PluginDiscovery initialized with directory: {plugins_dir}")

    def _sanitize_plugin_name(self, plugin_name: str) -> Optional[str]:
        """Sanitize and validate plugin name for security."""
        if not plugin_name:
            logger.warning("Empty plugin name rejected")
            return None

        # Length check
        if len(plugin_name) > self.max_plugin_name_length:
            logger.warning(f"Plugin name too long: {plugin_name}")
            return None

        # Pattern validation (letters, numbers, underscores only)
        if not self.valid_plugin_name_pattern.match(plugin_name):
            logger.warning(f"Invalid plugin name pattern: {plugin_name}")
            return None

        # Block dangerous names
        if plugin_name.lower() in self.blocked_names:
            logger.warning(f"Blocked plugin name: {plugin_name}")
            return None

        # Block path traversal attempts
        if '..' in plugin_name or '/' in plugin_name or '\\' in plugin_name:
            logger.warning(f"Path traversal attempt in plugin name: {plugin_name}")
            return None

        # Block shell metacharacters
        if any(char in plugin_name for char in [';', '&', '|', '`', '$', '"', "'"]):
            logger.warning(f"Shell metacharacters in plugin name: {plugin_name}")
            return None

        return plugin_name

    def _verify_plugin_location(self, plugin_name: str) -> bool:
        """Verify plugin file exists in expected location."""
        try:
            # Construct expected file path (plugin_name already includes _plugin suffix)
            plugin_file = self.plugins_dir / f"{plugin_name}.py"

            # Resolve to absolute path to prevent symlink attacks
            plugin_file = plugin_file.resolve()

            # Verify it's within the plugins directory
            plugins_dir = self.plugins_dir.resolve()
            if not str(plugin_file).startswith(str(plugins_dir)):
                logger.error(f"Plugin file outside plugins directory: {plugin_file}")
                return False

            # Verify file exists and is a regular file
            if not plugin_file.is_file():
                logger.error(f"Plugin file not found: {plugin_file}")
                return False

            # Additional security: check file permissions (Unix only)
            if not IS_WINDOWS:
                if plugin_file.stat().st_mode & 0o777 != 0o644:
                    logger.warning(f"Plugin file has unusual permissions: {plugin_file}")

            return True

        except Exception as e:
            logger.error(f"Error verifying plugin location: {e}")
            return False

    def _verify_loaded_module(self, module, plugin_name: str) -> bool:
        """Verify the loaded module is actually our plugin."""
        try:
            # Check module name matches
            expected_module_name = f"plugins.{plugin_name}"
            if module.__name__ != expected_module_name:
                logger.error(f"Module name mismatch: {module.__name__} != {expected_module_name}")
                return False

            # Check module file location
            if hasattr(module, '__file__'):
                module_file = Path(module.__file__).resolve()
                plugins_dir = self.plugins_dir.resolve()

                if not str(module_file).startswith(str(plugins_dir)):
                    logger.error(f"Module file outside plugins directory: {module_file}")
                    return False

            # Verify module has expected plugin attributes
            if not hasattr(module, '__dict__'):
                logger.error(f"Module {plugin_name} has no __dict__ attribute")
                return False

            return True

        except Exception as e:
            logger.error(f"Error verifying loaded module {plugin_name}: {e}")
            return False
    
    def scan_plugin_files(self) -> List[str]:
        """Scan the plugins directory for plugin files with security validation.

        Returns:
            List of discovered plugin module names.
        """
        discovered = []

        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory does not exist: {self.plugins_dir}")
            return discovered

        # Resolve plugins directory to prevent symlink attacks
        try:
            plugins_dir = self.plugins_dir.resolve()

            # Verify directory permissions (Unix only - Windows doesn't use these bits)
            if not IS_WINDOWS:
                if plugins_dir.stat().st_mode & 0o002:
                    logger.error(f"Plugins directory is world-writable: {plugins_dir}")
                    return discovered

        except Exception as e:
            logger.error(f"Error resolving plugins directory: {e}")
            return discovered

        for plugin_file in plugins_dir.glob("*_plugin.py"):
            try:
                # Extract module name from file (KEEP _plugin suffix for import)
                module_name = plugin_file.stem  # e.g., "enhanced_input_plugin"

                # Apply security validation
                safe_name = self._sanitize_plugin_name(module_name)
                if not safe_name:
                    logger.warning(f"Skipping invalid plugin: {module_name}")
                    continue

                # Verify plugin location
                if not self._verify_plugin_location(safe_name):
                    logger.warning(f"Plugin location verification failed: {safe_name}")
                    continue

                discovered.append(safe_name)
                logger.debug(f"Discovered valid plugin: {safe_name}")

            except Exception as e:
                logger.error(f"Error processing plugin file {plugin_file}: {e}")
                continue

        self.discovered_modules = discovered
        logger.info(f"Discovered {len(discovered)} validated plugin modules")
        return discovered
    
    def load_module(self, module_name: str) -> bool:
        """Load a single plugin module and extract plugin classes.

        Args:
            module_name: Name of the plugin module to load.

        Returns:
            True if module loaded successfully, False otherwise.
        """
        # Validate module name before loading
        safe_name = self._sanitize_plugin_name(module_name)
        if not safe_name:
            logger.error(f"Invalid plugin name rejected: {module_name}")
            return False

        # Verify plugin location again for safety
        if not self._verify_plugin_location(safe_name):
            logger.error(f"Plugin location verification failed during loading: {safe_name}")
            return False

        def _import_and_extract():
            # Import the plugin module with security validation
            module_path = f"plugins.{safe_name}"

            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                logger.error(f"Failed to import plugin module {safe_name}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error importing plugin module {safe_name}: {e}")
                raise

            # Verify the loaded module is actually our plugin
            if not self._verify_loaded_module(module, safe_name):
                raise ValueError(f"Module verification failed: {safe_name}")
            
            # Find classes that look like plugins (end with 'Plugin')
            found_plugins = False
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith('Plugin') and has_method(obj, 'get_default_config'):
                    # Store the plugin class
                    self.loaded_classes[name] = obj
                    
                    # Get and store plugin configuration
                    config = get_plugin_config_safely(obj)
                    self.plugin_configs[name] = config
                    
                    if config:
                        logger.info(f"Loaded plugin class: {name} with config keys: {list(config.keys())}")
                    else:
                        logger.info(f"Loaded plugin class: {name} with no configuration")
                    
                    found_plugins = True
            
            return found_plugins
        
        result = safe_execute(
            _import_and_extract,
            f"loading plugin module {module_name}",
            default=False,
            logger_instance=logger
        )
        
        return result
    
    def load_all_modules(self) -> int:
        """Load all discovered plugin modules.
        
        Returns:
            Number of successfully loaded plugin classes.
        """
        initial_count = len(self.loaded_classes)
        
        for module_name in self.discovered_modules:
            self.load_module(module_name)
        
        loaded_count = len(self.loaded_classes) - initial_count
        logger.info(f"Loaded {loaded_count} plugin classes from {len(self.discovered_modules)} modules")
        
        return loaded_count
    
    def discover_and_load(self) -> Dict[str, Type]:
        """Perform complete discovery and loading process.
        
        Returns:
            Dictionary mapping plugin names to their classes.
        """
        # Scan for plugin files
        self.scan_plugin_files()
        
        # Load all discovered modules
        self.load_all_modules()
        
        logger.info(f"Discovery complete: {len(self.loaded_classes)} plugins loaded")
        return self.loaded_classes
    
    def get_plugin_class(self, plugin_name: str) -> Type:
        """Get a loaded plugin class by name.
        
        Args:
            plugin_name: Name of the plugin class.
            
        Returns:
            Plugin class if found.
            
        Raises:
            KeyError: If plugin class not found.
        """
        if plugin_name not in self.loaded_classes:
            raise KeyError(f"Plugin class '{plugin_name}' not found")
        
        return self.loaded_classes[plugin_name]
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """Get configuration for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin.
            
        Returns:
            Plugin configuration dictionary, or empty dict if not found.
        """
        return self.plugin_configs.get(plugin_name, {})
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get configurations for all loaded plugins.
        
        Returns:
            Dictionary mapping plugin names to their configurations.
        """
        return self.plugin_configs.copy()
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get statistics about the discovery process.
        
        Returns:
            Dictionary with discovery statistics.
        """
        return {
            "plugins_directory": str(self.plugins_dir),
            "directory_exists": self.plugins_dir.exists(),
            "discovered_modules": len(self.discovered_modules),
            "loaded_classes": len(self.loaded_classes),
            "plugins_with_config": sum(1 for c in self.plugin_configs.values() if c),
            "module_names": self.discovered_modules,
            "class_names": list(self.loaded_classes.keys())
        }
    
    def has_plugin_method(self, plugin_name: str, method_name: str) -> bool:
        """Check if a loaded plugin has a specific method.
        
        Args:
            plugin_name: Name of the plugin class.
            method_name: Name of the method to check for.
            
        Returns:
            True if plugin has the method, False otherwise.
        """
        if plugin_name not in self.loaded_classes:
            return False
        
        plugin_class = self.loaded_classes[plugin_name]
        return has_method(plugin_class, method_name)
    
    def call_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """Safely call a method on a loaded plugin class.
        
        Args:
            plugin_name: Name of the plugin class.
            method_name: Name of the method to call.
            *args: Positional arguments to pass.
            **kwargs: Keyword arguments to pass.
            
        Returns:
            Method result or None if method doesn't exist or call failed.
        """
        if plugin_name not in self.loaded_classes:
            logger.warning(f"Plugin {plugin_name} not found for method call: {method_name}")
            return None
        
        plugin_class = self.loaded_classes[plugin_name]
        
        try:
            if has_method(plugin_class, method_name):
                method = getattr(plugin_class, method_name)
                return method(*args, **kwargs)
            else:
                logger.debug(f"Plugin {plugin_name} has no method: {method_name}")
                return None
        except Exception as e:
            logger.error(f"Failed to call {plugin_name}.{method_name}: {e}")
            return None