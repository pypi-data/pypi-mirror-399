"""Core system commands for Kollabor CLI."""

import logging
from typing import Dict, Any, List
from datetime import datetime

from ..events.models import (
    CommandDefinition,
    CommandMode,
    CommandCategory,
    CommandResult,
    SlashCommand,
    UIConfig,
    EventType,
    Hook,
    Event,
)

logger = logging.getLogger(__name__)


class SystemCommandsPlugin:
    """Core system commands plugin.

    Provides essential system management commands like /help, /config, /status.
    These commands are automatically registered at application startup.
    """

    def __init__(
        self,
        command_registry,
        event_bus,
        config_manager,
        llm_service=None,
        profile_manager=None,
        agent_manager=None,
    ) -> None:
        """Initialize system commands plugin.

        Args:
            command_registry: Command registry for registration.
            event_bus: Event bus for system events.
            config_manager: Configuration manager for system settings.
            llm_service: LLM service for conversation management.
            profile_manager: LLM profile manager.
            agent_manager: Agent/skill manager.
        """
        self.name = "system"
        self.command_registry = command_registry
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.llm_service = llm_service
        self.profile_manager = profile_manager
        self.agent_manager = agent_manager
        self.logger = logger

    def register_commands(self) -> None:
        """Register all system commands."""
        try:
            # Register /help command
            help_command = CommandDefinition(
                name="help",
                description="Show available commands and usage",
                handler=self.handle_help,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.INSTANT,
                aliases=["h", "?"],
                icon="❓"
            )
            self.command_registry.register_command(help_command)

            # Register /config command
            config_command = CommandDefinition(
                name="config",
                description="Open system configuration panel",
                handler=self.handle_config,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["settings", "preferences"],
                icon="[INFO]",
                ui_config=UIConfig(
                    type="tree",
                    navigation=["↑↓←→", "Enter", "Esc"],
                    height=15,
                    title="System Configuration",
                    footer="↑↓←→ navigate • Enter edit • Esc exit"
                )
            )
            self.command_registry.register_command(config_command)

            # Register /status command
            status_command = CommandDefinition(
                name="status",
                description="Show system status and diagnostics",
                handler=self.handle_status,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["info", "diagnostics"],
                icon="[STATS]",
                ui_config=UIConfig(
                    type="table",
                    navigation=["↑↓", "Esc"],
                    height=12,
                    title="System Status",
                    footer="↑↓ navigate • Esc exit"
                )
            )
            self.command_registry.register_command(status_command)

            # Register /version command
            version_command = CommandDefinition(
                name="version",
                description="Show application version information",
                handler=self.handle_version,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.INSTANT,
                aliases=["v", "ver"],
                icon="[INFO]"
            )
            self.command_registry.register_command(version_command)

            # Register /resume command
            resume_command = CommandDefinition(
                name="resume",
                description="Resume a previous conversation session",
                handler=self.handle_resume,
                plugin_name=self.name,
                category=CommandCategory.CONVERSATION,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["restore", "continue"],
                icon="[RESUME]",
                ui_config=UIConfig(
                    type="modal",
                    width=80,
                    height=20,
                    title="Resume Conversation",
                    footer="↑↓ navigate • Enter select • Esc exit • /help resume"
                )
            )
            self.command_registry.register_command(resume_command)

            # Register /profile command
            profile_command = CommandDefinition(
                name="profile",
                description="Manage LLM API profiles",
                handler=self.handle_profile,
                plugin_name=self.name,
                category=CommandCategory.SYSTEM,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["prof", "llm"],
                icon="[PROF]",
                ui_config=UIConfig(
                    type="modal",
                    navigation=["↑↓", "Enter", "Esc"],
                    height=15,
                    title="LLM Profiles",
                    footer="↑↓ navigate • Enter select • Esc exit"
                )
            )
            self.command_registry.register_command(profile_command)

            # Register /agent command
            agent_command = CommandDefinition(
                name="agent",
                description="Manage agents and their configurations",
                handler=self.handle_agent,
                plugin_name=self.name,
                category=CommandCategory.AGENT,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["ag"],
                icon="[AGENT]",
                ui_config=UIConfig(
                    type="modal",
                    navigation=["↑↓", "Enter", "Esc"],
                    height=15,
                    title="Agents",
                    footer="↑↓ navigate • Enter select • Esc exit"
                )
            )
            self.command_registry.register_command(agent_command)

            # Register /skill command
            skill_command = CommandDefinition(
                name="skill",
                description="Load or unload agent skills",
                handler=self.handle_skill,
                plugin_name=self.name,
                category=CommandCategory.AGENT,
                mode=CommandMode.STATUS_TAKEOVER,
                aliases=["sk"],
                icon="[SKILL]",
                ui_config=UIConfig(
                    type="modal",
                    navigation=["↑↓", "Enter", "Esc"],
                    height=15,
                    title="Agent Skills",
                    footer="↑↓ navigate • Enter select • Esc exit"
                )
            )
            self.command_registry.register_command(skill_command)

            self.logger.info("System commands registered successfully")

        except Exception as e:
            self.logger.error(f"Error registering system commands: {e}")

    async def register_hooks(self) -> None:
        """Register event hooks for modal command handling."""
        try:
            hook = Hook(
                name="system_modal_command",
                plugin_name="system",
                event_type=EventType.MODAL_COMMAND_SELECTED,
                priority=10,
                callback=self._handle_modal_command
            )
            await self.event_bus.register_hook(hook)
            self.logger.info("System modal command hook registered")
        except Exception as e:
            self.logger.error(f"Error registering system hooks: {e}")

    async def _handle_modal_command(
        self, data: Dict[str, Any], event: Event
    ) -> Dict[str, Any]:
        """Handle modal command selection events for profile/agent/skill.

        Args:
            data: Event data containing command info.
            event: Event object.

        Returns:
            Modified data dict with display_messages key.
        """
        command = data.get("command", {})
        action = command.get("action")

        self.logger.info(f"System modal command received: action={action}")

        # Handle profile selection
        if action == "select_profile":
            profile_name = command.get("profile_name")
            if profile_name and self.profile_manager:
                if self.profile_manager.set_active_profile(profile_name):
                    profile = self.profile_manager.get_active_profile()
                    # Update the API service with new profile settings
                    if self.llm_service and hasattr(self.llm_service, 'api_service'):
                        self.llm_service.api_service.update_from_profile(
                            api_url=profile.api_url,
                            model=profile.model,
                            temperature=profile.temperature,
                            tool_format=profile.tool_format
                        )
                    data["display_messages"] = [
                        ("system", f"[ok] Switched to profile: {profile_name}\n  Model: {profile.model}\n  API: {profile.api_url}\n  Tool format: {profile.tool_format}", {}),
                    ]
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Profile not found: {profile_name}", {}),
                    ]

        # Handle agent selection
        elif action == "select_agent":
            agent_name = command.get("agent_name")
            if agent_name and self.agent_manager:
                if self.agent_manager.set_active_agent(agent_name):
                    # Rebuild system prompt for the new agent
                    if self.llm_service:
                        self.llm_service.rebuild_system_prompt()
                    agent = self.agent_manager.get_active_agent()
                    skills = agent.list_skills() if agent else []
                    skill_info = f" ({len(skills)} skills)" if skills else ""
                    msg = f"[ok] Switched to agent: {agent_name}{skill_info}"
                    if agent and agent.profile:
                        msg += f"\n  Preferred profile: {agent.profile}"
                    data["display_messages"] = [("system", msg, {})]
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Agent not found: {agent_name}", {}),
                    ]

        # Handle agent clear
        elif action == "clear_agent":
            if self.agent_manager:
                self.agent_manager.clear_active_agent()
                # Rebuild system prompt without agent
                if self.llm_service:
                    self.llm_service.rebuild_system_prompt()
                data["display_messages"] = [
                    ("system", "[ok] Cleared active agent", {}),
                ]

        # Handle skill load
        elif action == "load_skill":
            skill_name = command.get("skill_name")
            if skill_name and self.agent_manager:
                if self.agent_manager.load_skill(skill_name):
                    # Rebuild system prompt to include the skill
                    if self.llm_service:
                        self.llm_service.rebuild_system_prompt()
                    data["display_messages"] = [
                        ("system", f"[ok] Loaded skill: {skill_name}", {}),
                    ]
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Skill not found: {skill_name}", {}),
                    ]

        # Handle skill unload
        elif action == "unload_skill":
            skill_name = command.get("skill_name")
            if skill_name and self.agent_manager:
                if self.agent_manager.unload_skill(skill_name):
                    # Rebuild system prompt to remove the skill
                    if self.llm_service:
                        self.llm_service.rebuild_system_prompt()
                    data["display_messages"] = [
                        ("system", f"[ok] Unloaded skill: {skill_name}", {}),
                    ]
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Skill not loaded: {skill_name}", {}),
                    ]

        # Handle migrate profile
        elif action == "migrate_profile":
            if self.profile_manager:
                profile = self.profile_manager.migrate_current_config("glm")
                if profile:
                    data["display_messages"] = [
                        ("system", f"[ok] Migrated current config to profile: glm\n  API: {profile.api_url}\n  Model: {profile.model}\n  Saved to config.json", {}),
                    ]
                else:
                    data["display_messages"] = [
                        ("error", "[err] Failed to migrate. Profile 'glm' may already exist.", {}),
                    ]

        # Handle create profile - show form modal
        elif action == "create_profile_prompt":
            data["show_modal"] = self._get_create_profile_modal_definition()

        # Handle create profile form submission
        elif action == "create_profile_submit":
            form_data = command.get("form_data", {})
            name = form_data.get("name", "").strip()
            api_url = form_data.get("api_url", "").strip()
            model = form_data.get("model", "").strip()
            temperature = float(form_data.get("temperature", 0.7))
            tool_format = form_data.get("tool_format", "openai")
            description = form_data.get("description", "").strip()

            if not name or not api_url or not model:
                data["display_messages"] = [
                    ("error", "[err] Name, API URL, and Model are required", {}),
                ]
            elif self.profile_manager:
                profile = self.profile_manager.create_profile(
                    name=name,
                    api_url=api_url,
                    model=model,
                    temperature=temperature,
                    tool_format=tool_format,
                    description=description or f"Created via /profile",
                    save_to_config=True
                )
                if profile:
                    data["display_messages"] = [
                        ("system", f"[ok] Created profile: {name}\n  API: {api_url}\n  Model: {model}\n  Saved to config.json", {}),
                    ]
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Failed. Profile '{name}' may already exist.", {}),
                    ]

        # Handle create agent - show form modal
        elif action == "create_agent_prompt":
            data["show_modal"] = self._get_create_agent_modal_definition()

        # Handle create agent form submission
        elif action == "create_agent_submit":
            form_data = command.get("form_data", {})
            name = form_data.get("name", "").strip()
            description = form_data.get("description", "").strip()
            profile = form_data.get("profile", "").strip()
            system_prompt = form_data.get("system_prompt", "").strip()

            if not name:
                data["display_messages"] = [
                    ("error", "[err] Agent name is required", {}),
                ]
            elif self.agent_manager:
                agent = self.agent_manager.create_agent(
                    name=name,
                    description=description,
                    profile=profile if profile else None,
                    system_prompt=system_prompt,
                )
                if agent:
                    data["display_messages"] = [
                        ("system", f"[ok] Created agent: {name}\n  Directory: .kollabor-cli/agents/{name}/\n  System prompt created", {}),
                    ]
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Failed. Agent '{name}' may already exist.", {}),
                    ]

        # Handle edit profile - show form modal with profile data
        elif action == "edit_profile_prompt":
            profile_name = command.get("profile_name")
            if profile_name and self.profile_manager:
                modal_def = self._get_edit_profile_modal_definition(profile_name)
                if modal_def:
                    data["show_modal"] = modal_def
                else:
                    data["display_messages"] = [
                        ("error", f"[err] Profile not found: {profile_name}", {}),
                    ]
            else:
                data["display_messages"] = [
                    ("error", "[err] Select a profile to edit", {}),
                ]

        # Handle edit profile form submission
        elif action == "edit_profile_submit":
            form_data = command.get("form_data", {})
            original_name = command.get("edit_profile_name", "")
            new_name = form_data.get("name", "").strip()
            api_url = form_data.get("api_url", "").strip()
            model = form_data.get("model", "").strip()
            temperature = float(form_data.get("temperature", 0.7))
            tool_format = form_data.get("tool_format", "openai")
            api_token_env = form_data.get("api_token_env", "").strip()
            description = form_data.get("description", "").strip()

            if not new_name or not api_url or not model:
                data["display_messages"] = [
                    ("error", "[err] Name, API URL, and Model are required", {}),
                ]
            elif self.profile_manager:
                success = self.profile_manager.update_profile(
                    original_name=original_name,
                    new_name=new_name,
                    api_url=api_url,
                    model=model,
                    temperature=temperature,
                    tool_format=tool_format,
                    api_token_env=api_token_env,
                    description=description,
                    save_to_config=True
                )
                if success:
                    # If this profile is active (check both original and new name), update the API service
                    is_active = (self.profile_manager.is_active(new_name) or
                                self.profile_manager.is_active(original_name))
                    if is_active and self.llm_service and hasattr(self.llm_service, 'api_service'):
                        self.llm_service.api_service.update_from_profile(
                            api_url=api_url,
                            model=model,
                            temperature=temperature,
                            tool_format=tool_format
                        )
                    msg = f"[ok] Updated profile: {new_name}\n  API: {api_url}\n  Model: {model}\n  Tool format: {tool_format}"
                    if is_active:
                        msg += "\n  [reloaded - changes applied]"
                    data["display_messages"] = [("system", msg, {})]
                else:
                    data["display_messages"] = [
                        ("error", "[err] Failed to update profile", {}),
                    ]

        return data

    def _get_create_profile_modal_definition(self) -> Dict[str, Any]:
        """Get modal definition for creating a new profile."""
        return {
            "title": "Create LLM Profile",
            "footer": "Tab navigate • Enter confirm • Ctrl+S save • Esc cancel",
            "width": 70,
            "height": 20,
            "form_action": "create_profile_submit",
            "sections": [
                {
                    "title": "Profile Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "Profile Name",
                            "field": "name",
                            "placeholder": "my-profile",
                            "help": "Unique identifier for this profile"
                        },
                        {
                            "type": "text_input",
                            "label": "API URL",
                            "field": "api_url",
                            "placeholder": "http://localhost:1234",
                            "help": "LLM API endpoint URL"
                        },
                        {
                            "type": "text_input",
                            "label": "Model",
                            "field": "model",
                            "placeholder": "qwen/qwen3-4b",
                            "help": "Model identifier"
                        },
                        {
                            "type": "slider",
                            "label": "Temperature",
                            "field": "temperature",
                            "min_value": 0.0,
                            "max_value": 2.0,
                            "step": 0.1,
                            "current_value": 0.7,
                            "help": "Creativity/randomness (0.0-2.0)"
                        },
                        {
                            "type": "dropdown",
                            "label": "Tool Format",
                            "field": "tool_format",
                            "options": ["openai", "anthropic"],
                            "current_value": "openai",
                            "help": "API tool calling format"
                        },
                        {
                            "type": "text_input",
                            "label": "Description",
                            "field": "description",
                            "placeholder": "Optional description",
                            "help": "Human-readable description"
                        },
                    ]
                }
            ],
            "actions": [
                {"key": "Ctrl+S", "label": "Create", "action": "submit", "style": "primary"},
                {"key": "Escape", "label": "Cancel", "action": "cancel", "style": "secondary"}
            ]
        }

    def _get_edit_profile_modal_definition(self, profile_name: str) -> Dict[str, Any]:
        """Get modal definition for editing an existing profile.

        Args:
            profile_name: Name of the profile to edit.

        Returns:
            Modal definition dict with pre-populated values.
        """
        if not self.profile_manager:
            return {}

        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            return {}

        return {
            "title": f"Edit Profile: {profile_name}",
            "footer": "Tab navigate • Enter confirm • Ctrl+S save • Esc cancel",
            "width": 70,
            "height": 22,
            "form_action": "edit_profile_submit",
            "edit_profile_name": profile_name,  # Track which profile we're editing
            "sections": [
                {
                    "title": "Profile Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "Profile Name",
                            "field": "name",
                            "value": profile.name,
                            "placeholder": "my-profile",
                            "help": "Unique identifier for this profile"
                        },
                        {
                            "type": "text_input",
                            "label": "API URL",
                            "field": "api_url",
                            "value": profile.api_url,
                            "placeholder": "http://localhost:1234",
                            "help": "LLM API endpoint URL"
                        },
                        {
                            "type": "text_input",
                            "label": "Model",
                            "field": "model",
                            "value": profile.model,
                            "placeholder": "qwen/qwen3-4b",
                            "help": "Model identifier"
                        },
                        {
                            "type": "slider",
                            "label": "Temperature",
                            "field": "temperature",
                            "min_value": 0.0,
                            "max_value": 2.0,
                            "step": 0.1,
                            "current_value": profile.temperature,
                            "help": "Creativity/randomness (0.0-2.0)"
                        },
                        {
                            "type": "dropdown",
                            "label": "Tool Format",
                            "field": "tool_format",
                            "options": ["openai", "anthropic"],
                            "current_value": profile.tool_format,
                            "help": "API tool calling format"
                        },
                        {
                            "type": "text_input",
                            "label": "API Token Env",
                            "field": "api_token_env",
                            "value": profile.api_token_env or "",
                            "placeholder": "ANTHROPIC_API_KEY",
                            "help": "Environment variable for API token"
                        },
                        {
                            "type": "text_input",
                            "label": "Description",
                            "field": "description",
                            "value": profile.description or "",
                            "placeholder": "Optional description",
                            "help": "Human-readable description"
                        },
                    ]
                }
            ],
            "actions": [
                {"key": "Ctrl+S", "label": "Save", "action": "submit", "style": "primary"},
                {"key": "Escape", "label": "Cancel", "action": "cancel", "style": "secondary"}
            ]
        }

    def _get_create_agent_modal_definition(self) -> Dict[str, Any]:
        """Get modal definition for creating a new agent."""
        # Get available profiles for dropdown
        profile_options = ["(none)"]
        if self.profile_manager:
            profile_options.extend(self.profile_manager.get_profile_names())

        return {
            "title": "Create Agent",
            "footer": "Tab navigate • Enter confirm • Ctrl+S save • Esc cancel",
            "width": 70,
            "height": 22,
            "form_action": "create_agent_submit",
            "sections": [
                {
                    "title": "Agent Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "Agent Name",
                            "field": "name",
                            "placeholder": "my-agent",
                            "help": "Unique identifier (creates agents/<name>/ directory)"
                        },
                        {
                            "type": "text_input",
                            "label": "Description",
                            "field": "description",
                            "placeholder": "Agent description",
                            "help": "What this agent specializes in"
                        },
                        {
                            "type": "dropdown",
                            "label": "Preferred Profile",
                            "field": "profile",
                            "options": profile_options,
                            "current_value": "(none)",
                            "help": "LLM profile to use with this agent"
                        },
                        {
                            "type": "text_input",
                            "label": "System Prompt",
                            "field": "system_prompt",
                            "placeholder": "You are a helpful assistant...",
                            "help": "Base system prompt for the agent",
                            "multiline": True
                        },
                    ]
                }
            ],
            "actions": [
                {"key": "Ctrl+S", "label": "Create", "action": "submit", "style": "primary"},
                {"key": "Escape", "label": "Cancel", "action": "cancel", "style": "secondary"}
            ]
        }

    async def handle_help(self, command: SlashCommand) -> CommandResult:
        """Handle /help command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            if command.args:
                # Show help for specific command
                command_name = command.args[0]
                return await self._show_command_help(command_name)
            else:
                # Show all commands categorized by plugin
                return await self._show_all_commands()

        except Exception as e:
            self.logger.error(f"Error in help command: {e}")
            return CommandResult(
                success=False,
                message=f"Error displaying help: {str(e)}",
                display_type="error"
            )

    async def handle_config(self, command: SlashCommand) -> CommandResult:
        """Handle /config command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result with status UI.
        """
        try:
            # Import the comprehensive config widget definitions
            from ..ui.config_widgets import ConfigWidgetDefinitions

            # Get the complete configuration modal definition
            modal_definition = ConfigWidgetDefinitions.get_config_modal_definition()

            return CommandResult(
                success=True,
                message="Configuration modal opened",
                ui_config=UIConfig(
                    type="modal",
                    title=modal_definition["title"],
                    width=modal_definition["width"],
                    modal_config=modal_definition
                ),
                display_type="modal"
            )

        except Exception as e:
            self.logger.error(f"Error in config command: {e}")
            return CommandResult(
                success=False,
                message=f"Error opening configuration: {str(e)}",
                display_type="error"
            )

    async def handle_status(self, command: SlashCommand) -> CommandResult:
        """Handle /status command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result with status modal UI.
        """
        try:
            # Create status modal definition (similar to config modal)
            status_definition = self._get_status_modal_definition()

            return CommandResult(
                success=True,
                message="System status opened",
                ui_config=UIConfig(
                    type="modal",
                    title=status_definition["title"],
                    width=status_definition.get("width", 70),
                    modal_config=status_definition
                ),
                display_type="modal"
            )

        except Exception as e:
            self.logger.error(f"Error in status command: {e}")
            return CommandResult(
                success=False,
                message=f"Error showing status: {str(e)}",
                display_type="error"
            )

    def _get_status_modal_definition(self) -> Dict[str, Any]:
        """Get status modal definition with live system data.

        Returns:
            Modal definition dictionary for status display.
        """
        import platform
        import sys
        import os

        stats = self.command_registry.get_registry_stats()

        return {
            "title": "System Status",
            "footer": "Esc to close",
            "width": 70,
            "height": 18,
            "sections": [
                {
                    "title": "Commands",
                    "widgets": [
                        {"type": "label", "label": "Registered", "value": str(stats.get('total_commands', 0))},
                        {"type": "label", "label": "Enabled", "value": str(stats.get('enabled_commands', 0))},
                        {"type": "label", "label": "Categories", "value": str(stats.get('categories', 0))},
                    ]
                },
                {
                    "title": "Plugins",
                    "widgets": [
                        {"type": "label", "label": "Active", "value": str(stats.get('plugins', 0))},
                    ]
                },
                {
                    "title": "System",
                    "widgets": [
                        {"type": "label", "label": "Python", "value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"},
                        {"type": "label", "label": "Platform", "value": platform.system()},
                        {"type": "label", "label": "Architecture", "value": platform.machine()},
                    ]
                },
                {
                    "title": "Services",
                    "widgets": [
                        {"type": "label", "label": "Event Bus", "value": "[ok] Active"},
                        {"type": "label", "label": "Input Handler", "value": "[ok] Running"},
                        {"type": "label", "label": "Terminal Renderer", "value": "[ok] Active"},
                    ]
                }
            ],
            "actions": [
                {"key": "Escape", "label": "Close", "action": "cancel", "style": "secondary"}
            ]
        }

    async def handle_version(self, command: SlashCommand) -> CommandResult:
        """Handle /version command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            # Get version information
            version_info = self._get_version_info()

            message = f"""Kollabor CLI v{version_info['version']}
Built: {version_info['build_date']}
Python: {version_info['python_version']}
Platform: {version_info['platform']}"""

            return CommandResult(
                success=True,
                message=message,
                display_type="info",
                data=version_info
            )

        except Exception as e:
            self.logger.error(f"Error in version command: {e}")
            return CommandResult(
                success=False,
                message=f"Error getting version: {str(e)}",
                display_type="error"
            )

    async def handle_profile(self, command: SlashCommand) -> CommandResult:
        """Handle /profile command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            if not self.profile_manager:
                return CommandResult(
                    success=False,
                    message="Profile manager not available",
                    display_type="error"
                )

            args = command.args or []

            if not args or args[0] in ("list", "ls"):
                # Show profile selection modal
                return await self._show_profiles_modal()
            elif args[0] == "migrate":
                # Migrate current config to a profile
                profile_name = args[1] if len(args) > 1 else "current"
                return await self._migrate_current_profile(profile_name)
            elif args[0] == "create" and len(args) >= 4:
                # Create new profile: /profile create <name> <api_url> <model>
                name = args[1]
                api_url = args[2]
                model = args[3]
                temp = float(args[4]) if len(args) > 4 else 0.7
                return await self._create_profile(name, api_url, model, temp)
            else:
                # Switch to specified profile (direct command)
                profile_name = args[0]
                return await self._switch_profile(profile_name)

        except Exception as e:
            self.logger.error(f"Error in profile command: {e}")
            return CommandResult(
                success=False,
                message=f"Error managing profiles: {str(e)}",
                display_type="error"
            )

    async def _show_profiles_modal(self) -> CommandResult:
        """Show profile selection modal.

        Returns:
            Command result with modal UI.
        """
        # Reload profiles from config to pick up any changes
        self.profile_manager.reload()

        profiles = self.profile_manager.list_profiles()
        active_name = self.profile_manager.active_profile_name

        # Build profile list for modal
        profile_items = []
        for profile in profiles:
            is_active = profile.name == active_name
            profile_items.append({
                "name": f"{'[*] ' if is_active else '    '}{profile.name}",
                "description": f"{profile.model} @ {profile.api_url}",
                "profile_name": profile.name,
                "action": "select_profile"
            })

        # Add management options
        management_items = [
            {
                "name": "    [+] Migrate Current Config",
                "description": "Save current LLM config as a named profile",
                "action": "migrate_profile"
            },
            {
                "name": "    [+] Create New Profile",
                "description": "Create a new profile from scratch",
                "action": "create_profile_prompt"
            },
        ]

        modal_definition = {
            "title": "LLM Profiles",
            "footer": "↑↓ navigate • Enter select • e edit • Esc exit",
            "width": 75,
            "height": 18,
            "sections": [
                {
                    "title": f"Available Profiles (active: {active_name})",
                    "commands": profile_items
                },
                {
                    "title": "Management",
                    "commands": management_items
                }
            ],
            "actions": [
                {"key": "Enter", "label": "Select", "action": "select"},
                {"key": "e", "label": "Edit", "action": "edit_profile_prompt"},
                {"key": "Escape", "label": "Close", "action": "cancel"}
            ]
        }

        return CommandResult(
            success=True,
            message="Select a profile",
            ui_config=UIConfig(
                type="modal",
                title=modal_definition["title"],
                width=modal_definition["width"],
                height=modal_definition["height"],
                modal_config=modal_definition
            ),
            display_type="modal"
        )

    async def _switch_profile(self, profile_name: str) -> CommandResult:
        """Switch to a different profile.

        Args:
            profile_name: Name of profile to switch to.

        Returns:
            Command result.
        """
        if self.profile_manager.set_active_profile(profile_name):
            profile = self.profile_manager.get_active_profile()
            # Update the API service with new profile settings
            if self.llm_service and hasattr(self.llm_service, 'api_service'):
                self.llm_service.api_service.update_from_profile(
                    api_url=profile.api_url,
                    model=profile.model,
                    temperature=profile.temperature,
                    tool_format=profile.tool_format
                )
            return CommandResult(
                success=True,
                message=f"Switched to profile: {profile_name}\n  API: {profile.api_url}\n  Model: {profile.model}",
                display_type="success"
            )
        else:
            available = ", ".join(self.profile_manager.get_profile_names())
            return CommandResult(
                success=False,
                message=f"Profile not found: {profile_name}\nAvailable: {available}",
                display_type="error"
            )

    async def _migrate_current_profile(self, profile_name: str) -> CommandResult:
        """Migrate current LLM config to a named profile.

        Args:
            profile_name: Name for the new profile.

        Returns:
            Command result.
        """
        profile = self.profile_manager.migrate_current_config(profile_name)
        if profile:
            return CommandResult(
                success=True,
                message=f"[ok] Migrated current config to profile: {profile_name}\n  API: {profile.api_url}\n  Model: {profile.model}\n  Saved to config.json",
                display_type="success"
            )
        else:
            return CommandResult(
                success=False,
                message=f"[err] Failed to migrate config. Profile '{profile_name}' may already exist.",
                display_type="error"
            )

    async def _create_profile(
        self, name: str, api_url: str, model: str, temperature: float = 0.7
    ) -> CommandResult:
        """Create a new profile.

        Args:
            name: Profile name.
            api_url: API endpoint URL.
            model: Model identifier.
            temperature: Sampling temperature.

        Returns:
            Command result.
        """
        profile = self.profile_manager.create_profile(
            name=name,
            api_url=api_url,
            model=model,
            temperature=temperature,
            description=f"Created via /profile create",
            save_to_config=True
        )
        if profile:
            return CommandResult(
                success=True,
                message=f"[ok] Created profile: {name}\n  API: {api_url}\n  Model: {model}\n  Saved to config.json",
                display_type="success"
            )
        else:
            return CommandResult(
                success=False,
                message=f"[err] Failed to create profile. '{name}' may already exist.",
                display_type="error"
            )

    async def handle_agent(self, command: SlashCommand) -> CommandResult:
        """Handle /agent command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            if not self.agent_manager:
                return CommandResult(
                    success=False,
                    message="Agent manager not available",
                    display_type="error"
                )

            args = command.args or []

            if not args or args[0] in ("list", "ls"):
                # Show agent selection modal
                return await self._show_agents_modal()
            elif args[0] == "clear":
                # Clear active agent
                self.agent_manager.clear_active_agent()
                return CommandResult(
                    success=True,
                    message="Cleared active agent, using default behavior",
                    display_type="success"
                )
            else:
                # Switch to specified agent (direct command)
                agent_name = args[0]
                return await self._switch_agent(agent_name)

        except Exception as e:
            self.logger.error(f"Error in agent command: {e}")
            return CommandResult(
                success=False,
                message=f"Error managing agents: {str(e)}",
                display_type="error"
            )

    async def _show_agents_modal(self) -> CommandResult:
        """Show agent selection modal.

        Returns:
            Command result with modal UI.
        """
        # Refresh agents from directories to pick up any changes
        self.agent_manager.refresh()

        agents = self.agent_manager.list_agents()
        active_agent = self.agent_manager.get_active_agent()
        active_name = active_agent.name if active_agent else None

        if not agents:
            return CommandResult(
                success=True,
                message="No agents found.\nCreate agents in .kollabor-cli/agents/<name>/system_prompt.md",
                display_type="info"
            )

        # Build agent list for modal
        agent_items = []
        for agent in agents:
            is_active = agent.name == active_name
            skills = agent.list_skills()
            skill_count = f" ({len(skills)} skills)" if skills else ""
            description = agent.description or "No description"

            agent_items.append({
                "name": f"{'[*] ' if is_active else '    '}{agent.name}{skill_count}",
                "description": description,
                "agent_name": agent.name,
                "action": "select_agent"
            })

        # Add clear option
        agent_items.append({
            "name": "    [Clear Agent]",
            "description": "Use default system prompt behavior",
            "agent_name": None,
            "action": "clear_agent"
        })

        # Management options
        management_items = [
            {
                "name": "    [+] Create New Agent",
                "description": "Create a new agent with system prompt",
                "action": "create_agent_prompt"
            }
        ]

        modal_definition = {
            "title": "Agents",
            "footer": "↑↓ navigate • Enter select • Esc exit",
            "width": 70,
            "height": 18,
            "sections": [
                {
                    "title": f"Available Agents (active: {active_name or 'none'})",
                    "commands": agent_items
                },
                {
                    "title": "Management",
                    "commands": management_items
                }
            ],
            "actions": [
                {"key": "Enter", "label": "Select", "action": "select"},
                {"key": "Escape", "label": "Close", "action": "cancel"}
            ]
        }

        return CommandResult(
            success=True,
            message="Select an agent",
            ui_config=UIConfig(
                type="modal",
                title=modal_definition["title"],
                width=modal_definition["width"],
                height=modal_definition["height"],
                modal_config=modal_definition
            ),
            display_type="modal"
        )

    async def _switch_agent(self, agent_name: str) -> CommandResult:
        """Switch to a different agent.

        Args:
            agent_name: Name of agent to switch to.

        Returns:
            Command result.
        """
        if self.agent_manager.set_active_agent(agent_name):
            # Rebuild system prompt for the new agent
            if self.llm_service:
                self.llm_service.rebuild_system_prompt()

            agent = self.agent_manager.get_active_agent()
            skills = agent.list_skills()
            skill_info = f", {len(skills)} skills available" if skills else ""

            # If agent has a preferred profile, mention it
            profile_info = ""
            if agent.profile:
                profile_info = f"\n  Preferred profile: {agent.profile}"

            return CommandResult(
                success=True,
                message=f"Switched to agent: {agent_name}{skill_info}{profile_info}",
                display_type="success"
            )
        else:
            available = ", ".join(self.agent_manager.get_agent_names())
            return CommandResult(
                success=False,
                message=f"Agent not found: {agent_name}\nAvailable: {available}",
                display_type="error"
            )

    async def handle_skill(self, command: SlashCommand) -> CommandResult:
        """Handle /skill command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            if not self.agent_manager:
                return CommandResult(
                    success=False,
                    message="Agent manager not available",
                    display_type="error"
                )

            active_agent = self.agent_manager.get_active_agent()
            if not active_agent:
                return CommandResult(
                    success=False,
                    message="No active agent. Use /agent <name> first.",
                    display_type="error"
                )

            args = command.args or []

            if not args:
                # Show skill selection modal
                return await self._show_skills_modal()
            elif args[0] in ("list", "ls"):
                # Show skill selection modal
                return await self._show_skills_modal()
            elif args[0] == "load" and len(args) > 1:
                # Load skill
                skill_name = args[1]
                return await self._load_skill(skill_name)
            elif args[0] == "unload" and len(args) > 1:
                # Unload skill
                skill_name = args[1]
                return await self._unload_skill(skill_name)
            else:
                # Try to load skill by name directly
                skill_name = args[0]
                return await self._load_skill(skill_name)

        except Exception as e:
            self.logger.error(f"Error in skill command: {e}")
            return CommandResult(
                success=False,
                message=f"Error managing skills: {str(e)}",
                display_type="error"
            )

    async def _show_skills_modal(self) -> CommandResult:
        """Show skill selection modal for active agent.

        Returns:
            Command result with modal UI.
        """
        active_agent = self.agent_manager.get_active_agent()
        skills = active_agent.list_skills()
        active_skills = active_agent.active_skills

        if not skills:
            return CommandResult(
                success=True,
                message=f"Agent '{active_agent.name}' has no skills defined.\nAdd .md files to the agent directory to create skills.",
                display_type="info"
            )

        # Build skill list for modal
        skill_items = []
        for skill in skills:
            is_loaded = skill.name in active_skills
            marker = "[*]" if is_loaded else "[ ]"
            action = "unload_skill" if is_loaded else "load_skill"
            description = skill.description or f"Skill file: {skill.file_path.name}"

            skill_items.append({
                "name": f"{marker} {skill.name}",
                "description": description,
                "skill_name": skill.name,
                "action": action,
                "loaded": is_loaded
            })

        loaded_count = len(active_skills)
        total_count = len(skills)

        modal_definition = {
            "title": f"Skills - {active_agent.name}",
            "footer": "↑↓ navigate • Enter toggle • Esc exit",
            "width": 70,
            "height": 15,
            "sections": [
                {
                    "title": f"Available Skills ({loaded_count}/{total_count} loaded)",
                    "commands": skill_items
                }
            ],
            "actions": [
                {"key": "Enter", "label": "Toggle", "action": "toggle"},
                {"key": "Escape", "label": "Close", "action": "cancel"}
            ]
        }

        return CommandResult(
            success=True,
            message="Select a skill to load/unload",
            ui_config=UIConfig(
                type="modal",
                title=modal_definition["title"],
                width=modal_definition["width"],
                height=modal_definition["height"],
                modal_config=modal_definition
            ),
            display_type="modal"
        )

    async def _load_skill(self, skill_name: str) -> CommandResult:
        """Load a skill into active agent.

        Args:
            skill_name: Name of skill to load.

        Returns:
            Command result.
        """
        if self.agent_manager.load_skill(skill_name):
            # Rebuild system prompt to include the skill
            if self.llm_service:
                self.llm_service.rebuild_system_prompt()
            return CommandResult(
                success=True,
                message=f"Loaded skill: {skill_name}\nSkill content added to system prompt.",
                display_type="success"
            )
        else:
            active_agent = self.agent_manager.get_active_agent()
            available = ", ".join(s.name for s in active_agent.list_skills())
            return CommandResult(
                success=False,
                message=f"Skill not found: {skill_name}\nAvailable: {available}",
                display_type="error"
            )

    async def _unload_skill(self, skill_name: str) -> CommandResult:
        """Unload a skill from active agent.

        Args:
            skill_name: Name of skill to unload.

        Returns:
            Command result.
        """
        if self.agent_manager.unload_skill(skill_name):
            # Rebuild system prompt to remove the skill
            if self.llm_service:
                self.llm_service.rebuild_system_prompt()
            return CommandResult(
                success=True,
                message=f"Unloaded skill: {skill_name}",
                display_type="success"
            )
        else:
            return CommandResult(
                success=False,
                message=f"Skill not loaded: {skill_name}",
                display_type="error"
            )

    async def _show_command_help(self, command_name: str) -> CommandResult:
        """Show help for a specific command.

        Args:
            command_name: Name of command to show help for.

        Returns:
            Command result with help information.
        """
        command_def = self.command_registry.get_command(command_name)
        if not command_def:
            return CommandResult(
                success=False,
                message=f"Unknown command: /{command_name}",
                display_type="error"
            )

        # Format detailed help for the command
        help_text = f"""Command: /{command_def.name}
