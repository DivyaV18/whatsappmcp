#!/usr/bin/env python3
"""
WhatsApp MCP Server - Main Entry Point
Model Context Protocol server for WhatsApp Business API integration.
"""

import asyncio
import sys
import os

# Ensure package is importable whether run directly or via run_server.py
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_src = os.path.join(_root, "src")
if _root not in sys.path:
    sys.path.insert(0, _root)
if _src not in sys.path:
    sys.path.insert(0, _src)

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from whatsapp_mcp.config import oauth_manager, USE_OAUTH2, WHATSAPP_BUSINESS_ACCOUNT_ID
from whatsapp_mcp.utils import create_error_response
from whatsapp_mcp.tools import (
    get_template_tools,
    handle_template_tool,
    get_profile_tools,
    handle_profile_tool,
    get_media_tools,
    handle_media_tool,
    get_messaging_tools,
    handle_messaging_tool,
)

# Initialize MCP server
server = Server("whatsapp-mcp-server")

TEMPLATE_TOOLS = {
    "WHATSAPP_CREATE_MESSAGE_TEMPLATE",
    "WHATSAPP_DELETE_MESSAGE_TEMPLATE",
    "WHATSAPP_GET_MESSAGE_TEMPLATES",
    "WHATSAPP_GET_TEMPLATE_STATUS",
}
PROFILE_TOOLS = {
    "WHATSAPP_GET_BUSINESS_PROFILE",
    "WHATSAPP_GET_PHONE_NUMBER",
    "WHATSAPP_GET_PHONE_NUMBERS",
}
MEDIA_TOOLS = {
    "WHATSAPP_UPLOAD_MEDIA",
    "WHATSAPP_GET_MEDIA",
    "WHATSAPP_GET_MEDIA_INFO",
}
MESSAGING_TOOLS = {
    "WHATSAPP_SEND_MESSAGE",
    "WHATSAPP_SEND_REPLY",
    "WHATSAPP_SEND_TEMPLATE_MESSAGE",
    "WHATSAPP_SEND_MEDIA",
    "WHATSAPP_SEND_MEDIA_BY_ID",
    "WHATSAPP_SEND_CONTACTS",
    "WHATSAPP_SEND_LOCATION",
    "WHATSAPP_SEND_INTERACTIVE_BUTTONS",
    "WHATSAPP_SEND_INTERACTIVE_LIST",
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available WhatsApp tools."""
    tools = []
    tools.extend(get_template_tools())
    tools.extend(get_profile_tools())
    tools.extend(get_media_tools())
    tools.extend(get_messaging_tools())
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    """Handle tool execution requests."""
    if name in TEMPLATE_TOOLS:
        return await handle_template_tool(name, arguments)
    if name in PROFILE_TOOLS:
        return await handle_profile_tool(name, arguments)
    if name in MEDIA_TOOLS:
        return await handle_media_tool(name, arguments)
    if name in MESSAGING_TOOLS:
        return await handle_messaging_tool(name, arguments)
    return create_error_response(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server."""
    # Validate OAuth2 configuration
    if oauth_manager is None:
        print(
            "ERROR: OAuth2 manager not available. Ensure oauth_manager.py exists.",
            file=sys.stderr,
        )
    elif not USE_OAUTH2:
        print(
            "ERROR: OAuth2 not configured. Set WHATSAPP_CLIENT_ID and WHATSAPP_CLIENT_SECRET in .env",
            file=sys.stderr,
        )
        print(
            "Then run 'python oauth_manager.py' to complete authorization.",
            file=sys.stderr,
        )
    else:
        print(
            "Info: OAuth2 authentication enabled. Run 'python oauth_manager.py' to get access token.",
            file=sys.stderr,
        )
        if oauth_manager and not oauth_manager.get_access_token():
            print(
                "Warning: OAuth2 token not available. Complete OAuth2 flow to use tools.",
                file=sys.stderr,
            )
    
    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        print(
            "Warning: WHATSAPP_BUSINESS_ACCOUNT_ID not set. Tools will return errors.",
            file=sys.stderr,
        )
    
    # Run the server using stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
