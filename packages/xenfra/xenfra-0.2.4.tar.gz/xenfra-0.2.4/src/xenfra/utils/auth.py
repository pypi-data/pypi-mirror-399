"""
Authentication utilities for Xenfra CLI.
Handles OAuth2 PKCE flow and token management.
"""
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import httpx
import keyring
from rich.console import Console

from .security import validate_and_get_api_url

console = Console()

# Get validated API URL (includes all security checks)
API_BASE_URL = validate_and_get_api_url()
SERVICE_ID = "xenfra"

# CLI OAuth2 Configuration
CLI_CLIENT_ID = "xenfra-cli"
CLI_REDIRECT_PATH = "/auth/callback"
CLI_LOCAL_SERVER_START_PORT = 8001
CLI_LOCAL_SERVER_END_PORT = 8005

# Global storage for OAuth callback data
oauth_data = {"code": None, "state": None, "error": None}


class AuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth redirect callback."""

    def do_GET(self):
        global oauth_data
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        query_params = parse_qs(urlparse(self.path).query)

        if "code" in query_params:
            oauth_data["code"] = query_params["code"][0]
            oauth_data["state"] = query_params["state"][0] if "state" in query_params else None
            self.wfile.write(
                b"<html><body><h1>Authentication successful!</h1><p>You can close this window.</p></body></html>"
            )
        elif "error" in query_params:
            oauth_data["error"] = query_params["error"][0]
            self.wfile.write(
                f"<html><body><h1>Authentication failed!</h1><p>Error: {oauth_data['error']}</p></body></html>".encode()
            )
        else:
            self.wfile.write(
                b"<html><body><h1>Authentication callback received.</h1><p>Waiting for code...</p></body></html>"
            )

        # Shut down the server after processing
        self.server.shutdown()  # type: ignore


def run_local_oauth_server(port: int, redirect_path: str):
    """Start a local HTTP server to capture the OAuth redirect."""
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, AuthCallbackHandler)
    httpd.timeout = 30  # seconds
    console.print(
        f"[dim]Listening for OAuth redirect on http://localhost:{port}{redirect_path}...[/dim]"
    )

    # Store the server instance in the handler for shutdown
    AuthCallbackHandler.server = httpd  # type: ignore

    # Handle a single request (blocking call)
    httpd.handle_request()
    console.print("[dim]Local OAuth server shut down.[/dim]")


def get_auth_token() -> str | None:
    """
    Retrieve a valid access token, refreshing it if necessary.

    Returns:
        Valid access token or None if not authenticated
    """
    access_token = keyring.get_password(SERVICE_ID, "access_token")
    refresh_token = keyring.get_password(SERVICE_ID, "refresh_token")

    if not access_token:
        return None

    # Check if access token is expired
    try:
        from jose import JWTError, jwt

        # Decode without verifying signature to check expiration
        claims = jwt.decode(access_token, options={"verify_signature": False, "verify_exp": True})
    except JWTError:
        claims = None
    except Exception as e:
        console.print(f"[dim]Error decoding access token: {e}[/dim]")
        claims = None

    # Refresh token if expired
    if not claims and refresh_token:
        console.print("[dim]Access token expired. Attempting to refresh...[/dim]")
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{API_BASE_URL}/auth/refresh",
                    data={"refresh_token": refresh_token, "client_id": CLI_CLIENT_ID},
                )
                response.raise_for_status()
                token_data = response.json()
                new_access_token = token_data.get("access_token")
                new_refresh_token = token_data.get("refresh_token")

                if new_access_token:
                    keyring.set_password(SERVICE_ID, "access_token", new_access_token)
                    if new_refresh_token:
                        keyring.set_password(SERVICE_ID, "refresh_token", new_refresh_token)
                    console.print("[bold green]Token refreshed successfully.[/bold green]")
                    return new_access_token
                else:
                    console.print("[bold red]Failed to get new access token.[/bold red]")
                    return None
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 400:
                console.print("[bold red]Refresh token expired. Please log in again.[/bold red]")
            else:
                console.print(f"[bold red]Token refresh failed: {exc.response.status_code}[/bold red]")
            keyring.delete_password(SERVICE_ID, "access_token")
            keyring.delete_password(SERVICE_ID, "refresh_token")
            return None
        except httpx.RequestError as exc:
            console.print(f"[bold red]Token refresh failed: {exc}[/bold red]")
            return None

    return access_token


def clear_tokens():
    """Clear stored access and refresh tokens."""
    try:
        keyring.delete_password(SERVICE_ID, "access_token")
        keyring.delete_password(SERVICE_ID, "refresh_token")
    except keyring.errors.PasswordDeleteError:
        pass  # Tokens already cleared
