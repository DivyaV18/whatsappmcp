#!/usr/bin/env python3
"""
Entry point script to run WhatsApp MCP Server.
This script runs the server from the new src/whatsapp_mcp structure.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from whatsapp_mcp.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
