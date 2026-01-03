"""Configuration management system for Kollabor CLI."""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from ..utils import deep_merge, safe_get, safe_set
from ..utils.error_utils import safe_execute, log_and_continue

logger = logging.getLogger(__name__)


class ConfigManager:
    """Configuration management system.
    
    Handles loading and saving JSON configuration files with defaults.
    """
    
    def __init__(self, config_path: Path) -> None:
        """Initialize the config manager.
        
        Args:
            config_path: Path to the config JSON file.
        """
        self.config_path = config_path
        self.config = {}
        logger.info(f"Config manager initialized: {config_path}")
    
    def load_config_file(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary from file, or empty dict if load fails.
        """
        if not self.config_path.exists():
            logger.debug(f"Config file does not exist: {self.config_path}")
            return {}
        
        def load_json():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        config = safe_execute(
            load_json,
            f"loading config from {self.config_path}",
            default={},
            logger_instance=logger
        )
        
        if config:
            logger.info("Loaded configuration from file")
        
        return config
    
    def save_config_file(self, config: Dict[str, Any]) -> bool:
        """Save configuration to file.
        
        Args:
            config: Configuration dictionary to save.
            
        Returns:
            True if save successful, False otherwise.
        """
        def save_json():
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        
        success = safe_execute(
            save_json,
            f"saving config to {self.config_path}",
            default=False,
            logger_instance=logger
        )
        
        if success is not False:
            logger.debug("Configuration saved to file")
            return True
        return False
    
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value (e.g., "llm.api_url").
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return safe_get(self.config, key_path, default)
    
    def set(self, key_path: str, value: Any) -> bool:
        """Set a configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to the config value.
            value: Value to set.
            
        Returns:
            True if set and save successful, False otherwise.
        """
        if safe_set(self.config, key_path, value):
            success = self.save_config_file(self.config)
            if success:
                logger.debug(f"Set config: {key_path} = {value}")
                return True
        
        logger.error(f"Failed to set config key: {key_path}")
        return False
    
