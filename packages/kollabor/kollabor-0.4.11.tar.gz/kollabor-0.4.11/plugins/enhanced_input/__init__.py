"""Enhanced Input Plugin Package.

A modular, DRY implementation of enhanced input rendering with bordered boxes.
"""

from .box_styles import BoxStyleRegistry, BoxStyle
from .color_engine import ColorEngine
from .geometry import GeometryCalculator
from .box_renderer import BoxRenderer
from .cursor_manager import CursorManager
from .text_processor import TextProcessor
from .config import InputConfig
from .state import PluginState

__all__ = [
    'BoxStyleRegistry', 'BoxStyle', 'ColorEngine', 'GeometryCalculator',
    'BoxRenderer', 'CursorManager', 'TextProcessor', 'InputConfig', 'PluginState'
]