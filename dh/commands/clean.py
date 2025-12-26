"""Cleanup commands."""

import typer
from rich.console import Console

from dh.context import get_context
from dh.utils.commands import check_command_exists, run_command
from dh.utils.prompts import display_success

app = typer.Typer(help="Cleanup commands")
console = Console()


@app.command()
def clean():
    """Remove build artifacts and caches."""
    console.print("🧹 Cleaning build artifacts...\n")

    ctx = get_context()

    if ctx.is_frontend or (not ctx.is_backend and ctx.has_frontend):
        console.print("Cleaning frontend...")

        # Remove node_modules
        if (ctx.frontend_path / "node_modules").exists():
            run_command("rm -rf node_modules", cwd=ctx.frontend_path)
            display_success("Removed node_modules")

        # Remove .next
        if (ctx.frontend_path / ".next").exists():
            run_command("rm -rf .next", cwd=ctx.frontend_path)
            display_success("Removed .next")

        # Remove out
        if (ctx.frontend_path / "out").exists():
            run_command("rm -rf out", cwd=ctx.frontend_path)
            display_success("Removed out")

        # Remove .turbo
        if (ctx.frontend_path / ".turbo").exists():
            run_command("rm -rf .turbo", cwd=ctx.frontend_path)
            display_success("Removed .turbo")

        console.print()

    if ctx.is_backend or (not ctx.is_frontend and ctx.has_backend):
        console.print("Cleaning backend...")

        # Remove Python cache
        run_command(
            'find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true',
            cwd=ctx.backend_path,
        )
        run_command(
            'find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true',
            cwd=ctx.backend_path,
        )
        run_command(
            'find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true',
            cwd=ctx.backend_path,
        )
        run_command(
            'find . -type f -name "*.pyc" -delete 2>/dev/null || true',
            cwd=ctx.backend_path,
        )

        display_success("Removed Python cache files")
        console.print()

    # Clean Docker images (optional)
    if check_command_exists("docker"):
        console.print("Cleaning Docker images...")

        try:
            # Check if images exist
            run_command(
                "docker images -q hello-world-fe hello-world-be | xargs -r docker rmi 2>/dev/null || true",
                cwd=ctx.workspace_root,
            )
            display_success("Docker images cleaned")
        except Exception:
            pass

    console.print("\n✅ [bold green]Clean complete![/bold green]")
