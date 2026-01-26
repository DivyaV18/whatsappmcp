# WhatsApp MCP Server

A comprehensive Model Context Protocol (MCP) server for WhatsApp Business API integration. This server provides 19+ tools for managing templates, sending messages, handling media, and interacting with WhatsApp Business accounts—similar to Composio's WhatsApp toolkit.

## 🚀 Features

### Template Management (4 tools)
- ✅ **WHATSAPP_CREATE_MESSAGE_TEMPLATE** - Create new message templates
- ✅ **WHATSAPP_DELETE_MESSAGE_TEMPLATE** - Delete existing templates
- ✅ **WHATSAPP_GET_MESSAGE_TEMPLATES** - List all templates with filters
- ✅ **WHATSAPP_GET_TEMPLATE_STATUS** - Check template approval status

### Profile & Phone Number Management (3 tools)
- ✅ **WHATSAPP_GET_BUSINESS_PROFILE** - Get business profile information
- ✅ **WHATSAPP_GET_PHONE_NUMBER** - Get details of a specific phone number
- ✅ **WHATSAPP_GET_PHONE_NUMBERS** - List all phone numbers in your account

### Media Management (3 tools)
- ✅ **WHATSAPP_UPLOAD_MEDIA** - Upload media files to WhatsApp servers
- ✅ **WHATSAPP_GET_MEDIA** - Get media info with download URL (valid 5 min)
- ✅ **WHATSAPP_GET_MEDIA_INFO** - Get media metadata without download URL

### Messaging (9 tools)
- ✅ **WHATSAPP_SEND_MESSAGE** - Send plain text messages
- ✅ **WHATSAPP_SEND_REPLY** - Send contextual replies to messages
- ✅ **WHATSAPP_SEND_TEMPLATE_MESSAGE** - Send approved template messages
- ✅ **WHATSAPP_SEND_MEDIA** - Send media by URL (image/video/audio/document/sticker)
- ✅ **WHATSAPP_SEND_MEDIA_BY_ID** - Send media using uploaded media ID
- ✅ **WHATSAPP_SEND_CONTACTS** - Send contact cards
- ✅ **WHATSAPP_SEND_LOCATION** - Send location messages
- ✅ **WHATSAPP_SEND_INTERACTIVE_BUTTONS** - Send interactive button messages (up to 3 buttons)
- ✅ **WHATSAPP_SEND_INTERACTIVE_LIST** - Send interactive list messages (up to 10 options)

## 📋 Prerequisites

