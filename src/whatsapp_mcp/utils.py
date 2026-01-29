"""Shared utilities for WhatsApp MCP tools."""

import os
import json
from typing import Optional, Sequence
from mcp.types import TextContent

from .config import oauth_manager


def get_access_token() -> Optional[str]:
    """Get OAuth2 access token (OAuth2 is required). Use get_valid_token() in async tools to auto-refresh."""
    if oauth_manager is None:
        return None
    return oauth_manager.get_access_token()


async def get_valid_token() -> Optional[str]:
    """Refresh token if expiring soon, then return access token. Use this in tool handlers."""
    if oauth_manager is None:
        return None
    await oauth_manager.refresh_if_needed()
    return oauth_manager.get_access_token()


def has_valid_token() -> bool:
    """Check if we have a valid OAuth2 token"""
    if oauth_manager is None:
        return False
    if not oauth_manager.is_configured():
        return False
    token = oauth_manager.get_access_token()
    if token:
        return True
    token_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".oauth_token_cache.json")
    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as f:
                data = json.load(f)
                if data.get("access_token"):
                    oauth_manager._access_token = data.get("access_token")
                    oauth_manager._token_expires_at = data.get("expires_at")
                    oauth_manager._refresh_token = data.get("refresh_token")
                    return True
        except Exception:
            pass
    return False


def get_token_error_message() -> str:
    """Get error message for missing OAuth2 token"""
    if oauth_manager is None:
        return (
            "OAuth2 manager not available. Ensure oauth_manager.py exists in the project directory."
        )
    if not oauth_manager.is_configured():
        return (
            "OAuth2 is not configured. Please set WHATSAPP_CLIENT_ID and WHATSAPP_CLIENT_SECRET in .env file. "
            "Then run 'python oauth_manager.py' to complete authorization."
        )
    return (
        "OAuth2 token not available. Please complete OAuth2 authorization flow. "
        "Run 'python oauth_manager.py' to get and save the access token."
    )


def create_error_response(error: str, data: dict = None) -> Sequence[TextContent]:
    """Create a standardized error response."""
    result = {
        "successful": False,
        "error": error,
    }
    if data:
        result["data"] = data
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def create_success_response(data: dict) -> Sequence[TextContent]:
    """Create a standardized success response."""
    result = {
        "successful": True,
        "data": data,
    }
    return [TextContent(type="text", text=json.dumps(result, indent=2))]
