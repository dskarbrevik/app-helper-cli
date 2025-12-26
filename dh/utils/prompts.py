"""Interactive prompt utilities using Rich."""

from typing import Optional

from rich.console import Console
from rich.prompt import Confirm, Prompt

console = Console()


def prompt_text(
    message: str,
    default: Optional[str] = None,
    password: bool = False,
) -> str:
    """Prompt for text input with optional default."""
    return Prompt.ask(message, default=default, password=password, console=console)


def prompt_confirm(message: str, default: bool = False) -> bool:
    """Prompt for yes/no confirmation."""
    return Confirm.ask(message, default=default, console=console)


def prompt_email() -> str:
    """Prompt for email with basic validation."""
    while True:
        email = prompt_text("Enter email address")
        if "@" in email and "." in email:
            return email
        console.print("⚠️  Invalid email format", style="yellow")


def display_success(message: str) -> None:
    """Display a success message."""
    console.print(f"✅ {message}", style="green")


def display_error(message: str) -> None:
    """Display an error message."""
    console.print(f"❌ {message}", style="red")


def display_warning(message: str) -> None:
    """Display a warning message."""
    console.print(f"⚠️  {message}", style="yellow")


def display_info(message: str) -> None:
    """Display an info message."""
    console.print(f"ℹ️  {message}", style="blue")


def display_step(step: int, message: str) -> None:
    """Display a numbered step."""
    console.print(f"\n[bold]Step {step}:[/bold] {message}")
