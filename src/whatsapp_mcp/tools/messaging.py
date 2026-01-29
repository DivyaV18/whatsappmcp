"""Messaging tools for WhatsApp Business API."""

from typing import Any, Sequence
import httpx
from mcp.types import Tool

from ..config import WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_API_VERSION
from ..utils import get_valid_token, get_token_error_message, create_error_response, create_success_response


def get_messaging_tools() -> list[Tool]:
    """Get all messaging tools."""
    return [
        Tool(
            name="WHATSAPP_SEND_MESSAGE",
            description="Send a text message to a WhatsApp number. Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format (e.g., +9198xxxxxx)"},
                    "text": {"type": "string", "description": "Text message body"},
                    "preview_url": {"type": "boolean", "description": "Show URL preview (default: false)"},
                    "message_id": {"type": "string", "description": "Optional message ID to reply to"},
                },
                "required": ["to_number", "text"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_REPLY",
            description="Send a reply to a specific message. Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "text": {"type": "string", "description": "Text message body"},
                    "reply_to_message_id": {"type": "string", "description": "Message ID to reply to"},
                    "preview_url": {"type": "boolean", "description": "Show URL preview (default: false)"},
                },
                "required": ["to_number", "reply_to_message_id", "text"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_TEMPLATE_MESSAGE",
            description="Send a template message to a WhatsApp number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "template_name": {"type": "string", "description": "Approved template name"},
                    "language_code": {"type": "string", "description": "Template language (default: en_US)"},
                    "components": {"type": "array", "description": "Optional template components", "items": {"type": "object"}},
                },
                "required": ["to_number", "template_name"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_MEDIA",
            description="Send a media message by URL. Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "media_type": {"type": "string", "enum": ["image", "video", "audio", "document", "sticker"]},
                    "link": {"type": "string", "description": "Publicly accessible HTTPS URL to the media"},
                    "caption": {"type": "string", "description": "Optional caption"},
                },
                "required": ["to_number", "media_type", "link"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_MEDIA_BY_ID",
            description="Send media using a media ID from previously uploaded media. Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "media_type": {"type": "string", "enum": ["image", "video", "audio", "document", "sticker"]},
                    "media_id": {"type": "string", "description": "Media ID from upload or webhooks"},
                    "caption": {"type": "string", "description": "Optional caption"},
                    "filename": {"type": "string", "description": "Optional filename (document only)"},
                    "reply_to_message_id": {"type": "string", "description": "Optional message ID to reply to"},
                },
                "required": ["to_number", "media_type", "media_id"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_CONTACTS",
            description="Send contacts to a WhatsApp number. Delivered only if recipient has initiated a conversation first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "contacts": {"type": "array", "description": "Array of contact objects (WhatsApp payload format)", "items": {"type": "object"}},
                },
                "required": ["to_number", "contacts"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_LOCATION",
            description="Send a location message. Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "latitude": {"type": "string", "description": "Latitude (e.g., 12.9716)"},
                    "longitude": {"type": "string", "description": "Longitude (e.g., 77.5946)"},
                    "name": {"type": "string", "description": "Location name"},
                    "address": {"type": "string", "description": "Location address"},
                },
                "required": ["to_number", "latitude", "longitude", "name", "address"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_INTERACTIVE_BUTTONS",
            description="Send an interactive button message (up to 3 buttons). Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "body_text": {"type": "string", "description": "Main body text"},
                    "buttons": {"type": "array", "description": "Up to 3 buttons: [{id?, title}]", "items": {"type": "object"}},
                    "header_text": {"type": "string", "description": "Optional header"},
                    "footer_text": {"type": "string", "description": "Optional footer"},
                    "reply_to_message_id": {"type": "string", "description": "Optional message ID to reply to"},
                },
                "required": ["to_number", "body_text", "buttons"],
            },
        ),
        Tool(
            name="WHATSAPP_SEND_INTERACTIVE_LIST",
            description="Send an interactive list message (up to 10 options). Delivered only if recipient has texted first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "to_number": {"type": "string", "description": "Recipient in international format"},
                    "body_text": {"type": "string", "description": "Main body text"},
                    "button_text": {"type": "string", "description": "Text on the list button"},
                    "sections": {"type": "array", "description": "Sections: [{title?, rows: [{id?, title, description?}]}]", "items": {"type": "object"}},
                    "header_text": {"type": "string", "description": "Optional header"},
                    "footer_text": {"type": "string", "description": "Optional footer"},
                    "reply_to_message_id": {"type": "string", "description": "Optional message ID to reply to"},
                },
                "required": ["to_number", "body_text", "button_text", "sections"],
            },
        ),
    ]


