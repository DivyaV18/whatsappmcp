#!/usr/bin/env python3
"""
WhatsApp MCP Server
A Model Context Protocol server for WhatsApp Business API integration.
"""

import asyncio
import json
import os
import sys
import mimetypes
from typing import Any, Sequence

import httpx
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# WhatsApp API configuration
WHATSAPP_BEARER_TOKEN = os.getenv("WHATSAPP_BEARER_TOKEN")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v18.0")

# Initialize MCP server
server = Server("whatsapp-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available WhatsApp tools."""
    return [
        Tool(
            name="WHATSAPP_CREATE_MESSAGE_TEMPLATE",
            description=(
                "Create a new message template for the WhatsApp Business Account. "
                "Templates must be approved by WhatsApp before they can be used. "
                "Templates are required for marketing messages and messages sent outside the 24-hour window."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the message template",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language code for the template (e.g., 'en_US', 'es_ES')",
                    },
                    "category": {
                        "type": "string",
                        "description": (
                            "Category of the template. Must be one of: MARKETING, UTILITY, AUTHENTICATION"
                        ),
                        "enum": ["MARKETING", "UTILITY", "AUTHENTICATION"],
                    },
                    "components": {
                        "type": "array",
                        "description": (
                            "Array of template components (header, body, footer, buttons, etc.). "
                            "Each component should have a 'type' field (HEADER, BODY, FOOTER, BUTTONS) "
                            "and appropriate fields based on the type."
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {
                                    "type": "string",
                                    "description": "Component type: HEADER, BODY, FOOTER, or BUTTONS",
                                    "enum": ["HEADER", "BODY", "FOOTER", "BUTTONS"],
                                },
                                "format": {
                                    "type": "string",
                                    "description": "Format for HEADER component (TEXT, IMAGE, VIDEO, DOCUMENT)",
                                    "enum": ["TEXT", "IMAGE", "VIDEO", "DOCUMENT"],
                                },
                                "text": {
                                    "type": "string",
                                    "description": "Text content for TEXT components",
                                },
                                "example": {
                                    "type": "object",
                                    "description": "Example values for variables in the template",
                                },
                                "buttons": {
                                    "type": "array",
                                    "description": "Array of buttons (for BUTTONS type component)",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": ["QUICK_REPLY", "URL", "PHONE_NUMBER"],
                                            },
                                            "text": {"type": "string"},
                                            "url": {"type": "string"},
                                            "phone_number": {"type": "string"},
                                        },
                                    },
                                },
                            },
                            "required": ["type"],
                        },
                    },
                },
                "required": ["name", "language", "category", "components"],
            },
        ),
        Tool(
            name="WHATSAPP_DELETE_MESSAGE_TEMPLATE",
            description=(
                "Delete a message template from the WhatsApp Business Account. "
                "This permanently removes the template and it cannot be recovered. "
                "Only delete templates that are no longer needed."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "The ID of the message template to delete",
                    }
                },
                "required": ["template_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_BUSINESS_PROFILE",
            description=(
                "Get the business profile information for a WhatsApp Business phone number. "
                "This includes business details like description, address, website, and contact info."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "WhatsApp Business phone number ID to fetch profile for",
                    },
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated list of fields to return",
                        "default": "about,address,description,email,profile_picture_url,websites,vertical",
                    },
                },
                "required": ["phone_number_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_MEDIA",
            description=(
                "Get information about uploaded media including a temporary download URL. "
                "The download URL is valid for a short time (typically ~5 minutes) and can be used "
                "to retrieve the actual media file."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "media_id": {
                        "type": "string",
                        "description": "The media ID to fetch info for",
                    }
                },
                "required": ["media_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_MEDIA_INFO",
            description=(
                "Get metadata about uploaded media without generating a download URL. "
                "This is useful for checking file size, type, and hash without downloading the file. "
                "Use WHATSAPP_GET_MEDIA if you need the actual download URL."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "media_id": {
                        "type": "string",
                        "description": "The media ID to fetch metadata for",
                    }
                },
                "required": ["media_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_MESSAGE_TEMPLATES",
            description=(
                "Get all message templates for the WhatsApp Business Account. Templates are required "
                "for sending messages outside the 24-hour window and for marketing/utility messages."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "after": {
                        "type": "string",
                        "description": "Pagination cursor to fetch the next page (from response.paging.cursors.after)",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (e.g., MARKETING, UTILITY, AUTHENTICATION)",
                    },
                    "language": {
                        "type": "string",
                        "description": "Filter by language (e.g., en_US)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of templates to return",
                        "default": 25,
                    },
                    "name_or_content": {
                        "type": "string",
                        "description": "Search templates by name or content substring",
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status (e.g., APPROVED, PENDING, REJECTED, DISABLED)",
                    },
                },
            },
        ),
        Tool(
            name="WHATSAPP_GET_PHONE_NUMBER",
            description=(
                "Get details of a specific phone number associated with a WhatsApp Business Account."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "WhatsApp Business phone number ID to fetch details for",
                    },
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated list of fields to return",
                        "default": "id,display_phone_number,verified_name,code_verification_status,quality_rating,platform_type,throughput,webhook_configuration,last_onboarded_time",
                    },
                },
                "required": ["phone_number_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_PHONE_NUMBERS",
            description=(
                "Get all phone numbers associated with a WhatsApp Business Account (WABA)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of phone numbers to return",
                        "default": 25,
                    }
                },
            },
        ),
        Tool(
            name="WHATSAPP_GET_TEMPLATE_STATUS",
            description=(
                "Get the status and details of a specific message template. "
                "This is useful for checking if a template has been approved, rejected, "
                "or is still pending review."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "The ID of the message template",
                    },
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated list of fields to return",
                        "default": "id,name,status,category,language",
                    },
                },
                "required": ["template_id"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_CONTACTS",
            description=(
                "Send contacts to a WhatsApp number. Note: The message will be delivered to the recipient "
                "only if they have initiated a conversation first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "contacts": {
                        "type": "array",
                        "description": "Array of contact objects to send (WhatsApp contacts payload format)",
                        "items": {"type": "object"},
                    },
                },
                "required": ["phone_number_id", "to_number", "contacts"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_INTERACTIVE_BUTTONS",
            description=(
                "Send an interactive button message to a WhatsApp number. Button messages allow users "
                "to quickly respond by tapping up to 3 predefined buttons. Note: The message will be "
                "delivered to the recipient only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "body_text": {
                        "type": "string",
                        "description": "Main body text shown above the buttons",
                    },
                    "buttons": {
                        "type": "array",
                        "description": "Up to 3 buttons. Each item: {\"id\"?: \"btn1\", \"title\": \"Yes\"}",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "title": {"type": "string"},
                            },
                            "required": ["title"],
                        },
                    },
                    "header_text": {
                        "type": "string",
                        "description": "Optional header text (text header only)",
                    },
                    "footer_text": {
                        "type": "string",
                        "description": "Optional footer text",
                    },
                    "reply_to_message_id": {
                        "type": "string",
                        "description": "Optional message ID to reply to (context.message_id)",
                    },
                },
                "required": ["phone_number_id", "to_number", "body_text", "buttons"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_INTERACTIVE_LIST",
            description=(
                "Send an interactive list message to a WhatsApp number. List messages allow users to "
                "select from up to 10 options in a structured format. Note: The message will be delivered "
                "to the recipient only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "body_text": {
                        "type": "string",
                        "description": "Main body text shown above the list",
                    },
                    "button_text": {
                        "type": "string",
                        "description": "Text shown on the list button (e.g., 'Choose an option')",
                    },
                    "sections": {
                        "type": "array",
                        "description": "List sections. Each: {\"title\"?:\"Section\", \"rows\":[{\"id\"?:\"row1\",\"title\":\"Item\",\"description\"?:\"...\"}]}",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "rows": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "string"},
                                            "title": {"type": "string"},
                                            "description": {"type": "string"},
                                        },
                                        "required": ["title"],
                                    },
                                },
                            },
                            "required": ["rows"],
                        },
                    },
                    "header_text": {
                        "type": "string",
                        "description": "Optional header text (text header only)",
                    },
                    "footer_text": {
                        "type": "string",
                        "description": "Optional footer text",
                    },
                    "reply_to_message_id": {
                        "type": "string",
                        "description": "Optional message ID to reply to (context.message_id)",
                    },
                },
                "required": ["phone_number_id", "to_number", "body_text", "button_text", "sections"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_LOCATION",
            description=(
                "Send a location message to a WhatsApp number. Note: The location will be shared with "
                "the recipient only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "latitude": {
                        "type": "string",
                        "description": "Latitude (e.g., 12.9716)",
                    },
                    "longitude": {
                        "type": "string",
                        "description": "Longitude (e.g., 77.5946)",
                    },
                    "name": {
                        "type": "string",
                        "description": "Location name (label shown in WhatsApp)",
                    },
                    "address": {
                        "type": "string",
                        "description": "Location address",
                    },
                },
                "required": ["phone_number_id", "to_number", "latitude", "longitude", "name", "address"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_MESSAGE",
            description=(
                "Send a text message to a WhatsApp number. Note: The message will reflect on the recipient's "
                "phone number only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "text": {
                        "type": "string",
                        "description": "Text message body",
                    },
                    "preview_url": {
                        "type": "boolean",
                        "description": "Whether to show a URL preview in the message (default: false)",
                    },
                    "message_id": {
                        "type": "string",
                        "description": "Optional message ID to reply to (context.message_id)",
                    },
                },
                "required": ["phone_number_id", "to_number", "text"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_REPLY",
            description=(
                "Send a reply to a specific message in a WhatsApp conversation. This creates a contextual reply "
                "that shows which message you're responding to. Note: The reply will be delivered to the "
                "recipient only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "text": {
                        "type": "string",
                        "description": "Text message body",
                    },
                    "reply_to_message_id": {
                        "type": "string",
                        "description": "Message ID to reply to (context.message_id)",
                    },
                    "preview_url": {
                        "type": "boolean",
                        "description": "Whether to show a URL preview in the message (default: false)",
                    },
                },
                "required": ["phone_number_id", "to_number", "reply_to_message_id", "text"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_TEMPLATE_MESSAGE",
            description="Send a template message to a WhatsApp number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Approved template name to send",
                    },
                    "language_code": {
                        "type": "string",
                        "description": "Template language code (e.g., en_US)",
                        "default": "en_US",
                    },
                    "components": {
                        "type": "array",
                        "description": "Optional template components (parameters, buttons). If omitted, sends template without components.",
                        "items": {"type": "object"},
                    },
                },
                "required": ["phone_number_id", "to_number", "template_name"],
            },
        ),
        Tool(
            name="WHATSAPP_UPLOAD_MEDIA",
            description=(
                "Upload media files (images, videos, audio, documents, stickers) to WhatsApp servers. "
                "Returns a media ID that you can use with WHATSAPP_SEND_MEDIA_BY_ID."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (used for upload endpoint)",
                    },
                    "media_type": {
                        "type": "string",
                        "description": "Type of media being uploaded",
                        "enum": ["image", "video", "audio", "document", "sticker"],
                    },
                    "file_to_upload": {
                        "type": "object",
                        "description": "Local file to upload",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Absolute or relative path to the file on this machine",
                            },
                            "filename": {
                                "type": "string",
                                "description": "Optional filename override (defaults to basename of path)",
                            },
                            "mime_type": {
                                "type": "string",
                                "description": "Optional MIME type override (e.g., image/jpeg)",
                            },
                        },
                        "required": ["path"],
                    },
                },
                "required": ["phone_number_id", "media_type", "file_to_upload"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_MEDIA",
            description=(
                "Send a media message to a WhatsApp number. Note: The media will be delivered to the recipient "
                "only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "media_type": {
                        "type": "string",
                        "description": "Type of media to send",
                        "enum": ["image", "video", "audio", "document", "sticker"],
                    },
                    "link": {
                        "type": "string",
                        "description": "Publicly accessible HTTPS URL to the media",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Optional caption (supported for image/video/document)",
                    },
                },
                "required": ["phone_number_id", "to_number", "media_type", "link"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_MEDIA_BY_ID",
            description=(
                "Send media using a media ID from previously uploaded media. This is more efficient than "
                "sending media by URL as the media is already on WhatsApp servers. Note: The media will be "
                "delivered to the recipient only if they have texted first."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {
                        "type": "string",
                        "description": "Your WhatsApp Business phone number ID (sender)",
                    },
                    "to_number": {
                        "type": "string",
                        "description": "Recipient phone number in international format (e.g., +9198xxxxxx)",
                    },
                    "media_type": {
                        "type": "string",
                        "description": "Type of media to send",
                        "enum": ["image", "video", "audio", "document", "sticker"],
                    },
                    "media_id": {
                        "type": "string",
                        "description": "Media ID returned by upload media API or found in webhooks",
                    },
                    "caption": {
                        "type": "string",
                        "description": "Optional caption (supported for image/video/document)",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Optional filename (document only)",
                    },
                    "reply_to_message_id": {
                        "type": "string",
                        "description": "Optional message ID to reply to (context.message_id)",
                    },
                },
                "required": ["phone_number_id", "to_number", "media_type", "media_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle tool execution requests."""
    
    if name == "WHATSAPP_CREATE_MESSAGE_TEMPLATE":
        return await create_message_template(arguments)

    if name == "WHATSAPP_DELETE_MESSAGE_TEMPLATE":
        return await delete_message_template(arguments)

    if name == "WHATSAPP_GET_BUSINESS_PROFILE":
        return await get_business_profile(arguments)

    if name == "WHATSAPP_GET_MEDIA":
        return await get_media(arguments)

    if name == "WHATSAPP_GET_MEDIA_INFO":
        return await get_media_info(arguments)

    if name == "WHATSAPP_GET_MESSAGE_TEMPLATES":
        return await get_message_templates(arguments)

    if name == "WHATSAPP_GET_PHONE_NUMBER":
        return await get_phone_number(arguments)

    if name == "WHATSAPP_GET_PHONE_NUMBERS":
        return await get_phone_numbers(arguments)

    if name == "WHATSAPP_GET_TEMPLATE_STATUS":
        return await get_template_status(arguments)

    if name == "WHATSAPP_SEND_MESSAGE":
        return await send_message(arguments)

    if name == "WHATSAPP_SEND_REPLY":
        return await send_reply(arguments)

    if name == "WHATSAPP_SEND_TEMPLATE_MESSAGE":
        return await send_template_message(arguments)

    if name == "WHATSAPP_UPLOAD_MEDIA":
        return await upload_media(arguments)

    if name == "WHATSAPP_SEND_CONTACTS":
        return await send_contacts(arguments)

    if name == "WHATSAPP_SEND_INTERACTIVE_BUTTONS":
        return await send_interactive_buttons(arguments)

    if name == "WHATSAPP_SEND_INTERACTIVE_LIST":
        return await send_interactive_list(arguments)

    if name == "WHATSAPP_SEND_LOCATION":
        return await send_location(arguments)

    if name == "WHATSAPP_SEND_MEDIA":
        return await send_media(arguments)

    if name == "WHATSAPP_SEND_MEDIA_BY_ID":
        return await send_media_by_id(arguments)
    
    raise ValueError(f"Unknown tool: {name}")


async def create_message_template(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Create a WhatsApp message template."""
    
    # Validate configuration
    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    
    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BUSINESS_ACCOUNT_ID is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    
    # Validate required parameters
    required_params = ["name", "language", "category", "components"]
    missing_params = [param for param in required_params if param not in arguments]
    
    if missing_params:
        error_response = {
            "successful": False,
            "error": f"Missing required parameters: {', '.join(missing_params)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    
    # Prepare request body
    request_body = {
        "name": arguments["name"],
        "language": arguments["language"],
        "category": arguments["category"],
        "components": arguments["components"],
    }
    
    # Make API call to WhatsApp Business API
    # NOTE: Template creation uses the WhatsApp Business Account (WABA) ID, not the phone number ID.
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            
            result = {
                "successful": True,
                "data": response.json(),
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))
        
        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def delete_message_template(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Delete a WhatsApp message template by template ID."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BUSINESS_ACCOUNT_ID is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    template_id = arguments.get("template_id")
    if not template_id:
        error_response = {
            "successful": False,
            "error": "Missing required parameter: template_id",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
    }

    # Per Graph API docs, deletion is performed on the WABA edge and may include both name + hsm_id.
    # We'll try to resolve template name from the template node first for maximum compatibility.
    template_name: str | None = None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Best-effort: fetch template name from its node
            try:
                info_resp = await client.get(
                    f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{template_id}",
                    params={"fields": "name"},
                    headers=headers,
                )
                if info_resp.status_code == 200:
                    template_name = (info_resp.json() or {}).get("name")
            except Exception:
                template_name = None

            params: dict[str, Any] = {"hsm_id": template_id}
            if template_name:
                params["name"] = template_name

            delete_resp = await client.delete(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates",
                params=params,
                headers=headers,
            )
            delete_resp.raise_for_status()

            data = {}
            try:
                data = delete_resp.json()
            except Exception:
                data = {"raw": delete_resp.text}

            result = {
                "successful": True,
                "data": {
                    "template_id": template_id,
                    "template_name": template_name,
                    "response": data,
                },
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_business_profile(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get WhatsApp business profile for a phone number ID."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    if not phone_number_id:
        error_response = {
            "successful": False,
            "error": "Missing required parameter: phone_number_id",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    fields = arguments.get(
        "fields",
        "about,address,description,email,profile_picture_url,websites,vertical",
    )

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/whatsapp_business_profile",
                params={"fields": fields},
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_media(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get WhatsApp media metadata (includes temporary download URL)."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_id = arguments.get("media_id")
    if not media_id:
        error_response = {
            "successful": False,
            "error": "Missing required parameter: media_id",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Graph API: GET /{media-id}
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{media_id}",
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_media_info(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get WhatsApp media metadata without returning a download URL."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_id = arguments.get("media_id")
    if not media_id:
        error_response = {
            "successful": False,
            "error": "Missing required parameter: media_id",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Best-effort: request only metadata fields (omit url). If the API still returns a url,
            # we strip it before returning.
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{media_id}",
                params={"fields": "id,mime_type,sha256,file_size"},
                headers=headers,
            )
            resp.raise_for_status()

            data = resp.json()
            if isinstance(data, dict) and "url" in data:
                data = {k: v for k, v in data.items() if k != "url"}

            result = {
                "successful": True,
                "data": data,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_message_templates(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """List message templates for the WhatsApp Business Account (WABA)."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BUSINESS_ACCOUNT_ID is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    params: dict[str, Any] = {}

    # Pagination / filters
    after = arguments.get("after")
    if after:
        params["after"] = after

    category = arguments.get("category")
    if category:
        params["category"] = category

    language = arguments.get("language")
    if language:
        params["language"] = language

    name_or_content = arguments.get("name_or_content")
    if name_or_content:
        params["name_or_content"] = name_or_content

    status = arguments.get("status")
    if status:
        params["status"] = status

    limit = arguments.get("limit", 25)
    try:
        params["limit"] = int(limit)
    except Exception:
        params["limit"] = 25

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()

            payload = resp.json()
            # Expected shape: { "data": [...], "paging": {...}, ... }
            result = {
                "successful": True,
                "data": payload.get("data") if isinstance(payload, dict) else payload,
                "paging": payload.get("paging") if isinstance(payload, dict) else None,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_phone_number(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get details for a WhatsApp Business phone number by ID."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    if not phone_number_id:
        error_response = {
            "successful": False,
            "error": "Missing required parameter: phone_number_id",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    fields = arguments.get(
        "fields",
        "id,display_phone_number,verified_name,code_verification_status,quality_rating,platform_type,throughput,webhook_configuration,last_onboarded_time",
    )

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}",
                params={"fields": fields},
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_phone_numbers(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get phone numbers associated with the WhatsApp Business Account (WABA)."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BUSINESS_ACCOUNT_ID is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    limit = arguments.get("limit", 25)
    try:
        limit = int(limit)
    except Exception:
        limit = 25

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/phone_numbers",
                params={"limit": limit},
                headers=headers,
            )
            resp.raise_for_status()

            payload = resp.json()
            result = {
                "successful": True,
                "data": payload.get("data") if isinstance(payload, dict) else payload,
                "paging": payload.get("paging") if isinstance(payload, dict) else None,
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def get_template_status(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get WhatsApp message template details by template ID."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    template_id = arguments.get("template_id")
    if not template_id:
        error_response = {
            "successful": False,
            "error": "Missing required parameter: template_id",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    fields = arguments.get("fields", "id,name,status,category,language")
    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{template_id}",
                params={"fields": fields},
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_contacts(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send one or more contact cards to a WhatsApp recipient."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    contacts = arguments.get("contacts")

    missing = [
        p
        for p, v in (("phone_number_id", phone_number_id), ("to_number", to_number), ("contacts", contacts))
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if not isinstance(contacts, list) or len(contacts) == 0:
        error_response = {
            "successful": False,
            "error": "contacts must be a non-empty array",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "contacts",
        "contacts": contacts,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_interactive_buttons(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send an interactive (button) message."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    body_text = arguments.get("body_text")
    buttons = arguments.get("buttons")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("body_text", body_text),
            ("buttons", buttons),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if not isinstance(buttons, list) or len(buttons) == 0:
        error_response = {
            "successful": False,
            "error": "buttons must be a non-empty array",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if len(buttons) > 3:
        error_response = {
            "successful": False,
            "error": "buttons can have at most 3 items",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    wa_buttons = []
    for idx, b in enumerate(buttons):
        if not isinstance(b, dict) or not b.get("title"):
            error_response = {
                "successful": False,
                "error": "Each button must be an object with at least a non-empty 'title' field",
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

        btn_id = b.get("id") or f"btn_{idx+1}"
        wa_buttons.append(
            {
                "type": "reply",
                "reply": {"id": str(btn_id), "title": str(b["title"])},
            }
        )

    interactive: dict[str, Any] = {
        "type": "button",
        "body": {"text": str(body_text)},
        "action": {"buttons": wa_buttons},
    }

    header_text = arguments.get("header_text")
    if header_text:
        interactive["header"] = {"type": "text", "text": str(header_text)}

    footer_text = arguments.get("footer_text")
    if footer_text:
        interactive["footer"] = {"text": str(footer_text)}

    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "interactive",
        "interactive": interactive,
    }

    reply_to_message_id = arguments.get("reply_to_message_id")
    if reply_to_message_id:
        body["context"] = {"message_id": str(reply_to_message_id)}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_interactive_list(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send an interactive (list) message."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    body_text = arguments.get("body_text")
    button_text = arguments.get("button_text")
    sections = arguments.get("sections")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("body_text", body_text),
            ("button_text", button_text),
            ("sections", sections),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    if not isinstance(sections, list) or len(sections) == 0:
        error_response = {
            "successful": False,
            "error": "sections must be a non-empty array",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    # Build WhatsApp sections and enforce the 10 rows total limit.
    total_rows = 0
    wa_sections = []
    for s_idx, s in enumerate(sections):
        if not isinstance(s, dict) or not isinstance(s.get("rows"), list) or len(s.get("rows")) == 0:
            error_response = {
                "successful": False,
                "error": "Each section must be an object with a non-empty 'rows' array",
            }
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

        wa_rows = []
        for r_idx, r in enumerate(s["rows"]):
            if not isinstance(r, dict) or not r.get("title"):
                error_response = {
                    "successful": False,
                    "error": "Each row must be an object with at least a non-empty 'title' field",
                }
                return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

            row_id = r.get("id") or f"row_{s_idx+1}_{r_idx+1}"
            row_obj: dict[str, Any] = {"id": str(row_id), "title": str(r["title"])}
            if r.get("description"):
                row_obj["description"] = str(r["description"])

            wa_rows.append(row_obj)
            total_rows += 1
            if total_rows > 10:
                error_response = {
                    "successful": False,
                    "error": "List messages support at most 10 total rows across all sections",
                }
                return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

        section_obj: dict[str, Any] = {"rows": wa_rows}
        if s.get("title"):
            section_obj["title"] = str(s["title"])
        wa_sections.append(section_obj)

    interactive: dict[str, Any] = {
        "type": "list",
        "body": {"text": str(body_text)},
        "action": {"button": str(button_text), "sections": wa_sections},
    }

    header_text = arguments.get("header_text")
    if header_text:
        interactive["header"] = {"type": "text", "text": str(header_text)}

    footer_text = arguments.get("footer_text")
    if footer_text:
        interactive["footer"] = {"text": str(footer_text)}

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "interactive",
        "interactive": interactive,
    }

    reply_to_message_id = arguments.get("reply_to_message_id")
    if reply_to_message_id:
        payload["context"] = {"message_id": str(reply_to_message_id)}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_message(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send a text message."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    text = arguments.get("text")
    preview_url = arguments.get("preview_url", False)
    # message_id is optional (reply context); accept both keys for convenience
    message_id = arguments.get("message_id") or arguments.get("reply_to_message_id")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("text", text),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    # Best-effort normalize preview_url to bool (some clients send strings)
    preview_url_bool = False
    if isinstance(preview_url, bool):
        preview_url_bool = preview_url
    elif preview_url is not None:
        preview_url_bool = str(preview_url).strip().lower() in {"1", "true", "yes", "y", "on"}

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "text",
        "text": {"body": str(text), "preview_url": preview_url_bool},
    }

    if message_id:
        payload["context"] = {"message_id": str(message_id)}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_reply(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send a contextual reply to a specific message."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    text = arguments.get("text")
    reply_to_message_id = arguments.get("reply_to_message_id")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("reply_to_message_id", reply_to_message_id),
            ("text", text),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    # Reuse send_message payload logic, but force reply context.
    args2 = dict(arguments)
    args2["message_id"] = str(reply_to_message_id)
    return await send_message(args2)


async def send_template_message(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send a WhatsApp template message."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    template_name = arguments.get("template_name")
    language_code = arguments.get("language_code") or "en_US"
    components = arguments.get("components")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("template_name", template_name),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    template_obj: dict[str, Any] = {
        "name": str(template_name),
        "language": {"code": str(language_code)},
    }
    if components:
        template_obj["components"] = components

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "template",
        "template": template_obj,
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def upload_media(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Upload a media file to WhatsApp and return a media ID."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    media_type = arguments.get("media_type")
    file_to_upload = arguments.get("file_to_upload") or {}

    file_path = file_to_upload.get("path")
    filename = file_to_upload.get("filename")
    mime_type = file_to_upload.get("mime_type")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("media_type", media_type),
            ("file_to_upload.path", file_path),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_type = str(media_type).lower().strip()
    if media_type not in {"image", "video", "audio", "document", "sticker"}:
        error_response = {
            "successful": False,
            "error": "media_type must be one of: image, video, audio, document, sticker",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    file_path = str(file_path)
    if not os.path.isabs(file_path):
        # Resolve relative paths from current working directory
        file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        error_response = {
            "successful": False,
            "error": f"File not found: {file_path}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    # Determine filename and MIME type
    upload_filename = str(filename) if filename else os.path.basename(file_path)
    if mime_type:
        upload_mime = str(mime_type)
    else:
        guessed, _ = mimetypes.guess_type(upload_filename)
        if media_type == "sticker":
            upload_mime = guessed or "image/webp"
        else:
            upload_mime = guessed or "application/octet-stream"

    headers = {"Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}"}

    # WhatsApp Cloud API upload endpoint: /{phone_number_id}/media
    # Requires multipart with messaging_product=whatsapp, type=<mime>, file=<binary>
    data = {"messaging_product": "whatsapp", "type": upload_mime}

    try:
        with open(file_path, "rb") as f:
            files = {"file": (upload_filename, f, upload_mime)}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/media",
                    data=data,
                    files=files,
                    headers=headers,
                )
                resp.raise_for_status()

        result = {
            "successful": True,
            "data": resp.json(),
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_location(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send a location message."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    latitude = arguments.get("latitude")
    longitude = arguments.get("longitude")
    name = arguments.get("name")
    address = arguments.get("address")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("latitude", latitude),
            ("longitude", longitude),
            ("name", name),
            ("address", address),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    try:
        lat_val = float(str(latitude))
        lon_val = float(str(longitude))
    except Exception:
        error_response = {
            "successful": False,
            "error": "latitude and longitude must be valid numbers",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "location",
        "location": {
            "latitude": lat_val,
            "longitude": lon_val,
            "name": str(name),
            "address": str(address),
        },
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_media(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send a media message by link (image/video/audio/document/sticker)."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    media_type = arguments.get("media_type")
    link = arguments.get("link")
    caption = arguments.get("caption")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("media_type", media_type),
            ("link", link),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_type = str(media_type).lower().strip()
    if media_type not in {"image", "video", "audio", "document", "sticker"}:
        error_response = {
            "successful": False,
            "error": "media_type must be one of: image, video, audio, document, sticker",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_obj: dict[str, Any] = {"link": str(link)}
    if caption and media_type in {"image", "video", "document"}:
        media_obj["caption"] = str(caption)

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": media_type,
        media_type: media_obj,
    }

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def send_media_by_id(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Send a media message using a WhatsApp media ID."""

    if not WHATSAPP_BEARER_TOKEN:
        error_response = {
            "successful": False,
            "error": "WHATSAPP_BEARER_TOKEN is not set in environment variables",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    phone_number_id = arguments.get("phone_number_id")
    to_number = arguments.get("to_number")
    media_type = arguments.get("media_type")
    media_id = arguments.get("media_id")
    caption = arguments.get("caption")
    filename = arguments.get("filename")
    reply_to_message_id = arguments.get("reply_to_message_id")

    missing = [
        p
        for p, v in (
            ("phone_number_id", phone_number_id),
            ("to_number", to_number),
            ("media_type", media_type),
            ("media_id", media_id),
        )
        if not v
    ]
    if missing:
        error_response = {
            "successful": False,
            "error": f"Missing required parameter(s): {', '.join(missing)}",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_type = str(media_type).lower().strip()
    if media_type not in {"image", "video", "audio", "document", "sticker"}:
        error_response = {
            "successful": False,
            "error": "media_type must be one of: image, video, audio, document, sticker",
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

    media_obj: dict[str, Any] = {"id": str(media_id)}
    if caption and media_type in {"image", "video", "document"}:
        media_obj["caption"] = str(caption)
    if filename and media_type == "document":
        media_obj["filename"] = str(filename)

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": media_type,
        media_type: media_obj,
    }

    if reply_to_message_id:
        payload["context"] = {"message_id": str(reply_to_message_id)}

    headers = {
        "Authorization": f"Bearer {WHATSAPP_BEARER_TOKEN}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()

            result = {
                "successful": True,
                "data": resp.json(),
            }
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        error_message = error_data.get("error", {}).get("message", str(e))

        result = {
            "successful": False,
            "error": error_message,
            "data": error_data,
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        result = {
            "successful": False,
            "error": f"Unexpected error: {str(e)}",
        }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main entry point for the MCP server."""
    # Validate environment variables on startup
    if not WHATSAPP_BEARER_TOKEN:
        print(
            "Warning: WHATSAPP_BEARER_TOKEN not set. Tools will return errors.",
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
