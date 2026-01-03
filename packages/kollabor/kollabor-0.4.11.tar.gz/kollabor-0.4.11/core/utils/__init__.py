"""Shared utility modules for Kollabor CLI."""

from .dict_utils import deep_merge, safe_get, safe_set
from .plugin_utils import has_method, safe_call_method, get_plugin_metadata
from .error_utils import log_and_continue, safe_execute

__all__ = [
    'deep_merge', 'safe_get', 'safe_set',
    'has_method', 'safe_call_method', 'get_plugin_metadata',
    'log_and_continue', 'safe_execute'
]