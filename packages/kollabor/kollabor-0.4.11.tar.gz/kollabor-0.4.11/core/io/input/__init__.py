"""Input handling components for Kollabor CLI.

This package contains modular components extracted from the monolithic InputHandler.
Each component has a single responsibility and can be tested independently.
"""

from .status_modal_renderer import StatusModalRenderer
from .paste_processor import PasteProcessor
from .display_controller import DisplayController
from .command_mode_handler import CommandModeHandler
from .key_press_handler import KeyPressHandler
from .modal_controller import ModalController
from .hook_registrar import HookRegistrar
from .input_loop_manager import InputLoopManager

__all__ = [
    "StatusModalRenderer",
    "PasteProcessor",
    "DisplayController",
    "CommandModeHandler",
    "KeyPressHandler",
    "ModalController",
    "HookRegistrar",
    "InputLoopManager",
]
