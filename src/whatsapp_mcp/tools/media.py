"""Media tools for WhatsApp Business API."""

import os
import mimetypes
from typing import Any, Sequence
import httpx
from mcp.types import Tool

from ..config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_API_VERSION
from ..utils import get_valid_token, get_token_error_message, create_error_response, create_success_response


def get_media_tools() -> list[Tool]:
    """Get all media tools."""
    return [
        Tool(
            name="WHATSAPP_UPLOAD_MEDIA",
            description=(
                "Upload media files (images, videos, audio, documents, stickers) to WhatsApp servers. "
                "Returns a media ID for use with WHATSAPP_SEND_MEDIA_BY_ID."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "media_type": {
                        "type": "string",
                        "description": "Type of media being uploaded",
                        "enum": ["image", "video", "audio", "document", "sticker"],
                    },
                    "file_to_upload": {
                        "type": "object",
                        "description": "Local file to upload",
                        "properties": {
                            "path": {"type": "string", "description": "Absolute or relative path to the file"},
                            "filename": {"type": "string", "description": "Optional filename override"},
                            "mime_type": {"type": "string", "description": "Optional MIME type override"},
                        },
                        "required": ["path"],
                    },
                },
                "required": ["media_type", "file_to_upload"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_MEDIA",
            description=(
                "Get information about uploaded media including a temporary download URL. "
                "The download URL is valid for a short time (typically ~5 minutes)."
            ),
            inputSchema={
                "type": "object",
                "properties": {"media_id": {"type": "string", "description": "The media ID to fetch info for"}},
                "required": ["media_id"],
            },
        ),
        Tool(
            name="WHATSAPP_GET_MEDIA_INFO",
            description=(
                "Get metadata about uploaded media without generating a download URL. "
                "Useful for checking file size, type, and hash."
            ),
            inputSchema={
                "type": "object",
                "properties": {"media_id": {"type": "string", "description": "The media ID to fetch metadata for"}},
                "required": ["media_id"],
            },
        ),
    ]


async def handle_media_tool(name: str, arguments: dict[str, Any]) -> Sequence:
    """Handle media tool execution."""
    if name == "WHATSAPP_UPLOAD_MEDIA":
        return await upload_media(arguments)
    elif name == "WHATSAPP_GET_MEDIA":
        return await get_media(arguments)
    elif name == "WHATSAPP_GET_MEDIA_INFO":
        return await get_media_info(arguments)
    raise ValueError(f"Unknown media tool: {name}")


async def upload_media(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")

    media_type = arguments.get("media_type")
    file_to_upload = arguments.get("file_to_upload") or {}
    file_path = file_to_upload.get("path")
    filename = file_to_upload.get("filename")
    mime_type = file_to_upload.get("mime_type")

    if not media_type or not file_path:
        return create_error_response("Missing required parameter(s): media_type and file_to_upload.path")

    media_type = str(media_type).lower().strip()
    if media_type not in {"image", "video", "audio", "document", "sticker"}:
        return create_error_response("media_type must be one of: image, video, audio, document, sticker")

    file_path = str(file_path)
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return create_error_response(f"File not found: {file_path}")

    upload_filename = str(filename) if filename else os.path.basename(file_path)
    if mime_type:
        upload_mime = str(mime_type)
    else:
        guessed, _ = mimetypes.guess_type(upload_filename)
        upload_mime = (guessed or "image/webp") if media_type == "sticker" else (guessed or "application/octet-stream")

    headers = {"Authorization": f"Bearer {token}"}
    data = {"messaging_product": "whatsapp", "type": upload_mime}
    try:
        with open(file_path, "rb") as f:
            files = {"file": (upload_filename, f, upload_mime)}
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(
                    f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/media",
                    data=data,
                    files=files,
                    headers=headers,
                )
                resp.raise_for_status()
                return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def get_media(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    media_id = arguments.get("media_id")
    if not media_id:
        return create_error_response("Missing required parameter: media_id")

    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{media_id}",
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def get_media_info(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    media_id = arguments.get("media_id")
    if not media_id:
        return create_error_response("Missing required parameter: media_id")

    headers = {"Authorization": f"Bearer {token}"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{media_id}",
                params={"fields": "id,mime_type,sha256,file_size"},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "url" in data:
                data = {k: v for k, v in data.items() if k != "url"}
            return create_success_response(data)
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")
