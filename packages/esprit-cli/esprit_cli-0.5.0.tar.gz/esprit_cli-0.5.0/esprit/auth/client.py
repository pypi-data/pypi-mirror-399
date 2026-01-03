"""
Supabase authentication client for Esprit CLI.

Handles OAuth flow and API communication with Supabase.
"""

from __future__ import annotations

import asyncio
import http.server
import json
import os
import secrets
import socketserver
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from typing import Any

import requests

from esprit.auth.credentials import Credentials, save_credentials


# Configuration - can be overridden by environment variables
SUPABASE_URL = os.getenv("ESPRIT_SUPABASE_URL", "https://frzsqgyzuikwgqsrdkgz.supabase.co")
SUPABASE_ANON_KEY = os.getenv(
    "ESPRIT_SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZyenNxZ3l6dWlrd2dxc3Jka2d6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxOTU5MDYsImV4cCI6MjA3OTc3MTkwNn0.ZRVsq1lCp8_HPy4EsljdYAn3GhqFfZ1yekQOV2d6KLQ",
)

# Local callback server configuration
CALLBACK_PORT = 54321
CALLBACK_HOST = "localhost"


@dataclass
class AuthResult:
    """Result of authentication attempt."""

    success: bool
    error: str | None = None
    credentials: Credentials | None = None


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler to receive OAuth callback."""

    auth_code: str | None = None
    error: str | None = None
    received_callback = threading.Event()

    def do_GET(self) -> None:
        """Handle GET request from OAuth callback."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == "/auth/callback":
            query_params = urllib.parse.parse_qs(parsed.query)

            if "error" in query_params:
                OAuthCallbackHandler.error = query_params["error"][0]
                self._send_error_page()
            elif "access_token" in query_params:
                # Token is in URL fragment, need to extract from hash
                OAuthCallbackHandler.auth_code = query_params.get("access_token", [None])[0]
                self._send_success_page()
            else:
                # Supabase sends tokens in URL fragment, serve JS to extract
                self._send_token_extractor_page()

            OAuthCallbackHandler.received_callback.set()
        elif parsed.path == "/auth/token":
            # Endpoint to receive token from JS
            query_params = urllib.parse.parse_qs(parsed.query)
            OAuthCallbackHandler.auth_code = query_params.get("token", [None])[0]
            self._send_json_response({"status": "ok"})
            OAuthCallbackHandler.received_callback.set()
        else:
            self.send_response(404)
            self.end_headers()

    def _send_success_page(self) -> None:
        """Send success HTML page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Esprit - Login Successful</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #e8e8e8;
                }
                .container {
                    text-align: center;
                    padding: 40px;
                    background: white;
                    border: 1px solid #d0d0d0;
                    box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
                }
                h1 { color: #111; margin-bottom: 10px; }
                p { color: #666; }
                .checkmark { font-size: 48px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="checkmark">✓</div>
                <h1>Login Successful!</h1>
                <p>You can close this window and return to your terminal.</p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_error_page(self) -> None:
        """Send error HTML page."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Esprit - Login Failed</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #e8e8e8;
                }}
                .container {{
                    text-align: center;
                    padding: 40px;
                    background: white;
                    border: 1px solid #d0d0d0;
                    box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
                }}
                h1 {{ color: #e53935; margin-bottom: 10px; }}
                p {{ color: #666; }}
                .icon {{ font-size: 48px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="icon">✗</div>
                <h1>Login Failed</h1>
                <p>Error: {OAuthCallbackHandler.error}</p>
                <p>Please try again.</p>
            </div>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_token_extractor_page(self) -> None:
        """Send page with JS to extract token from URL fragment."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Esprit - Completing Login...</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background: #e8e8e8;
                }
                .container {
                    text-align: center;
                    padding: 40px;
                    background: white;
                    border: 1px solid #d0d0d0;
                    box-shadow: 4px 4px 0 rgba(0,0,0,0.1);
                }
                .spinner {
                    width: 40px;
                    height: 40px;
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #ff4d00;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 20px;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="spinner"></div>
                <h2>Completing login...</h2>
            </div>
            <script>
                // Extract token from URL hash
                const hash = window.location.hash.substring(1);
                const params = new URLSearchParams(hash);
                const accessToken = params.get('access_token');

                if (accessToken) {
                    // Send token to local server
                    fetch('/auth/token?token=' + encodeURIComponent(accessToken))
                        .then(() => {
                            document.body.innerHTML = `
                                <div class="container">
                                    <div style="font-size: 48px; margin-bottom: 20px;">✓</div>
                                    <h1>Login Successful!</h1>
                                    <p>You can close this window and return to your terminal.</p>
                                </div>
                            `;
                        });
                } else {
                    document.body.innerHTML = `
                        <div class="container">
                            <div style="font-size: 48px; margin-bottom: 20px;">✗</div>
                            <h1>Login Failed</h1>
                            <p>No access token received.</p>
                        </div>
                    `;
                }
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def _send_json_response(self, data: dict[str, Any]) -> None:
        """Send JSON response."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        """Suppress HTTP server logging."""


class SupabaseAuthClient:
    """Client for Supabase authentication."""

    def __init__(
        self,
        supabase_url: str = SUPABASE_URL,
        supabase_key: str = SUPABASE_ANON_KEY,
    ) -> None:
        self.supabase_url = supabase_url.rstrip("/")
        self.supabase_key = supabase_key
        self.headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }

    def login_with_oauth(self, provider: str = "github") -> AuthResult:
        """
        Initiate OAuth login flow.

        Opens browser for user to authenticate, then captures callback.
        """
        # Reset callback handler state
        OAuthCallbackHandler.auth_code = None
        OAuthCallbackHandler.error = None
        OAuthCallbackHandler.received_callback.clear()

        # Start local callback server
        redirect_uri = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}/auth/callback"

        # Build OAuth URL
        oauth_url = (
            f"{self.supabase_url}/auth/v1/authorize?"
            f"provider={provider}&"
            f"redirect_to={urllib.parse.quote(redirect_uri)}"
        )

        # Start callback server in background thread
        server = socketserver.TCPServer(
            (CALLBACK_HOST, CALLBACK_PORT),
            OAuthCallbackHandler,
        )
        server_thread = threading.Thread(target=server.handle_request)
        server_thread.daemon = True
        server_thread.start()

        # Open browser
        webbrowser.open(oauth_url)

        # Wait for callback (with timeout)
        if not OAuthCallbackHandler.received_callback.wait(timeout=300):
            server.shutdown()
            return AuthResult(success=False, error="Login timed out")

        # Give time for token extraction JS to send token
        time.sleep(1)

        server.shutdown()

        if OAuthCallbackHandler.error:
            return AuthResult(success=False, error=OAuthCallbackHandler.error)

        if not OAuthCallbackHandler.auth_code:
            return AuthResult(success=False, error="No access token received")

        # Get user info and save credentials
        return self._complete_login(OAuthCallbackHandler.auth_code)

    def login_with_email(self, email: str, password: str) -> AuthResult:
        """Login with email and password."""
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"

        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"email": email, "password": password},
                timeout=30,
            )

            if response.status_code != 200:
                error_data = response.json()
                return AuthResult(
                    success=False,
                    error=error_data.get("error_description", "Login failed"),
                )

            data = response.json()
            return self._complete_login(data["access_token"], data.get("refresh_token"))

        except requests.RequestException as e:
            return AuthResult(success=False, error=str(e))

    def _complete_login(
        self,
        access_token: str,
        refresh_token: str | None = None,
    ) -> AuthResult:
        """Complete login by fetching user info and saving credentials."""
        # Get user info
        user_info = self._get_user_info(access_token)

        if not user_info:
            return AuthResult(success=False, error="Failed to get user info")

        # Get profile info (plan, etc.)
        profile = self._get_user_profile(access_token, user_info["id"])

        credentials: Credentials = {
            "access_token": access_token,
            "refresh_token": refresh_token or "",
            "expires_at": user_info.get("expires_at", 0),
            "user_id": user_info["id"],
            "email": user_info.get("email", ""),
            "full_name": user_info.get("user_metadata", {}).get("full_name"),
            "plan": profile.get("plan", "free") if profile else "free",
        }

        save_credentials(credentials)

        return AuthResult(success=True, credentials=credentials)

    def _get_user_info(self, access_token: str) -> dict[str, Any] | None:
        """Get user info from Supabase."""
        url = f"{self.supabase_url}/auth/v1/user"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass

        return None

    def _get_user_profile(
        self,
        access_token: str,
        user_id: str,
    ) -> dict[str, Any] | None:
        """Get user profile from profiles table."""
        url = f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}&select=*"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
        except requests.RequestException:
            pass

        return None

    def get_usage(self, access_token: str, user_id: str) -> dict[str, Any] | None:
        """Get user's current usage stats."""
        # Get current month
        from datetime import datetime

        current_month = datetime.now(tz=timezone.utc).strftime("%Y-%m")

        url = (
            f"{self.supabase_url}/rest/v1/usage?"
            f"user_id=eq.{user_id}&month=eq.{current_month}&select=*"
        )
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else {"scans_count": 0, "tokens_used": 0}
        except requests.RequestException:
            pass

        return None


# Import timezone at module level for use in get_usage
from datetime import timezone
