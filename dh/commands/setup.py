"""Setup command for initial project configuration."""

import re

import typer
from rich.console import Console

from dh.context import get_context
from dh.utils.commands import check_command_exists, check_tool_version, run_command
from dh.utils.config import save_local_config, save_project_config
from dh.utils.prompts import (
    display_error,
    display_info,
    display_step,
    display_success,
    display_warning,
    prompt_confirm,
    prompt_text,
)

app = typer.Typer(help="Setup and installation commands")
console = Console()


@app.command()
def setup():
    """One-time setup of development environment."""
    console.print("\n🚀 [bold]Setting up development environment...[/bold]\n")

    ctx = get_context()

    # Step 1: Detect project type
    display_step(1, "Detecting project structure...")

    if ctx.has_frontend:
        display_success(f"Frontend detected: {ctx.frontend_path}")
    if ctx.has_backend:
        display_success(f"Backend detected: {ctx.backend_path}")

    if not ctx.has_frontend and not ctx.has_backend:
        display_error("No projects detected in workspace")
        display_info("Expected FE: package.json + next.config.ts")
        display_info("Expected BE: pyproject.toml + main.py")
        raise typer.Exit(1)

    # Step 2: Check required tools
    display_step(2, "Checking required tools...")

    tools_ok = True
    if ctx.has_frontend:
        if not check_command_exists("node"):
            display_error("Node.js not installed (required for frontend)")
            tools_ok = False
        else:
            node_version = check_tool_version("node", "--version")
            display_success(f"Node.js: {node_version}")

        if not check_command_exists("npm"):
            display_error("npm not installed (required for frontend)")
            tools_ok = False
        else:
            npm_version = check_tool_version("npm", "--version")
            display_success(f"npm: {npm_version}")

    if ctx.has_backend:
        if not check_command_exists("uv"):
            display_error("uv not installed (required for backend)")
            display_info("Install: curl -LsSf https://astral.sh/uv/install.sh | sh")
            tools_ok = False
        else:
            uv_version = check_tool_version("uv", "--version")
            display_success(f"uv: {uv_version}")

    # Check Docker (optional)
    if check_command_exists("docker"):
        docker_version = check_tool_version("docker", "--version")
        display_success(f"Docker: {docker_version}")
    else:
        display_warning("Docker not found (optional, needed for containerization)")

    if not tools_ok:
        display_error("Please install missing tools and run setup again")
        raise typer.Exit(1)

    # Step 3: Configure database credentials
    display_step(3, "Configuring database credentials...")

    configure_db = prompt_confirm(
        "Configure database (Supabase) credentials?", default=True
    )

    if configure_db:
        db_url = prompt_text(
            "Database URL (e.g., https://xxx.supabase.co)",
            default=ctx.config.db.url,
        )

        # Extract project ref
        match = re.search(r"https://([^.]+)\.supabase\.co", db_url)
        project_ref = match.group(1) if match else None

        service_role_key = prompt_text(
            "Service role key (from Supabase dashboard)",
            default=ctx.config.db.service_role_key,
            password=True,
        )

        anon_key = prompt_text(
            "Anonymous key (from Supabase dashboard)",
            default=ctx.config.db.anon_key,
            password=False,
        )

        db_password = prompt_text(
            "Database password (for migrations)",
            default=ctx.config.db.password,
            password=True,
        )

        # Update config
        ctx.config.db.url = db_url
        ctx.config.db.service_role_key = service_role_key
        ctx.config.db.anon_key = anon_key
        ctx.config.db.password = db_password
        ctx.config.db.project_ref = project_ref

        # Save to .dh.local.toml
        save_local_config(ctx.workspace_root, ctx.config)
        display_success("Database credentials saved to .dh.local.toml")

    # Step 4: Install dependencies
    display_step(4, "Installing dependencies...")

    if ctx.has_frontend:
        console.print("\n📦 Installing frontend dependencies...")
        try:
            run_command("npm install", cwd=ctx.frontend_path)
            display_success("Frontend dependencies installed")
        except Exception as e:
            display_error(f"Failed to install frontend dependencies: {e}")

    if ctx.has_backend:
        console.print("\n📦 Installing backend dependencies...")
        try:
            run_command("uv sync --dev", cwd=ctx.backend_path)
            display_success("Backend dependencies installed")
        except Exception as e:
            display_error(f"Failed to install backend dependencies: {e}")

    # Step 5: Update .gitignore
    display_step(5, "Updating .gitignore...")

    gitignore_path = ctx.workspace_root / ".gitignore"
    gitignore_entries = [".dh.local.toml"]

    if gitignore_path.exists():
        with open(gitignore_path) as f:
            existing = f.read()

        to_add = [entry for entry in gitignore_entries if entry not in existing]

        if to_add:
            with open(gitignore_path, "a") as f:
                f.write("\n# DevHand CLI\n")
                for entry in to_add:
                    f.write(f"{entry}\n")
            display_success("Updated .gitignore")
        else:
            display_info(".gitignore already configured")
    else:
        with open(gitignore_path, "w") as f:
            f.write("# DevHand CLI\n")
            for entry in gitignore_entries:
                f.write(f"{entry}\n")
        display_success("Created .gitignore")

    # Save project config
    save_project_config(ctx.workspace_root, ctx.config)

    # Final message
    console.print("\n✨ [bold green]Setup complete![/bold green]\n")
    console.print("Next steps:")
    console.print("  1. Run [bold]dh validate[/bold] to verify everything")
    console.print("  2. Run [bold]dh db setup[/bold] to initialize database tables")
    console.print("  3. Run [bold]dh dev[/bold] to start development server")


@app.command()
def install():
    """Install project dependencies."""
    ctx = get_context()

    if ctx.has_frontend:
        console.print("📦 Installing frontend dependencies...")
        try:
            run_command("npm install", cwd=ctx.frontend_path)
            display_success("Frontend dependencies installed")
        except Exception as e:
            display_error(f"Failed: {e}")
            raise typer.Exit(1)

    if ctx.has_backend:
        console.print("📦 Installing backend dependencies...")
        try:
            run_command("uv sync --dev", cwd=ctx.backend_path)
            display_success("Backend dependencies installed")
        except Exception as e:
            display_error(f"Failed: {e}")
            raise typer.Exit(1)