- **Python 3.8+** installed
- **WhatsApp Business API credentials** from [Meta for Developers](https://developers.facebook.com/):
  - **Bearer Token** (API Key) - Temporary or permanent access token
  - **WhatsApp Business Account ID (WABA ID)** - Required for template operations
  - **Phone Number ID** - Required for messaging operations
- **MCP Inspector** or any MCP-compatible client

## 🔧 Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Create a `.env` file** in the project root:

```bash
# Windows (PowerShell)
New-Item -Path .env -ItemType File

# Linux/Mac
touch .env
```

2. **Copy configuration from `env.example`** and fill in your credentials:

```env
# Your WhatsApp Business API Bearer Token (API Key)
WHATSAPP_BEARER_TOKEN=your_bearer_token_here

# Your WhatsApp Business Account ID (WABA ID) - used for template creation
WHATSAPP_BUSINESS_ACCOUNT_ID=your_whatsapp_business_account_id_here

# Your WhatsApp Business Phone Number ID - used for messaging
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here

# WhatsApp API Version (default: v18.0)
WHATSAPP_API_VERSION=v18.0
```

### How to Get Credentials

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create or select your app
3. Add **WhatsApp** product to your app
4. Navigate to **WhatsApp → API Setup**
5. Copy:
   - **Temporary Access Token** (or generate a permanent one)
   - **WhatsApp Business Account ID** (WABA ID)
   - **Phone Number ID**

> ⚠️ **Security Note**: Never commit your `.env` file to version control. It contains sensitive credentials.

## 🎯 Usage

### Running the Server

```bash
python server.py
```

The server runs on **stdio** and is ready to accept connections from MCP clients.

### Using with MCP Inspector

1. **Start the server:**
```bash
python server.py
```

2. **In MCP Inspector**, configure the server:
   - **Command**: `python`
   - **Args**: `["server.py"]`
   - **Working Directory**: Path to this project directory

3. **Connect** - MCP Inspector will automatically discover and list all 19 available tools

4. **Test tools** directly from MCP Inspector's UI!

## 📚 Complete API Reference

### Template Management

#### WHATSAPP_CREATE_MESSAGE_TEMPLATE
Create a new message template for your WhatsApp Business Account.

**Parameters:**
- `name` (string, required) - Template name
- `language` (string, required) - Language code (e.g., `en_US`, `es_ES`)
- `category` (string, required) - One of: `MARKETING`, `UTILITY`, `AUTHENTICATION`
- `components` (array, required) - Template components (HEADER, BODY, FOOTER, BUTTONS)

**Example:**
```json
{
  "name": "welcome_template",
  "language": "en_US",
  "category": "UTILITY",
  "components": [
    {
      "type": "BODY",
      "text": "Hello {{1}}, welcome to our service!"
    }
  ]
}
```

#### WHATSAPP_DELETE_MESSAGE_TEMPLATE
Delete a message template permanently.

**Parameters:**
- `template_id` (string, required) - Template ID to delete

#### WHATSAPP_GET_MESSAGE_TEMPLATES
Get all message templates with optional filters.

**Parameters:**
- `after` (string, optional) - Pagination cursor
- `category` (string, optional) - Filter by category
- `language` (string, optional) - Filter by language
- `limit` (integer, optional, default: 25) - Number of results
- `name_or_content` (string, optional) - Search term
- `status` (string, optional) - Filter by status

#### WHATSAPP_GET_TEMPLATE_STATUS
Get the status and details of a specific template.

**Parameters:**
- `template_id` (string, required) - Template ID
- `fields` (string, optional) - Comma-separated fields to return

### Profile & Phone Number Management

#### WHATSAPP_GET_BUSINESS_PROFILE
Get business profile information.

**Parameters:**
- `phone_number_id` (string, required) - Phone number ID
- `fields` (string, optional) - Comma-separated fields (default: `about,address,description,email,profile_picture_url,websites,vertical`)

#### WHATSAPP_GET_PHONE_NUMBER
Get details of a specific phone number.

**Parameters:**
- `phone_number_id` (string, required) - Phone number ID
- `fields` (string, optional) - Comma-separated fields to return

#### WHATSAPP_GET_PHONE_NUMBERS
List all phone numbers in your WhatsApp Business Account.

**Parameters:**
- `limit` (integer, optional, default: 25) - Number of results

### Media Management

#### WHATSAPP_UPLOAD_MEDIA
Upload media files to WhatsApp servers. Returns a media ID for use with `WHATSAPP_SEND_MEDIA_BY_ID`.

**Supported formats:**
- **Images**: JPEG, PNG (max 5MB)
- **Videos**: MP4, 3GPP (max 16MB)
- **Audio**: AAC, M4A, AMR, MP3, OGG (max 16MB)
- **Documents**: PDF, DOC, DOCX, PPT, PPTX, XLS, XLSX (max 100MB)
- **Stickers**: WebP (max 500KB, 512x512 pixels)

**Parameters:**
- `phone_number_id` (string, required) - Phone number ID
- `media_type` (string, required) - One of: `image`, `video`, `audio`, `document`, `sticker`
- `file_to_upload` (object, required) - File object:
  - `path` (string, required) - Absolute or relative file path
  - `filename` (string, optional) - Override filename
  - `mime_type` (string, optional) - Override MIME type

**Example:**
```json
{
  "phone_number_id": "123456789",
  "media_type": "image",
  "file_to_upload": {
    "path": "D:\\images\\photo.jpg"
  }
}
```

**Response:** Returns `id` (media_id) that can be used with `WHATSAPP_SEND_MEDIA_BY_ID`.

#### WHATSAPP_GET_MEDIA
Get media information including a temporary download URL (valid for 5 minutes).

**Parameters:**
- `media_id` (string, required) - Media ID

#### WHATSAPP_GET_MEDIA_INFO
Get media metadata (size, type, hash) without download URL.

**Parameters:**
- `media_id` (string, required) - Media ID

### Messaging

#### WHATSAPP_SEND_MESSAGE
Send a plain text message.

**Parameters:**
- `phone_number_id` (string, required) - Sender phone number ID
- `to_number` (string, required) - Recipient in international format (e.g., `+919876543210`)
- `text` (string, required) - Message text
- `preview_url` (boolean, optional, default: `false`) - Show URL preview
- `message_id` (string, optional) - Message ID to reply to

**Example:**
```json
{
  "phone_number_id": "123456789",
  "to_number": "+919876543210",
  "text": "Hello from WhatsApp MCP!",
  "preview_url": false
}
```

> ⚠️ **Note**: Messages are only delivered if the recipient has texted first (24-hour window) or you're using an approved template.

#### WHATSAPP_SEND_REPLY
Send a contextual reply to a specific message.

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `text` (string, required)
- `reply_to_message_id` (string, required) - Message ID to reply to
- `preview_url` (boolean, optional) - Show URL preview

#### WHATSAPP_SEND_TEMPLATE_MESSAGE
Send an approved template message.

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `template_name` (string, required) - Approved template name
- `language_code` (string, optional, default: `en_US`) - Template language
- `components` (array, optional) - Template components (for variables/buttons)

**Example:**
```json
{
  "phone_number_id": "123456789",
  "to_number": "+919876543210",
  "template_name": "welcome_template",
  "language_code": "en_US"
}
```

#### WHATSAPP_SEND_MEDIA
Send media using a publicly accessible URL.

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `media_type` (string, required) - One of: `image`, `video`, `audio`, `document`, `sticker`
- `link` (string, required) - Publicly accessible HTTPS URL
- `caption` (string, optional) - Caption (for image/video/document)

#### WHATSAPP_SEND_MEDIA_BY_ID
Send media using a previously uploaded media ID (more efficient).

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `media_type` (string, required) - One of: `image`, `video`, `audio`, `document`, `sticker`
- `media_id` (string, required) - Media ID from upload
- `caption` (string, optional) - Caption
- `filename` (string, optional) - Filename (for documents)
- `reply_to_message_id` (string, optional) - Message ID to reply to

#### WHATSAPP_SEND_CONTACTS
Send contact cards.

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `contacts` (array, required) - Array of contact objects

**Example:**
```json
{
  "phone_number_id": "123456789",
  "to_number": "+919876543210",
  "contacts": [
    {
      "name": {
        "formatted_name": "John Doe",
        "first_name": "John",
        "last_name": "Doe"
      },
      "phones": [
        {
          "phone": "+1234567890",
          "type": "WORK"
        }
      ]
    }
  ]
}
```

#### WHATSAPP_SEND_LOCATION
Send a location message.

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `latitude` (string, required) - Latitude (e.g., `12.9716`)
- `longitude` (string, required) - Longitude (e.g., `77.5946`)
- `name` (string, required) - Location name
- `address` (string, required) - Location address

#### WHATSAPP_SEND_INTERACTIVE_BUTTONS
Send an interactive button message (up to 3 buttons).

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `body_text` (string, required) - Main body text
- `buttons` (array, required) - Up to 3 buttons, each with `id` and `title`
- `header_text` (string, optional) - Header text
- `footer_text` (string, optional) - Footer text
- `reply_to_message_id` (string, optional) - Message ID to reply to

**Example:**
```json
{
  "phone_number_id": "123456789",
  "to_number": "+919876543210",
  "body_text": "Choose an option:",
  "buttons": [
    {"id": "btn1", "title": "Yes"},
    {"id": "btn2", "title": "No"}
  ]
}
```

#### WHATSAPP_SEND_INTERACTIVE_LIST
Send an interactive list message (up to 10 options across sections).

**Parameters:**
- `phone_number_id` (string, required)
- `to_number` (string, required)
- `body_text` (string, required) - Main body text
- `button_text` (string, required) - Text on the list button
- `sections` (array, required) - List sections, each with `title` and `rows`
- `header_text` (string, optional) - Header text
- `footer_text` (string, optional) - Footer text
- `reply_to_message_id` (string, optional) - Message ID to reply to

**Example:**
```json
{
  "phone_number_id": "123456789",
  "to_number": "+919876543210",
  "body_text": "Select an option:",
  "button_text": "View Options",
  "sections": [
    {
      "title": "Main",
      "rows": [
        {"id": "opt1", "title": "Option 1", "description": "First choice"},
        {"id": "opt2", "title": "Option 2", "description": "Second choice"}
      ]
    }
  ]
}
```

## 🔍 Response Format

All tools return a consistent JSON response:

```json
{
  "successful": true,
  "data": {
    // API response data
  }
}
```

On error:
```json
{
  "successful": false,
  "error": "Error message here",
  "data": {
    // Additional error details
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### 1. **"WHATSAPP_BEARER_TOKEN is not set"**
- Ensure your `.env` file exists and contains `WHATSAPP_BEARER_TOKEN`
- Restart the server after updating `.env`

#### 2. **"Error validating access token: Session has expired" (OAuthException, code 190)**
- Your temporary access token has expired
- Generate a new token from [Meta for Developers](https://developers.facebook.com/apps/)
- Update `.env` and restart the server

#### 3. **"Recipient phone number not in allowed list" (Code 131030)**
- This is a **sandbox limitation**
- Add the recipient number to the allowed list:
  1. Go to Meta for Developers → Your App → WhatsApp → API Setup
  2. Add recipient phone number
  3. Verify the number
- Or ensure the recipient has sent you a message first

#### 4. **"Invalid parameter" / "Missing both components and library template name"**
- For template creation, ensure `components` is a valid non-empty array
- At minimum, include a `BODY` component

#### 5. **"Unsupported post request. Object with ID does not exist"**
- Verify your `phone_number_id` is correct
- Ensure you're using the correct ID (not WABA ID) for messaging operations

#### 6. **File not found (WHATSAPP_UPLOAD_MEDIA)**
- Use absolute paths or ensure relative paths are correct
- Check file permissions
- Verify the file exists and is readable

### Debugging Tips

1. **Check server logs** - The server prints warnings on startup if credentials are missing
2. **Verify credentials** - Use `WHATSAPP_GET_PHONE_NUMBERS` to test your token
3. **Test with MCP Inspector** - Use the UI to test tools and see full error responses
4. **Check API version** - Ensure `WHATSAPP_API_VERSION` matches your account's supported version

## 📁 Project Structure

```
whatsappmcp/
├── server.py           # Main MCP server implementation (all 19 tools)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from env.example)
├── env.example        # Example environment file
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## 🔐 Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Use permanent tokens** - For production, generate long-lived tokens
3. **Rotate tokens regularly** - Update tokens periodically
4. **Limit token scope** - Only grant necessary permissions
5. **Monitor API usage** - Check Meta Business Suite for unusual activity

## 📖 References

- [Composio WhatsApp Toolkit](https://docs.composio.dev/toolkits/whatsapp) - Inspiration for this project
- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp) - Official API docs
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- [Meta for Developers](https://developers.facebook.com/) - Get your credentials

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available for use.

## ⚡ Quick Start Example

1. **Install:**
```bash
pip install -r requirements.txt
```

2. **Configure `.env`:**
```env
WHATSAPP_BEARER_TOKEN=your_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_waba_id
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
```

3. **Run:**
```bash
python server.py
```

4. **Connect MCP Inspector** and start using the tools!

---

**Made with ❤️ for the MCP community**
