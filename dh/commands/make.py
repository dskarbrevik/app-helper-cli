"""Make commands for generating project artifacts."""

from pathlib import Path

import typer
from rich.console import Console

from dh.context import get_context
from dh.utils.commands import check_command_exists, run_command
from dh.utils.env import read_env_file
from dh.utils.prompts import display_error, display_info, display_success

app = typer.Typer(help="Generate project artifacts")
console = Console()

# Expected environment variables for frontend
FRONTEND_ENV_VARS = {
    # For Vercel deployment (NEXT_PUBLIC_ vars are exposed to browser)
    "NEXT_PUBLIC_SUPABASE_URL": {
        "description": "Supabase project URL",
        "section": "vercel",
    },
    "NEXT_PUBLIC_SUPABASE_KEY": {
        "description": "Supabase public/anon key (safe for client-side)",
        "section": "vercel",
    },
    "NEXT_PUBLIC_API_URL": {
        "description": "Backend API URL",
        "section": "vercel",
    },
    # After Vercel deployment
    "VERCEL_URL": {
        "description": "Vercel deployment URL (add after deploying)",
        "section": "post_vercel",
    },
    # For DevHand CLI only (not needed in Vercel)
    "SUPABASE_SECRET_KEY": {
        "description": "Supabase service_role key (for dh db commands)",
        "section": "cli",
    },
    "SUPABASE_DB_PASSWORD": {
        "description": "Database password (for migrations)",
        "section": "cli",
    },
    "SUPABASE_ACCESS_TOKEN": {
        "description": "Supabase Management API token (for admin operations)",
        "section": "cli",
    },
    # For testing with dh auth token
    "SUPABASE_TEST_EMAIL": {
        "description": "Test user email (for dh auth token)",
        "section": "testing",
    },
    "SUPABASE_TEST_PASSWORD": {
        "description": "Test user password (for dh auth token)",
        "section": "testing",
    },
}

# Expected environment variables for backend
BACKEND_ENV_VARS = {
    "SUPABASE_URL": {
        "description": "Supabase project URL",
        "section": "railway",
    },
    "SUPABASE_KEY": {
        "description": "Supabase service_role key (for backend operations)",
        "section": "railway",
    },
}


@app.command()
def env(
    target: str = typer.Option(
        None,
        "--target",
        "-t",
        help="Target project: 'frontend', 'backend', or 'all' (default: auto-detect)",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing values with placeholders",
    ),
):
    """Generate .env file with all expected environment variables.

    Reads existing .env file and only adds missing keys.
    Existing values are preserved unless --force is used.

    Example usage:
        dh make env              # Auto-detect and create .env
        dh make env -t frontend  # Create frontend .env
        dh make env -t backend   # Create backend .env
        dh make env -t all       # Create both
    """
    ctx = get_context()

    targets = []
    if target == "all":
        if ctx.has_frontend:
            targets.append(("frontend", ctx.frontend_path, FRONTEND_ENV_VARS))
        if ctx.has_backend:
            targets.append(("backend", ctx.backend_path, BACKEND_ENV_VARS))
    elif target == "frontend":
        if not ctx.has_frontend:
            display_error("No frontend project found")
            raise typer.Exit(1)
        targets.append(("frontend", ctx.frontend_path, FRONTEND_ENV_VARS))
    elif target == "backend":
        if not ctx.has_backend:
            display_error("No backend project found")
            raise typer.Exit(1)
        targets.append(("backend", ctx.backend_path, BACKEND_ENV_VARS))
    else:
        # Auto-detect based on current directory or available projects
        if ctx.is_frontend:
            targets.append(("frontend", ctx.frontend_path, FRONTEND_ENV_VARS))
        elif ctx.is_backend:
            targets.append(("backend", ctx.backend_path, BACKEND_ENV_VARS))
        elif ctx.has_frontend and not ctx.has_backend:
            targets.append(("frontend", ctx.frontend_path, FRONTEND_ENV_VARS))
        elif ctx.has_backend and not ctx.has_frontend:
            targets.append(("backend", ctx.backend_path, BACKEND_ENV_VARS))
        elif ctx.has_frontend and ctx.has_backend:
            display_info("Both frontend and backend detected")
            display_info("Use --target to specify: 'frontend', 'backend', or 'all'")
            raise typer.Exit(1)
        else:
            display_error("No frontend or backend project found")
            raise typer.Exit(1)

    for name, path, env_vars in targets:
        _generate_env_file(name, path, env_vars, force)


