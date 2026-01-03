"""Event system data models and enums for Kollabor CLI."""

from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class HookPriority(Enum):
    """Priority levels for hook execution."""
    SYSTEM = 1000
    SECURITY = 900
    PREPROCESSING = 500
    LLM = 100
    POSTPROCESSING = 50
    DISPLAY = 10


class HookStatus(Enum):
    """Status states for hook execution."""
    PENDING = "pending"
    STARTING = "starting"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class EventType(Enum):
    """Event types for the hook system."""
    # User input events
    USER_INPUT_PRE = "user_input_pre"
    USER_INPUT = "user_input"
    USER_INPUT_POST = "user_input_post"
    
    # Key press events
    KEY_PRESS_PRE = "key_press_pre"
    KEY_PRESS = "key_press"
    KEY_PRESS_POST = "key_press_post"
    
    # Paste events
    PASTE_DETECTED = "paste_detected"
    
    # LLM events
    LLM_REQUEST_PRE = "llm_request_pre"
    LLM_REQUEST = "llm_request"
    LLM_REQUEST_POST = "llm_request_post"
    LLM_RESPONSE_PRE = "llm_response_pre"
    LLM_RESPONSE = "llm_response"
    LLM_RESPONSE_POST = "llm_response_post"
    LLM_THINKING = "llm_thinking"
    CANCEL_REQUEST = "cancel_request"
    
    # Tool events
    TOOL_CALL_PRE = "tool_call_pre"
    TOOL_CALL = "tool_call"
    TOOL_CALL_POST = "tool_call_post"
    
    # System events
    SYSTEM_STARTUP = "system_startup"
    SYSTEM_SHUTDOWN = "system_shutdown"
    RENDER_FRAME = "render_frame"
    
    # Input rendering events
    INPUT_RENDER_PRE = "input_render_pre"
    INPUT_RENDER = "input_render"
    INPUT_RENDER_POST = "input_render_post"
    
    # Command menu events
    COMMAND_MENU_SHOW = "command_menu_show"
    COMMAND_MENU_NAVIGATE = "command_menu_navigate"
    COMMAND_MENU_SELECT = "command_menu_select"
    COMMAND_MENU_HIDE = "command_menu_hide"
    COMMAND_MENU_RENDER = "command_menu_render"

    # Status display events
    STATUS_VIEW_CHANGED = "status_view_changed"
    STATUS_CONTENT_UPDATE = "status_content_update"
    STATUS_BLOCK_RESIZE = "status_block_resize"

    # Slash command events
    SLASH_COMMAND_DETECTED = "slash_command_detected"
    SLASH_COMMAND_EXECUTE = "slash_command_execute"
    SLASH_COMMAND_COMPLETE = "slash_command_complete"
    SLASH_COMMAND_ERROR = "slash_command_error"

    # Command output display events
    COMMAND_OUTPUT_DISPLAY = "command_output_display"

    # Message injection events
    ADD_MESSAGE = "add_message"

    # Command menu events (enhanced)
    COMMAND_MENU_FILTER = "command_menu_filter"

    # Modal events
    MODAL_TRIGGER = "modal_trigger"
    STATUS_MODAL_TRIGGER = "status_modal_trigger"
    STATUS_MODAL_RENDER = "status_modal_render"
    LIVE_MODAL_TRIGGER = "live_modal_trigger"
    MODAL_COMMAND_SELECTED = "modal_command_selected"

    # Rendering control events
    PAUSE_RENDERING = "pause_rendering"
    RESUME_RENDERING = "resume_rendering"
    MODAL_SHOW = "modal_show"
    MODAL_HIDE = "modal_hide"
    MODAL_SAVE = "modal_save"
    FULLSCREEN_INPUT = "fullscreen_input"
    COMMAND_MENU_ACTIVATE = "command_menu_activate"

    # Status area takeover events
    STATUS_TAKEOVER_START = "status_takeover_start"
    STATUS_TAKEOVER_NAVIGATE = "status_takeover_navigate"
    STATUS_TAKEOVER_ACTION = "status_takeover_action"
    STATUS_TAKEOVER_END = "status_takeover_end"


