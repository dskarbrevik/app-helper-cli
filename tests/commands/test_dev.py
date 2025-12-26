"""Tests for dev commands."""

import pytest
import typer

from dh.commands import dev


class TestDevCommand:
    """Test suite for the dev command."""

    def test_dev_frontend(self, mock_context, mock_run_command):
        """Test starting frontend dev server."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        # Run dev command
        dev.dev()

        # Verify npm run dev was called
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args
        assert "npm run dev" in call_args[0]
        assert call_args[1]["cwd"] == mock_context.frontend_path

    def test_dev_backend(self, mock_context, mock_run_command):
        """Test starting backend dev server."""
        mock_context.is_frontend = False
        mock_context.is_backend = True

        # Run dev command
        dev.dev()

        # Verify uvicorn was called
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args
        assert "uvicorn" in call_args[0][0]
        assert "main:app" in call_args[0][0]
        assert call_args[1]["cwd"] == mock_context.backend_path

    def test_dev_only_frontend_available(self, mock_context, mock_run_command):
        """Test dev when only frontend is available."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = True
        mock_context.has_backend = False

        # Run dev command
        dev.dev()

        # Should start frontend
        mock_run_command.assert_called_once()
        assert "npm run dev" in mock_run_command.call_args[0]

    def test_dev_only_backend_available(self, mock_context, mock_run_command):
        """Test dev when only backend is available."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = False
        mock_context.has_backend = True

        # Run dev command
        dev.dev()

        # Should start backend
        mock_run_command.assert_called_once()
        assert "uvicorn" in mock_run_command.call_args[0][0]

    def test_dev_ambiguous_context(self, mock_context):
        """Test dev fails when both projects are available and context is ambiguous."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = True
        mock_context.has_backend = True

        # Should raise Exit
        with pytest.raises(typer.Exit) as exc_info:
            dev.dev()

        assert exc_info.value.exit_code == 1


class TestLintCommand:
    """Test suite for the lint command."""

    def test_lint_frontend(self, mock_context, mock_run_command):
        """Test linting frontend code."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        # Run lint command
        dev.lint()

        # Verify npm run lint was called
        mock_run_command.assert_called_once()
        assert "npm run lint" in mock_run_command.call_args[0]

    def test_lint_backend(self, mock_context, mock_run_command):
        """Test linting backend code."""
        mock_context.is_frontend = False
        mock_context.is_backend = True

        # Run lint command
        dev.lint()

        # Verify ruff check was called
        mock_run_command.assert_called_once()
        assert "ruff check" in mock_run_command.call_args[0][0]


class TestFormatCommand:
    """Test suite for the format command."""

    def test_format_frontend(self, mock_context, mock_run_command):
        """Test formatting frontend code - shows warning about Prettier."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        # Run format command
        dev.format()

        # Frontend format shows a warning, doesn't call run_command
        mock_run_command.assert_not_called()

    def test_format_backend(self, mock_context, mock_run_command):
        """Test formatting backend code."""
        mock_context.is_frontend = False
        mock_context.is_backend = True

        # Run format command
        dev.format()

        # Verify ruff commands were called (format + check --fix)
        assert mock_run_command.call_count >= 2


class TestTestCommand:
    """Test suite for the test command."""

    def test_run_frontend_tests(self, mock_context, mock_run_command):
        """Test running frontend tests."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        # Run test command
        dev.test()

        # Verify npm test was called
        mock_run_command.assert_called_once()
        assert "npm test" in mock_run_command.call_args[0]

    def test_run_backend_tests(self, mock_context, mock_run_command):
        """Test running backend tests."""
        mock_context.is_frontend = False
        mock_context.is_backend = True

        # Run test command
        dev.test()

        # Verify pytest was called
        mock_run_command.assert_called_once()
        assert "pytest" in mock_run_command.call_args[0][0]
