"""Configuration for WhatsApp MCP Server."""

import os
from dotenv import load_dotenv

# Load .env from project root (parent of src/whatsapp_mcp)
_config_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_config_dir, "..", ".."))
load_dotenv(os.path.join(_project_root, ".env"))

# WhatsApp API configuration
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v18.0")

# OAuth2 manager import - look in project root
import sys
parent_dir = _project_root
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from oauth_manager import OAuth2TokenManager
    oauth_manager = OAuth2TokenManager()
    USE_OAUTH2 = oauth_manager.is_configured() if oauth_manager else False
except ImportError:
    oauth_manager = None
    USE_OAUTH2 = False
