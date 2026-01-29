"""WhatsApp MCP Tools - Organized by functionality."""

from .templates import get_template_tools, handle_template_tool
from .profile import get_profile_tools, handle_profile_tool
from .media import get_media_tools, handle_media_tool
from .messaging import get_messaging_tools, handle_messaging_tool

__all__ = [
    "get_template_tools",
    "handle_template_tool",
    "get_profile_tools",
    "handle_profile_tool",
    "get_media_tools",
    "handle_media_tool",
    "get_messaging_tools",
    "handle_messaging_tool",
]
