"""Core status views for the Kollabor CLI application.

All views use the agnoster powerline style with lime/cyan color scheme.
"""

import logging
from pathlib import Path
from typing import List

from .status_renderer import StatusViewConfig, BlockConfig
from .visual_effects import AgnosterSegment, ColorPalette

logger = logging.getLogger(__name__)


class CoreStatusViews:
    """Provides agnoster-styled core status views."""

    def __init__(self, llm_service=None, config=None, profile_manager=None, agent_manager=None):
        """Initialize core status views."""
        self.llm_service = llm_service
        self.config = config
        self.profile_manager = profile_manager
        self.agent_manager = agent_manager

    def register_all_views(self, status_registry) -> None:
        """Register all core status views."""
        try:
            # View 1: Overview (priority 1100 - highest)
            status_registry.register_status_view("core", StatusViewConfig(
                name="Overview",
                plugin_source="core",
                priority=1100,
                blocks=[BlockConfig(
                    width_fraction=1.0,
                    content_provider=self._overview_content,
                    title="Overview",
                    priority=100,
                )],
            ))

            # View 2: Session Stats (priority 1000)
            status_registry.register_status_view("core", StatusViewConfig(
                name="Session",
                plugin_source="core",
                priority=1000,
                blocks=[BlockConfig(
                    width_fraction=1.0,
                    content_provider=self._session_content,
                    title="Session",
                    priority=100,
                )],
            ))

            # View 3: LLM Details (priority 900)
            status_registry.register_status_view("core", StatusViewConfig(
                name="LLM Details",
                plugin_source="core",
                priority=900,
                blocks=[BlockConfig(
                    width_fraction=1.0,
                    content_provider=self._llm_details_content,
                    title="LLM",
                    priority=100,
                )],
            ))

            # View 4: Minimal (priority 600)
            status_registry.register_status_view("core", StatusViewConfig(
                name="Minimal",
                plugin_source="core",
                priority=600,
                blocks=[BlockConfig(
                    width_fraction=1.0,
                    content_provider=self._minimal_content,
                    title="Minimal",
                    priority=100,
                )],
            ))

            logger.info("Registered 4 core status views")

        except Exception as e:
            logger.error(f"Failed to register core status views: {e}")

    def _get_dir_display(self) -> str:
        """Get formatted directory display."""
        try:
            cwd = Path.cwd()
            home = Path.home()
            if cwd == home:
                return "~"
            elif cwd.is_relative_to(home):
                rel_path = cwd.relative_to(home)
                parts = rel_path.parts
                if len(parts) > 2:
                    return f"~/{'/'.join(parts[-2:])}"
                return f"~/{rel_path}"
            return cwd.name or str(cwd)
        except Exception:
            return "?"

    def _get_profile_name(self) -> str:
        """Get active profile name."""
        if self.profile_manager:
            profile = self.profile_manager.get_active_profile()
            if profile:
                return profile.name
        return "default"

    def _get_model_info(self) -> tuple:
        """Get model name and endpoint."""
        model = "unknown"
        endpoint = ""
        if self.llm_service and hasattr(self.llm_service, "api_service"):
            api_service = self.llm_service.api_service
            model = getattr(api_service, "model", "unknown")
            api_url = getattr(api_service, "api_url", "")
            if api_url:
                try:
                    from urllib.parse import urlparse
                    endpoint = urlparse(api_url).hostname or ""
                except Exception:
                    pass
        return model, endpoint

    def _get_status(self) -> tuple:
        """Get status text and variant."""
        if self.llm_service and self.llm_service.is_processing:
            return "* Working", "light"
        return "* Ready", "normal"

    def _get_stats(self) -> tuple:
        """Get message count and token display."""
        msgs = 0
        tokens = 0
        if self.llm_service and hasattr(self.llm_service, "session_stats"):
            stats = self.llm_service.session_stats
            msgs = stats.get("messages", 0)
            tokens = stats.get("input_tokens", 0) + stats.get("output_tokens", 0)

        if tokens < 1000:
            token_display = f"{tokens}"
        elif tokens < 1000000:
            token_display = f"{tokens/1000:.1f}K"
        else:
            token_display = f"{tokens/1000000:.1f}M"

        return msgs, token_display

    def _overview_content(self) -> List[str]:
        """Agnoster overview: dir | profile | model@endpoint | status | stats."""
        try:
            seg = AgnosterSegment()

            # Directory (lime dark)
            seg.add_lime(self._get_dir_display(), "dark")

            # Profile (cyan dark)
            seg.add_cyan(self._get_profile_name(), "dark")

            # Model @ Endpoint (lime)
            model, endpoint = self._get_model_info()
            model_text = f"{model} @ {endpoint}" if endpoint else model
            seg.add_lime(model_text)

            # Status (cyan)
            status_text, variant = self._get_status()
            seg.add_cyan(status_text, variant)

            # Stats (neutral)
            msgs, token_display = self._get_stats()
            seg.add_neutral(f"{msgs} msg | {token_display} tok", "mid")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Overview error: {e}")
            return [f"{ColorPalette.DIM}Status unavailable{ColorPalette.RESET}"]

    def _session_content(self) -> List[str]:
        """Agnoster session: messages | tokens in | tokens out | total."""
        try:
            seg = AgnosterSegment()

            msgs = 0
            tokens_in = 0
            tokens_out = 0
            if self.llm_service and hasattr(self.llm_service, "session_stats"):
                stats = self.llm_service.session_stats
                msgs = stats.get("messages", 0)
                tokens_in = stats.get("input_tokens", 0)
                tokens_out = stats.get("output_tokens", 0)

            seg.add_lime(f"Messages: {msgs}", "dark")
            seg.add_cyan(f"In: {tokens_in}", "dark")
            seg.add_lime(f"Out: {tokens_out}")
            seg.add_cyan(f"Total: {tokens_in + tokens_out}")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Session error: {e}")
            return [f"{ColorPalette.DIM}Session unavailable{ColorPalette.RESET}"]

    def _llm_details_content(self) -> List[str]:
        """Agnoster LLM details: status | model | endpoint | temp | max_tokens."""
        try:
            seg = AgnosterSegment()

            status_text, _ = self._get_status()
            model, endpoint = self._get_model_info()

            temp = "?"
            max_tokens = "?"
            if self.llm_service and hasattr(self.llm_service, "api_service"):
                api_service = self.llm_service.api_service
                temp = getattr(api_service, "temperature", "?")
                max_tokens = getattr(api_service, "max_tokens", None) or "None"

            seg.add_lime(status_text, "dark")
            seg.add_cyan(f"Model: {model}", "dark")
            seg.add_lime(f"@ {endpoint}" if endpoint else "local")
            seg.add_cyan(f"Temp: {temp}")
            seg.add_neutral(f"Max: {max_tokens}", "mid")

            return [seg.render()]

        except Exception as e:
            logger.error(f"LLM details error: {e}")
            return [f"{ColorPalette.DIM}LLM unavailable{ColorPalette.RESET}"]

    def _minimal_content(self) -> List[str]:
        """Agnoster minimal: status | model | msgs | tokens."""
        try:
            seg = AgnosterSegment()

            status_text, variant = self._get_status()
            model, _ = self._get_model_info()
            msgs, token_display = self._get_stats()

            seg.add_lime(status_text, "dark")
            seg.add_cyan(model, "dark")
            seg.add_neutral(f"{msgs} msg | {token_display} tok", "mid")

            return [seg.render()]

        except Exception as e:
            logger.error(f"Minimal error: {e}")
            return [f"{ColorPalette.DIM}--{ColorPalette.RESET}"]
