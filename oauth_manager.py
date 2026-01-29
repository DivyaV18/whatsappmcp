#!/usr/bin/env python3
"""
OAuth2 Token Manager for WhatsApp MCP Server
Handles OAuth2 token acquisition, storage, and refresh
"""

import asyncio
import os
import json
import time
from typing import Optional, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()


class OAuth2TokenManager:
    """Manages OAuth2 tokens for WhatsApp Business API"""
    
    def __init__(self):
        self.client_id = os.getenv("WHATSAPP_CLIENT_ID")
        self.client_secret = os.getenv("WHATSAPP_CLIENT_SECRET")
        # redirect_uri is always overridden to localhost:8080 in start_local_oauth_flow
        # Keeping for potential future manual OAuth flows
        self.redirect_uri = os.getenv(
            "WHATSAPP_OAUTH_REDIRECT_URI",
            "http://localhost:8080/callback"
        )
        self.scopes = os.getenv(
            "WHATSAPP_OAUTH_SCOPES",
            "whatsapp_business_management,whatsapp_business_messaging,business_management"
        )
        # WHATSAPP_GENERIC_ID removed - was never used
        
        # Token storage
        self.token_file = os.path.join(
            os.path.dirname(__file__), ".oauth_token_cache.json"
        )
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
        self._refresh_token: Optional[str] = None
        
        # Load cached token if available
        self._load_cached_token()
    
    def _load_cached_token(self) -> None:
        """Load token from cache file"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, "r") as f:
                    data = json.load(f)
                    self._access_token = data.get("access_token")
                    self._token_expires_at = data.get("expires_at")
                    self._refresh_token = data.get("refresh_token")
            except Exception:
                pass
    
    def _save_token(self, access_token: str, expires_in: int, refresh_token: Optional[str] = None) -> None:
        """Save token to cache file"""
        self._access_token = access_token
        self._token_expires_at = time.time() + expires_in
        if refresh_token:
            self._refresh_token = refresh_token
        
        try:
            with open(self.token_file, "w") as f:
                json.dump(
                    {
                        "access_token": access_token,
                        "expires_at": self._token_expires_at,
                        "refresh_token": refresh_token,
                    },
                    f,
                )
        except Exception:
            pass
    
    def is_configured(self) -> bool:
        """Check if OAuth2 is configured"""
        return bool(self.client_id and self.client_secret)
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth2 authorization URL"""
        if not self.is_configured():
            raise ValueError("OAuth2 not configured. Set WHATSAPP_CLIENT_ID and WHATSAPP_CLIENT_SECRET")
        
        import urllib.parse
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": self.scopes,
            "response_type": "code",
            "state": state or "whatsapp_mcp_oauth",
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://www.facebook.com/v18.0/dialog/oauth?{query_string}"
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        if not self.is_configured():
            raise ValueError("OAuth2 not configured")
        
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": authorization_code,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params=params,
                )
                response.raise_for_status()
                token_data = response.json()
                
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
                
                # Try to exchange for long-lived token
                long_lived_token = await self._exchange_for_long_lived_token(access_token)
                if long_lived_token:
                    access_token = long_lived_token.get("access_token", access_token)
                    expires_in = long_lived_token.get("expires_in", expires_in)
                
                self._save_token(access_token, expires_in, token_data.get("refresh_token"))
                
                return {
                    "access_token": access_token,
                    "expires_in": expires_in,
                    "success": True,
                }
        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            return {
                "success": False,
                "error": error_data.get("error", {}).get("message", str(e)),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _exchange_for_long_lived_token(self, short_lived_token: str) -> Optional[Dict[str, Any]]:
        """Exchange short-lived token for long-lived token (60 days)"""
        if not self.is_configured():
            return None
        
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": short_lived_token,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except Exception:
            return None
    
    async def refresh_token(self) -> bool:
        """Refresh access token using refresh token"""
        if not self._refresh_token:
            return False
        
        params = {
            "grant_type": "fb_exchange_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "fb_exchange_token": self._refresh_token,
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://graph.facebook.com/v18.0/oauth/access_token",
                    params=params,
                )
                response.raise_for_status()
                token_data = response.json()
                
                access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in", 3600)
                
                self._save_token(access_token, expires_in, self._refresh_token)
                return True
        except Exception:
            return False

    # Refresh when token expires within this many seconds (1 day)
    REFRESH_BUFFER_SECONDS = 1 * 24 * 3600

    async def refresh_if_needed(self) -> None:
        """
        If the current token is expired or expiring within 1 day, exchange it for a new
        long-lived token using fb_exchange_token. Works without refresh_token.
        """
        if not self._access_token or not self._token_expires_at:
            return
        now = time.time()
        if now < (self._token_expires_at - self.REFRESH_BUFFER_SECONDS):
            return
        if not self.is_configured():
            return
        new_data = await self._exchange_for_long_lived_token(self._access_token)
        if new_data:
            access_token = new_data.get("access_token")
            expires_in = new_data.get("expires_in", 5184000)
            if access_token:
                self._save_token(access_token, expires_in, self._refresh_token)
    
    def get_access_token(self) -> Optional[str]:
        """Get current access token (call refresh_if_needed() first if in async context)."""
        if self._access_token and self._token_expires_at:
            if time.time() < (self._token_expires_at - 300):
                return self._access_token
        return self._access_token
    
    def set_access_token(self, token: str, expires_in: int = 3600) -> None:
        """Manually set access token (for external OAuth flows like Composio)"""
        self._save_token(token, expires_in)
    
    def clear_token(self) -> None:
        """Clear cached token"""
        self._access_token = None
        self._token_expires_at = None
        self._refresh_token = None
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
            except Exception:
                pass

    async def start_local_oauth_flow(self, port: int = 8080) -> str:
        """
        Starts a local HTTP server to listen for the OAuth callback.
        Returns the authorization URL that the user should visit.
        """
        if not self.is_configured():
            raise ValueError("OAuth2 not configured. Set WHATSAPP_CLIENT_ID and WHATSAPP_CLIENT_SECRET")
            
        import http.server
        import socketserver
        import threading
        import urllib.parse
        import webbrowser
        
        # Define handler to capture the code
        auth_code_future = asyncio.Future()
        
        class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urllib.parse.urlparse(self.path)
                if parsed_path.path == '/callback':
                    query_params = urllib.parse.parse_qs(parsed_path.query)
                    
                    if 'code' in query_params:
                        code = query_params['code'][0]
                        auth_code_future.set_result(code)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b"""
                            <html>
                            <head><title>Authentication Successful</title></head>
                            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                                <h1 style="color: #4CAF50;">Authentication Successful!</h1>
                                <p>You have successfully authenticated with WhatsApp.</p>
                                <p>You can close this window and return to your application.</p>
                                <script>window.close();</script>
                            </body>
                            </html>
                        """)
                    else:
                        auth_code_future.set_exception(ValueError("No code found in callback"))
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b"Authentication failed: No code provided.")
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not found")
            
            def log_message(self, format, *args):
                pass  # Suppress logging

        # Start server in a separate thread
        server = socketserver.TCPServer(("localhost", port), OAuthCallbackHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        try:
            # Generate auth URL with the local redirect URI
            original_redirect_uri = self.redirect_uri
            self.redirect_uri = f"http://localhost:{port}/callback"
            auth_url = self.get_authorization_url()
            webbrowser.open(auth_url)
            
            # Wait for the code (with timeout)
            try:
                code = await asyncio.wait_for(auth_code_future, timeout=300) # 5 minutes timeout
            except asyncio.TimeoutError:
                 raise TimeoutError("OAuth flow timed out. Please try again.")
            
            # Exchange code for token
            result = await self.exchange_code_for_token(code)
            
            # Restore original redirect URI (though instance might be short lived)
            self.redirect_uri = original_redirect_uri
            
            if result.get("success"):
                return "Successfully authenticated and token cached."
            else:
                raise ValueError(f"Failed to exchange token: {result.get('error')}")
                
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    """
    Run as script to get OAuth2 token and save to .oauth_token_cache.json.
    Usage: python oauth_manager.py
    Prerequisites: .env with WHATSAPP_CLIENT_ID and WHATSAPP_CLIENT_SECRET.
    Add http://localhost:8080/callback to Meta app Valid OAuth Redirect URIs.
    """
    import sys

    async def main():
        manager = OAuth2TokenManager()
        if not manager.is_configured():
            print("Error: OAuth2 not configured.")
            print("Set WHATSAPP_CLIENT_ID and WHATSAPP_CLIENT_SECRET in your .env file.")
            sys.exit(1)
        port = 8080
        print("Starting OAuth flow. Browser will open; authorize the app.")
        print("Listening on http://localhost:{port}/callback ...".format(port=port))
        try:
            result = await manager.start_local_oauth_flow(port=port)
            print(result)
            token_file = os.path.join(os.path.dirname(__file__), ".oauth_token_cache.json")
            print("Token saved to:", token_file)
            print("You can now run the MCP server (python run_server.py); it will use this token.")
        except TimeoutError as e:
            print("Error:", e)
            sys.exit(1)
        except ValueError as e:
            print("Error:", e)
            sys.exit(1)

    asyncio.run(main())
