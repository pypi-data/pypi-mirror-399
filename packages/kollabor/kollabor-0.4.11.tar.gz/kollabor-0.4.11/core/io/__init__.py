"""Input/Output subsystem for Kollabor CLI.

This module provides comprehensive input/output handling for the Kollabor CLI application,
including terminal rendering, input processing, message display, and visual effects.
"""

from .input_handler import InputHandler
from .terminal_renderer import TerminalRenderer
from .key_parser import KeyParser, KeyPress, KeyType
from .buffer_manager import BufferManager
from .input_errors import InputErrorHandler, ErrorType, ErrorSeverity
from .visual_effects import (
    VisualEffects,
    ColorPalette,
    EffectType,
    ColorSupport,
    get_color_support,
    set_color_support,
    reset_color_support,
    detect_color_support,
    rgb_to_256,
    color_code,
)
from .terminal_state import TerminalState, TerminalCapabilities, TerminalMode
from .layout import LayoutManager, LayoutArea, ThinkingAnimationManager
from .status_renderer import StatusRenderer, StatusViewRegistry, StatusViewConfig, BlockConfig
from .message_renderer import (
    MessageRenderer,
    ConversationMessage,
    MessageType,
    MessageFormat,
)

__all__ = [
    # Core components
    "InputHandler",
    "TerminalRenderer",
    # Input handling
    "KeyParser",
    "KeyPress",
    "KeyType",
    "BufferManager",
    "InputErrorHandler",
    "ErrorType",
    "ErrorSeverity",
    # Visual effects
    "VisualEffects",
    "ColorPalette",
    "EffectType",
    # Color support detection
    "ColorSupport",
    "get_color_support",
    "set_color_support",
    "reset_color_support",
    "detect_color_support",
    "rgb_to_256",
    "color_code",
    # Terminal management
    "TerminalState",
    "TerminalCapabilities",
    "TerminalMode",
    # Layout management
    "LayoutManager",
    "LayoutArea",
    "ThinkingAnimationManager",
    # Status rendering
    "StatusRenderer",
    "StatusViewRegistry",
    "StatusViewConfig",
    "BlockConfig",
    # Message rendering
    "MessageRenderer",
    "ConversationMessage",
    "MessageType",
    "MessageFormat",
]
