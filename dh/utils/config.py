"""Configuration file handling for dh.toml and .dh.local.toml."""

from pathlib import Path
from typing import Any, Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

import toml
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: Optional[str] = None
    service_role_key: Optional[str] = None
    anon_key: Optional[str] = None
    password: Optional[str] = None
    project_ref: Optional[str] = None


class ProjectConfig(BaseModel):
    """Project paths configuration."""

    frontend_path: Optional[str] = None
    backend_path: Optional[str] = None


class PreferencesConfig(BaseModel):
    """User preferences."""

    disable_detection_warnings: bool = False
    auto_install_dependencies: bool = True


class Config(BaseModel):
    """Main configuration."""

    project: ProjectConfig = ProjectConfig()
    db: DatabaseConfig = DatabaseConfig()
    preferences: PreferencesConfig = PreferencesConfig()


def load_config(workspace_root: Path) -> Config:
    """Load configuration from .dh.local.toml.

    All configuration (project paths, preferences, database credentials)
    is stored in a single gitignored .dh.local.toml file.
    """
    config_data: dict[str, Any] = {}

    # Load .dh.local.toml (single config file)
    local_toml = workspace_root / ".dh.local.toml"
    if local_toml.exists():
        with open(local_toml, "rb") as f:
            config_data = tomllib.load(f)

    return Config(**config_data)


def save_local_config(workspace_root: Path, config: Config) -> None:
    """Save configuration to .dh.local.toml."""
    local_toml = workspace_root / ".dh.local.toml"

    # Only save database secrets to local config
    config_dict = {
        "db": config.db.model_dump(exclude_none=True),
    }

    with open(local_toml, "w") as f:
        toml.dump(config_dict, f)


def save_project_config(workspace_root: Path, config: Config) -> None:
    """Save project configuration to dh.toml (version controlled)."""
    dh_toml = workspace_root / "dh.toml"

    # Only save non-secret data to version-controlled config
    config_dict = {
        "project": config.project.model_dump(exclude_none=True),
        "preferences": config.preferences.model_dump(),
    }

    with open(dh_toml, "w") as f:
        toml.dump(config_dict, f)
