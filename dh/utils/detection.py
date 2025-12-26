"""Project detection utilities."""

from pathlib import Path
from typing import Literal, Optional

ProjectType = Literal["frontend", "backend"]


def _is_project_dir(path: Path) -> bool:
    """Check if a directory contains project markers (internal helper)."""
    # Frontend markers
    if (path / "package.json").exists() and (path / "next.config.ts").exists():
        return True
    # Backend markers
    if (path / "pyproject.toml").exists() and (path / "main.py").exists():
        return True
    return False


def find_workspace_root(start_path: Path | None = None) -> Path:
    """Find the workspace root by looking for common markers.

    For multi-repo workspaces, looks for parent directory containing
    multiple project directories.
    """
    current = Path(start_path or Path.cwd()).resolve()

    # First check if current directory is a project
    current_is_project = _is_project_dir(current)

    if current_is_project:
        # If we're in a project, go up one level to find workspace
        parent = current.parent

        # Check if parent contains multiple projects
        child_projects = sum(
            1 for child in parent.iterdir() if child.is_dir() and _is_project_dir(child)
        )

        if child_projects >= 1:
            return parent

    # Otherwise search upward for .git directory
    search_current = current
    while search_current != search_current.parent:
        if (search_current / ".git").exists():
            return search_current
        search_current = search_current.parent

    # If no .git found, use current directory
    return Path.cwd().resolve()


def detect_project_type(path: Path) -> Optional[ProjectType]:
    """Detect if a directory contains a frontend or backend project.

    Frontend markers: package.json + next.config.ts
    Backend markers: pyproject.toml + main.py
    """
    path = path.resolve()

    # Check for frontend
    if (path / "package.json").exists() and (path / "next.config.ts").exists():
        return "frontend"

    # Check for backend
    if (path / "pyproject.toml").exists() and (path / "main.py").exists():
        return "backend"

    return None


def find_project_dirs(workspace_root: Path) -> dict[ProjectType, Optional[Path]]:
    """Find frontend and backend project directories in workspace.

    Returns a dict with 'frontend' and 'backend' keys, values are paths or None.
    """
    projects: dict[ProjectType, Optional[Path]] = {
        "frontend": None,
        "backend": None,
    }

    # Check common patterns
    for child in workspace_root.iterdir():
        if not child.is_dir():
            continue

        project_type = detect_project_type(child)
        if project_type and projects[project_type] is None:
            projects[project_type] = child

    return projects
