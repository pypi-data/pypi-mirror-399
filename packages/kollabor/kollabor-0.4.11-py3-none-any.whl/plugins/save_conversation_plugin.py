"""Save conversation plugin for exporting chat transcripts.

Provides /save command to export conversations to file or clipboard
in various formats (transcript, markdown, jsonl).
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from core.events.models import CommandDefinition, CommandCategory, CommandMode
from core.io.visual_effects import AgnosterSegment

logger = logging.getLogger(__name__)


class SaveConversationPlugin:
    """Plugin for saving conversations to file or clipboard."""

    def __init__(self, name: str = "save_conversation", state_manager=None, event_bus=None,
                 renderer=None, config=None) -> None:
        """Initialize the save conversation plugin.

        Args:
            name: Plugin name (default: "save_conversation")
            state_manager: State manager instance
            event_bus: Event bus instance
            renderer: Terminal renderer instance
            config: Configuration manager instance
        """
        self.name = name
        self.version = "1.0.0"
        self.description = "Save conversations to file or clipboard"
        self.enabled = True
        self.logger = logger

        # Store injected dependencies
        self.state_manager = state_manager
        self.event_bus = event_bus
        self.renderer = renderer
        self.config_manager = config

        # References to be set during initialize()
        self.command_registry = None
        self.llm_service = None
        self.config = None

    async def initialize(self, event_bus, config, **kwargs) -> None:
        """Initialize the plugin and register commands.

        Args:
            event_bus: Application event bus.
            config: Configuration manager.
            **kwargs: Additional initialization parameters.
        """
        try:
            self.config = config
            self.command_registry = kwargs.get('command_registry')
            self.llm_service = kwargs.get('llm_service')

            if not self.command_registry:
                self.logger.warning("No command registry provided, /save not registered")
                return

            if not self.llm_service:
                self.logger.warning("No LLM service provided, /save may not work")

            # Register the /save command
            self._register_commands()

            # Register status view
            await self._register_status_view()

            self.logger.info("Save conversation plugin initialized successfully")

        except Exception as e:
            self.logger.error(f"Error initializing save conversation plugin: {e}")
            raise

    async def _register_status_view(self) -> None:
        """Register save conversation status view."""
        try:
            if (self.renderer and
                hasattr(self.renderer, 'status_renderer') and
                self.renderer.status_renderer and
                hasattr(self.renderer.status_renderer, 'status_registry') and
                self.renderer.status_renderer.status_registry):

                from core.io.status_renderer import StatusViewConfig, BlockConfig

                view = StatusViewConfig(
                    name="Save Conversation",
                    plugin_source="save_conversation",
                    priority=300,
                    blocks=[BlockConfig(
                        width_fraction=1.0,
                        content_provider=self._get_status_content,
                        title="Save",
                        priority=100
                    )],
                )

                registry = self.renderer.status_renderer.status_registry
                registry.register_status_view("save_conversation", view)
                self.logger.info("Registered 'Save Conversation' status view")

        except Exception as e:
            self.logger.error(f"Failed to register status view: {e}")

    def _get_status_content(self) -> List[str]:
        """Get save conversation status (agnoster style)."""
        try:
            seg = AgnosterSegment()
            seg.add_lime("Save", "dark")
            seg.add_cyan("/save", "dark")
            seg.add_neutral("file | clipboard | json | md", "mid")
            return [seg.render()]

        except Exception as e:
            self.logger.error(f"Error getting status content: {e}")
            seg = AgnosterSegment()
            seg.add_neutral("Save: Error", "dark")
            return [seg.render()]

    def _register_commands(self) -> None:
        """Register all plugin commands."""
        save_command = CommandDefinition(
            name="save",
            description="Save conversation to file or clipboard",
            handler=self._handle_save_command,
            plugin_name=self.name,
            aliases=["export", "transcript"],
            mode=CommandMode.INSTANT,
            category=CommandCategory.CONVERSATION,
            icon="[SAVE]"
        )

        self.command_registry.register_command(save_command)
        self.logger.info("Registered /save command")

    async def _handle_save_command(self, command) -> str:
        """Handle the /save command.

        Args:
            command: SlashCommand object with parsed command data.

        Returns:
            Status message about the save operation.
        """
        try:
            # Parse arguments: /save [format] [destination]
            # Formats: transcript (default), markdown, jsonl
            # Destinations: file (default), clipboard, both

            args = command.args if hasattr(command, 'args') else []

            # Get configuration
            save_format = self.config.get("plugins.save_conversation.default_format", "transcript")
            save_to = self.config.get("plugins.save_conversation.default_destination", "file")
            auto_timestamp = self.config.get("plugins.save_conversation.auto_timestamp", True)
            output_dir = self.config.get("plugins.save_conversation.output_directory", "logs/transcripts")

            # Parse command arguments
            if len(args) >= 1:
                save_format = args[0].lower()
            if len(args) >= 2:
                save_to = args[1].lower()

            # Validate format
            if save_format not in ["transcript", "markdown", "jsonl", "raw"]:
                return f"Error: Invalid format '{save_format}'. Use: transcript, markdown, jsonl, or raw"

            # Validate destination
            if save_to not in ["file", "clipboard", "both"]:
                return f"Error: Invalid destination '{save_to}'. Use: file, clipboard, or both"

            # Get conversation content
            if not self.llm_service:
                return "Error: LLM service not available"

            # Get messages from llm_service conversation_history
            conversation_history = self.llm_service.conversation_history
            if not conversation_history:
                return "No conversation to save"

            # Convert ConversationMessage objects to dict format
            # Preserves EXACT content as sent to/received from API
            messages = []
            for msg in conversation_history:
                msg_dict = {
                    "role": msg.role,
                    "content": msg.content,  # Exact content - no processing
                }
                # Use actual timestamp from message if available
                if hasattr(msg, 'timestamp') and msg.timestamp:
                    msg_dict["timestamp"] = msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
                else:
                    msg_dict["timestamp"] = datetime.now().isoformat()

                # Include thinking if present (for debugging)
                if hasattr(msg, 'thinking') and msg.thinking:
                    msg_dict["thinking"] = msg.thinking

                messages.append(msg_dict)

            # Format the conversation
            formatted_content = self._format_conversation(messages, save_format)

            # Save to file
            saved_path = None
            if save_to in ["file", "both"]:
                saved_path = self._save_to_file(formatted_content, output_dir, save_format, auto_timestamp)

            # Copy to clipboard
            if save_to in ["clipboard", "both"]:
                self._copy_to_clipboard(formatted_content)

            # Return status message
            if save_to == "both":
                return f"Conversation saved to {saved_path} and copied to clipboard"
            elif save_to == "clipboard":
                return f"Conversation copied to clipboard ({len(messages)} messages)"
            else:
                return f"Conversation saved to {saved_path}"

        except Exception as e:
            self.logger.error(f"Error handling /save command: {e}")
            return f"Error saving conversation: {str(e)}"

    def _format_conversation(self, messages, format_type: str) -> str:
        """Format conversation messages based on requested format.

        Args:
            messages: List of conversation messages.
            format_type: Format type (transcript, markdown, jsonl, raw).

        Returns:
            Formatted conversation string.
        """
        if format_type == "raw":
            return self._format_as_raw_api(messages)
        elif format_type == "transcript":
            return self._format_as_transcript(messages)
        elif format_type == "markdown":
            return self._format_as_markdown(messages)
        elif format_type == "jsonl":
            return self._format_as_jsonl(messages)
        else:
            return self._format_as_transcript(messages)

    def _format_as_transcript(self, messages) -> str:
        """Format messages as raw transcript.

        Args:
            messages: List of conversation messages.

        Returns:
            Transcript formatted string.
        """
        lines = []

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Map role to section header
            if role == "system":
                lines.append("--- system_prompt ---")
            elif role == "user":
                lines.append("\n--- user ---")
            elif role == "assistant":
                lines.append("\n--- llm ---")
            else:
                lines.append(f"\n--- {role} ---")

            lines.append(content)

        return "\n".join(lines)

    def _format_as_markdown(self, messages) -> str:
        """Format messages as markdown.

        Args:
            messages: List of conversation messages.

        Returns:
            Markdown formatted string.
        """
        lines = ["# Conversation Transcript", ""]

        # Add metadata
        if messages:
            first_timestamp = messages[0].get("timestamp", "")
            last_timestamp = messages[-1].get("timestamp", "")
            lines.append(f"**Started:** {first_timestamp}")
            lines.append(f"**Ended:** {last_timestamp}")
            lines.append(f"**Messages:** {len(messages)}")
            lines.append("")
            lines.append("---")
            lines.append("")

        for i, msg in enumerate(messages):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")

            # Format based on role
            if role == "system":
                lines.append("## System Prompt")
                lines.append("")
                lines.append(f"```\n{content}\n```")
            elif role == "user":
                lines.append(f"## User Message {i+1}")
                if timestamp:
                    lines.append(f"*{timestamp}*")
                lines.append("")
                lines.append(content)
            elif role == "assistant":
                lines.append(f"## Assistant Response {i+1}")
                if timestamp:
                    lines.append(f"*{timestamp}*")
                lines.append("")
                lines.append(content)
            else:
                lines.append(f"## {role.title()} {i+1}")
                lines.append("")
                lines.append(content)

            lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _format_as_jsonl(self, messages) -> str:
        """Format messages as JSONL (JSON Lines).

        Args:
            messages: List of conversation messages.

        Returns:
            JSONL formatted string.
        """
        import json
        lines = []

        for msg in messages:
            lines.append(json.dumps(msg))

        return "\n".join(lines)

    def _format_as_raw_api(self, messages) -> str:
        """Format messages as exact API payload JSON.

        This format mirrors EXACTLY what is sent to and received from the LLM API.
        Useful for debugging, replay, and verification.

        Args:
            messages: List of conversation messages.

        Returns:
            JSON formatted string matching API payload structure.
        """
        import json

        # Build the exact payload structure sent to the API
        api_messages = []
        for msg in messages:
            api_messages.append({
                "role": msg.get("role"),
                "content": msg.get("content")
            })

        # Get model info from config if available
        model = "unknown"
        temperature = 0.7
        if self.config:
            model = self.config.get("core.llm.model", "unknown")
            temperature = self.config.get("core.llm.temperature", 0.7)

        payload = {
            "model": model,
            "messages": api_messages,
            "temperature": temperature,
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "message_count": len(messages),
                "format": "raw_api_payload"
            }
        }

        return json.dumps(payload, indent=2, ensure_ascii=False)

    def _save_to_file(self, content: str, output_dir: str, format_type: str, auto_timestamp: bool) -> Path:
        """Save content to file.

        Args:
            content: Content to save.
            output_dir: Output directory path.
            format_type: Format type for file extension.
            auto_timestamp: Whether to add timestamp to filename.

        Returns:
            Path to saved file.
        """
        # Create output directory
        from core.utils.config_utils import get_config_directory
        config_dir = get_config_directory()

        # Handle relative paths
        if not output_dir.startswith('/'):
            save_dir = config_dir / output_dir
        else:
            save_dir = Path(output_dir)

        save_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if auto_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}"
        else:
            filename = "conversation"

        # Add extension based on format
        if format_type == "raw":
            filename += ".json"
        elif format_type == "jsonl":
            filename += ".jsonl"
        elif format_type == "markdown":
            filename += ".md"
        else:
            filename += ".txt"

        filepath = save_dir / filename

        # Write to file
        filepath.write_text(content, encoding='utf-8')

        self.logger.info(f"Saved conversation to: {filepath}")
        return filepath

    def _copy_to_clipboard(self, content: str) -> bool:
        """Copy content to system clipboard.

        Args:
            content: Content to copy.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Try pbcopy (macOS)
            try:
                process = subprocess.Popen(
                    ['pbcopy'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=content.encode('utf-8'))
                self.logger.info("Copied to clipboard using pbcopy")
                return True
            except FileNotFoundError:
                pass

            # Try xclip (Linux)
            try:
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=content.encode('utf-8'))
                self.logger.info("Copied to clipboard using xclip")
                return True
            except FileNotFoundError:
                pass

            # Try xsel (Linux alternative)
            try:
                process = subprocess.Popen(
                    ['xsel', '--clipboard', '--input'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=content.encode('utf-8'))
                self.logger.info("Copied to clipboard using xsel")
                return True
            except FileNotFoundError:
                pass

            # Try wl-copy (Wayland)
            try:
                process = subprocess.Popen(
                    ['wl-copy'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=content.encode('utf-8'))
                self.logger.info("Copied to clipboard using wl-copy")
                return True
            except FileNotFoundError:
                pass

            self.logger.warning("No clipboard utility found (pbcopy, xclip, xsel, wl-copy)")
            return False

        except Exception as e:
            self.logger.error(f"Error copying to clipboard: {e}")
            return False

    async def shutdown(self) -> None:
        """Shutdown the plugin and cleanup resources."""
        try:
            self.logger.info("Save conversation plugin shutdown completed")
        except Exception as e:
            self.logger.error(f"Error shutting down save conversation plugin: {e}")

    async def register_hooks(self) -> None:
        """Register event hooks for the plugin."""
        pass

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration for save conversation plugin."""
        return {
            "plugins": {
                "save_conversation": {
                    "enabled": True,
                    "default_format": "transcript",
                    "default_destination": "file",
                    "auto_timestamp": True,
                    "output_directory": "logs/transcripts"
                }
            }
        }