async def handle_messaging_tool(name: str, arguments: dict[str, Any]) -> Sequence:
    """Handle messaging tool execution."""
    handlers = {
        "WHATSAPP_SEND_MESSAGE": send_message,
        "WHATSAPP_SEND_REPLY": send_reply,
        "WHATSAPP_SEND_TEMPLATE_MESSAGE": send_template_message,
        "WHATSAPP_SEND_MEDIA": send_media,
        "WHATSAPP_SEND_MEDIA_BY_ID": send_media_by_id,
        "WHATSAPP_SEND_CONTACTS": send_contacts,
        "WHATSAPP_SEND_LOCATION": send_location,
        "WHATSAPP_SEND_INTERACTIVE_BUTTONS": send_interactive_buttons,
        "WHATSAPP_SEND_INTERACTIVE_LIST": send_interactive_list,
    }
    if name not in handlers:
        raise ValueError(f"Unknown messaging tool: {name}")
    return await handlers[name](arguments)


def _missing(*pairs):  # noqa
    return [p for p, v in pairs if not v]


async def send_message(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    text = arguments.get("text")
    if _missing((("to_number", to_number), ("text", text))):
        return create_error_response("Missing required parameter(s): to_number, text")
    preview_url = arguments.get("preview_url", False)
    if isinstance(preview_url, bool):
        preview_url_bool = preview_url
    else:
        preview_url_bool = str(preview_url).strip().lower() in {"1", "true", "yes", "y", "on"} if preview_url is not None else False
    message_id = arguments.get("message_id") or arguments.get("reply_to_message_id")
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "text",
        "text": {"body": str(text), "preview_url": preview_url_bool},
    }
    if message_id:
        payload["context"] = {"message_id": str(message_id)}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_reply(arguments: dict[str, Any]) -> Sequence:
    to_number = arguments.get("to_number")
    text = arguments.get("text")
    reply_to_message_id = arguments.get("reply_to_message_id")
    if _missing((("to_number", to_number), ("text", text), ("reply_to_message_id", reply_to_message_id))):
        return create_error_response("Missing required parameter(s): to_number, text, reply_to_message_id")
    args2 = dict(arguments)
    args2["message_id"] = str(reply_to_message_id)
    return await send_message(args2)


