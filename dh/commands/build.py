"""Build and Docker commands."""

import typer
from rich.console import Console

from dh.context import get_context
from dh.utils.commands import check_command_exists, run_command
from dh.utils.prompts import display_error, display_info, display_success, display_warning

app = typer.Typer(help="Build and Docker commands")
console = Console()


@app.command()
def build(
    docker: bool = typer.Option(False, "--docker", help="Build Docker image"),
):
    """Build project for production."""
    ctx = get_context()
    
    if docker:
        if not check_command_exists("docker"):
            display_error("Docker not installed")
            raise typer.Exit(1)
        
        # Build Docker image
        if ctx.is_frontend:
            console.print("🐳 Building frontend Docker image...\n")
            run_command("docker build -t hello-world-fe .", cwd=ctx.frontend_path)
            display_success("Docker image built: hello-world-fe")
        elif ctx.is_backend:
            console.print("🐳 Building backend Docker image...\n")
            run_command("docker build -t hello-world-be .", cwd=ctx.backend_path)
            display_success("Docker image built: hello-world-be")
        else:
            # Build both
            if ctx.has_frontend:
                console.print("🐳 Building frontend Docker image...\n")
                run_command("docker build -t hello-world-fe .", cwd=ctx.frontend_path)
                display_success("Docker image built: hello-world-fe")
            
            if ctx.has_backend:
                console.print("🐳 Building backend Docker image...\n")
                run_command("docker build -t hello-world-be .", cwd=ctx.backend_path)
                display_success("Docker image built: hello-world-be")
    else:
        # Regular production build
        if ctx.is_frontend:
            console.print("🏗️  Building frontend for production...\n")
            run_command("npm run build", cwd=ctx.frontend_path)
            display_success("Frontend build complete")
        elif ctx.is_backend:
            display_info("Backend doesn't require a build step")
        else:
            if ctx.has_frontend:
                console.print("🏗️  Building frontend for production...\n")
                run_command("npm run build", cwd=ctx.frontend_path)
                display_success("Frontend build complete")
            if ctx.has_backend:
                display_info("Backend doesn't require a build step")


@app.command()
def run():
    """Run Docker container."""
    if not check_command_exists("docker"):
        display_error("Docker not installed")
        raise typer.Exit(1)
    
    ctx = get_context()
    
    if ctx.is_frontend:
        console.print("🚀 Starting frontend Docker container...\n")
        run_command("docker run --rm -p 3000:3000 hello-world-fe", cwd=ctx.frontend_path)
    elif ctx.is_backend:
        console.print("🚀 Starting backend Docker container...\n")
        run_command("docker run --rm -p 8000:8080 hello-world-be", cwd=ctx.backend_path)
    else:
        display_error("Ambiguous context - run from specific project directory")
        raise typer.Exit(1)
