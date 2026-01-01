"""Tests for project detection utilities."""

from pathlib import Path


from dh.utils.detection import (
    detect_project_type,
    find_project_dirs,
    find_workspace_root,
)


class TestDetectProjectType:
    """Test suite for detect_project_type function."""

    def test_detect_frontend_project(self, tmp_path: Path):
        """Test detecting a frontend project."""
        project_dir = tmp_path / "frontend"
        project_dir.mkdir()
        (project_dir / "package.json").write_text('{"name": "test"}')
        (project_dir / "next.config.ts").write_text("export default {}")

        result = detect_project_type(project_dir)

        assert result == "frontend"

    def test_detect_backend_project(self, tmp_path: Path):
        """Test detecting a backend project."""
        project_dir = tmp_path / "backend"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text('[project]\nname = "test"')
        (project_dir / "main.py").write_text("# FastAPI app")

        result = detect_project_type(project_dir)

        assert result == "backend"

    def test_detect_no_project(self, tmp_path: Path):
        """Test detecting when no project markers exist."""
        project_dir = tmp_path / "random"
        project_dir.mkdir()

        result = detect_project_type(project_dir)

        assert result is None

    def test_detect_frontend_missing_next_config(self, tmp_path: Path):
        """Test detection fails when Next.js config is missing."""
        project_dir = tmp_path / "frontend"
        project_dir.mkdir()
        (project_dir / "package.json").write_text('{"name": "test"}')
        # No next.config.ts

        result = detect_project_type(project_dir)

        assert result is None

    def test_detect_backend_missing_main(self, tmp_path: Path):
        """Test detection fails when main.py is missing."""
        project_dir = tmp_path / "backend"
        project_dir.mkdir()
        (project_dir / "pyproject.toml").write_text('[project]\nname = "test"')
        # No main.py

        result = detect_project_type(project_dir)

        assert result is None


class TestFindWorkspaceRoot:
    """Test suite for find_workspace_root function."""

    def test_find_workspace_from_git_directory(self, tmp_path: Path):
        """Test finding workspace root from .git directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / ".git").mkdir()

        # Create a subdirectory
        subdir = workspace / "subdir"
        subdir.mkdir()

        result = find_workspace_root(subdir)

        assert result == workspace

    def test_find_workspace_from_project_directory(self, tmp_path: Path):
        """Test finding workspace root when in a project directory."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create a frontend project
        frontend = workspace / "frontend"
        frontend.mkdir()
        (frontend / "package.json").write_text('{"name": "test"}')
        (frontend / "next.config.ts").write_text("export default {}")

        result = find_workspace_root(frontend)

        assert result == workspace

    def test_find_workspace_from_nested_git(self, tmp_path: Path):
        """Test finding workspace root with nested structure and git."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / ".git").mkdir()

        # Create nested project
        project = workspace / "apps" / "frontend"
        project.mkdir(parents=True)

        result = find_workspace_root(project)

        assert result == workspace

    def test_find_workspace_no_git_no_parent_projects(self, tmp_path: Path):
        """Test finding workspace when no .git and no parent projects exist."""
        # Create a directory without .git
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # When no .git found and not in a project, returns current directory
        result = find_workspace_root(test_dir)

        # Should return the resolved current directory
        assert result.exists()


class TestFindProjectDirs:
    """Test suite for find_project_dirs function."""

    def test_find_both_projects(self, tmp_path: Path):
        """Test finding both frontend and backend projects."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create frontend
        frontend = workspace / "frontend"
        frontend.mkdir()
        (frontend / "package.json").write_text('{"name": "fe"}')
        (frontend / "next.config.ts").write_text("export default {}")

        # Create backend
        backend = workspace / "backend"
        backend.mkdir()
        (backend / "pyproject.toml").write_text('[project]\nname = "be"')
        (backend / "main.py").write_text("# app")

        result = find_project_dirs(workspace)

        assert result["frontend"] == frontend
        assert result["backend"] == backend

    def test_find_no_projects(self, tmp_path: Path):
        """Test finding no projects in workspace."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create some non-project directories
        (workspace / "docs").mkdir()
        (workspace / "scripts").mkdir()

        result = find_project_dirs(workspace)

        assert result["frontend"] is None
        assert result["backend"] is None

    def test_find_first_matching_project_only(self, tmp_path: Path):
        """Test that only the first matching project of each type is found."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create two frontend projects (alphabetically, fe1 comes first)
        fe1 = workspace / "fe1"
        fe1.mkdir()
        (fe1 / "package.json").write_text('{"name": "fe1"}')
        (fe1 / "next.config.ts").write_text("export default {}")

        fe2 = workspace / "fe2"
        fe2.mkdir()
        (fe2 / "package.json").write_text('{"name": "fe2"}')
        (fe2 / "next.config.ts").write_text("export default {}")

        result = find_project_dirs(workspace)

        # Should find only one frontend (whichever is discovered first)
        assert result["frontend"] in [fe1, fe2]
        assert result["backend"] is None

    def test_find_projects_with_nested_dirs(self, tmp_path: Path):
        """Test finding projects at workspace root level only."""
        workspace = tmp_path / "workspace"
        workspace.mkdir()

        # Create project at root
        frontend = workspace / "frontend"
        frontend.mkdir()
        (frontend / "package.json").write_text('{"name": "fe"}')
        (frontend / "next.config.ts").write_text("export default {}")

        # Create nested project that should be ignored
        nested = workspace / "apps" / "nested-fe"
        nested.mkdir(parents=True)
        (nested / "package.json").write_text('{"name": "nested"}')
        (nested / "next.config.ts").write_text("export default {}")

        result = find_project_dirs(workspace)

        # Should only find the root-level frontend
        assert result["frontend"] == frontend
        assert result["backend"] is None
