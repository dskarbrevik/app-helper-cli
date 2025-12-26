"""Context detection and management for devhand CLI."""

from pathlib import Path
from typing import Optional

import typer

from dh.utils.config import load_config
from dh.utils.detection import (
    ProjectType,
    detect_project_type,
    find_project_dirs,
    find_workspace_root,
)
from rich.console import Console

console = Console()


class ProjectContext:
    """Context information for the current project and workspace."""

    def __init__(self, start_path: Optional[Path] = None):
        """Initialize project context.

        Args:
            start_path: Starting path for detection (defaults to cwd)
        """
        self.start_path = Path(start_path or Path.cwd())
        self.workspace_root = find_workspace_root(self.start_path)
        self.config = load_config(self.workspace_root)

        # Detect current context
        self.current_type = detect_project_type(self.start_path)

        # Find all projects in workspace
        self.projects = find_project_dirs(self.workspace_root)

        # Override with config if provided
        if self.config.project.frontend_path:
            fe_path = self.workspace_root / self.config.project.frontend_path
            if fe_path.exists():
                self.projects["frontend"] = fe_path

        if self.config.project.backend_path:
            be_path = self.workspace_root / self.config.project.backend_path
            if be_path.exists():
                self.projects["backend"] = be_path

    @property
    def frontend_path(self) -> Optional[Path]:
        """Get frontend project path."""
        return self.projects.get("frontend")

    @property
    def backend_path(self) -> Optional[Path]:
        """Get backend project path."""
        return self.projects.get("backend")

    @property
    def is_frontend(self) -> bool:
        """Check if current directory is frontend project."""
        return self.current_type == "frontend"

    @property
    def is_backend(self) -> bool:
        """Check if current directory is backend project."""
        return self.current_type == "backend"

    @property
    def has_frontend(self) -> bool:
        """Check if workspace has a frontend project."""
        return self.frontend_path is not None

    @property
    def has_backend(self) -> bool:
        """Check if workspace has a backend project."""
        return self.backend_path is not None

    def get_target_path(self, target: Optional[ProjectType] = None) -> Optional[Path]:
        """Get the target project path.

        Args:
            target: Explicit target type, or None for auto-detect

        Returns:
            Path to target project, or None if not found
        """
        if target == "frontend":
            return self.frontend_path
        elif target == "backend":
            return self.backend_path
        elif target is None:
            # Auto-detect: use current type if available
            if self.is_frontend:
                return self.frontend_path
            elif self.is_backend:
                return self.backend_path
            # If not in a project, return None
            return None

        return None

    def require_frontend(self) -> Path:
        """Require frontend project to exist, raise error if not found."""
        if not self.has_frontend:
            console.print("❌ Frontend project not found in workspace", style="red")
            console.print("Expected: package.json + next.config.ts", style="yellow")
            raise typer.Exit(1)
        return self.frontend_path  # type: ignore

    def require_backend(self) -> Path:
        """Require backend project to exist, raise error if not found."""
        if not self.has_backend:
            console.print("❌ Backend project not found in workspace", style="red")
            console.print("Expected: pyproject.toml + main.py", style="yellow")
            raise typer.Exit(1)
        return self.backend_path  # type: ignore

    def require_project(self) -> tuple[ProjectType, Path]:
        """Require a project context (either FE or BE), raise error if ambiguous.

        Returns:
            Tuple of (project_type, project_path)
        """
        if self.current_type:
            path = self.get_target_path(self.current_type)
            if path:
                return self.current_type, path

        # Not in a specific project, check workspace
        if self.has_frontend and not self.has_backend:
            return "frontend", self.frontend_path  # type: ignore
        elif self.has_backend and not self.has_frontend:
            return "backend", self.backend_path  # type: ignore
        elif self.has_frontend and self.has_backend:
            console.print(
                "❌ Ambiguous context: workspace has both FE and BE projects",
                style="red",
            )
            console.print(
                "Run command from within a specific project directory", style="yellow"
            )
            raise typer.Exit(1)
        else:
            console.print("❌ No project found in workspace", style="red")
            console.print(
                "Expected FE markers: package.json + next.config.ts", style="yellow"
            )
            console.print(
                "Expected BE markers: pyproject.toml + main.py", style="yellow"
            )
            raise typer.Exit(1)


def get_context(start_path: Optional[Path] = None) -> ProjectContext:
    """Get the current project context.

    Args:
        start_path: Starting path for detection (defaults to cwd)

    Returns:
        ProjectContext instance
    """
    return ProjectContext(start_path)