@dataclass
class Hook:
    """Hook definition for the event system.
    
    Attributes:
        name: Unique name for the hook.
        plugin_name: Name of the plugin that owns this hook.
        event_type: Type of event this hook responds to.
        priority: Execution priority (higher numbers execute first).
        callback: Async function to call when event occurs.
        enabled: Whether the hook is currently enabled.
        timeout: Maximum execution time in seconds.
        retry_attempts: Number of retry attempts on failure.
        error_action: Action to take on error ("continue" or "stop").
        status: Current execution status.
        status_area: Status area identifier.
        icon_set: Icons for different states.
    """
    name: str
    plugin_name: str
    event_type: EventType
    priority: int
    callback: Callable
    enabled: bool = True
    timeout: int = 30
    retry_attempts: int = 3
    error_action: str = "continue"
    status: HookStatus = HookStatus.PENDING
    status_area: str = "A"
    icon_set: Dict[str, str] = field(default_factory=lambda: {
        "thinking": "[think]", "processing": "[proc]", "complete": "[ok]", "error": "[err]"
    })


@dataclass
class Event:
    """Event data structure for the hook system.
    
    Attributes:
        type: Type of event.
        data: Event-specific data.
        source: Source that generated the event.
        timestamp: When the event was created.
        processed: Whether the event has been processed.
        cancelled: Whether the event was cancelled during processing.
        result: Results from hook processing.
    """
    type: EventType
    data: Dict[str, Any]
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    processed: bool = False
    cancelled: bool = False
    result: Dict[str, Any] = field(default_factory=dict)


# Slash Command System Models

class CommandMode(Enum):
    """Different interaction modes for slash commands."""
    NORMAL = "normal"                    # Regular input mode
    INSTANT = "instant"                  # /clear - executes immediately
    MENU_POPUP = "menu_popup"           # Shows command menu overlay
    STATUS_TAKEOVER = "status_takeover"  # /agents - takes over status area
    STATUS_MODAL = "status_modal"        # Modal within status area only
    INLINE_INPUT = "inline_input"        # /save [filename] - inline parameters
    MODAL = "modal"                      # Modal overlay mode
    LIVE_MODAL = "live_modal"            # Live-updating modal (e.g., tmux view)


class CommandCategory(Enum):
    """Categories for organizing commands."""
    SYSTEM = "system"
    CONVERSATION = "conversation"
    AGENT = "agent"
    DEVELOPMENT = "development"
    FILE = "file"
    TASK = "task"
    CUSTOM = "custom"


@dataclass
class UIConfig:
    """Configuration for command UI interfaces."""
    type: str  # "list", "tree", "form", "table", "menu", "modal"
    navigation: List[str] = field(default_factory=lambda: ["↑↓", "Enter", "Esc"])
    height: int = 10
    width: Optional[int] = None
    scrollable: bool = True
    title: str = ""
    footer: str = ""
    modal_config: Optional[Dict[str, Any]] = None  # Modal-specific configuration


@dataclass
class ParameterDefinition:
    """Definition for command parameters."""
    name: str
    type: str  # "string", "int", "bool", "file", "choice"
    description: str
    required: bool = False
    default: Any = None
    choices: Optional[List[str]] = None
    validation: Optional[str] = None


@dataclass
class CommandDefinition:
    """Complete definition of a slash command."""
    name: str
    description: str
    handler: Callable
    plugin_name: str
    aliases: List[str] = field(default_factory=list)
    mode: CommandMode = CommandMode.INSTANT
    category: CommandCategory = CommandCategory.CUSTOM
    parameters: List[ParameterDefinition] = field(default_factory=list)
    ui_config: Optional[UIConfig] = None
    icon: str = ""
    hidden: bool = False
    enabled: bool = True


@dataclass
class SlashCommand:
    """Parsed slash command from user input."""
    name: str
    args: List[str] = field(default_factory=list)
    raw_input: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CommandResult:
    """Result from command execution."""
    success: bool
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    status_ui: Optional[Any] = None  # UI component for status takeover
    ui_config: Optional['UIConfig'] = None  # UI configuration for modal/status display
    display_type: str = "info"  # "info", "success", "warning", "error"
    should_clear_input: bool = True