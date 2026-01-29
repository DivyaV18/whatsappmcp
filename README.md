# WhatsApp MCP Server

A comprehensive Model Context Protocol (MCP) server for WhatsApp Business API integration. This server provides **19 powerful tools** for managing templates, sending messages, handling media, and interacting with WhatsApp Business accounts.

**Built with a clean, modular architecture** - organized by functionality for easy maintenance and extension.

## 🚀 Features

### 📋 Template Management (4 tools)
- ✅ **WHATSAPP_CREATE_MESSAGE_TEMPLATE** - Create new message templates
- ✅ **WHATSAPP_DELETE_MESSAGE_TEMPLATE** - Delete existing templates
- ✅ **WHATSAPP_GET_MESSAGE_TEMPLATES** - List all templates with filters
- ✅ **WHATSAPP_GET_TEMPLATE_STATUS** - Check template approval status

### 👤 Profile & Phone Number Management (3 tools)
- ✅ **WHATSAPP_GET_BUSINESS_PROFILE** - Get business profile information
- ✅ **WHATSAPP_GET_PHONE_NUMBER** - Get details of a specific phone number
- ✅ **WHATSAPP_GET_PHONE_NUMBERS** - List all phone numbers in your account

### 📎 Media Management (3 tools)
- ✅ **WHATSAPP_UPLOAD_MEDIA** - Upload media files to WhatsApp servers
- ✅ **WHATSAPP_GET_MEDIA** - Get media info with download URL (valid 5 min)
- ✅ **WHATSAPP_GET_MEDIA_INFO** - Get media metadata without download URL

### 💬 Messaging (9 tools)
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
- **WhatsApp Business API OAuth2 credentials** from [Meta for Developers](https://developers.facebook.com/):
  - **Client ID** (App ID)
  - **Client Secret** (App Secret)
  - **WhatsApp Business Account ID (WABA ID)**
  - **Phone Number ID**
- **MCP Inspector** or any MCP-compatible client

> **Note**: This server uses **OAuth2 authentication only**. Tokens are automatically managed and refreshed.

## 🔧 Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

### Step 1: Create `.env` File

Create a `.env` file in the project root:

```bash
# Windows (PowerShell)
New-Item -Path .env -ItemType File

# Linux/Mac
touch .env
```

### Step 2: Add Your Credentials

Copy the template from `env.example` and fill in your OAuth2 credentials:

```env
# OAuth2 Configuration (REQUIRED)
WHATSAPP_CLIENT_ID=your_client_id_here
WHATSAPP_CLIENT_SECRET=your_client_secret_here

# WhatsApp Business IDs (REQUIRED)
WHATSAPP_BUSINESS_ACCOUNT_ID=your_whatsapp_business_account_id_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here

# Optional (has defaults)
WHATSAPP_API_VERSION=v18.0
```

### Step 3: Get OAuth2 Credentials

#### From Meta for Developers:

1. **Go to [Meta for Developers](https://developers.facebook.com/)**
   - Sign in with your Facebook account

2. **Create or Select Your App**
   - Navigate to **My Apps** → **Create App** (or select existing)
   - Choose **"Business"** as the app type

3. **Add WhatsApp Product**
   - In your app dashboard, find **"WhatsApp"** in products
   - Click **"Set up"** or **"Get Started"**

4. **Get Your Credentials**
   - **Client ID & Secret**: Go to **Settings → Basic**
     - **App ID** → `WHATSAPP_CLIENT_ID`
     - **App Secret** → `WHATSAPP_CLIENT_SECRET` (click "Show")
   - **WABA ID**: Go to **WhatsApp → API Setup**
     - Copy **WhatsApp Business Account ID** → `WHATSAPP_BUSINESS_ACCOUNT_ID`
   - **Phone Number ID**: Go to **WhatsApp → API Setup**
     - Copy **Phone number ID** → `WHATSAPP_PHONE_NUMBER_ID`
     - If not visible, add a phone number first in **WhatsApp → Phone Numbers**

5. **Configure OAuth Redirect URI**
   - Go to **Settings → Basic**
   - Under **"Valid OAuth Redirect URIs"**, add:
     - `http://localhost:8080/callback` (for automated flow)
   - Click **"Save Changes"**

### Step 4: Complete OAuth2 Authorization

**Automated Flow (Recommended):**

```bash
python oauth_manager.py
```

This will:
1. Open your browser automatically
2. Prompt you to authorize the application
3. Capture the callback automatically
4. Save the token to `.oauth_token_cache.json`

**Manual Flow (Alternative):**

If automated flow doesn't work:
1. Run `python oauth_manager.py`
2. Copy the authorization URL from the output
3. Visit it in your browser
4. Copy the authorization code from the callback URL
5. Paste it when prompted

## 🎯 Usage

### Running the Server

```bash
python run_server.py
```

The server runs on **stdio** and is ready to accept connections from MCP clients.

### Using with MCP Inspector

1. **Start the server:**
```bash
python run_server.py
```

2. **Configure MCP Inspector:**
   - **Command**: `python`
   - **Args**: `["run_server.py"]`
   - **Working Directory**: Path to this project directory

3. **Connect** - MCP Inspector will automatically discover and list all 19 available tools

4. **Test tools** directly from MCP Inspector's UI!

### Using with Cursor/Claude Desktop

Add to your MCP configuration (`mcp_config.json` or Cursor settings):

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "python",
      "args": ["run_server.py"],
      "cwd": "/path/to/whatsappmcp",
      "env": {}
    }
  }
}
```

## 📁 Project Structure

```
whatsappmcp/
├── run_server.py              # Entry point script
├── oauth_manager.py           # OAuth2 token management & authorization flow
├── requirements.txt           # Python dependencies
├── mcp_config.json           # MCP server configuration example
├── env.example               # Environment variables template
├── .env                      # Your credentials (create from env.example)
├── .oauth_token_cache.json   # Cached OAuth tokens (auto-generated)
├── .gitignore                # Git ignore rules
├── README.md                  # This file
└── src/
    └── whatsapp_mcp/
        ├── __init__.py
        ├── main.py            # Main MCP server & routing
        ├── config.py          # Configuration & environment loading
        ├── utils.py           # Shared utilities (token handling, responses)
        └── tools/             # Tool implementations (organized by category)
            ├── __init__.py
            ├── templates.py   # Template management (4 tools)
            ├── profile.py     # Profile & phone numbers (3 tools)
            ├── media.py       # Media management (3 tools)
            └── messaging.py   # Messaging tools (9 tools)
