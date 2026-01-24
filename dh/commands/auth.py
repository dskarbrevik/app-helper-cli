"""Authentication commands for Supabase."""

import os

import requests
import typer
from rich.console import Console

from dh.context import get_context
from dh.utils.env import read_env_file
from dh.utils.prompts import (
    display_error,
    display_info,
    display_success,
    prompt_text,
)

app = typer.Typer(help="Authentication commands")
console = Console()


def _get_test_credentials(ctx) -> tuple[str | None, str | None]:
    """Get test credentials from .env files or environment."""
    email = os.environ.get("SUPABASE_TEST_EMAIL")
    password = os.environ.get("SUPABASE_TEST_PASSWORD")

    # Check .env files if not in environment
    env_paths = []
    if ctx.frontend_path:
        env_paths.append(ctx.frontend_path / ".env")
    if ctx.backend_path:
        env_paths.append(ctx.backend_path / ".env")
    if ctx.workspace_root:
        env_paths.append(ctx.workspace_root / ".env")

    for env_path in env_paths:
        if env_path.exists():
            env_vars = read_env_file(env_path)
            if not email and "SUPABASE_TEST_EMAIL" in env_vars:
                email = env_vars["SUPABASE_TEST_EMAIL"]
            if not password and "SUPABASE_TEST_PASSWORD" in env_vars:
                password = env_vars["SUPABASE_TEST_PASSWORD"]
            if email and password:
                break

    return email, password


@app.command()
def token(
    email: str = typer.Option(
        None,
        "--email",
        "-e",
        help="Email for authentication (or set SUPABASE_TEST_EMAIL)",
    ),
    password: str = typer.Option(
        None,
        "--password",
        "-p",
        help="Password for authentication (or set SUPABASE_TEST_PASSWORD)",
    ),
    export: bool = typer.Option(
        False,
        "--export",
        help="Print export command for shell (useful for eval)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-V",
        help="Show verbose information about configuration",
    ),
):
    """Get a JWT access token from Supabase and set it in environment.

    This command authenticates with Supabase using email/password and retrieves
    a JWT access token. The token is printed and can be exported to your shell.

    Environment variables used:
        SUPABASE_TEST_EMAIL: Default email for authentication
        SUPABASE_TEST_PASSWORD: Default password for authentication

    Example usage:
        dh auth token
        dh auth token --email test@example.com --password mypassword
        eval $(dh auth token --export)  # Export to current shell
    """
    ctx = get_context()

    # Check for Supabase URL and key
    supabase_url = ctx.config.db.url
    supabase_key = ctx.config.db.public_key

    if verbose:
        console.print("[dim]Configuration:[/dim]")
        console.print(f"[dim]  Workspace root: {ctx.workspace_root}[/dim]")
        console.print(f"[dim]  Frontend path: {ctx.frontend_path}[/dim]")
        console.print(f"[dim]  Backend path: {ctx.backend_path}[/dim]")
        console.print(f"[dim]  Supabase URL: {supabase_url}[/dim]")
        console.print(f"[dim]  Supabase Key: {supabase_key[:20] + '...' if supabase_key else 'None'}[/dim]")

    if not supabase_url:
        display_error("NEXT_PUBLIC_SUPABASE_URL not configured")
        display_info("Run 'dh setup' to configure Supabase credentials")
        raise typer.Exit(1)

    if not supabase_key:
        display_error("NEXT_PUBLIC_SUPABASE_KEY not configured")
        display_info("Run 'dh setup' to configure Supabase credentials")
        raise typer.Exit(1)

    # Get email/password from: CLI arg > env var / .env file > prompt
    if not email or not password:
        env_email, env_password = _get_test_credentials(ctx)
        if not email:
            email = env_email
        if not password:
            password = env_password

    if verbose:
        console.print(f"[dim]  Email: {email}[/dim]")
        console.print(
            f"[dim]  Password: {'*' * len(password) if password else 'None'}[/dim]"
        )

    if not email:
        email = prompt_text("Email", default="")
        if not email:
            display_error("Email is required")
            raise typer.Exit(1)

    if not password:
        password = prompt_text("Password", password=True, default="")
        if not password:
            display_error("Password is required")
            raise typer.Exit(1)

    # Authenticate with Supabase
    console.print("\n🔐 Authenticating with Supabase...\n")

    try:
        response = requests.post(
            f"{supabase_url}/auth/v1/token?grant_type=password",
            headers={
                "apikey": supabase_key,
                "Content-Type": "application/json",
            },
            json={
                "email": email,
                "password": password,
            },
            timeout=30,
        )

        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            expires_in = data.get("expires_in", 3600)

            if access_token:
                # Set in current process environment
                os.environ["SUPABASE_ACCESS_TOKEN_JWT"] = access_token

                if export:
                    # Print export command for shell evaluation
                    console.print(f"export SUPABASE_ACCESS_TOKEN_JWT='{access_token}'")
                else:
                    display_success("Authentication successful!")
                    console.print("\n[bold]Access Token:[/bold]")
                    console.print(f"[dim]{access_token}[/dim]\n")

                    console.print(f"[dim]Expires in: {expires_in} seconds[/dim]")
                    console.print(
                        "[dim]Token set in environment as: SUPABASE_ACCESS_TOKEN_JWT[/dim]\n"
                    )

                    display_info(
                        "To export to your shell, run: eval $(dh auth token --export)"
                    )

                    if refresh_token:
                        console.print("\n[bold]Refresh Token:[/bold]")
                        console.print(f"[dim]{refresh_token}[/dim]")
            else:
                display_error("No access token in response")
                raise typer.Exit(1)

        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get(
                "error_description", error_data.get("error", "Bad request")
            )
            display_error(f"Authentication failed: {error_msg}")
            raise typer.Exit(1)

        elif response.status_code == 401:
            display_error("Invalid email or password")
            raise typer.Exit(1)

        else:
            display_error(f"Authentication failed with status {response.status_code}")
            try:
                error_data = response.json()
                display_info(f"Error: {error_data}")
            except Exception:
                display_info(f"Response: {response.text}")
            raise typer.Exit(1)

    except requests.exceptions.Timeout:
        display_error("Request timed out")
        raise typer.Exit(1)
    except requests.exceptions.ConnectionError:
        display_error("Could not connect to Supabase")
        display_info(f"URL: {supabase_url}")
        raise typer.Exit(1)
    except requests.exceptions.RequestException as e:
        display_error(f"Request failed: {e}")
        raise typer.Exit(1)
