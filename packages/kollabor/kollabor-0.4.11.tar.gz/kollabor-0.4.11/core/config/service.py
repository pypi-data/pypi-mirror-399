"""Configuration service providing high-level configuration operations."""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional, Callable

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

from .manager import ConfigManager
from .loader import ConfigLoader

logger = logging.getLogger(__name__)


if WATCHDOG_AVAILABLE:
    class ConfigFileWatcher(FileSystemEventHandler):
        """File system event handler for configuration file changes."""

        def __init__(self, config_service: 'ConfigService'):
            super().__init__()
            self.config_service = config_service
            self.last_modified = 0
            self.debounce_delay = 0.5  # 500ms debounce

        def on_modified(self, event):
            """Handle file modification events."""
            if event.is_directory:
                return

            if event.src_path == str(self.config_service.config_manager.config_path):
                current_time = time.time()

                # Debounce rapid file changes
                if current_time - self.last_modified > self.debounce_delay:
                    self.last_modified = current_time
                    logger.info("Configuration file changed, triggering reload")
                    # Schedule the reload in a thread-safe way
                    try:
                        loop = asyncio.get_running_loop()
                        loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(self.config_service._handle_file_change())
                        )
                    except RuntimeError:
                        # No event loop running, fall back to sync reload
                        logger.warning("No event loop available, performing synchronous reload")
                        self.config_service.reload()
else:
    class ConfigFileWatcher:
        """Stub class when watchdog is not available."""
        def __init__(self, config_service: 'ConfigService'):
            pass


