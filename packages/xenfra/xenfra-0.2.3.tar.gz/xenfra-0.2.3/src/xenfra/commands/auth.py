"""
Authentication commands for Xenfra CLI.
"""

import base64
import hashlib
import secrets
import urllib.parse
import webbrowser
from http.server import HTTPServer

import click
import httpx
import keyring
from rich.console import Console

from ..utils.auth import (
    API_BASE_URL,
    CLI_CLIENT_ID,
    CLI_LOCAL_SERVER_END_PORT,
    CLI_LOCAL_SERVER_START_PORT,
    CLI_REDIRECT_PATH,
    SERVICE_ID,
    AuthCallbackHandler,
    clear_tokens,
    get_auth_token,
)

console = Console()


@click.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
def login():
    """Login to Xenfra using OAuth2 PKCE flow."""
    global oauth_data
    oauth_data = {"code": None, "state": None, "error": None}

    # 1. Generate PKCE parameters
    code_verifier = secrets.token_urlsafe(96)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .decode()
        .rstrip("=")
    )

    # 2. Generate state for CSRF protection
    state = secrets.token_urlsafe(32)

    # 3. Start local HTTP server
    server_port = None
    httpd_instance = None
    for port in range(CLI_LOCAL_SERVER_START_PORT, CLI_LOCAL_SERVER_END_PORT + 1):
        try:
            server_address = ("127.0.0.1", port)
            httpd_instance = HTTPServer(server_address, AuthCallbackHandler)
            server_port = port
            break
        except OSError:
            continue

    if not server_port:
        console.print(
            f"[bold red]Error: No available ports in range {CLI_LOCAL_SERVER_START_PORT}-{CLI_LOCAL_SERVER_END_PORT}[/bold red]"
        )
        return

    redirect_uri = f"http://localhost:{server_port}{CLI_REDIRECT_PATH}"

    # 4. Construct Authorization URL
    auth_url = (
        f"{API_BASE_URL}/auth/authorize?"
        f"client_id={CLI_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"response_type=code&"
        f"scope={urllib.parse.quote('openid profile')}&"
        f"state={state}&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256"
    )

    console.print("[bold blue]Opening browser for login...[/bold blue]")
    console.print(
        f"[dim]If browser doesn't open, navigate to:[/dim]\n[link={auth_url}]{auth_url}[/link]"
    )
    webbrowser.open(auth_url)

    # 5. Run local server to capture redirect
    try:
        AuthCallbackHandler.server = httpd_instance  # type: ignore
        httpd_instance.handle_request()  # type: ignore
        console.print("[dim]Local OAuth server shut down.[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error running OAuth server: {e}[/bold red]")
        if httpd_instance:
            httpd_instance.server_close()
        return

    if oauth_data["error"]:
        console.print(f"[bold red]Login failed: {oauth_data['error']}[/bold red]")
        return

    if not oauth_data["code"]:
        console.print("[bold red]Login failed: No authorization code received.[/bold red]")
        return

    # 6. Verify state
    if oauth_data["state"] != state:
        console.print("[bold red]Login failed: State mismatch (possible CSRF attack)[/bold red]")
        return

    # 7. Exchange code for tokens
    console.print("[bold cyan]Exchanging authorization code for tokens...[/bold cyan]")
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{API_BASE_URL}/auth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": CLI_CLIENT_ID,
                    "code": oauth_data["code"],
                    "code_verifier": code_verifier,
                    "redirect_uri": redirect_uri,
                },
            )
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")

            if access_token and refresh_token:
                keyring.set_password(SERVICE_ID, "access_token", access_token)
                keyring.set_password(SERVICE_ID, "refresh_token", refresh_token)
                console.print("[bold green]Login successful! Tokens saved securely.[/bold green]")
            else:
                console.print("[bold red]Login failed: No tokens received.[/bold red]")
    except httpx.RequestError as exc:
        console.print(f"[bold red]Token exchange failed: {exc}[/bold red]")
    except httpx.HTTPStatusError as exc:
        console.print(f"[bold red]Token exchange failed: {exc.response.status_code}[/bold red]")


@auth.command()
def logout():
    """Logout and clear stored tokens."""
    clear_tokens()
    console.print("[bold green]Logged out successfully.[/bold green]")


@auth.command()
@click.option("--token", is_flag=True, help="Show access token")
def whoami(token):
    """Show current authenticated user."""
    access_token = get_auth_token()

    if not access_token:
        console.print("[bold red]Not logged in. Run 'xenfra login' first.[/bold red]")
        return

    try:
        from jose import jwt

        # For display purposes only, in a CLI context where the token has just
        # been retrieved from a secure source (keyring), we can disable
        # signature verification.
        #
        # SECURITY BEST PRACTICE: In a real application, especially a server,
        # you would fetch the public key from the SSO's JWKS endpoint and
        # fully verify the token's signature to ensure its integrity.
        claims = jwt.decode(
            access_token, options={"verify_signature": False}  # OK for local display
        )

        console.print("[bold green]Logged in as:[/bold green]")
        console.print(f"  User ID: {claims.get('sub')}")
        console.print(f"  Email: {claims.get('email', 'N/A')}")

        if token:
            console.print(f"\n[dim]Access Token:[/dim]\n{access_token}")
    except Exception as e:
        console.print(f"[bold red]Failed to decode token: {e}[/bold red]")
