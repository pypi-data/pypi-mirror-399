"""
LLM Profile Manager.

Manages named LLM configuration profiles that define:
- API endpoint URL
- Model name
- Temperature and other parameters
- Tool calling format (OpenAI vs Anthropic)
- API token environment variable

Profiles can be defined in config.json under core.llm.profiles
or use built-in defaults.
"""

import json
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from .api_adapters import BaseAPIAdapter, OpenAIAdapter, AnthropicAdapter

logger = logging.getLogger(__name__)


@dataclass
class LLMProfile:
    """
    Configuration profile for LLM settings.

    Attributes:
        name: Profile identifier
        api_url: Base URL for the LLM API
        model: Model name/identifier
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate (None = no limit)
        api_token_env: Environment variable name containing API token
        tool_format: Tool calling format ("openai" or "anthropic")
        timeout: Request timeout in milliseconds (0 = no timeout)
        description: Human-readable description
        extra_headers: Additional HTTP headers to include
    """

    name: str
    api_url: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    api_token_env: str = ""
    tool_format: str = "openai"
    timeout: int = 0
    description: str = ""
    extra_headers: Dict[str, str] = field(default_factory=dict)

    def get_api_token(self) -> Optional[str]:
        """
        Get API token from environment variable.

        Returns:
            API token string or None if not set
        """
        if not self.api_token_env:
            return None
        return os.environ.get(self.api_token_env)

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary representation."""
        return {
            "name": self.name,
            "api_url": self.api_url,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_token_env": self.api_token_env,
            "tool_format": self.tool_format,
            "timeout": self.timeout,
            "description": self.description,
            "extra_headers": self.extra_headers,
        }

    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "LLMProfile":
        """
        Create profile from dictionary.

        Args:
            name: Profile name
            data: Profile configuration dictionary

        Returns:
            LLMProfile instance
        """
        return cls(
            name=name,
            api_url=data.get("api_url", "http://localhost:1234"),
            model=data.get("model", "default"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens"),
            api_token_env=data.get("api_token_env", ""),
            tool_format=data.get("tool_format", "openai"),
            timeout=data.get("timeout", 0),
            description=data.get("description", ""),
            extra_headers=data.get("extra_headers", {}),
        )


class ProfileManager:
    """
    Manages LLM configuration profiles.

    Features:
    - Built-in default profiles (default, fast, claude, openai)
    - User-defined profiles from config.json
    - Active profile switching
    - Adapter instantiation for profiles
    """

    # Built-in default profiles
    DEFAULT_PROFILES: Dict[str, Dict[str, Any]] = {
        "default": {
            "api_url": "http://localhost:1234",
            "model": "qwen/qwen3-4b",
            "temperature": 0.7,
            "tool_format": "openai",
            "description": "Local LLM for general use",
        },
        "fast": {
            "api_url": "http://localhost:1234",
            "model": "qwen/qwen3-0.6b",
            "temperature": 0.3,
            "tool_format": "openai",
            "description": "Fast local model for quick queries",
        },
        "claude": {
            "api_url": "https://api.anthropic.com",
            "model": "claude-sonnet-4-20250514",
            "temperature": 0.7,
            "max_tokens": 4096,
            "api_token_env": "ANTHROPIC_API_KEY",
            "tool_format": "anthropic",
            "description": "Anthropic Claude for complex tasks",
        },
        "openai": {
            "api_url": "https://api.openai.com",
            "model": "gpt-4-turbo",
            "temperature": 0.7,
            "max_tokens": 4096,
            "api_token_env": "OPENAI_API_KEY",
            "tool_format": "openai",
            "description": "OpenAI GPT-4 for general tasks",
        },
    }

    def __init__(self, config=None):
        """
        Initialize profile manager.

        Args:
            config: Configuration object with get() method
        """
        self.config = config
        self._profiles: Dict[str, LLMProfile] = {}
        self._active_profile_name: str = "default"
        self._load_profiles()

    def _load_profiles(self) -> None:
        """Load profiles from defaults and config."""
        # Start with built-in defaults
        for name, data in self.DEFAULT_PROFILES.items():
            self._profiles[name] = LLMProfile.from_dict(name, data)

        # Load user-defined profiles from config
        if self.config:
            user_profiles = self.config.get("core.llm.profiles", {})
            if isinstance(user_profiles, dict):
                for name, data in user_profiles.items():
                    if isinstance(data, dict):
                        self._profiles[name] = LLMProfile.from_dict(name, data)
                        logger.debug(f"Loaded user profile: {name}")

            # Get default profile from config
            default_profile = self.config.get("core.llm.default_profile", "default")
            if default_profile in self._profiles:
                self._active_profile_name = default_profile

        logger.info(
            f"Loaded {len(self._profiles)} profiles, active: {self._active_profile_name}"
        )

    def get_profile(self, name: str) -> Optional[LLMProfile]:
        """
        Get a profile by name.

        Args:
            name: Profile name

        Returns:
            LLMProfile or None if not found
        """
        return self._profiles.get(name)

    def get_active_profile(self) -> LLMProfile:
        """
        Get the currently active profile.

        Returns:
            Active LLMProfile (falls back to "default" if needed)
        """
        profile = self._profiles.get(self._active_profile_name)
        if not profile:
            logger.warning(
                f"Active profile '{self._active_profile_name}' not found, "
                "falling back to 'default'"
            )
            profile = self._profiles.get("default")
            if not profile:
                # Create minimal default profile
                profile = LLMProfile(
                    name="default",
                    api_url="http://localhost:1234",
                    model="default",
                )
        return profile

    def set_active_profile(self, name: str) -> bool:
        """
        Set the active profile.

        Args:
            name: Profile name to activate

        Returns:
            True if successful, False if profile not found
        """
        if name not in self._profiles:
            logger.error(f"Profile not found: {name}")
            return False

        old_profile = self._active_profile_name
        self._active_profile_name = name
        logger.info(f"Switched profile: {old_profile} -> {name}")
        return True

    def list_profiles(self) -> List[LLMProfile]:
        """
        List all available profiles.

        Returns:
            List of LLMProfile instances
        """
        return list(self._profiles.values())

    def get_profile_names(self) -> List[str]:
        """
        Get list of profile names.

        Returns:
            List of profile name strings
        """
        return list(self._profiles.keys())

    def add_profile(self, profile: LLMProfile) -> bool:
        """
        Add a new profile.

        Args:
            profile: LLMProfile to add

        Returns:
            True if added, False if name already exists
        """
        if profile.name in self._profiles:
            logger.warning(f"Profile already exists: {profile.name}")
            return False

        self._profiles[profile.name] = profile
        logger.info(f"Added profile: {profile.name}")
        return True

    def remove_profile(self, name: str) -> bool:
        """
        Remove a profile.

        Cannot remove built-in profiles or the current active profile.

        Args:
            name: Profile name to remove

        Returns:
            True if removed, False if protected or not found
        """
        if name in self.DEFAULT_PROFILES:
            logger.error(f"Cannot remove built-in profile: {name}")
            return False

        if name == self._active_profile_name:
            logger.error(f"Cannot remove active profile: {name}")
            return False

        if name not in self._profiles:
            logger.error(f"Profile not found: {name}")
            return False

        del self._profiles[name]
        logger.info(f"Removed profile: {name}")
        return True

    def get_adapter_for_profile(
        self, profile: Optional[LLMProfile] = None
    ) -> BaseAPIAdapter:
        """
        Get the appropriate API adapter for a profile.

        Args:
            profile: Profile to get adapter for (default: active profile)

        Returns:
            Configured API adapter instance
        """
        if profile is None:
            profile = self.get_active_profile()

        if profile.tool_format == "anthropic":
            return AnthropicAdapter(base_url=profile.api_url)
        else:
            return OpenAIAdapter(base_url=profile.api_url)

    def get_active_adapter(self) -> BaseAPIAdapter:
        """
        Get adapter for the active profile.

        Returns:
            Configured API adapter instance
        """
        return self.get_adapter_for_profile(self.get_active_profile())

    def is_active(self, name: str) -> bool:
        """
        Check if a profile is the active one.

        Args:
            name: Profile name

        Returns:
            True if this is the active profile
        """
        return name == self._active_profile_name

    @property
    def active_profile_name(self) -> str:
        """Get the name of the active profile."""
        return self._active_profile_name

    def get_profile_summary(self, name: Optional[str] = None) -> str:
        """
        Get a human-readable summary of a profile.

        Args:
            name: Profile name (default: active profile)

        Returns:
            Formatted summary string
        """
        profile = self._profiles.get(name) if name else self.get_active_profile()
        if not profile:
            return f"Profile '{name}' not found"

        lines = [
            f"Profile: {profile.name}",
            f"  API URL: {profile.api_url}",
            f"  Model: {profile.model}",
            f"  Temperature: {profile.temperature}",
            f"  Tool Format: {profile.tool_format}",
        ]
        if profile.description:
            lines.append(f"  Description: {profile.description}")
        if profile.max_tokens:
            lines.append(f"  Max Tokens: {profile.max_tokens}")
        if profile.api_token_env:
            token_set = "set" if profile.get_api_token() else "not set"
            lines.append(f"  API Token: ${profile.api_token_env} ({token_set})")

        return "\n".join(lines)

    def create_profile(
        self,
        name: str,
        api_url: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_token_env: str = "",
        tool_format: str = "openai",
        timeout: int = 0,
        description: str = "",
        save_to_config: bool = True,
    ) -> Optional[LLMProfile]:
        """
        Create a new profile and optionally save to config.

        Args:
            name: Profile name
            api_url: API endpoint URL
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Max tokens (None for unlimited)
            api_token_env: Environment variable for API token
            tool_format: Tool calling format (openai/anthropic)
            timeout: Request timeout
            description: Human-readable description
            save_to_config: Whether to persist to config.json

        Returns:
            Created LLMProfile or None on failure
        """
        if name in self._profiles:
            logger.warning(f"Profile already exists: {name}")
            return None

        profile = LLMProfile(
            name=name,
            api_url=api_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_token_env=api_token_env,
            tool_format=tool_format,
            timeout=timeout,
            description=description,
        )

        self._profiles[name] = profile
        logger.info(f"Created profile: {name}")

        if save_to_config:
            self._save_profile_to_config(profile)

        return profile

    def _save_profile_to_config(self, profile: LLMProfile) -> bool:
        """
        Save a profile to config.json.

        Args:
            profile: Profile to save

        Returns:
            True if saved successfully
        """
        try:
            # Find config file
            local_config = Path.cwd() / ".kollabor-cli" / "config.json"
            global_config = Path.home() / ".kollabor-cli" / "config.json"

            config_path = local_config if local_config.exists() else global_config

            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return False

            # Load current config
            config_data = json.loads(config_path.read_text(encoding="utf-8"))

            # Ensure core.llm.profiles exists
            if "core" not in config_data:
                config_data["core"] = {}
            if "llm" not in config_data["core"]:
                config_data["core"]["llm"] = {}
            if "profiles" not in config_data["core"]["llm"]:
                config_data["core"]["llm"]["profiles"] = {}

            # Add profile (without name field, as it's the key)
            profile_data = profile.to_dict()
            del profile_data["name"]  # Name is the key
            config_data["core"]["llm"]["profiles"][profile.name] = profile_data

            # Write back
            config_path.write_text(
                json.dumps(config_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            logger.info(f"Saved profile to config: {profile.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to save profile to config: {e}")
            return False

    def reload(self) -> None:
        """Reload profiles from config file."""
        self._profiles.clear()
        self._load_profiles()
        logger.debug(f"Reloaded {len(self._profiles)} profiles")

    def migrate_current_config(self, profile_name: str = "current") -> Optional[LLMProfile]:
        """
        Migrate current LLM config to a named profile.

        Reads api_url, model, temperature, etc. from core.llm
        and creates a new profile with those settings.

        Args:
            profile_name: Name for the new profile

        Returns:
            Created LLMProfile or None on failure
        """
        if not self.config:
            logger.error("No config available for migration")
            return None

        try:
            api_url = self.config.get("core.llm.api_url", "http://localhost:1234")
            model = self.config.get("core.llm.model", "default")
            temperature = self.config.get("core.llm.temperature", 0.7)
            timeout = self.config.get("core.llm.timeout", 0)

            # Check if api_token is directly in config (not env var)
            # In this case, we might need to set it up differently
            api_token = self.config.get("core.llm.api_token", "")
            api_token_env = ""  # Will be set if user has env var

            # Determine tool format from URL
            tool_format = "openai"  # Default
            if "anthropic" in api_url.lower():
                tool_format = "anthropic"

            profile = self.create_profile(
                name=profile_name,
                api_url=api_url,
                model=model,
                temperature=temperature,
                timeout=timeout,
                api_token_env=api_token_env,
                tool_format=tool_format,
                description=f"Migrated from config ({model})",
                save_to_config=True,
            )

            if profile:
                logger.info(f"Migrated current config to profile: {profile_name}")

            return profile

        except Exception as e:
            logger.error(f"Failed to migrate config: {e}")
            return None

    def update_profile(
        self,
        original_name: str,
        new_name: str = None,
        api_url: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: Optional[int] = None,
        api_token_env: str = None,
        tool_format: str = None,
        timeout: int = None,
        description: str = None,
        save_to_config: bool = True,
    ) -> bool:
        """
        Update an existing profile.

        Args:
            original_name: Current name of the profile to update
            new_name: New name for the profile (optional, for renaming)
            api_url: New API endpoint URL
            model: New model identifier
            temperature: New sampling temperature
            max_tokens: New max tokens
            api_token_env: New environment variable for API token
            tool_format: New tool calling format
            timeout: New request timeout
            description: New description
            save_to_config: Whether to persist to config.json

        Returns:
            True if updated successfully, False otherwise
        """
        if original_name not in self._profiles:
            logger.error(f"Profile not found: {original_name}")
            return False

        profile = self._profiles[original_name]
        target_name = new_name or original_name

        # Check for name collision if renaming
        if new_name and new_name != original_name and new_name in self._profiles:
            logger.error(f"Profile name already exists: {new_name}")
            return False

        # Update profile fields
        if api_url is not None:
            profile.api_url = api_url
        if model is not None:
            profile.model = model
        if temperature is not None:
            profile.temperature = temperature
        if max_tokens is not None:
            profile.max_tokens = max_tokens
        if api_token_env is not None:
            profile.api_token_env = api_token_env
        if tool_format is not None:
            profile.tool_format = tool_format
        if timeout is not None:
            profile.timeout = timeout
        if description is not None:
            profile.description = description

        # Handle renaming
        if new_name and new_name != original_name:
            profile.name = new_name
            del self._profiles[original_name]
            self._profiles[new_name] = profile

            # Update active profile name if this was the active one
            if self._active_profile_name == original_name:
                self._active_profile_name = new_name

            logger.info(f"Renamed profile: {original_name} -> {new_name}")

        logger.info(f"Updated profile: {target_name}")

        if save_to_config:
            self._update_profile_in_config(original_name, profile)

        return True

    def _update_profile_in_config(self, original_name: str, profile: LLMProfile) -> bool:
        """
        Update a profile in config.json.

        Args:
            original_name: Original profile name (for removal if renamed)
            profile: Updated profile to save

        Returns:
            True if saved successfully
        """
        try:
            # Find config file
            local_config = Path.cwd() / ".kollabor-cli" / "config.json"
            global_config = Path.home() / ".kollabor-cli" / "config.json"

            config_path = local_config if local_config.exists() else global_config

            if not config_path.exists():
                logger.error(f"Config file not found: {config_path}")
                return False

            # Load current config
            config_data = json.loads(config_path.read_text(encoding="utf-8"))

            # Ensure core.llm.profiles exists
            if "core" not in config_data:
                config_data["core"] = {}
            if "llm" not in config_data["core"]:
                config_data["core"]["llm"] = {}
            if "profiles" not in config_data["core"]["llm"]:
                config_data["core"]["llm"]["profiles"] = {}

            # Remove old profile if it was renamed
            if original_name != profile.name and original_name in config_data["core"]["llm"]["profiles"]:
                del config_data["core"]["llm"]["profiles"][original_name]

            # Add/update profile (without name field, as it's the key)
            profile_data = profile.to_dict()
            del profile_data["name"]  # Name is the key
            config_data["core"]["llm"]["profiles"][profile.name] = profile_data

            # Write back
            config_path.write_text(
                json.dumps(config_data, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            logger.info(f"Updated profile in config: {profile.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to update profile in config: {e}")
            return False
