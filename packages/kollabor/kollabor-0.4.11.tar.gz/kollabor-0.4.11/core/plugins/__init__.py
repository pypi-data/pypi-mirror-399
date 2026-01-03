"""Plugin subsystem for Kollabor CLI."""

from .registry import PluginRegistry
from .discovery import PluginDiscovery
from .factory import PluginFactory
from .collector import PluginStatusCollector

__all__ = [
    'PluginRegistry',
    'PluginDiscovery', 
    'PluginFactory',
    'PluginStatusCollector'
]