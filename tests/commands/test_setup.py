"""Tests for setup commands."""

from unittest.mock import patch

import pytest
import typer

from dh.commands import setup


class TestSetupCommand:
    """Test suite for the setup command."""

    def test_setup_detects_projects(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test that setup detects frontend and backend projects."""
        with (
            patch("dh.commands.setup.prompt_confirm", return_value=False),
            patch("dh.commands.setup.prompt_text", return_value="test"),
        ):
            # Run setup
            try:
                setup.setup()
            except typer.Exit:
                # Setup exits after user declines DB config
                pass

            # Verify tools were checked
            assert mock_check_command_exists.called

    def test_setup_no_projects_detected(self, mock_context, monkeypatch):
        """Test setup fails when no projects are detected."""
        # Mock context with no projects
        mock_context.has_frontend = False
        mock_context.has_backend = False

        # Should raise Exit
        with pytest.raises(typer.Exit) as exc_info:
            setup.setup()

        assert exc_info.value.exit_code == 1

    def test_setup_missing_tools(self, mock_context, mock_check_command_exists):
        """Test setup warns about missing tools."""
        with (
            patch("dh.commands.setup.check_command_exists") as mock_check,
            patch("dh.commands.setup.prompt_confirm", return_value=False),
        ):
            # Mock some tools missing
            def mock_exists(cmd):
                return cmd in ["node", "npm", "uv"]  # Docker missing

            mock_check.side_effect = mock_exists

            # Run setup - should warn but not fail
            try:
                setup.setup()
            except typer.Exit:
                pass

            assert mock_check.called

    def test_setup_checks_required_tools_frontend(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test that setup checks for required frontend tools."""
        mock_context.has_frontend = True
        mock_context.has_backend = False
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "20.0.0"

        try:
            setup.setup()
        except (typer.Exit, Exception):
            pass

        # Verify Node.js and npm were checked
        calls = [call[0][0] for call in mock_check_command_exists.call_args_list]
        assert "node" in calls
        assert "npm" in calls

    def test_setup_checks_required_tools_backend(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test that setup checks for required backend tools."""
        mock_context.has_frontend = False
        mock_context.has_backend = True

        with (
            patch(
                "dh.commands.setup.check_command_exists", return_value=True
            ) as mock_check,
            patch("dh.commands.setup.prompt_confirm", return_value=False),
        ):
            try:
                setup.setup()
            except (typer.Exit, Exception):
                pass

            # Verify uv was checked
            calls = [call[0][0] for call in mock_check.call_args_list]
            assert "uv" in calls


class TestInstallCommand:
    """Test suite for the install command."""

    def test_install_frontend_dependencies(self, mock_context, mock_run_command):
        """Test installing frontend dependencies."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        # Run install
        setup.install()

        # Verify commands were called (npm install + uv sync)
        assert mock_run_command.call_count >= 1

    def test_install_backend_dependencies(self, mock_context, mock_run_command):
        """Test installing backend dependencies."""
        mock_context.is_frontend = False
        mock_context.is_backend = True

        # Run install
        setup.install()

        # Verify commands were called
        assert mock_run_command.call_count >= 1

    def test_install_both_projects(self, mock_context, mock_run_command):
        """Test installing dependencies for both projects."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = True
        mock_context.has_backend = True

        # Run install
        setup.install()

        # Verify both installs were called
        assert mock_run_command.call_count >= 2

        calls = [call[0][0] for call in mock_run_command.call_args_list]
        assert any("npm install" in call for call in calls)
        assert any("uv sync" in call for call in calls)

    def test_install_no_projects(self, mock_context):
        """Test install when no projects - still installs dependencies."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = False
        mock_context.has_backend = False

        # Install runs even with no projects (installs both)
        setup.install()
        # Should complete without error
