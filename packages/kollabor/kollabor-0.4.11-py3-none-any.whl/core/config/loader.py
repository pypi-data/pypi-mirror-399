"""Configuration loading and plugin integration logic."""

import logging
from pathlib import Path
from typing import Any, Dict, List
from importlib.metadata import version as get_version, PackageNotFoundError

from ..utils import deep_merge
from ..utils.error_utils import safe_execute, log_and_continue
from ..utils.config_utils import get_system_prompt_content
from ..utils.prompt_renderer import render_system_prompt
from .manager import ConfigManager
from .plugin_config_manager import PluginConfigManager

def _get_version_from_pyproject() -> str:
    """Read version from pyproject.toml for development mode."""
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            for line in content.splitlines():
                if line.startswith("version ="):
                    # Extract version from: version = "0.4.10"
                    return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return None  # Return None if not found

def _is_running_from_source() -> bool:
    """Check if we're running from source (development mode) vs installed package."""
    try:
        # If pyproject.toml exists in parent directory, we're running from source
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        return pyproject_path.exists()
    except Exception:
        return False

# Get version: prefer pyproject.toml when running from source, otherwise use installed version
if _is_running_from_source():
    # Development mode: use pyproject.toml
    _package_version = _get_version_from_pyproject() or "0.0.0"
