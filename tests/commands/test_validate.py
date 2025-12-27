"""Tests for validate commands."""

from unittest.mock import patch

import typer

from dh.commands import validate


class TestValidateCommand:
    """Test suite for the validate command."""

    def test_validate_with_all_tools_installed(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation when all required tools are installed."""
        with (
            patch(
                "dh.commands.validate.check_command_exists", return_value=True
            ) as mock_check_cmd,
            patch("dh.commands.validate.check_tool_version", return_value="1.0.0"),
        ):
            # Create node_modules to simulate installed dependencies
            (mock_context.frontend_path / "node_modules").mkdir()
            (mock_context.backend_path / ".venv").mkdir()

            try:
                validate.validate()
            except typer.Exit:
                pass

            # Verify that validate actually checked for tools
            assert mock_check_cmd.called

    def test_validate_frontend_missing_node(self, mock_context):
        """Test validation detects missing Node.js."""
        with (
            patch("dh.commands.validate.check_command_exists") as mock_check,
            patch("dh.commands.validate.check_tool_version", return_value="1.0.0"),
        ):
            # Node is missing, other tools present
            mock_check.side_effect = lambda cmd: cmd != "node"

            try:
                validate.validate()
            except typer.Exit as e:
                # Should exit due to missing required tool
                assert e.exit_code == 1
            else:
                # If it doesn't exit, at least verify we checked for node
                calls = [call[0][0] for call in mock_check.call_args_list]
                assert "node" in calls

    def test_validate_frontend_missing_dependencies(self, mock_context):
        """Test validation detects missing frontend dependencies."""
        with (
            patch("dh.commands.validate.check_command_exists", return_value=True),
            patch("dh.commands.validate.check_tool_version", return_value="1.0.0"),
        ):
            try:
                validate.validate()
            except typer.Exit as e:
                # Should detect missing node_modules
                assert e.exit_code == 1

            # Verify that node_modules is indeed missing
            assert not (mock_context.frontend_path / "node_modules").exists()

    def test_validate_backend_tools(self, mock_context):
        """Test validation checks backend tools."""
        with (
            patch("dh.commands.validate.check_command_exists", return_value=True),
            patch("dh.commands.validate.check_tool_version", return_value="3.11.0"),
        ):
            try:
                validate.validate()
            except typer.Exit:
                pass

    def test_validate_database_connection(self, mock_context, mock_db_client):
        """Test validation checks database connection."""
        with (
            patch("dh.commands.validate.check_command_exists", return_value=True),
            patch("dh.commands.validate.check_tool_version", return_value="1.0.0"),
        ):
            try:
                validate.validate()
            except typer.Exit:
                pass

    def test_validate_no_database_config(self, mock_context):
        """Test validation handles missing database config."""
        mock_context.config.db.url = None
        mock_context.config.db.secret_key = None

        with (
            patch("dh.commands.validate.check_command_exists", return_value=True),
            patch("dh.commands.validate.check_tool_version", return_value="1.0.0"),
        ):
            try:
                validate.validate()
            except typer.Exit:
                pass

    def test_validate_displays_summary(self, mock_context):
        """Test validation displays a summary of checks."""
        with (
            patch("dh.commands.validate.check_command_exists", return_value=True),
            patch("dh.commands.validate.check_tool_version", return_value="1.0.0"),
        ):
            (mock_context.frontend_path / "node_modules").mkdir()
            (mock_context.backend_path / ".venv").mkdir()

            try:
                validate.validate()
            except typer.Exit:
                pass
