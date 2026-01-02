#!/usr/bin/env python3

# File: xnotify/xnotify/plugins/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2025-12-30
# Description: Plugin system for xnotify.
# License: MIT

"""Plugin system for xnotify."""

# import logging
from typing import Dict, List, Type
import os
from ..logger import setup_logger

logger = setup_logger('xnotify.plugins')
# logger = logging.getLogger(__name__)

from .base import NotificationPlugin
from .pushbullet import PushbulletPlugin
from .ntfy import NtfyPlugin
from .pushover import PushoverPlugin
from .telegram import TelegramPlugin
from .discord import DiscordPlugin
from .slack import SlackPlugin
from .growl import GrowlPlugin
from .syslog import SyslogPlugin


# Registry of available plugins with descriptions
AVAILABLE_PLUGINS: Dict[str, Type[NotificationPlugin]] = {
    'ntfy': NtfyPlugin,
    'pushbullet': PushbulletPlugin,
    'pushover': PushoverPlugin,
    'telegram': TelegramPlugin,
    'discord': DiscordPlugin,
    'slack': SlackPlugin,
    'growl': GrowlPlugin,
    'syslog': SyslogPlugin,
}


def get_plugin(name: str) -> Type[NotificationPlugin]:
    """
    Get plugin class by name.
    
    Args:
        name: Plugin name
        
    Returns:
        Plugin class
        
    Raises:
        KeyError: If plugin not found
    """
    return AVAILABLE_PLUGINS[name.lower()]


def list_plugins() -> List[str]:
    """Get list of available plugin names."""
    return list(AVAILABLE_PLUGINS.keys())


def get_plugin_info(name: str) -> Dict[str, str]:
    """
    Get plugin information.
    
    Args:
        name: Plugin name
        
    Returns:
        Dictionary with plugin info
    """
    plugin_class = get_plugin(name)
    return {
        'name': name,
        'class': plugin_class.__name__,
        'description': plugin_class.__doc__ or 'No description',
    }


__all__ = [
    'NotificationPlugin',
    'PushbulletPlugin',
    'NtfyPlugin',
    'PushoverPlugin',
    'TelegramPlugin',
    'DiscordPlugin',
    'SlackPlugin',
    'GrowlPlugin',
    'SyslogPlugin',
    'AVAILABLE_PLUGINS',
    'get_plugin',
    'list_plugins',
    'get_plugin_info',
]