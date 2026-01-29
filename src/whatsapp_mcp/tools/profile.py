"""Profile and phone number tools for WhatsApp Business API."""

from typing import Any, Sequence
import httpx
from mcp.types import Tool

from ..config import WHATSAPP_BUSINESS_ACCOUNT_ID, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_API_VERSION
from ..utils import get_valid_token, get_token_error_message, create_error_response, create_success_response


def get_profile_tools() -> list[Tool]:
    """Get all profile and phone number tools."""
    return [
        Tool(
            name="WHATSAPP_GET_BUSINESS_PROFILE",
            description=(
                "Get the business profile information for a WhatsApp Business phone number. "
                "Includes description, address, website, and contact info. Uses WHATSAPP_PHONE_NUMBER_ID from .env if not provided."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated list of fields to return",
                        "default": "about,address,description,email,profile_picture_url,websites,vertical",
                    },
                },
            },
        ),
        Tool(
            name="WHATSAPP_GET_PHONE_NUMBER",
            description="Get details of a specific phone number associated with a WhatsApp Business Account.",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number_id": {"type": "string", "description": "Phone number ID (optional, uses .env if omitted)"},
                    "fields": {
                        "type": "string",
                        "description": "Comma-separated list of fields to return",
                        "default": "id,display_phone_number,verified_name,code_verification_status,quality_rating,platform_type,throughput,webhook_configuration,last_onboarded_time",
                    },
                },
            },
        ),
        Tool(
            name="WHATSAPP_GET_PHONE_NUMBERS",
            description="Get all phone numbers associated with a WhatsApp Business Account (WABA).",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of phone numbers to return", "default": 25},
                },
            },
        ),
    ]


async def handle_profile_tool(name: str, arguments: dict[str, Any]) -> Sequence:
    """Handle profile tool execution."""
    if name == "WHATSAPP_GET_BUSINESS_PROFILE":
        return await get_business_profile(arguments)
    elif name == "WHATSAPP_GET_PHONE_NUMBER":
        return await get_phone_number(arguments)
    elif name == "WHATSAPP_GET_PHONE_NUMBERS":
        return await get_phone_numbers(arguments)
    raise ValueError(f"Unknown profile tool: {name}")


async def get_business_profile(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set in environment variables")

    fields = arguments.get("fields", "about,address,description,email,profile_picture_url,websites,vertical")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/whatsapp_business_profile",
                params={"fields": fields},
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def get_phone_number(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    phone_number_id = arguments.get("phone_number_id") or WHATSAPP_PHONE_NUMBER_ID
    if not phone_number_id:
        return create_error_response("Missing phone_number_id. Provide it or set WHATSAPP_PHONE_NUMBER_ID in .env")

    fields = arguments.get("fields", "id,display_phone_number,verified_name,code_verification_status,quality_rating,platform_type,throughput,webhook_configuration,last_onboarded_time")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}",
                params={"fields": fields},
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def get_phone_numbers(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_BUSINESS_ACCOUNT_ID:
        return create_error_response("WHATSAPP_BUSINESS_ACCOUNT_ID is not set")

    limit = arguments.get("limit", 25)
    try:
        limit = int(limit)
    except Exception:
        limit = 25
    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_BUSINESS_ACCOUNT_ID}/phone_numbers",
                params={"limit": limit},
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
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")