```

### Architecture Overview

- **Modular Design**: Tools are organized by functionality in separate modules
- **Centralized Routing**: `main.py` handles tool discovery and routing
- **Shared Utilities**: Common functions (token validation, error handling) in `utils.py`
- **Configuration Management**: Environment variables loaded in `config.py`
- **OAuth2 Integration**: Automatic token refresh and management

## 📚 API Reference

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
- `phone_number_id` (string, optional) - Uses `WHATSAPP_PHONE_NUMBER_ID` from `.env` if not provided
- `fields` (string, optional) - Comma-separated fields (default: `about,address,description,email,profile_picture_url,websites,vertical`)

#### WHATSAPP_GET_PHONE_NUMBER
Get details of a specific phone number.

**Parameters:**
- `phone_number_id` (string, optional) - Uses `WHATSAPP_PHONE_NUMBER_ID` from `.env` if not provided
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
- `media_type` (string, required) - One of: `image`, `video`, `audio`, `document`, `sticker`
- `file_to_upload` (object, required) - File object:
  - `path` (string, required) - Absolute or relative file path
  - `filename` (string, optional) - Override filename
  - `mime_type` (string, optional) - Override MIME type

**Example:**
```json
{
  "media_type": "image",
  "file_to_upload": {
    "path": "D:\\images\\photo.jpg"
  }
}
```

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
- `to_number` (string, required) - Recipient in international format (e.g., `+919876543210`)
- `text` (string, required) - Message text
- `preview_url` (boolean, optional, default: `false`) - Show URL preview
- `message_id` (string, optional) - Message ID to reply to

**Example:**
```json
{
  "to_number": "+919876543210",
  "text": "Hello from WhatsApp MCP!",
  "preview_url": false
}
```

> ⚠️ **Note**: Messages are only delivered if the recipient has texted first (24-hour window) or you're using an approved template.

#### WHATSAPP_SEND_REPLY
Send a contextual reply to a specific message.

**Parameters:**
- `to_number` (string, required)
- `text` (string, required)
- `reply_to_message_id` (string, required) - Message ID to reply to
- `preview_url` (boolean, optional) - Show URL preview

#### WHATSAPP_SEND_TEMPLATE_MESSAGE
Send an approved template message.

**Parameters:**
- `to_number` (string, required)
- `template_name` (string, required) - Approved template name
- `language_code` (string, optional, default: `en_US`) - Template language
- `components` (array, optional) - Template components (for variables/buttons)

**Example:**
```json
{
  "to_number": "+919876543210",
  "template_name": "welcome_template",
  "language_code": "en_US",
  "components": [
    {
      "type": "body",
      "parameters": [
        {"type": "text", "text": "John"}
      ]
    }
  ]
}
```

#### WHATSAPP_SEND_MEDIA
Send media using a publicly accessible URL.

**Parameters:**
- `to_number` (string, required)
- `media_type` (string, required) - One of: `image`, `video`, `audio`, `document`, `sticker`
- `link` (string, required) - Publicly accessible HTTPS URL
- `caption` (string, optional) - Caption (for image/video/document)

#### WHATSAPP_SEND_MEDIA_BY_ID
Send media using a previously uploaded media ID (more efficient).

**Parameters:**
- `to_number` (string, required)
- `media_type` (string, required) - One of: `image`, `video`, `audio`, `document`, `sticker`
- `media_id` (string, required) - Media ID from upload
- `caption` (string, optional) - Caption
- `filename` (string, optional) - Filename (for documents)
- `reply_to_message_id` (string, optional) - Message ID to reply to

#### WHATSAPP_SEND_CONTACTS
Send contact cards.

**Parameters:**
- `to_number` (string, required)
- `contacts` (array, required) - Array of contact objects

**Example:**
```json
{
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
- `to_number` (string, required)
- `latitude` (string, required) - Latitude (e.g., `12.9716`)
- `longitude` (string, required) - Longitude (e.g., `77.5946`)
- `name` (string, required) - Location name
- `address` (string, required) - Location address

#### WHATSAPP_SEND_INTERACTIVE_BUTTONS
Send an interactive button message (up to 3 buttons).

**Parameters:**
- `to_number` (string, required)
- `body_text` (string, required) - Main body text
- `buttons` (array, required) - Up to 3 buttons, each with `id` and `title`
- `header_text` (string, optional) - Header text
- `footer_text` (string, optional) - Footer text
- `reply_to_message_id` (string, optional) - Message ID to reply to

**Example:**
```json
{
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

**Success:**
```json
{
  "successful": true,
  "data": {
    // API response data
  }
}
```

**Error:**
```json
{
  "successful": false,
  "error": "Error message here",
  "data": {
    // Additional error details (if available)
  }
}
```

## 🔐 OAuth2 Token Management

### Automatic Token Refresh

The server automatically refreshes tokens before they expire:
- Tokens are checked on every API call
- If a token expires within 1 day, it's automatically refreshed
- New tokens are valid for 60 days
- Tokens are cached in `.oauth_token_cache.json`

### Manual Token Refresh

If you need to manually refresh your token:

```bash
python oauth_manager.py
```

This will:
1. Check if your current token is expiring soon
2. Automatically refresh it if needed
3. Save the new token to `.oauth_token_cache.json`

## 🐛 Troubleshooting

### Common Issues

#### 1. **"OAuth2 token not available"**
- **Solution**: Run `python oauth_manager.py` to complete authorization
- Ensure `.env` file has `WHATSAPP_CLIENT_ID` and `WHATSAPP_CLIENT_SECRET`

#### 2. **"Error validating access token: Session has expired"**
- **Solution**: Token has expired. Run `python oauth_manager.py` to refresh
- The server should auto-refresh, but manual refresh may be needed

#### 3. **"Recipient phone number not in allowed list" (Code 131030)**
- **Solution**: This is a sandbox limitation
- Add recipient number in Meta Dashboard → WhatsApp → API Setup → "To" field
- Or ensure recipient has sent you a message first (24-hour window)

#### 4. **"WHATSAPP_PHONE_NUMBER_ID is not set"**
- **Solution**: Add `WHATSAPP_PHONE_NUMBER_ID` to your `.env` file
- Get it from Meta Dashboard → WhatsApp → API Setup

#### 5. **"WHATSAPP_BUSINESS_ACCOUNT_ID is not set"**
- **Solution**: Add `WHATSAPP_BUSINESS_ACCOUNT_ID` to your `.env` file
- Get it from Meta Dashboard → WhatsApp → API Setup

#### 6. **OAuth callback not working**
- **Solution**: Ensure `http://localhost:8080/callback` is in your app's Valid OAuth Redirect URIs
- Check that your app is in Development Mode (not Live Mode)
- Try the manual flow if automated flow fails

#### 7. **File not found (WHATSAPP_UPLOAD_MEDIA)**
- **Solution**: Use absolute paths or ensure relative paths are correct
- Check file permissions
- Verify the file exists and is readable

#### 8. **Import errors**
- **Solution**: Ensure you're running from the project root directory
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version is 3.8+

### Debugging Tips

1. **Check server logs** - The server prints warnings on startup if credentials are missing
2. **Verify credentials** - Use `WHATSAPP_GET_PHONE_NUMBERS` to test your token
3. **Test with MCP Inspector** - Use the UI to test tools and see full error responses
4. **Check API version** - Ensure `WHATSAPP_API_VERSION` matches your account's supported version
5. **Check token file** - Verify `.oauth_token_cache.json` exists and contains valid token

## 🔒 Security Best Practices

1. **Never commit `.env`** - Already in `.gitignore`
2. **Never commit `.oauth_token_cache.json`** - Already in `.gitignore`
3. **Use environment variables** - Never hardcode credentials
4. **Rotate tokens regularly** - Update tokens periodically for security
5. **Limit token scope** - Only grant necessary permissions
6. **Monitor API usage** - Check Meta Business Suite for unusual activity
7. **Keep dependencies updated** - Regularly update packages for security patches

## 🏗️ Development

### Project Structure

The project follows a modular architecture:

- **`src/whatsapp_mcp/main.py`**: Main MCP server, tool discovery, and routing
- **`src/whatsapp_mcp/config.py`**: Configuration loading and OAuth manager initialization
- **`src/whatsapp_mcp/utils.py`**: Shared utilities (token validation, response formatting)
- **`src/whatsapp_mcp/tools/`**: Tool implementations organized by category
  - `templates.py`: Template management tools
  - `profile.py`: Profile and phone number tools
  - `media.py`: Media management tools
  - `messaging.py`: Messaging tools

### Adding New Tools

1. **Add tool definition** in the appropriate `tools/*.py` file:
   ```python
   Tool(
       name="WHATSAPP_NEW_TOOL",
       description="Tool description",
       inputSchema={...}
   )
   ```

2. **Add handler function**:
   ```python
   async def handle_new_tool(arguments: dict[str, Any]) -> Sequence:
       token = await get_valid_token()
       if not token:
           return create_error_response(get_token_error_message())
       # Implementation...
   ```

3. **Update handler router** in the same file:
   ```python
   async def handle_category_tool(name: str, arguments: dict[str, Any]) -> Sequence:
       if name == "WHATSAPP_NEW_TOOL":
           return await handle_new_tool(arguments)
       # ...
   ```

4. **Export in `tools/__init__.py`** (if needed)

5. **Add to tool set** in `main.py`:
   ```python
   CATEGORY_TOOLS = {
       "WHATSAPP_NEW_TOOL",
       # ...
   }
   ```

6. **Update routing** in `main.py`:
   ```python
   if name in CATEGORY_TOOLS:
       return await handle_category_tool(name, arguments)
   ```

### Running Tests

```bash
# Test tool discovery
python -c "import sys; sys.path.insert(0, 'src'); from whatsapp_mcp.main import list_tools; import asyncio; tools = asyncio.run(list_tools()); print(f'Found {len(tools)} tools')"

# Test imports
python -c "import sys; sys.path.insert(0, 'src'); from whatsapp_mcp.tools import *; print('All imports successful')"
```

## 📖 References

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp) - Official API docs
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP specification
- [Meta for Developers](https://developers.facebook.com/) - Get your credentials
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Test your MCP server

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Contribution Guidelines

1. Follow the existing code structure and organization
2. Add tools to the appropriate category module
3. Include proper error handling
4. Update documentation for new tools
5. Test your changes thoroughly

## 📝 License

This project is open source and available for use.

## ⚡ Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure `.env`:**
```env
WHATSAPP_CLIENT_ID=your_client_id
WHATSAPP_CLIENT_SECRET=your_client_secret
WHATSAPP_BUSINESS_ACCOUNT_ID=your_waba_id
WHATSAPP_PHONE_NUMBER_ID=your_phone_id
```

3. **Complete OAuth flow:**
```bash
python oauth_manager.py
```

4. **Run the server:**
```bash
python run_server.py
```

5. **Connect MCP Inspector** and start using the tools!

---

**Made with ❤️ for the MCP community**
