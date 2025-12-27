"""Pytest configuration and shared fixtures."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Provide a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_context(tmp_path: Path):
    """Provide a mock context for testing."""
    # Create temporary project structure
    frontend_path = tmp_path / "fe"
    backend_path = tmp_path / "be"
    frontend_path.mkdir()
    backend_path.mkdir()

    # Create frontend markers with proper structure
    (frontend_path / "package.json").write_text(
        '{"name": "test-fe", "scripts": {"dev": "echo dev", "build": "echo build", "lint": "echo lint", "test": "echo test", "format": "echo format"}}'
    )
    (frontend_path / "next.config.ts").write_text("export default {}")

    # Create backend markers with valid pyproject.toml
    (backend_path / "pyproject.toml").write_text(
        '[project]\nname = "test-be"\nversion = "0.1.0"'
    )
    (backend_path / "main.py").write_text("# FastAPI app")

    # Create mock context object
    class MockContext:
        def __init__(self):
            self.workspace_root = tmp_path
            self.start_path = tmp_path
            self.frontend_path = frontend_path
            self.backend_path = backend_path
            self.has_frontend = True
            self.has_backend = True
            self.is_frontend = False
            self.is_backend = False

            # Mock config
            from dh.utils.config import Config, DatabaseConfig

            self.config = Config(
                db=DatabaseConfig(
                    url="https://test.supabase.co",
                    secret_key="test-key",
                    password="test-pass",
                    project_ref="test-ref",
                )
            )

    return MockContext()


@pytest.fixture(autouse=True)
def mock_get_context(mock_context, monkeypatch):
    """Automatically mock get_context in all tests."""

    def _mock_get_context():
        return mock_context

    monkeypatch.setattr("dh.context.get_context", _mock_get_context)
    monkeypatch.setattr("dh.commands.build.get_context", _mock_get_context)
    monkeypatch.setattr("dh.commands.clean.get_context", _mock_get_context)
    monkeypatch.setattr("dh.commands.db.get_context", _mock_get_context)
    monkeypatch.setattr("dh.commands.dev.get_context", _mock_get_context)
    monkeypatch.setattr("dh.commands.setup.get_context", _mock_get_context)
    monkeypatch.setattr("dh.commands.validate.get_context", _mock_get_context)


@pytest.fixture(autouse=True)
def mock_subprocess_run():
    """Mock subprocess.run to prevent actual command execution - applies to all tests."""
    with patch("dh.utils.commands.subprocess.run") as mock:
        # Create a mock result object with proper attributes
        result = MagicMock()
        result.returncode = 0
        result.stdout = "1.0.0"
        result.stderr = ""
        mock.return_value = result
        yield mock


@pytest.fixture
def mock_run_command(mock_subprocess_run):
    """Provides access to the subprocess mock for assertion checks."""
    return mock_subprocess_run


@pytest.fixture
def mock_check_command_exists():
    """Mock the check_command_exists utility."""
    with patch("dh.utils.commands.check_command_exists") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_check_tool_version():
    """Mock the check_tool_version utility."""
    with patch("dh.utils.commands.check_tool_version") as mock:
        mock.return_value = "1.0.0"
        yield mock


@pytest.fixture
def mock_db_client():
    """Mock the database client."""
    with patch("dh.utils.db.create_db_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_prompts():
    """Mock user prompt utilities."""
    with (
        patch("dh.utils.prompts.prompt_confirm") as mock_confirm,
        patch("dh.utils.prompts.prompt_text") as mock_text,
    ):
        mock_confirm.return_value = True
        mock_text.return_value = "test-value"
        yield {
            "confirm": mock_confirm,
            "text": mock_text,
        }
