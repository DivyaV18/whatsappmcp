"""Template management tools for WhatsApp Business API."""

import json
from typing import Any, Sequence
import httpx
from mcp.types import Tool, TextContent

from ..config import WHATSAPP_BUSINESS_ACCOUNT_ID, WHATSAPP_API_VERSION
from ..utils import get_valid_token, get_token_error_message, create_error_response, create_success_response


def get_template_tools() -> list[Tool]:
    """Get all template management tools."""
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
                    "name": {"type": "string", "description": "Name of the message template"},
                    "language": {"type": "string", "description": "Language code (e.g., 'en_US', 'es_ES')"},
                    "category": {
                        "type": "string",
                        "description": "Category: MARKETING, UTILITY, or AUTHENTICATION",
                        "enum": ["MARKETING", "UTILITY", "AUTHENTICATION"],
                    },
                    "components": {
                        "type": "array",
                        "description": "Array of template components (HEADER, BODY, FOOTER, BUTTONS)",
                        "items": {"type": "object"},
                    },
                },
                "required": ["name", "language", "category", "components"],
            },
        ),
        Tool(
            name="WHATSAPP_DELETE_MESSAGE_TEMPLATE",
            description="Delete a message template from the WhatsApp Business Account permanently.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "The ID of the template to delete"}
                },
                "required": ["template_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_MESSAGE_TEMPLATES",
            description="Get all message templates for the WhatsApp Business Account with optional filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "after": {"type": "string", "description": "Pagination cursor"},
                    "category": {"type": "string", "description": "Filter by category"},
                    "language": {"type": "string", "description": "Filter by language"},
                    "limit": {"type": "integer", "description": "Number of templates", "default": 25},
                    "name_or_content": {"type": "string", "description": "Search by name or content"},
                    "status": {"type": "string", "description": "Filter by status"},
                },
            },
        ),
        Tool(
            name="WHATSAPP_GET_TEMPLATE_STATUS",
            description="Get the status and details of a specific message template.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "The template ID"},
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated fields",
                        "default": "id,name,status,category,language",
                    },
                },
                "required": ["template_id"],
            },
        ),
    ]


async def handle_template_tool(name: str, arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Handle template tool execution."""
    if name == "WHATSAPP_CREATE_MESSAGE_TEMPLATE":
        return await create_message_template(arguments)
    elif name == "WHATSAPP_DELETE_MESSAGE_TEMPLATE":
        return await delete_message_template(arguments)
    elif name == "WHATSAPP_GET_MESSAGE_TEMPLATES":
        return await get_message_templates(arguments)
    elif name == "WHATSAPP_GET_TEMPLATE_STATUS":
        return await get_template_status(arguments)
    else:
        raise ValueError(f"Unknown template tool: {name}")


async def create_message_template(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Create a WhatsApp message template."""
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    
    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        return create_error_response("WHATSAPP_BUSINESS_ACCOUNT_ID is not set in environment variables")
    
    required_params = ["name", "language", "category", "components"]
    missing = [p for p in required_params if p not in arguments]
    if missing:
        return create_error_response(f"Missing required parameters: {', '.join(missing)}")
    
    request_body = {
        "name": arguments["name"],
        "language": arguments["language"],
        "category": arguments["category"],
        "components": arguments["components"],
    }
    
    url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=request_body, headers=headers)
            response.raise_for_status()
            return create_success_response(response.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(
            error_data.get("error", {}).get("message", str(e)),
            error_data
        )
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def delete_message_template(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Delete a WhatsApp message template."""
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    
    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        return create_error_response("WHATSAPP_BUSINESS_ACCOUNT_ID is not set")
    
    template_id = arguments.get("template_id")
    if not template_id:
        return create_error_response("Missing required parameter: template_id")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            template_name = None
            try:
                info_resp = await client.get(
                    f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{template_id}",
                    params={"fields": "name"},
                    headers=headers,
                )
                if info_resp.status_code == 200:
                    template_name = (info_resp.json() or {}).get("name")
            except Exception:
                pass
            
            params = {"hsm_id": template_id}
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
            
            return create_success_response({
                "template_id": template_id,
                "template_name": template_name,
                "response": data,
            })
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(
            error_data.get("error", {}).get("message", str(e)),
            error_data
        )
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def get_message_templates(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """List message templates for the WhatsApp Business Account."""
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    
    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        return create_error_response("WHATSAPP_BUSINESS_ACCOUNT_ID is not set")
    
    params: dict[str, Any] = {}
    for key in ["after", "category", "language", "name_or_content", "status"]:
        if key in arguments and arguments[key]:
            params[key] = arguments[key]
    
    limit = arguments.get("limit", 25)
    try:
        params["limit"] = int(limit)
    except Exception:
        params["limit"] = 25
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            payload = resp.json()
            return create_success_response({
                "data": payload.get("data") if isinstance(payload, dict) else payload,
                "paging": payload.get("paging") if isinstance(payload, dict) else None,
            })
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(
            error_data.get("error", {}).get("message", str(e)),
            error_data
        )
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def get_template_status(arguments: dict[str, Any]) -> Sequence[TextContent]:
    """Get WhatsApp message template details by template ID."""
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    
    template_id = arguments.get("template_id")
    if not template_id:
        return create_error_response("Missing required parameter: template_id")
    
    fields = arguments.get("fields", "id,name,status,category,language")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{template_id}",
                params={"fields": fields},
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(
            error_data.get("error", {}).get("message", str(e)),
            error_data
        )
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")
