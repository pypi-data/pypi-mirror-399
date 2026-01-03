"""Main application orchestrator for Kollabor CLI."""

import asyncio
import logging
import re
import sys
from pathlib import Path
from importlib.metadata import version as get_version, PackageNotFoundError

from .config import ConfigService

def _get_version_from_pyproject() -> str:
    """Read version from pyproject.toml for development mode."""
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
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
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        return pyproject_path.exists()
    except Exception:
        return False

# Get version: prefer pyproject.toml when running from source, otherwise use installed version
if _is_running_from_source():
    # Development mode: use pyproject.toml
    __version__ = _get_version_from_pyproject() or "0.0.0"
else:
    # Production mode: use installed package version
    try:
        __version__ = get_version("kollabor")
    except PackageNotFoundError:
        __version__ = "0.0.0"
from .events import EventBus
from .io import InputHandler, TerminalRenderer
from .io.visual_effects import VisualEffects
from .llm import LLMService, KollaborConversationLogger, LLMHookSystem, MCPIntegration, KollaborPluginSDK
from .llm.profile_manager import ProfileManager
from .llm.agent_manager import AgentManager
from .logging import setup_from_config
from .plugins import PluginRegistry
from .storage import StateManager

logger = logging.getLogger(__name__)


class TerminalLLMChat:
    """Main Kollabor CLI application.
    
    Orchestrates all components including rendering, input handling,
    event processing, and plugin management.
    """
    
    def __init__(
        self,
        system_prompt_file: str | None = None,
        agent_name: str | None = None,
        profile_name: str | None = None,
    ) -> None:
        """Initialize the chat application.

        Args:
            system_prompt_file: Optional path to a custom system prompt file
                               (overrides all other system prompt sources)
            agent_name: Optional agent name to use (e.g., "lint-editor")
            profile_name: Optional LLM profile name to use (e.g., "claude")
        """
        # Get configuration directory using standard resolution
        from .utils.config_utils import (
            get_config_directory,
            ensure_config_directory,
            initialize_system_prompt,
            set_cli_system_prompt_file,
        )

        # Set CLI system prompt override if provided
        if system_prompt_file:
            set_cli_system_prompt_file(system_prompt_file)

        self.config_dir = ensure_config_directory()
        logger.info(f"Using config directory: {self.config_dir}")

        # Initialize system prompt (copies default.md to config directories)
        initialize_system_prompt()

        # Flag to indicate if we're in pipe mode (for plugins to check)
        self.pipe_mode = False

        # Initialize plugin registry and discover plugins
        # Try package installation directory first (for pip install), then cwd (for development)
        package_dir = Path(__file__).parent.parent  # Go up from core/ to package root
        plugins_dir = package_dir / "plugins"
        if not plugins_dir.exists():
            plugins_dir = Path.cwd() / "plugins"  # Fallback for development mode
            logger.info(f"Using development plugins directory: {plugins_dir}")
        else:
            logger.info(f"Using installed package plugins directory: {plugins_dir}")

        self.plugin_registry = PluginRegistry(plugins_dir)
        self.plugin_registry.load_all_plugins()
        
        # Initialize configuration service with plugin registry
        self.config = ConfigService(self.config_dir / "config.json", self.plugin_registry)

        # Update config file with plugin configurations
        self.config.update_from_plugins()

        # Initialize profile manager (for LLM endpoint profiles)
        self.profile_manager = ProfileManager(self.config)
        if profile_name:
            if not self.profile_manager.set_active_profile(profile_name):
                logger.warning(f"Profile '{profile_name}' not found, using default")

        # Initialize agent manager (for agent/skill system)
        self.agent_manager = AgentManager(self.config)
        if agent_name:
            if not self.agent_manager.set_active_agent(agent_name):
                logger.warning(f"Agent '{agent_name}' not found")

        # If agent has a preferred profile, use it (unless profile was explicitly set)
        if not profile_name:
            agent_profile = self.agent_manager.get_preferred_profile()
            if agent_profile:
                if self.profile_manager.set_active_profile(agent_profile):
                    logger.info(f"Using agent's preferred profile: {agent_profile}")

        # Reconfigure logging now that config system is available
        setup_from_config(self.config.config_manager.config)
        
        # Initialize core components
        self.state_manager = StateManager(str(self.config_dir / "state.db"))
        self.event_bus = EventBus()

        # Initialize status view registry for flexible status display
        from .io.status_renderer import StatusViewRegistry
        from .io.config_status_view import ConfigStatusView
        self.status_registry = StatusViewRegistry(self.event_bus)

        # Add config status view to registry
        config_status_view = ConfigStatusView(self.config, self.event_bus)
        config_view_config = config_status_view.get_status_view_config()
        self.status_registry.register_status_view("core", config_view_config)

        # Initialize renderer with status registry and config
        self.renderer = TerminalRenderer(self.event_bus, self.config)
        if hasattr(self.renderer, 'status_renderer'):
            self.renderer.status_renderer.status_registry = self.status_registry

        self.input_handler = InputHandler(self.event_bus, self.renderer, self.config)

        # Give terminal renderer access to input handler for modal state checking
        self.renderer.input_handler = self.input_handler

        # Initialize visual effects system
        self.visual_effects = VisualEffects()

        # Initialize slash command system
        logger.info("About to initialize slash command system")
        self._initialize_slash_commands()

        # Initialize fullscreen plugin commands
        self._initialize_fullscreen_commands()
        logger.info("Slash command system initialization completed")

        # Initialize LLM core service components
        conversations_dir = self.config_dir / "conversations"
        conversations_dir.mkdir(parents=True, exist_ok=True)
        self.conversation_logger = KollaborConversationLogger(conversations_dir)
        self.llm_hook_system = LLMHookSystem(self.event_bus)
        self.mcp_integration = MCPIntegration()
        self.plugin_sdk = KollaborPluginSDK()
        self.llm_service = LLMService(
            config=self.config,
            state_manager=self.state_manager,
            event_bus=self.event_bus,
            renderer=self.renderer,
            profile_manager=self.profile_manager,
            agent_manager=self.agent_manager,
        )
        
        # Configure renderer with thinking effect and shimmer parameters
        thinking_effect = self.config.get("terminal.thinking_effect", "shimmer")
        shimmer_speed = self.config.get("terminal.shimmer_speed", 3)
        shimmer_wave_width = self.config.get("terminal.shimmer_wave_width", 4)
        thinking_limit = self.config.get("terminal.thinking_message_limit", 2)
        
        self.renderer.set_thinking_effect(thinking_effect)
        self.renderer.configure_shimmer(shimmer_speed, shimmer_wave_width)
        self.renderer.configure_thinking_limit(thinking_limit)
        
        # Dynamically instantiate all discovered plugins
        self.plugin_instances = self.plugin_registry.instantiate_plugins(
            self.state_manager, self.event_bus, self.renderer, self.config
        )

        # Task tracking for race condition prevention
        self.running = False
        self._startup_complete = False
        self._background_tasks = []
        self._task_lock = asyncio.Lock()

        logger.info("Kollabor CLI initialized")
    
    async def start(self) -> None:
        """Start the chat application with guaranteed cleanup."""
        # Display startup messages using config
        self._display_startup_messages()

        logger.info("Application starting")

        render_task = None
        input_task = None

        try:
            # Initialize LLM core service
            await self._initialize_llm_core()

            # Initialize all plugins dynamically
            await self._initialize_plugins()

            # Register default core status views
            await self._register_core_status_views()

            # Mark startup as complete
            self._startup_complete = True
            logger.info("Application startup complete")

            # Start main loops with task tracking
            self.running = True
            render_task = self.create_background_task(
                self._render_loop(), "render_loop"
            )
            input_task = self.create_background_task(
                self.input_handler.start(), "input_handler"
            )

            # Wait for completion
            await asyncio.gather(render_task, input_task)

        except KeyboardInterrupt:
            print("\r\n")
            # print("\r\nInterrupted by user")
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error during startup: {e}")
            raise
        finally:
            # Guaranteed cleanup - always runs regardless of how we exit
            logger.info("Executing guaranteed cleanup")
            await self.cleanup()

    async def start_pipe_mode(self, piped_input: str, timeout: int = 120) -> None:
        """Start in pipe mode: process input and exit after response.

        Args:
            piped_input: Input text from stdin/pipe
            timeout: Maximum time to wait for processing in seconds (default: 120)
        """
        # Set a flag to indicate we're in pipe mode (plugins can check this)
        self.pipe_mode = True
        self.renderer.pipe_mode = True  # Also set on renderer for llm_service access
        # Propagate pipe_mode to message renderer and conversation renderer
        if hasattr(self.renderer, 'message_renderer'):
            self.renderer.message_renderer.pipe_mode = True
            if hasattr(self.renderer.message_renderer, 'conversation_renderer'):
                self.renderer.message_renderer.conversation_renderer.pipe_mode = True

        try:
            # Initialize LLM core service
            await self._initialize_llm_core()

            # Initialize plugins (they should check self.pipe_mode if needed)
            await self._initialize_plugins()

            # Mark startup as complete
            self._startup_complete = True
            self.running = True
            logger.info("Pipe mode initialized with plugins")

            # Send input to LLM and wait for response
            # The LLM service will handle the response display
            await self.llm_service.process_user_input(piped_input)

            # Wait for processing to start (max 10 seconds)
            start_timeout = 10
            start_wait = 0
            while not self.llm_service.is_processing and start_wait < start_timeout:
                await asyncio.sleep(0.1)
                start_wait += 0.1

            # Wait for processing to complete (including all tool calls and continuations)
            max_wait = timeout
            wait_time = 0
            while self.llm_service.is_processing and not self.llm_service.cancel_processing and wait_time < max_wait:
                await asyncio.sleep(0.1)
                wait_time += 0.1

            # Give a tiny bit of extra time for final display rendering
            await asyncio.sleep(0.2)

            logger.info("Pipe mode processing complete")

        except KeyboardInterrupt:
            logger.info("Pipe mode interrupted by user")
        except Exception as e:
            logger.error(f"Pipe mode error: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            # Cleanup
            self.running = False
            # Keep pipe_mode=True during cleanup so cancellation messages can be suppressed
            await self.cleanup()
            # DON'T reset pipe_mode here - let main.py's finally block check it to avoid double cleanup

    def _display_startup_messages(self) -> None:
        """Display startup messages with plugin information."""
        # Display Kollabor banner with version from package metadata
        kollabor_banner = self.renderer.create_kollabor_banner(f"v{__version__}")
        print(kollabor_banner)

        # LLM Core status
        #print(f"\033[2;35mLLM Core: \033[2;32mActive\033[0m")

        # Plugin discovery section - clean and compact
        discovered_plugins = self.plugin_registry.list_plugins()
        if discovered_plugins:
            # Simple plugin list
            plugin_list = "//".join(discovered_plugins)
            #print(f"\033[2;36mPlugins enabled: \033[2;37m{plugin_list}\033[0m")
            print()
        else:
            #print("\033[2;31mNo plugins found\033[0m")
            print()

        # Ready message with gradient and bold Enter
        ready_msg = "Ready! Type your message and press "
        enter_text = "Enter"
        end_text = "."

        # Apply white to dim white gradient to the message
        gradient_msg = self.visual_effects.apply_message_gradient(ready_msg, "dim_white")
        bold_enter = f"\033[1m{enter_text}\033[0m"  # Bold Enter
        gradient_end = self.visual_effects.apply_message_gradient(end_text, "dim_white")

        print(gradient_msg + bold_enter + gradient_end)
        print()

    
    async def _initialize_llm_core(self) -> None:
        """Initialize LLM core service components."""
        # Initialize LLM service
        await self.llm_service.initialize()
        logger.info("LLM core service initialized")

        # Update system_commands with llm_service reference (it was None during init)
        if hasattr(self, 'system_commands') and self.system_commands:
            self.system_commands.llm_service = self.llm_service
            logger.debug("Updated system_commands with llm_service reference")

        # Register LLM hooks
        await self.llm_hook_system.register_hooks()
        logger.info("LLM hook system registered")

        # Initialize conversation logger
        await self.conversation_logger.initialize()
        logger.info("Conversation logger initialized")

        # Discover MCP servers
        mcp_servers = await self.mcp_integration.discover_mcp_servers()
        if mcp_servers:
            logger.info(f"Discovered {len(mcp_servers)} MCP servers")

        # Register LLM service hooks for user input processing
        await self.llm_service.register_hooks()
    
    async def _initialize_plugins(self) -> None:
        """Initialize all discovered plugins."""
        # Deduplicate plugin instances by ID (same instance may be stored under multiple keys)
        initialized_instances = set()

        for plugin_name, plugin_instance in self.plugin_instances.items():
            instance_id = id(plugin_instance)

            # Skip if we've already initialized this instance
            if instance_id in initialized_instances:
                continue

            initialized_instances.add(instance_id)

            if hasattr(plugin_instance, 'initialize'):
                # Pass command registry, input handler, llm_service, and renderer to plugins that might need it
                init_kwargs = {
                    'event_bus': self.event_bus,
                    'config': self.config,
                    'command_registry': getattr(self.input_handler, 'command_registry', None),
                    'input_handler': self.input_handler,
                    'renderer': self.renderer,
                    'llm_service': self.llm_service,
                    # Use llm_service's conversation_logger (the one actively logging)
                    'conversation_logger': getattr(self.llm_service, 'conversation_logger', self.conversation_logger),
                    'conversation_manager': getattr(self.llm_service, 'conversation_manager', None),
                    'state_manager': self.state_manager
                }

                # Check if initialize method accepts keyword arguments
                import inspect
                sig = inspect.signature(plugin_instance.initialize)
                if len(sig.parameters) > 0:
                    await plugin_instance.initialize(**init_kwargs)
                else:
                    await plugin_instance.initialize()
                logger.debug(f"Initialized plugin: {plugin_name}")

            if hasattr(plugin_instance, 'register_hooks'):
                await plugin_instance.register_hooks()
                logger.debug(f"Registered hooks for plugin: {plugin_name}")

        # Register system commands hooks (for modal command handling)
        if hasattr(self, 'system_commands') and self.system_commands:
            await self.system_commands.register_hooks()
            logger.debug("Registered hooks for system commands")

    def _initialize_slash_commands(self) -> None:
        """Initialize the slash command system with core commands."""
        logger.info("Starting slash command system initialization...")
        try:
            from core.commands.system_commands import SystemCommandsPlugin
            logger.info("SystemCommandsPlugin imported successfully")

            # Create and register system commands
            # Note: llm_service is passed if available, but may be None at this point
            self.system_commands = SystemCommandsPlugin(
                command_registry=self.input_handler.command_registry,
                event_bus=self.event_bus,
                config_manager=self.config,
                llm_service=getattr(self, 'llm_service', None),
                profile_manager=getattr(self, 'profile_manager', None),
                agent_manager=getattr(self, 'agent_manager', None),
            )
            logger.info("SystemCommandsPlugin instance created")

            # Register all system commands
            self.system_commands.register_commands()
            logger.info("System commands registration completed")

            stats = self.input_handler.command_registry.get_registry_stats()
            logger.info("Slash command system initialized with system commands")
            logger.info(f"[INFO] {stats['total_commands']} commands registered")

        except Exception as e:
            logger.error(f"Failed to initialize slash command system: {e}")
            import traceback
            logger.error(f"[INFO] Traceback: {traceback.format_exc()}")

    def _initialize_fullscreen_commands(self) -> None:
        """Initialize dynamic fullscreen plugin commands."""
        try:
            from core.fullscreen.command_integration import FullScreenCommandIntegrator

            # Create the integrator
            self.fullscreen_integrator = FullScreenCommandIntegrator(
                command_registry=self.input_handler.command_registry,
                event_bus=self.event_bus
            )

            # Discover and register all fullscreen plugins
            # Use same plugin directory resolution as main plugin registry
            package_dir = Path(__file__).parent.parent
            plugins_dir = package_dir / "plugins"
            if not plugins_dir.exists():
                plugins_dir = Path.cwd() / "plugins"
            registered_count = self.fullscreen_integrator.discover_and_register_plugins(plugins_dir)

            logger.info(f"Fullscreen plugin commands initialized: {registered_count} plugins registered")

        except Exception as e:
            logger.error(f"Failed to initialize fullscreen commands: {e}")
            import traceback
            logger.error(f"Fullscreen commands traceback: {traceback.format_exc()}")

    async def _render_loop(self) -> None:
        """Main rendering loop for status updates."""
        logger.info("Render loop starting...")
        while self.running:
            try:
                # Render active area (status views use content providers)
                await self.renderer.render_active_area()

                # Use configured FPS for render timing
                render_fps = self.config.get("terminal.render_fps", 20)
                await asyncio.sleep(1.0 / render_fps)

            except Exception as e:
                logger.error(f"Render loop error: {e}")
                error_delay = self.config.get("terminal.render_error_delay", 0.1)
                await asyncio.sleep(error_delay)

    async def _register_core_status_views(self) -> None:
        """Register default core status views."""
        try:
            from .io.core_status_views import CoreStatusViews
            core_views = CoreStatusViews(
                llm_service=self.llm_service,
                config=self.config,
                profile_manager=getattr(self, 'profile_manager', None),
                agent_manager=getattr(self, 'agent_manager', None),
            )
            core_views.register_all_views(self.status_registry)
        except Exception as e:
            logger.error(f"Failed to register core status views: {e}")

    def create_background_task(self, coro, name: str = "unnamed"):
        """Create and track a background task with automatic cleanup.

        Args:
            coro: Coroutine to run as background task
            name: Human-readable name for the task

        Returns:
            The created asyncio.Task
        """
        task = asyncio.create_task(coro)
        task.set_name(name)
        self._background_tasks.append(task)
        logger.debug(f"Created background task: {name}")

        # Add callback to remove task from tracking when done
        def remove_task(t):
            try:
                self._background_tasks.remove(t)
                logger.debug(f"Background task completed: {name}")
            except ValueError:
                pass  # Task already removed

        task.add_done_callback(remove_task)
        return task

    async def cleanup(self) -> None:
        """Clean up all resources and cancel background tasks.

        This method is guaranteed to run on all exit paths via finally block.
        Ensures no orphaned tasks or resources remain.
        """
        logger.info("Starting application cleanup...")

        # Cancel all tracked background tasks
        if self._background_tasks:
            logger.info(f"Cancelling {len(self._background_tasks)} background tasks")
            for task in self._background_tasks[:]:  # Copy list to avoid modification during iteration
                if not task.done():
                    task.cancel()

            # Wait for all tasks to complete with timeout
            if self._background_tasks:
                try:
                    await asyncio.wait_for(
                        asyncio.gather(*self._background_tasks, return_exceptions=True),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    logger.warning("Some tasks did not complete within timeout")
                except Exception as e:
                    logger.error(f"Error during task cleanup: {e}")

        # Clear task list
        self._background_tasks.clear()

        # Mark startup as incomplete
        self._startup_complete = False
        self.running = False

        # Call full shutdown to cleanup other resources
        await self.shutdown()

        logger.info("Application cleanup complete")

    def get_system_status(self):
        """Get current system status for monitoring and debugging.

        Returns:
            Dictionary containing system status information
        """
        return {
            "running": self.running,
            "startup_complete": self._startup_complete,
            "background_tasks": len(self._background_tasks),
            "plugins_loaded": len(self.plugin_instances),
            "task_names": [task.get_name() for task in self._background_tasks]
        }

    async def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        logger.info("Application shutting down")
        self.running = False
        
        # Stop input handler
        await self.input_handler.stop()
        
        # Shutdown LLM core service
        await self.llm_service.shutdown()
        await self.conversation_logger.shutdown()
        await self.mcp_integration.shutdown()
        logger.info("LLM core service shutdown complete")
        
        # Shutdown all plugins dynamically
        for plugin_name, plugin_instance in self.plugin_instances.items():
            if hasattr(plugin_instance, 'shutdown'):
                try:
                    await plugin_instance.shutdown()
                    logger.debug(f"Shutdown plugin: {plugin_name}")
                except Exception as e:
                    logger.warning(f"Error shutting down plugin {plugin_name}: {e}")
        
        # Clear active area (input box) before restoring terminal
        if not self.pipe_mode:
            self.renderer.clear_active_area(force=True)

        # Restore terminal
        self.renderer.exit_raw_mode()
        # Only show cursor if not in pipe mode
        if not self.pipe_mode:
            print("\033[?25h")  # Show cursor
        
        # Close state manager
        self.state_manager.close()
        logger.info("Application shutdown complete")