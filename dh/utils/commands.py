"""Command execution utilities."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def check_command_exists(command: str) -> bool:
    """Check if a command exists in PATH."""
    return shutil.which(command) is not None


def run_command(
    command: str | list[str],
    cwd: Optional[Path] = None,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    """Run a shell command.

    Args:
        command: Command string or list of arguments
        cwd: Working directory for command
        check: If True, raise exception on non-zero exit
        capture_output: If True, capture stdout/stderr

    Returns:
        CompletedProcess instance
    """
    if isinstance(command, str):
        shell = True
    else:
        shell = False

    return subprocess.run(
        command,
        cwd=cwd,
        check=check,
        shell=shell,
        capture_output=capture_output,
        text=True,
    )


def get_command_output(
    command: str | list[str],
    cwd: Optional[Path] = None,
) -> str:
    """Run a command and return its output."""
    result = run_command(command, cwd=cwd, capture_output=True)
    return result.stdout.strip()


def check_tool_version(command: str, version_flag: str = "--version") -> Optional[str]:
    """Check if a tool is installed and return its version."""
    if not check_command_exists(command):
        return None

    try:
        version = get_command_output([command, version_flag])
        return version
    except subprocess.CalledProcessError:
        return "installed"