class ConfigService:
    """High-level configuration service providing a clean API.
    
    This service coordinates between the file-based ConfigManager and
    the plugin-aware ConfigLoader to provide a simple interface for
    all configuration operations.
    """
    
    def __init__(self, config_path: Path, plugin_registry=None):
        """Initialize the configuration service.

        Args:
            config_path: Path to the configuration file.
            plugin_registry: Optional plugin registry for plugin configs.
        """
        self.config_manager = ConfigManager(config_path)
        self.config_loader = ConfigLoader(self.config_manager, plugin_registry)
        self.plugin_registry = plugin_registry

        # Cached configuration for fallback
        self._cached_config = None
        self._config_error = None
        self._reload_callbacks = []

        # File watching setup
        self._file_watcher = None
        self._observer = None

        # Load initial configuration
        self._initialize_config()

        # Start file watching if successful
        self._start_file_watching()

        logger.info(f"Configuration service initialized: {config_path}")
    
    def _initialize_config(self) -> None:
        """Initialize configuration on service startup."""
        try:
            if self.config_manager.config_path.exists():
                # Load existing config and merge with defaults
                complete_config = self.config_loader.load_complete_config()
                self.config_manager.config = complete_config
                self._cached_config = complete_config.copy()
                self._config_error = None
                logger.info("Loaded and merged existing configuration")
            else:
                # Create new config with defaults and plugin configs
                complete_config = self.config_loader.load_complete_config()
                self.config_manager.config = complete_config
                self._cached_config = complete_config.copy()
                self.config_loader.save_merged_config(complete_config)
                self._config_error = None
                logger.info("Created new configuration file")
        except Exception as e:
            self._config_error = str(e)
            logger.error(f"Failed to initialize configuration: {e}")
            if self._cached_config:
                logger.warning("Using cached configuration as fallback")
                self.config_manager.config = self._cached_config
            else:
                # Use minimal base config as last resort
                base_config = self.config_loader.get_base_config()
                self.config_manager.config = base_config
                self._cached_config = base_config.copy()
                logger.warning("Using base configuration as fallback")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self.config_manager.get(key_path, default)
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value.
            value: Value to set.
            
        Returns:
            True if set successful, False otherwise.
        """
        success = self.config_manager.set(key_path, value)
        if success:
            logger.debug(f"Configuration updated: {key_path}")
        return success
    
    def reload(self) -> bool:
        """Reload configuration from file and plugins.

        Returns:
            True if reload successful, False otherwise.
        """
        try:
            complete_config = self.config_loader.load_complete_config()

            # Validate the new configuration
            old_config = self.config_manager.config
            self.config_manager.config = complete_config
            validation_result = self.validate_config()

            if validation_result["valid"]:
                # Success - update cache and clear error
                self._cached_config = complete_config.copy()
                self._config_error = None
                logger.info("Configuration reloaded successfully")
                self._notify_reload_callbacks()
                return True
            else:
                # Validation failed - revert to cached config
                self.config_manager.config = old_config
                error_msg = f"Invalid configuration: {validation_result['errors']}"
                self._config_error = error_msg
                logger.error(error_msg)
                return False

        except Exception as e:
            error_msg = f"Failed to reload configuration: {e}"
            self._config_error = error_msg
            logger.error(error_msg)

            # Fallback to cached config if available
            if self._cached_config:
                logger.warning("Using cached configuration as fallback")
                self.config_manager.config = self._cached_config

            return False
    
    def update_from_plugins(self) -> bool:
        """Update configuration with newly discovered plugins.
        
        Returns:
            True if update successful, False otherwise.
        """
        return self.config_loader.update_with_plugins()
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration.
        
        Returns:
            Dictionary with configuration metadata.
        """
        config = self.config_manager.config
        plugin_count = len(self.plugin_registry.list_plugins()) if self.plugin_registry else 0
        
        return {
            "config_file": str(self.config_manager.config_path),
            "file_exists": self.config_manager.config_path.exists(),
            "plugin_count": plugin_count,
            "config_sections": list(config.keys()) if config else [],
            "total_keys": self._count_keys(config),
        }
    
    def _count_keys(self, config: Dict[str, Any]) -> int:
        """Recursively count all keys in configuration."""
        count = 0
        for key, value in config.items():
            count += 1
            if isinstance(value, dict):
                count += self._count_keys(value)
        return count
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate current configuration structure.
        
        Returns:
            Dictionary with validation results.
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        config = self.config_manager.config
        
        # Check for required sections
        required_sections = ["terminal", "input", "logging", "application"]
        for section in required_sections:
            if section not in config:
                validation_result["errors"].append(f"Missing required section: {section}")
                validation_result["valid"] = False
        
        # Check for required terminal settings
        if "terminal" in config:
            required_terminal_keys = ["render_fps", "thinking_effect"]
            for key in required_terminal_keys:
                if key not in config["terminal"]:
                    validation_result["warnings"].append(f"Missing terminal.{key}, using default")
        
        # Check for valid FPS value
        fps = self.get("terminal.render_fps")
        if fps is not None and (not isinstance(fps, int) or fps <= 0 or fps > 120):
            validation_result["warnings"].append(f"Invalid render_fps: {fps}, should be 1-120")
        
        logger.debug(f"Configuration validation: {validation_result}")
        return validation_result
    
    def backup_config(self, backup_suffix: str = ".backup") -> Optional[Path]:
        """Create a backup of the current configuration file.
        
        Args:
            backup_suffix: Suffix to add to backup filename.
            
        Returns:
            Path to backup file if successful, None otherwise.
        """
        if not self.config_manager.config_path.exists():
            logger.warning("Cannot backup non-existent config file")
            return None
        
        try:
            backup_path = self.config_manager.config_path.with_suffix(
                self.config_manager.config_path.suffix + backup_suffix
            )
            
            import shutil
            shutil.copy2(self.config_manager.config_path, backup_path)
            
            logger.info(f"Configuration backed up to: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to backup configuration: {e}")
            return None
    
    def restore_from_backup(self, backup_path: Path) -> bool:
        """Restore configuration from a backup file.
        
        Args:
            backup_path: Path to backup file.
            
        Returns:
            True if restore successful, False otherwise.
        """
        if not backup_path.exists():
            logger.error(f"Backup file does not exist: {backup_path}")
            return False
        
        try:
            import shutil
            shutil.copy2(backup_path, self.config_manager.config_path)
            
            # Reload configuration after restore
            return self.reload()
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

    def _start_file_watching(self) -> None:
        """Start watching the configuration file for changes."""
        if not WATCHDOG_AVAILABLE:
            logger.debug("Watchdog not available, file watching disabled")
            return

        # Prevent duplicate watchers
        if self._observer is not None:
            logger.debug("File watcher already running, skipping initialization")
            return

        try:
            self._file_watcher = ConfigFileWatcher(self)
            self._observer = Observer()
            self._observer.schedule(
                self._file_watcher,
                str(self.config_manager.config_path.parent),
                recursive=False
            )
            self._observer.start()
            logger.debug("Configuration file watcher started")
        except RuntimeError as e:
            if "already scheduled" in str(e):
                logger.debug("File watcher path already being watched by another instance")
            else:
                logger.warning(f"Could not start configuration file watcher: {e}")
        except Exception as e:
            logger.warning(f"Could not start configuration file watcher: {e}")

    def _stop_file_watching(self) -> None:
        """Stop watching the configuration file."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
            self._file_watcher = None
            logger.debug("Configuration file watcher stopped")

    async def _handle_file_change(self) -> None:
        """Handle configuration file changes with hot reload."""
        success = self.reload()
        if not success:
            logger.warning("Configuration reload failed, using cached fallback")

    def register_reload_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to be notified when configuration reloads.

        Args:
            callback: Function to call after successful configuration reload.
        """
        self._reload_callbacks.append(callback)

    def _notify_reload_callbacks(self) -> None:
        """Notify all registered callbacks about configuration reload."""
        for callback in self._reload_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Config reload callback failed: {e}")

    def get_config_error(self) -> Optional[str]:
        """Get the current configuration error, if any.

        Returns:
            Error message string if there's a config error, None otherwise.
        """
        return self._config_error

    def has_config_error(self) -> bool:
        """Check if there's a current configuration error.

        Returns:
            True if there's an error, False otherwise.
        """
        return self._config_error is not None

    def shutdown(self) -> None:
        """Shutdown the configuration service and file watcher."""
        self._stop_file_watching()
        logger.info("Configuration service shutdown")