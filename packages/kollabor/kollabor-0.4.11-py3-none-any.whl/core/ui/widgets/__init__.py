"""Widget system for modal UI components.

This package provides interactive widgets for use in modal dialogs:
- BaseWidget: Foundation class for all widgets
- CheckboxWidget: Boolean toggle with ✓ symbol
- DropdownWidget: Option selection with ▼ indicator
- TextInputWidget: Text entry with cursor ▌
- SliderWidget: Numeric slider with █░ visual bar

All widgets integrate with the ColorPalette system and configuration management.
"""

from .base_widget import BaseWidget
from .checkbox import CheckboxWidget
from .dropdown import DropdownWidget
from .text_input import TextInputWidget
from .slider import SliderWidget
from .label import LabelWidget

__all__ = [
    "BaseWidget",
    "CheckboxWidget",
    "DropdownWidget",
    "TextInputWidget",
    "SliderWidget",
    "LabelWidget"
]