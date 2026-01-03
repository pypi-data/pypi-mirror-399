"""Configuration widget definitions for modal UI."""

from typing import Dict, Any, List
import logging
import importlib
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigWidgetDefinitions:
    """Defines which config values get which widgets in the modal."""

    @staticmethod
    def get_available_plugins() -> List[Dict[str, Any]]:
        """Dynamically discover available plugins for configuration.

        Scans the plugins directory for *_plugin.py files and extracts
        metadata from each plugin class.

        Returns:
            List of plugin widget dictionaries.
        """
        plugins = []

        # Find plugins directory
        plugins_dir = Path(__file__).parent.parent.parent / "plugins"
        if not plugins_dir.exists():
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return plugins

        # Scan for plugin files
        for plugin_file in sorted(plugins_dir.glob("*_plugin.py")):
            try:
                module_name = plugin_file.stem  # e.g., "tmux_plugin"
                plugin_id = module_name.replace("_plugin", "")  # e.g., "tmux"

                # Try to import and get metadata
                try:
                    module = importlib.import_module(f"plugins.{module_name}")

                    # Find the plugin class (ends with "Plugin")
                    plugin_class = None
                    for name in dir(module):
                        obj = getattr(module, name)
                        if isinstance(obj, type) and name.endswith("Plugin") and name != "Plugin":
                            plugin_class = obj
                            break

                    if plugin_class:
                        # Get name and description from class attributes
                        instance_name = getattr(plugin_class, 'name', None)
                        if instance_name is None:
                            # Try to get from a temporary instance or use default
                            instance_name = plugin_id.replace("_", " ").title()

                        description = getattr(plugin_class, 'description', None)
                        if description is None:
                            description = f"{instance_name} plugin"

                        # Use class-level name/description or instance defaults
                        display_name = instance_name if isinstance(instance_name, str) else plugin_id.replace("_", " ").title()

                        plugins.append({
                            "type": "checkbox",
                            "label": display_name.replace("_", " ").title() if display_name == plugin_id else display_name,
                            "config_path": f"plugins.{plugin_id}.enabled",
                            "help": description if isinstance(description, str) else f"{display_name} plugin"
                        })
                        logger.debug(f"Discovered plugin: {plugin_id}")

                except ImportError as e:
                    logger.debug(f"Could not import plugin {module_name}: {e}")
                    # Still add it with basic info
                    plugins.append({
                        "type": "checkbox",
                        "label": plugin_id.replace("_", " ").title(),
                        "config_path": f"plugins.{plugin_id}.enabled",
                        "help": f"{plugin_id.replace('_', ' ').title()} plugin"
                    })

            except Exception as e:
                logger.error(f"Error processing plugin file {plugin_file}: {e}")

        logger.info(f"Discovered {len(plugins)} plugins for configuration")
        return plugins

    @staticmethod
    def get_plugin_config_sections() -> List[Dict[str, Any]]:
        """Dynamically collect config widget sections from plugins.

        Looks for get_config_widgets() method on each plugin class.

        Returns:
            List of section definitions from plugins.
        """
        sections = []

        # Known plugin modules and their class names
        plugin_modules = {
            "plugins.enhanced_input_plugin": "EnhancedInputPlugin",
            "plugins.hook_monitoring_plugin": "HookMonitoringPlugin",
            "plugins.query_enhancer_plugin": "QueryEnhancerPlugin",
            "plugins.workflow_enforcement_plugin": "WorkflowEnforcementPlugin",
            "plugins.system_commands_plugin": "SystemCommandsPlugin",
        }

        for module_name, class_name in plugin_modules.items():
            try:
                module = importlib.import_module(module_name)
                plugin_class = getattr(module, class_name, None)

                if plugin_class and hasattr(plugin_class, "get_config_widgets"):
                    widget_section = plugin_class.get_config_widgets()
                    if widget_section:
                        sections.append(widget_section)
                        logger.debug(f"Loaded config widgets from {class_name}")
            except Exception as e:
                logger.debug(f"Could not load config widgets from {module_name}: {e}")

        return sections

    @staticmethod
    def get_config_modal_definition() -> Dict[str, Any]:
        """Get the complete modal definition for /config command.

        Returns:
            Dictionary defining the modal layout and widgets.
        """
        # Get plugin widgets
        plugin_widgets = ConfigWidgetDefinitions.get_available_plugins()

        return {
            "title": "System Configuration",
            "footer": "↑↓/PgUp/PgDn navigate • Enter toggle • Ctrl+S save • Esc cancel",
            "width": 120,  # 80% of screen width
            "height": 40,
            "sections": [
                {
                    "title": "Terminal Settings",
                    "widgets": [
                        {
                            "type": "slider",
                            "label": "Render FPS",
                            "config_path": "terminal.render_fps",
                            "min_value": 1,
                            "max_value": 60,
                            "step": 1,
                            "help": "Terminal refresh rate (1-60 FPS)"
                        },
                        {
                            "type": "slider",
                            "label": "Status Lines",
                            "config_path": "terminal.status_lines",
                            "min_value": 1,
                            "max_value": 10,
                            "step": 1,
                            "help": "Number of status lines to display"
                        },
                        {
                            "type": "dropdown",
                            "label": "Thinking Effect",
                            "config_path": "terminal.thinking_effect",
                            "options": ["shimmer", "pulse", "wave", "none"],
                            "help": "Visual effect for thinking animations"
                        },
                        {
                            "type": "slider",
                            "label": "Shimmer Speed",
                            "config_path": "terminal.shimmer_speed",
                            "min_value": 1,
                            "max_value": 10,
                            "step": 1,
                            "help": "Speed of shimmer animation effect"
                        },
                        {
                            "type": "checkbox",
                            "label": "Enable Render Cache",
                            "config_path": "terminal.render_cache_enabled",
                            "help": "Cache renders to reduce unnecessary terminal I/O when idle"
                        }
                    ]
                },
                {
                    "title": "Input Settings",
                    "widgets": [
                        {
                            "type": "checkbox",
                            "label": "Ctrl+C Exit",
                            "config_path": "input.ctrl_c_exit",
                            "help": "Allow Ctrl+C to exit application"
                        },
                        {
                            "type": "checkbox",
                            "label": "Backspace Enabled",
                            "config_path": "input.backspace_enabled",
                            "help": "Enable backspace key for text editing"
                        },
                        {
                            "type": "slider",
                            "label": "History Limit",
                            "config_path": "input.history_limit",
                            "min_value": 10,
                            "max_value": 1000,
                            "step": 10,
                            "help": "Maximum number of history entries"
                        }
                    ]
                },
                {
                    "title": "LLM Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "API URL",
                            "config_path": "core.llm.api_url",
                            "placeholder": "http://localhost:1234",
                            "help": "LLM API endpoint URL"
                        },
                        {
                            "type": "text_input",
                            "label": "Model",
                            "config_path": "core.llm.model",
                            "placeholder": "qwen/qwen3-4b",
                            "help": "LLM model identifier"
                        },
                        {
                            "type": "slider",
                            "label": "Temperature",
                            "config_path": "core.llm.temperature",
                            "min_value": 0.0,
                            "max_value": 2.0,
                            "step": 0.1,
                            "help": "Creativity/randomness of responses (0.0-2.0)"
                        },
                        {
                            "type": "slider",
                            "label": "Max History",
                            "config_path": "core.llm.max_history",
                            "min_value": 10,
                            "max_value": 200,
                            "step": 10,
                            "help": "Maximum conversation history entries"
                        }
                    ]
                },
                {
                    "title": "Application Settings",
                    "widgets": [
                        {
                            "type": "text_input",
                            "label": "Application Name",
                            "config_path": "application.name",
                            "placeholder": "Kollabor CLI",
                            "help": "Display name for the application"
                        },
                        {
                            "type": "text_input",
                            "label": "Version",
                            "config_path": "application.version",
                            "placeholder": "1.0.0",
                            "help": "Current application version"
                        }
                    ]
                },
                {
                    "title": "Plugin Settings",
                    "widgets": plugin_widgets
                },
                # Plugin config sections are loaded dynamically below
            ] + ConfigWidgetDefinitions.get_plugin_config_sections(),
            "actions": [
                {
                    "key": "Ctrl+S",
                    "label": "Save",
                    "action": "save",
                    "style": "primary"
                },
                {
                    "key": "Escape",
                    "label": "Cancel",
                    "action": "cancel",
                    "style": "secondary"
                }
            ]
        }

    @staticmethod
    def create_widgets_from_definition(config_service, definition: Dict[str, Any]) -> List[Any]:
        """Create widget instances from modal definition.

        Args:
            config_service: ConfigService for reading current values.
            definition: Modal definition dictionary.

        Returns:
            List of instantiated widgets.
        """
        widgets = []

        try:
            from .widgets.checkbox import CheckboxWidget
            from .widgets.dropdown import DropdownWidget
            from .widgets.text_input import TextInputWidget
            from .widgets.slider import SliderWidget
            from .widgets.label import LabelWidget

            widget_classes = {
                "checkbox": CheckboxWidget,
                "dropdown": DropdownWidget,
                "text_input": TextInputWidget,
                "slider": SliderWidget,
                "label": LabelWidget
            }

            for section in definition.get("sections", []):
                for widget_def in section.get("widgets", []):
                    widget_type = widget_def["type"]
                    widget_class = widget_classes.get(widget_type)

                    if not widget_class:
                        logger.error(f"Unknown widget type: {widget_type}")
                        continue

                    # Get current value from config (optional for labels)
                    config_path = widget_def.get("config_path", "")
                    if config_path:
                        current_value = config_service.get(config_path)
                    else:
                        # For label widgets, use the "value" field directly
                        current_value = widget_def.get("value", "")

                    # Create widget with configuration
                    widget = widget_class(
                        label=widget_def["label"],
                        config_path=config_path,
                        help_text=widget_def.get("help", ""),
                        current_value=current_value,
                        **{k: v for k, v in widget_def.items()
                           if k not in ["type", "label", "config_path", "help", "value"]}
                    )

                    widgets.append(widget)
                    logger.debug(f"Created {widget_type} widget for {config_path}")

        except Exception as e:
            logger.error(f"Error creating widgets from definition: {e}")

        logger.info(f"Created {len(widgets)} widgets from definition")
        return widgets

    @staticmethod
    def get_widget_navigation_info() -> Dict[str, str]:
        """Get navigation key information for modal help.

        Returns:
            Dictionary mapping keys to their descriptions.
        """
        return {
            "up_down": "Navigate between widgets",
            "left_right": "Adjust slider values",
            "enter": "Toggle checkbox",
            "space": "Toggle checkbox",
            "tab": "Next widget",
            "shift_tab": "Previous widget",
            "ctrl_s": "Save all changes",
            "escape": "Cancel and exit"
        }
