"""Validation commands for checking environment health."""

import typer
from rich.console import Console
from rich.table import Table

from dh.context import get_context
from dh.utils.commands import check_command_exists, check_tool_version
from dh.utils.db import create_db_client
from dh.utils.prompts import display_error, display_success, display_warning

app = typer.Typer(help="Environment validation commands")
console = Console()


@app.command()
def validate():
    """Check if environment is properly configured."""
    console.print("\n🔍 [bold]Validating development environment...[/bold]\n")
    
    ctx = get_context()
    issues = []
    
    # Check frontend
    if ctx.has_frontend:
        console.print("[bold]Frontend:[/bold]")
        
        # Check Node.js
        if check_command_exists("node"):
            version = check_tool_version("node", "--version")
            display_success(f"Node.js: {version}")
        else:
            display_error("Node.js not installed")
            issues.append("Node.js missing")
        
        # Check npm
        if check_command_exists("npm"):
            version = check_tool_version("npm", "--version")
            display_success(f"npm: {version}")
        else:
            display_error("npm not installed")
            issues.append("npm missing")
        
        # Check node_modules
        if (ctx.frontend_path / "node_modules").exists():
            display_success("node_modules exists")
        else:
            display_warning("node_modules not found - run 'dh install'")
            issues.append("Frontend dependencies not installed")
        
        # Check package.json
        if (ctx.frontend_path / "package.json").exists():
            display_success("package.json exists")
        else:
            display_error("package.json not found")
            issues.append("package.json missing")
        
        console.print()
    
    # Check backend
    if ctx.has_backend:
        console.print("[bold]Backend:[/bold]")
        
        # Check Python
        if check_command_exists("python3"):
            version = check_tool_version("python3", "--version")
            display_success(f"Python: {version}")
        else:
            display_error("Python 3 not installed")
            issues.append("Python 3 missing")
        
        # Check uv
        if check_command_exists("uv"):
            version = check_tool_version("uv", "--version")
            display_success(f"uv: {version}")
        else:
            display_error("uv not installed")
            issues.append("uv missing")
        
        # Check .venv
        if (ctx.backend_path / ".venv").exists():
            display_success(".venv exists")
        else:
            display_warning(".venv not found - run 'dh install'")
            issues.append("Backend virtual environment not created")
        
        # Check pyproject.toml
        if (ctx.backend_path / "pyproject.toml").exists():
            display_success("pyproject.toml exists")
        else:
            display_error("pyproject.toml not found")
            issues.append("pyproject.toml missing")
        
        console.print()
    
    # Check Docker (optional)
    console.print("[bold]Optional Tools:[/bold]")
    if check_command_exists("docker"):
        version = check_tool_version("docker", "--version")
        display_success(f"Docker: {version}")
    else:
        display_warning("Docker not installed (optional)")
    
    console.print()
    
    # Check database configuration
    console.print("[bold]Database Configuration:[/bold]")
    if ctx.config.db.url:
        display_success(f"Database URL configured: {ctx.config.db.url}")
        
        # Test connection
        if ctx.config.db.service_role_key:
            try:
                db_client = create_db_client(
                    ctx.config.db.url,
                    ctx.config.db.service_role_key,
                    ctx.config.db.password,
                    ctx.config.db.project_ref,
                )
                if db_client.test_connection():
                    display_success("Database connection successful")
                else:
                    display_error("Database connection failed")
                    issues.append("Cannot connect to database")
            except Exception as e:
                display_error(f"Database connection error: {e}")
                issues.append("Database connection error")
        else:
            display_warning("Service role key not configured")
            issues.append("Database credentials incomplete")
    else:
        display_warning("Database not configured - run 'dh setup'")
        issues.append("Database not configured")
    
    # Summary
    console.print()
    if issues:
        console.print(f"[bold yellow]⚠️  Found {len(issues)} issue(s):[/bold yellow]")
        for issue in issues:
            console.print(f"  - {issue}")
        console.print("\nRun [bold]dh setup[/bold] to fix configuration issues")
        raise typer.Exit(1)
    else:
        console.print("✨ [bold green]All checks passed![/bold green]")
