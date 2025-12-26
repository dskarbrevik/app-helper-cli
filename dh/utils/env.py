"""Environment variable and .env file utilities."""

from pathlib import Path
from typing import Optional


def read_env_file(env_path: Path) -> dict[str, str]:
    """Read a .env file and return key-value pairs."""
    env_vars = {}

    if not env_path.exists():
        return env_vars

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def write_env_file(
    env_path: Path, env_vars: dict[str, str], append: bool = False
) -> None:
    """Write environment variables to a .env file.

    Args:
        env_path: Path to .env file
        env_vars: Dictionary of key-value pairs to write
        append: If True, append to existing file; if False, overwrite
    """
    mode = "a" if append else "w"

    with open(env_path, mode) as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")


def update_env_var(env_path: Path, key: str, value: str) -> None:
    """Update a single environment variable in .env file.

    If the key exists, updates its value. Otherwise, appends it.
    """
    env_vars = read_env_file(env_path)
    env_vars[key] = value
    write_env_file(env_path, env_vars, append=False)


def get_env_var(env_path: Path, key: str) -> Optional[str]:
    """Get a single environment variable from .env file."""
    env_vars = read_env_file(env_path)
    return env_vars.get(key)