async def send_template_message(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    template_name = arguments.get("template_name")
    if _missing((("to_number", to_number), ("template_name", template_name))):
        return create_error_response("Missing required parameter(s): to_number, template_name")
    language_code = arguments.get("language_code") or "en_US"
    components = arguments.get("components")
    template_obj = {"name": str(template_name), "language": {"code": str(language_code)}}
    if components:
        template_obj["components"] = components
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "template",
        "template": template_obj,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_media(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    phone_number_id = arguments.get("phone_number_id") or WHATSAPP_PHONE_NUMBER_ID
    if not phone_number_id:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    media_type = arguments.get("media_type")
    link = arguments.get("link")
    caption = arguments.get("caption")
    if _missing((("to_number", to_number), ("media_type", media_type), ("link", link))):
        return create_error_response("Missing required parameter(s): to_number, media_type, link")
    media_type = str(media_type).lower().strip()
    if media_type not in {"image", "video", "audio", "document", "sticker"}:
        return create_error_response("media_type must be one of: image, video, audio, document, sticker")
    media_obj = {"link": str(link)}
    if caption and media_type in {"image", "video", "document"}:
        media_obj["caption"] = str(caption)
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": media_type,
        media_type: media_obj,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{phone_number_id}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_media_by_id(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    media_type = arguments.get("media_type")
    media_id = arguments.get("media_id")
    caption = arguments.get("caption")
    filename = arguments.get("filename")
    reply_to_message_id = arguments.get("reply_to_message_id")
    if _missing((("to_number", to_number), ("media_type", media_type), ("media_id", media_id))):
        return create_error_response("Missing required parameter(s): to_number, media_type, media_id")
    media_type = str(media_type).lower().strip()
    if media_type not in {"image", "video", "audio", "document", "sticker"}:
        return create_error_response("media_type must be one of: image, video, audio, document, sticker")
    media_obj = {"id": str(media_id)}
    if caption and media_type in {"image", "video", "document"}:
        media_obj["caption"] = str(caption)
    if filename and media_type == "document":
        media_obj["filename"] = str(filename)
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": media_type,
        media_type: media_obj,
    }
    if reply_to_message_id:
        payload["context"] = {"message_id": str(reply_to_message_id)}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_contacts(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    contacts = arguments.get("contacts")
    if _missing((("to_number", to_number), ("contacts", contacts))):
        return create_error_response("Missing required parameter(s): to_number, contacts")
    if not isinstance(contacts, list) or len(contacts) == 0:
        return create_error_response("contacts must be a non-empty array")
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_number,
        "type": "contacts",
        "contacts": contacts,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_location(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    latitude = arguments.get("latitude")
    longitude = arguments.get("longitude")
    name = arguments.get("name")
    address = arguments.get("address")
    if _missing((("to_number", to_number), ("latitude", latitude), ("longitude", longitude), ("name", name), ("address", address))):
        return create_error_response("Missing required parameter(s): to_number, latitude, longitude, name, address")
    try:
        lat_val = float(str(latitude))
        lon_val = float(str(longitude))
    except Exception:
        return create_error_response("latitude and longitude must be valid numbers")
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "location",
        "location": {"latitude": lat_val, "longitude": lon_val, "name": str(name), "address": str(address)},
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_interactive_buttons(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    body_text = arguments.get("body_text")
    buttons = arguments.get("buttons")
    if _missing((("to_number", to_number), ("body_text", body_text), ("buttons", buttons))):
        return create_error_response("Missing required parameter(s): to_number, body_text, buttons")
    if not isinstance(buttons, list) or len(buttons) == 0:
        return create_error_response("buttons must be a non-empty array")
    if len(buttons) > 3:
        return create_error_response("buttons can have at most 3 items")
    wa_buttons = []
    for idx, b in enumerate(buttons):
        if not isinstance(b, dict) or not b.get("title"):
            return create_error_response("Each button must be an object with at least a non-empty 'title' field")
        btn_id = b.get("id") or f"btn_{idx+1}"
        wa_buttons.append({"type": "reply", "reply": {"id": str(btn_id), "title": str(b["title"])}})
    interactive = {"type": "button", "body": {"text": str(body_text)}, "action": {"buttons": wa_buttons}}
    if arguments.get("header_text"):
        interactive["header"] = {"type": "text", "text": str(arguments["header_text"])}
    if arguments.get("footer_text"):
        interactive["footer"] = {"text": str(arguments["footer_text"])}
    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "interactive",
        "interactive": interactive,
    }
    if arguments.get("reply_to_message_id"):
        body["context"] = {"message_id": str(arguments["reply_to_message_id"])}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=body,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")


async def send_interactive_list(arguments: dict[str, Any]) -> Sequence:
    token = await get_valid_token()
    if not token:
        return create_error_response(get_token_error_message())
    if not WHATSAPP_PHONE_NUMBER_ID:
        return create_error_response("WHATSAPP_PHONE_NUMBER_ID is not set")
    to_number = arguments.get("to_number")
    body_text = arguments.get("body_text")
    button_text = arguments.get("button_text")
    sections = arguments.get("sections")
    if _missing((("to_number", to_number), ("body_text", body_text), ("button_text", button_text), ("sections", sections))):
        return create_error_response("Missing required parameter(s): to_number, body_text, button_text, sections")
    if not isinstance(sections, list) or len(sections) == 0:
        return create_error_response("sections must be a non-empty array")
    total_rows = 0
    wa_sections = []
    for s_idx, s in enumerate(sections):
        if not isinstance(s, dict) or not isinstance(s.get("rows"), list) or len(s.get("rows")) == 0:
            return create_error_response("Each section must be an object with a non-empty 'rows' array")
        wa_rows = []
        for r_idx, r in enumerate(s["rows"]):
            if not isinstance(r, dict) or not r.get("title"):
                return create_error_response("Each row must be an object with at least a non-empty 'title' field")
            row_id = r.get("id") or f"row_{s_idx+1}_{r_idx+1}"
            row_obj = {"id": str(row_id), "title": str(r["title"])}
            if r.get("description"):
                row_obj["description"] = str(r["description"])
            wa_rows.append(row_obj)
            total_rows += 1
            if total_rows > 10:
                return create_error_response("List messages support at most 10 total rows across all sections")
        section_obj = {"rows": wa_rows}
        if s.get("title"):
            section_obj["title"] = str(s["title"])
        wa_sections.append(section_obj)
    interactive = {"type": "list", "body": {"text": str(body_text)}, "action": {"button": str(button_text), "sections": wa_sections}}
    if arguments.get("header_text"):
        interactive["header"] = {"type": "text", "text": str(arguments["header_text"])}
    if arguments.get("footer_text"):
        interactive["footer"] = {"text": str(arguments["footer_text"])}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(to_number),
        "type": "interactive",
        "interactive": interactive,
    }
    if arguments.get("reply_to_message_id"):
        payload["context"] = {"message_id": str(arguments["reply_to_message_id"])}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return create_success_response(resp.json())
    except httpx.HTTPStatusError as e:
        error_data = e.response.json() if e.response.content else {}
        return create_error_response(error_data.get("error", {}).get("message", str(e)), error_data)
    except Exception as e:
        return create_error_response(f"Unexpected error: {str(e)}")