def _generate_env_file(name: str, path: Path, expected_vars: dict, force: bool) -> None:
    """Generate or update .env file for a project."""
    env_path = path / ".env"

    console.print(f"\n📝 Generating {name} .env file...\n")

    # Read existing .env
    existing_vars = {}
    existing_content = ""
    if env_path.exists():
        existing_content = env_path.read_text()
        existing_vars = read_env_file(env_path)
        display_info(f"Found existing .env with {len(existing_vars)} variables")

    # Determine which vars are missing
    missing_vars = []
    for key in expected_vars:
        if key not in existing_vars:
            missing_vars.append(key)

    if not missing_vars and not force:
        display_success(f"All expected variables already present in {name} .env")
        return

    if force:
        # Force mode: rewrite entire file with template
        _write_full_env_file(env_path, name, expected_vars, existing_vars, force=True)
        console.print(
            f"[yellow]Overwrote .env with {len(expected_vars)} variables[/yellow]"
        )
    else:
        # Append mode: keep existing content and add missing vars
        _append_missing_vars(
            env_path, name, expected_vars, missing_vars, existing_content
        )
        console.print(f"[yellow]Added {len(missing_vars)} missing variables:[/yellow]")
        for key in missing_vars:
            console.print(f"  • {key}")

    display_success(f"Updated {env_path}")


def _write_full_env_file(
    env_path: Path,
    name: str,
    expected_vars: dict,
    existing_vars: dict,
    force: bool,
) -> None:
    """Write a complete .env file with all expected variables."""
    sections = {
        "vercel": (
            "For Vercel Deployment",
            "Copy these to your Vercel project settings",
        ),
        "post_vercel": ("After Vercel Deployment", "Add your deployment URL"),
        "cli": (
            "For DevHand CLI Only",
            "Used by 'dh db' commands - NOT needed in Vercel",
        ),
        "testing": (
            "For Testing",
            "Used by 'dh auth token' for authentication testing",
        ),
        "railway": (
            "For Railway Deployment",
            "Copy these to your Railway project settings",
        ),
    }

    # Group vars by section
    vars_by_section: dict[str, list[str]] = {}
    for key, info in expected_vars.items():
        section = info["section"]
        if section not in vars_by_section:
            vars_by_section[section] = []
        vars_by_section[section].append(key)

    with open(env_path, "w") as f:
        f.write(f"# {name.title()} Environment Variables\n")
        f.write("# Generated by 'dh make env'\n\n")

        for section_key, section_keys in vars_by_section.items():
            if section_key in sections:
                title, subtitle = sections[section_key]
                f.write(f"# === {title} ===\n")
                f.write(f"# {subtitle}\n\n")

            for key in section_keys:
                info = expected_vars[key]
                f.write(f"# {info['description']}\n")

                if key in existing_vars and not force:
                    f.write(f"{key}={existing_vars[key]}\n\n")
                else:
                    f.write(f"{key}=\n\n")


def _append_missing_vars(
    env_path: Path,
    name: str,
    expected_vars: dict,
    missing_vars: list[str],
    existing_content: str,
) -> None:
    """Append missing variables to an existing .env file."""
    sections = {
        "vercel": "For Vercel Deployment",
        "post_vercel": "After Vercel Deployment",
        "cli": "For DevHand CLI Only",
        "testing": "For Testing",
        "railway": "For Railway Deployment",
    }

    # Group missing vars by section
    missing_by_section: dict[str, list[str]] = {}
    for key in missing_vars:
        section = expected_vars[key]["section"]
        if section not in missing_by_section:
            missing_by_section[section] = []
        missing_by_section[section].append(key)

    with open(env_path, "w") as f:
        # Write existing content first
        content = existing_content.rstrip()
        f.write(content)

        # Add separator if file has content
        if content:
            f.write("\n\n")

        # Add missing variables header
        f.write("# === Added by 'dh make env' ===\n\n")

        for section_key, section_keys in missing_by_section.items():
            if section_key in sections:
                f.write(f"# {sections[section_key]}\n")

            for key in section_keys:
                info = expected_vars[key]
                f.write(f"# {info['description']}\n")
                f.write(f"{key}=\n\n")


@app.command()
def requirements():
    """Generate requirements.txt from pyproject.toml using uv."""
    if not check_command_exists("uv"):
        display_error("uv not installed. Install it with: pip install uv")
        raise typer.Exit(1)

    ctx = get_context()

    if not ctx.is_backend and not ctx.has_backend:
        display_error("No backend project found")
        raise typer.Exit(1)

    backend_path = ctx.backend_path if ctx.has_backend else ctx.project_root

    console.print("📦 Generating requirements.txt...\n")
    run_command(
        "uv export --no-dev --no-hashes --output-file requirements.txt",
        cwd=backend_path,
    )
    display_success("requirements.txt generated")