else:
    # Production mode: use installed package version
    try:
        _package_version = get_version("kollabor")
    except PackageNotFoundError:
        _package_version = "0.0.0"

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Handles complex configuration loading with plugin integration.
    
    This class manages the coordination between file-based configuration
    and plugin-provided configurations, implementing the complex merging
    logic that was previously in ConfigManager.
    """
    
    def __init__(self, config_manager: ConfigManager, plugin_registry=None):
        """Initialize the config loader.
        
        Args:
            config_manager: Basic config manager for file operations.
            plugin_registry: Optional plugin registry for plugin configs.
        """
        self.config_manager = config_manager
        self.plugin_registry = plugin_registry
        self.plugin_config_manager = None
        
        # Initialize plugin config manager if registry is available
        if plugin_registry and hasattr(plugin_registry, 'discovery'):
            self.plugin_config_manager = PluginConfigManager(plugin_registry.discovery)
            logger.debug("PluginConfigManager initialized")
        
        logger.debug("ConfigLoader initialized")
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from env vars or file and render dynamic content.

        Processes <trender>command</trender> tags by executing commands
        and replacing tags with their output.

        Priority:
        1. KOLLABOR_SYSTEM_PROMPT environment variable (direct string)
        2. KOLLABOR_SYSTEM_PROMPT_FILE environment variable (custom file path)
        3. Local/global system_prompt/default.md files
        4. Fallback default

        Returns:
            System prompt content with rendered commands or fallback message.
        """
        try:
            # Use the new unified function that checks env vars and files
            content = get_system_prompt_content()

            # Render dynamic <trender> tags
            rendered_content = render_system_prompt(content, timeout=5)

            return rendered_content
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return "You are Kollabor, an intelligent coding assistant."

    def get_base_config(self) -> Dict[str, Any]:
        """Get the base application configuration with defaults.

        Returns:
            Base configuration dictionary with application defaults.
        """
        # Load system prompt from file
        system_prompt = self._load_system_prompt()

        return {
            "terminal": {
                "render_fps": 20,
                "spinner_frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧"],
                "status_lines": 4,
                "thinking_message_limit": 25,
                "thinking_effect": "shimmer",
                "shimmer_speed": 3,
                "shimmer_wave_width": 4,
                "render_error_delay": 0.1,
                "render_cache_enabled": True
            },
            "input": {
                "ctrl_c_exit": True,
                "backspace_enabled": True,
                "input_buffer_limit": 100000,
                "polling_delay": 0.01,
                "error_delay": 0.1,
                "history_limit": 100,
                "error_threshold": 10,
                "error_window_minutes": 5,
                "max_errors": 100,
                "paste_detection_enabled": True,
                "paste_threshold_ms": 50,
                "paste_min_chars": 3,
                "paste_max_chars": 10000,
                "bracketed_paste_enabled": True
            },
            "logging": {
                "level": "INFO",
                "file": ".kollabor-cli/logs/kollabor.log",
                "format_type": "compact",
                "format": "%(asctime)s - %(levelname)-4s - %(message)-100s - %(filename)s:%(lineno)04d"
            },
            "hooks": {
                "default_timeout": 30,
                "default_retries": 3,
                "default_error_action": "continue"
            },
            "application": {
                "name": "Kollabor CLI",
                "version": _package_version,
                "description": "AI Edition"
            },
            "core": {
                "llm": {
                    "api_url": "http://localhost:1234",
                    "api_token": "",
                    "model": "qwen/qwen3-4b",
                    "temperature": 0.7,
                    "timeout": 0,
                    "max_history": 90,
                    "save_conversations": True,
                    "conversation_format": "jsonl",
                    "show_status": True,
                    "http_connector_limit": 10,
                    "message_history_limit": 20,
                    "thinking_phase_delay": 0.5,
                    "log_message_truncate": 50,
                    "enable_streaming": False,
                    "processing_delay": 0.1,
                    "thinking_delay": 0.3,
                    "api_poll_delay": 0.01,
                    "terminal_timeout": 30,
                    "mcp_timeout": 60,
                    "system_prompt": {
                        "base_prompt": system_prompt,
                        "include_project_structure": True,
                        "attachment_files": [],
                        "custom_prompt_files": []
                    },
                    "task_management": {
                        "background_tasks": {
                            "max_concurrent": 10000,
                            "default_timeout": 0,
                            "cleanup_interval": 60,
                            "enable_monitoring": True,
                            "log_task_events": True,
                            "log_task_errors": True,
                            "enable_metrics": True,
                            "task_retry_attempts": 0,
                            "task_retry_delay": 1.0,
                            "enable_task_circuit_breaker": False,
                            "circuit_breaker_threshold": 5,
                            "circuit_breaker_timeout": 60.0
                        },
                        "queue": {
                            "max_size": 1000,
                            "overflow_strategy": "drop_oldest",
                            "block_timeout": 1.0,
                            "enable_queue_metrics": True,
                            "log_queue_events": True
                        }
                    }
                }
            },
            "performance": {
                "failure_rate_warning": 0.05,
                "failure_rate_critical": 0.15,
                "degradation_threshold": 0.15
            },
            "plugins": {
                "enhanced_input": {
                    "enabled": True,
                    "style": "rounded",
                    "width": "auto",
                    "placeholder": "Type your message here...",
                    "show_placeholder": True,
                    "min_width": 60,
                    "max_width": 120,
                    "randomize_style": False,
                    "randomize_interval": 5.0,
                    "dynamic_sizing": True,
                    "min_height": 3,
                    "max_height": 10,
                    "wrap_text": True,
                    "colors": {
                        "border": "cyan",
                        "text": "white",
                        "placeholder": "dim",
                        "gradient_mode": True,
                        "gradient_colors": [
                            "#333333",
                            "#999999",
                            "#222222"
                        ],
                        "border_gradient": True,
                        "text_gradient": True
                    },
                    "cursor_blink_rate": 0.5,
                    "show_status": True
                },
                "system_commands": {
                    "enabled": True
                },
                "hook_monitoring": {
                    "enabled": False,
                    "debug_logging": True,
                    "show_status": True,
                    "hook_timeout": 5,
                    "log_all_events": True,
                    "log_event_data": False,
                    "log_performance": True,
                    "log_failures_only": False,
                    "performance_threshold_ms": 100,
                    "max_error_log_size": 50,
                    "enable_plugin_discovery": True,
                    "discovery_interval": 30,
                    "auto_analyze_capabilities": True,
                    "enable_service_registration": True,
                    "register_performance_service": True,
                    "register_health_service": True,
                    "register_metrics_service": True,
                    "enable_cross_plugin_communication": True,
                    "message_history_limit": 20,
                    "auto_respond_to_health_checks": True,
                    "health_check_interval": 30,
                    "memory_threshold_mb": 50,
                    "performance_degradation_threshold": 0.15,
                    "collect_plugin_metrics": True,
                    "metrics_retention_hours": 24,
                    "detailed_performance_tracking": True,
                    "enable_health_dashboard": True,
                    "dashboard_update_interval": 10,
                    "show_plugin_interactions": True,
                    "show_service_usage": True
                },
                "query_enhancer": {
                    "enabled": False,
                    "show_status": True,
                    "fast_model": {
                        "api_url": "http://localhost:1234",
                        "model": "qwen3-0.6b",
                        "temperature": 0.3,
                        "timeout": 5
                    },
                    "enhancement_prompt": "You are a query enhancement specialist. Your job is to improve user queries to get better responses from AI assistants.\n\nTake this user query and enhance it by:\n1. Making it more specific and detailed\n2. Adding relevant context\n3. Clarifying any ambiguity\n4. Keeping the original intent\n\nReturn ONLY the enhanced query, nothing else.\n\nOriginal query: {query}\n\nEnhanced query:",
                    "max_length": 500,
                    "min_query_length": 10,
                    "skip_enhancement_keywords": [
                        "hi",
                        "hello",
                        "thanks",
                        "thank you",
                        "ok",
                        "okay",
                        "yes",
                        "no"
                    ],
                    "performance_tracking": True
                },
                "workflow_enforcement": {
                    "enabled": False
                },
                "fullscreen": {
                    "enabled": False
                }
            },
            "workflow_enforcement": {
                "enabled": False,
                "require_tool_calls": True,
                "confirmation_timeout": 300,
                "bypass_keywords": [
                    "bypass",
                    "skip",
                    "blocked",
                    "issue",
                    "problem"
                ],
                "auto_start_workflows": True,
                "show_progress_in_status": True
            }
        }
    
    def get_plugin_configs(self) -> Dict[str, Any]:
        """Get merged configuration from all plugins.
        
        Returns:
            Merged plugin configurations or empty dict if no plugins.
        """
        if not self.plugin_registry:
            return {}
        
        # Discover plugin schemas first
        self.discover_plugin_schemas()
        
        def get_configs():
            return self.plugin_registry.get_merged_config()
        
        plugin_configs = safe_execute(
            get_configs,
            "getting plugin configurations",
            default={},
            logger_instance=logger
        )
        
        return plugin_configs if isinstance(plugin_configs, dict) else {}
    
    def discover_plugin_schemas(self) -> None:
        """Discover and register plugin configuration schemas."""
        if not self.plugin_config_manager:
            return
        
        def discover():
            self.plugin_config_manager.discover_plugin_schemas()
        
        safe_execute(
            discover,
            "discovering plugin schemas",
            default=None,
            logger_instance=logger
        )
    
    def get_plugin_config_sections(self) -> List[Dict[str, Any]]:
        """Get UI sections for plugin configuration.
        
        Returns:
            List of section definitions for the configuration UI.
        """
        if not self.plugin_config_manager:
            return []
        
        def get_sections():
            return self.plugin_config_manager.get_plugin_config_sections()
        
        sections = safe_execute(
            get_sections,
            "getting plugin config sections",
            default=[],
            logger_instance=logger
        )
        
        return sections if isinstance(sections, list) else []
    
    def get_plugin_widget_definitions(self) -> List[Dict[str, Any]]:
        """Get widget definitions for all plugin configurations.
        
        Returns:
            List of widget definition dictionaries.
        """
        if not self.plugin_config_manager:
            return []
        
        def get_widgets():
            return self.plugin_config_manager.get_widget_definitions()
        
        widgets = safe_execute(
            get_widgets,
            "getting plugin widget definitions",
            default=[],
            logger_instance=logger
        )
        
        return widgets if isinstance(widgets, list) else []
    
    def load_complete_config(self) -> Dict[str, Any]:
        """Load complete configuration including plugins.

        This is the main entry point for getting a fully merged configuration
        that includes base defaults, plugin configs, and user overrides.

        Priority order for user config:
        1. Local config (.kollabor-cli/config.json in current directory)
        2. Global config (~/.kollabor-cli/config.json in home directory)
        3. Base defaults (if neither exists)

        Returns:
            Complete merged configuration dictionary.
        """
        # Start with base application configuration
        base_config = self.get_base_config()

        # Add plugin configurations
        plugin_configs = self.get_plugin_configs()
        if plugin_configs:
            base_config = deep_merge(base_config, plugin_configs)
            logger.debug(f"Merged configurations from plugins")

        # Load user configuration with fallback to global
        user_config = self._load_user_config_with_fallback()
        if user_config:
            # User config takes precedence over defaults and plugins
            base_config = deep_merge(base_config, user_config)
            logger.debug("Merged user configuration")

        return base_config

    def _load_user_config_with_fallback(self) -> Dict[str, Any]:
        """Load user configuration, falling back to global config if local doesn't exist.

        Priority order:
        1. Local config (current directory's .kollabor-cli/config.json)
        2. Global config (~/.kollabor-cli/config.json)

        Returns:
            User configuration dictionary, or empty dict if none found.
        """
        # Check if local config exists
        if self.config_manager.config_path.exists():
            user_config = self.config_manager.load_config_file()
            if user_config:
                logger.debug(f"Loaded local config from: {self.config_manager.config_path}")
                return user_config

        # Fall back to global config
        global_config_path = Path.home() / ".kollabor-cli" / "config.json"
        if global_config_path.exists():
            try:
                import json
                with open(global_config_path, 'r') as f:
                    global_config = json.load(f)
                if global_config:
                    logger.info(f"Using global config as fallback from: {global_config_path}")
                    return global_config
            except Exception as e:
                logger.warning(f"Failed to load global config: {e}")

        logger.debug("No user configuration found (local or global)")
        return {}
    
    def save_merged_config(self, config: Dict[str, Any]) -> bool:
        """Save the complete merged configuration to file.

        Note: base_prompt is excluded from saving because it should always
        be dynamically loaded from the system_prompt/*.md files on startup.

        Args:
            config: Configuration dictionary to save.

        Returns:
            True if save successful, False otherwise.
        """
        import copy
        config_to_save = copy.deepcopy(config)

        # Remove base_prompt - it should always be loaded fresh from .md files
        try:
            if "core" in config_to_save and "llm" in config_to_save["core"]:
                if "system_prompt" in config_to_save["core"]["llm"]:
                    config_to_save["core"]["llm"]["system_prompt"].pop("base_prompt", None)
        except (KeyError, TypeError):
            pass  # Config structure doesn't match expected format

        return self.config_manager.save_config_file(config_to_save)
    
    def update_with_plugins(self) -> bool:
        """Update the configuration file with newly discovered plugins.
        
        This method reloads the complete configuration including any new
        plugin configurations and saves it to the config file.
        
        Returns:
            True if update successful, False otherwise.
        """
        if not self.plugin_registry:
            logger.warning("No plugin registry available for config update")
            return False
        
        try:
            # Load complete config including plugins
            updated_config = self.load_complete_config()
            
            # Save the updated configuration
            success = self.save_merged_config(updated_config)
            
            if success:
                # Update the config manager's in-memory config
                self.config_manager.config = updated_config
                plugin_count = len(self.plugin_registry.list_plugins())
                logger.info(f"Updated config with configurations from {plugin_count} plugins")
            
            return success
            
        except Exception as e:
            log_and_continue(logger, "updating config with plugins", e)
            return False