Description: {command_def.description}
Plugin: {command_def.plugin_name}
Category: {command_def.category.value}
Mode: {command_def.mode.value}"""

        if command_def.aliases:
            help_text += f"\nAliases: {', '.join(command_def.aliases)}"

        if command_def.parameters:
            help_text += "\nParameters:"
            for param in command_def.parameters:
                required = " (required)" if param.required else ""
                help_text += f"\n  {param.name}: {param.description}{required}"

        return CommandResult(
            success=True,
            message=help_text,
            display_type="info"
        )

    async def _show_all_commands(self) -> CommandResult:
        """Show all available commands grouped by plugin in a status modal.

        Returns:
            Command result with status modal UI config.
        """
        # Get commands grouped by plugin
        plugin_categories = self.command_registry.get_plugin_categories()

        # Build command list for modal display
        command_sections = []

        for plugin_name in sorted(plugin_categories.keys()):
            commands = self.command_registry.get_commands_by_plugin(plugin_name)
            if not commands:
                continue

            # Create section for this plugin
            section_commands = []
            for cmd in sorted(commands, key=lambda c: c.name):
                aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
                section_commands.append({
                    "name": f"/{cmd.name}{aliases}",
                    "description": cmd.description
                })

            command_sections.append({
                "title": f"{plugin_name.title()} Commands",
                "commands": section_commands
            })

        return CommandResult(
            success=True,
            message="Help opened in status modal",
            ui_config=UIConfig(
                type="status_modal",
                title="Available Commands",
                height=15,
                width=80,
                modal_config={
                    "sections": command_sections,
                    "footer": "Esc/Enter close • /help <command> for details",
                    "scrollable": True
                }
            ),
            display_type="status_modal"
        )

    async def handle_resume(self, command: SlashCommand) -> CommandResult:
        """Handle /resume command.

        Args:
            command: Parsed slash command.

        Returns:
            Command execution result.
        """
        try:
            # Parse arguments
            args = command.args or []
            force = False
            if args:
                force = "--force" in args
                args = [arg for arg in args if arg != "--force"]
            
            if len(args) == 0:
                # Show session selection modal
                return await self._show_session_selector()
            elif len(args) == 1:
                # Resume specific session by ID
                session_id = args[0]
                return await self._resume_session(session_id, force=force)
            elif len(args) >= 2 and args[0].lower() == "search":
                # Search sessions
                query = " ".join(args[1:])
                return await self._search_and_resume(query)
            else:
                # Handle other arguments (filters, etc.)
                return await self._handle_resume_args(args)
                
        except Exception as e:
            self.logger.error(f"Error in resume command: {e}")
            return CommandResult(
                success=False,
                message=f"Error resuming session: {str(e)}",
                display_type="error"
            )

    async def _show_session_selector(self) -> CommandResult:
        """Show session selection modal.
        
        Returns:
            Command result with session selection modal.
        """
        try:
            # Prefer ConversationManager so saved sessions can actually be loaded
            conversation_manager = self._get_conversation_manager()
            sessions = conversation_manager.get_available_sessions() if conversation_manager else None

            if not sessions:
                # Fall back to the conversation logger listing
                try:
                    from ...utils.config_utils import get_config_directory
                    from ..llm.conversation_logger import KollaborConversationLogger
                except ImportError:
                    try:
                        from core.utils.config_utils import get_config_directory
                        from core.llm.conversation_logger import KollaborConversationLogger
                    except ImportError:
                        from ..utils.config_utils import get_config_directory
                        from ..llm.conversation_logger import KollaborConversationLogger
                
                config_dir = get_config_directory()
                conversations_dir = config_dir / "conversations"
                conversation_logger = KollaborConversationLogger(conversations_dir)
                sessions = conversation_logger.list_sessions()
            
            if not sessions:
                return CommandResult(
                    success=False,
                    message="No saved conversations found. Use /save to save current conversations for future resumption.",
                    display_type="info"
                )
            
            # Build modal definition
            modal_definition = self._get_resume_modal_definition(sessions)
            
            return CommandResult(
                success=True,
                message="Select a conversation to resume",
                ui_config=UIConfig(
                    type="modal",
                    title=modal_definition["title"],
                    width=modal_definition["width"],
                    height=modal_definition["height"],
                    modal_config=modal_definition
                ),
                display_type="modal"
            )
            
        except Exception as e:
            self.logger.error(f"Error showing session selector: {e}")
            return CommandResult(
                success=False,
                message=f"Error loading conversations: {str(e)}",
                display_type="error"
            )

    async def _resume_session(self, session_id: str, force: bool = False) -> CommandResult:
        """Resume specific session by ID.

        Args:
            session_id: Session identifier
            force: Whether to bypass validation warnings

        Returns:
            Command result.
        """
        try:
            # Get conversation manager instance
            conversation_manager = self._get_conversation_manager()
            if not conversation_manager:
                return CommandResult(
                    success=False,
                    message="Conversation manager not available",
                    display_type="error"
                )

            # Validate session
            validation = conversation_manager.validate_session(session_id)
            if not validation["valid"]:
                issues = ", ".join(validation["issues"])
                return CommandResult(
                    success=False,
                    message=f"Session validation failed: {issues}",
                    display_type="error"
                )

            # Show warnings if any
            if validation["warnings"] and not force:
                warnings = "\n".join(f"[!] {warning}" for warning in validation["warnings"])
                return CommandResult(
                    success=False,
                    message=f"Session has warnings:\n{warnings}\n\nUse /resume {session_id} --force to override.",
                    display_type="warning"
                )

            # Load session via conversation manager
            success = conversation_manager.load_session(session_id)
            if not success:
                return CommandResult(
                    success=False,
                    message=f"Failed to load session: {session_id}",
                    display_type="error"
                )

            # Now load messages into LLM service conversation history for UI display
            if self.llm_service:
                try:
                    # Get the loaded messages from the conversation manager
                    raw_messages = conversation_manager.messages
                    if raw_messages:
                        # Import ConversationMessage to convert the dict format
                        from ..models import ConversationMessage

                        # Convert dict messages to ConversationMessage objects
                        converted_messages = []
                        for msg in raw_messages:
                            converted_messages.append(ConversationMessage(
                                role=msg.get("role", "user"),
                                content=msg.get("content", "")
                            ))

                        # Clear current conversation and load the resumed session
                        self.llm_service.conversation_history = converted_messages
                        self.logger.info(f"Loaded {len(converted_messages)} messages into LLM service")

                        # Trigger UI refresh via event bus
                        if self.event_bus:
                            from ..events.models import Event, EventType
                            refresh_event = Event(
                                type=EventType.STATUS_CONTENT_UPDATE,
                                data={"action": "conversation_resumed", "session_id": session_id},
                                source="system_commands"
                            )
                            await self.event_bus.emit_with_hooks(refresh_event)
                except Exception as e:
                    self.logger.warning(f"Could not load messages into LLM service: {e}")

            message_count = len(conversation_manager.messages) if conversation_manager else 0

            return CommandResult(
                success=True,
                message=f"[ok] Resumed conversation: {session_id[:8]}... ({message_count} messages loaded)",
                display_type="success",
                data={
                    "session_id": session_id,
                    "compatibility_score": validation["compatibility_score"],
                    "message_count": message_count
                }
            )

        except Exception as e:
            self.logger.error(f"Error resuming session: {e}")
            return CommandResult(
                success=False,
                message=f"Error resuming session: {str(e)}",
                display_type="error"
            )

    async def _search_and_resume(self, query: str) -> CommandResult:
        """Search sessions and show results.
        
        Args:
            query: Search query
            
        Returns:
            Command result with search modal.
        """
        try:
            from ...utils.config_utils import get_config_directory
            from ..llm.conversation_logger import KollaborConversationLogger
            
            config_dir = get_config_directory()
            conversations_dir = config_dir / "conversations"
            
            conversation_logger = KollaborConversationLogger(conversations_dir)
            sessions = conversation_logger.search_sessions(query)
            
            if not sessions:
                return CommandResult(
                    success=False,
                    message=f"No conversations found matching: {query}",
                    display_type="info"
                )
            
            # Build search results modal
            modal_definition = self._get_search_modal_definition(sessions, query)
            
            return CommandResult(
                success=True,
                message=f"Found {len(sessions)} conversations matching: {query}",
                ui_config=UIConfig(
                    type="modal",
                    title=modal_definition["title"],
                    width=modal_definition["width"],
                    height=modal_definition["height"],
                    modal_config=modal_definition
                ),
                display_type="modal"
            )
            
        except Exception as e:
            self.logger.error(f"Error searching sessions: {e}")
            return CommandResult(
                success=False,
                message=f"Error searching conversations: {str(e)}",
                display_type="error"
            )

    async def _handle_resume_args(self, args: List[str]) -> CommandResult:
        """Handle additional resume arguments (filters, etc.).
        
        Args:
            args: Command arguments
            
        Returns:
            Command result.
        """
        # Handle filters like --today, --week, --limit N
        filters = {}
        limit = 20
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            if arg == "--today":
                # Filter for today's sessions
                from datetime import date
                today = date.today().isoformat()
                filters["date"] = today
            elif arg == "--week":
                # Filter for this week's sessions
                from datetime import date, timedelta
                week_ago = (date.today() - timedelta(days=7)).isoformat()
                filters["date_range"] = (week_ago, date.today().isoformat())
            elif arg == "--limit" and i + 1 < len(args):
                try:
                    limit = int(args[i + 1])
                    i += 1  # Skip the next argument
                except ValueError:
                    pass
            elif arg.startswith("--"):
                # Unknown filter
                return CommandResult(
                    success=False,
                    message=f"Unknown filter: {arg}",
                    display_type="error"
                )
            
            i += 1
        
        # Apply filters and show results
        return await self._show_filtered_sessions(filters, limit)

    async def _show_filtered_sessions(self, filters: Dict, limit: int) -> CommandResult:
        """Show sessions with applied filters.
        
        Args:
            filters: Filters to apply
            limit: Maximum sessions to show
            
        Returns:
            Command result with filtered sessions modal.
        """
        try:
            from ...utils.config_utils import get_config_directory
            from ..llm.conversation_logger import KollaborConversationLogger
            
            config_dir = get_config_directory()
            conversations_dir = config_dir / "conversations"
            
            conversation_logger = KollaborConversationLogger(conversations_dir)
            sessions = conversation_logger.list_sessions(filters)
            
            # Apply limit
            if limit > 0:
                sessions = sessions[:limit]
            
            if not sessions:
                return CommandResult(
                    success=True,
                    message="No conversations found matching the specified filters",
                    display_type="info"
                )
            
            # Build filtered results modal
            modal_definition = self._get_filtered_modal_definition(sessions, filters)
            
            return CommandResult(
                success=True,
                message=f"Showing {len(sessions)} filtered conversations",
                ui_config=UIConfig(
                    type="modal",
                    title=modal_definition["title"],
                    width=modal_definition["width"],
                    height=modal_definition["height"],
                    modal_config=modal_definition
                ),
                display_type="modal"
            )
            
        except Exception as e:
            self.logger.error(f"Error showing filtered sessions: {e}")
            return CommandResult(
                success=False,
                message=f"Error loading filtered conversations: {str(e)}",
                display_type="error"
            )

    def _get_conversation_manager(self):
        """Get conversation manager instance.
        
        Returns:
            Conversation manager instance or None.
        """
        # Try to get conversation manager from various sources
        try:
            # First try to get from event bus if available
            if self.event_bus:
                # Try to get registered conversation manager
                try:
                    return self.event_bus.get_service('conversation_manager')
                except:
                    pass
            
            # Try to import and create if we have config
            try:
                from ..llm.conversation_manager import ConversationManager
                from ..utils.config_utils import get_config_directory
                
                # Use a basic config if no manager available
                class BasicConfig:
                    def get(self, key, default=None):
                        return default
                
                config = BasicConfig()
                conversations_dir = get_config_directory() / "conversations"
                conversations_dir.mkdir(parents=True, exist_ok=True)
                
                return ConversationManager(config)
            except Exception as e:
                self.logger.warning(f"Could not create conversation manager: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting conversation manager: {e}")
            return None

    def _get_resume_modal_definition(self, sessions: List[Dict]) -> Dict[str, Any]:
        """Get modal definition for session selection.
        
        Args:
            sessions: List of available sessions
            
        Returns:
            Modal definition dictionary.
        """
        # Convert sessions to commands format for status modal
        session_commands = []
        for session in sessions:
            message_count = session.get("message_count", 0)
            # Filter out sessions with 2 or fewer messages
            if message_count <= 2:
                continue
            # Limit to 20 for display
            if len(session_commands) >= 20:
                break

            session_id = session["session_id"]
            start_time = session.get("start_time", "Unknown")
            working_dir = session.get("working_directory", "Unknown")
            
            # Format start time
            if start_time and start_time != "Unknown":
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_time = start_time
            else:
                formatted_time = "Unknown"
            
            # Create command entry with full session data
            session_commands.append({
                "name": f"[{session_id[:8]}] {formatted_time}",
                "description": f"{message_count} messages • {working_dir}",
                "session_id": session_id,  # Full session ID for resume action
                "action": "resume_session"
            })
        
        # Add action commands
        action_commands = [
            {
                "name": "Search Conversations",
                "description": "Find conversations by content",
                "action": "search"
            },
            {
                "name": "Filter Options",
                "description": "Filter by date, directory, or branch",
                "action": "filter"
            }
        ]
        
        return {
            "title": "Resume Conversation",
            "footer": "↑↓ navigate • Enter select • Tab search • F filter • Esc exit",
            "width": 80,
            "height": 20,
            "sections": [
                {
                    "title": "Recent Conversations",
                    "commands": session_commands
                },
                {
                    "title": "Actions",
                    "commands": action_commands
                }
            ],
            "actions": [
                {"key": "Tab", "label": "Search", "action": "search"},
                {"key": "f", "label": "Filter", "action": "filter"},
            ]
        }

    def _get_search_modal_definition(self, sessions: List[Dict], query: str) -> Dict[str, Any]:
        """Get modal definition for search results.
        
        Args:
            sessions: Search results
            query: Search query
            
        Returns:
            Modal definition dictionary.
        """
        session_items = []
        for session in sessions:
            session_id = session["session_id"]
            relevance = session.get("search_relevance", 0)
            
            session_items.append({
                "id": session_id,
                "title": f"Session {session_id[:8]}... (Relevance: {relevance:.2f})",
                "subtitle": f"{session.get('message_count', 0)} messages • {session.get('duration', 'Unknown')}",
                "preview": session.get("preview_messages", [{}])[0].get("content", "")[:80],
                "metadata": session
            })
        
        return {
            "title": f"Search Results: {query}",
            "footer": "↑↓ navigate • Enter select • Esc back",
            "width": 80,
            "height": 20,
            "sections": [
                {
                    "title": f"Found {len(sessions)} conversations",
                    "type": "session_list",
                    "sessions": session_items
                }
            ],
            "actions": [
                {"key": "Enter", "label": "Resume", "action": "select"},
                {"key": "Escape", "label": "Back", "action": "cancel"}
            ]
        }

    def _get_filtered_modal_definition(self, sessions: List[Dict], filters: Dict) -> Dict[str, Any]:
        """Get modal definition for filtered results.
        
        Args:
            sessions: Filtered sessions
            filters: Applied filters
            
        Returns:
            Modal definition dictionary.
        """
        filter_desc = []
        if "date" in filters:
            filter_desc.append(f"Date: {filters['date']}")
        if "date_range" in filters:
            start, end = filters["date_range"]
            filter_desc.append(f"Date: {start} to {end}")
        
        filter_text = " • ".join(filter_desc) if filter_desc else "Filtered"
        
        session_items = []
        for session in sessions:
            session_id = session["session_id"]
            
            session_items.append({
                "id": session_id,
                "title": f"Session {session_id[:8]}...",
                "subtitle": f"{session.get('message_count', 0)} messages • {session.get('duration', 'Unknown')}",
                "preview": session.get("preview_messages", [{}])[0].get("content", "")[:80],
                "metadata": session
            })
        
        return {
            "title": f"Filtered Conversations ({filter_text})",
            "footer": "↑↓ navigate • Enter select • Esc back",
            "width": 80,
            "height": 20,
            "sections": [
                {
                    "title": f"Showing {len(sessions)} conversations",
                    "type": "session_list",
                    "sessions": session_items
                }
            ],
            "actions": [
                {"key": "Enter", "label": "Resume", "action": "select"},
                {"key": "Escape", "label": "Back", "action": "cancel"}
            ]
        }

    def _get_version_info(self) -> Dict[str, str]:
        """Get application version information.

        Returns:
            Dictionary with version details.
        """
        import sys
        import platform

        return {
            "version": "1.0.0-dev",
            "build_date": datetime.now().strftime("%Y-%m-%d"),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.system(),
            "architecture": platform.machine()
        }


class SystemConfigUI:
    """UI component for system configuration."""

    def __init__(self, config_manager, event_bus) -> None:
        """Initialize config UI.

        Args:
            config_manager: Configuration manager.
            event_bus: Event bus for configuration events.
        """
        self.config_manager = config_manager
        self.event_bus = event_bus

    def render(self) -> List[str]:
        """Render configuration interface.

        Returns:
            List of lines for display.
        """
        # This would be implemented to show actual config options
        return [
            "╭─ System Configuration ─────────────────────────────────────╮",
            "│                                                             │",
            "│ ❯ Terminal Settings                                         │",
            "│   Input Configuration                                       │",
            "│   Display Options                                           │",
            "│   Performance Settings                                      │",
            "│                                                             │",
            "│ Plugin Settings                                             │",
            "│   Event Bus Configuration                                   │",
            "│   Logging Options                                           │",
            "│                                                             │",
            "╰─────────────────────────────────────────────────────────────╯",
            "   ↑↓←→ navigate • Enter edit • Esc exit"
        ]


class SystemStatusUI:
    """UI component for system status display."""

    def __init__(self, event_bus, command_registry) -> None:
        """Initialize status UI.

        Args:
            event_bus: Event bus for status information.
            command_registry: Command registry for statistics.
        """
        self.event_bus = event_bus
        self.command_registry = command_registry

    def render(self) -> List[str]:
        """Render status interface.

        Returns:
            List of lines for display.
        """
        stats = self.command_registry.get_registry_stats()

        return [
            "╭─ System Status ─────────────────────────────────────────────╮",
            "│                                                             │",
            f"│ Commands: {stats['total_commands']} registered, {stats['enabled_commands']} enabled              │",
            f"│ Plugins: {stats['plugins']} active                                    │",
            f"│ Categories: {stats['categories']} in use                               │",
            "│                                                             │",
            "│ Event Bus: [ok] Active                                        │",
            "│ Input Handler: [ok] Running                                   │",
            "│ Terminal Renderer: [ok] Active                                │",
            "│                                                             │",
            "│ Memory Usage: ~ 45MB                                        │",
            "│ Uptime: 00:15:32                                            │",
            "│                                                             │",
            "╰─────────────────────────────────────────────────────────────╯",
            "   ↑↓ navigate • Esc exit"
        ]
