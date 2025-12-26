"""Tests for CLI entry point and main app."""

from typer.testing import CliRunner

from dh.cli import app


class TestCLI:
    """Test suite for the main CLI application."""

    def test_cli_help(self):
        """Test CLI displays help message."""
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "CLI tool to improve devX for webapps" in result.output

    def test_cli_version(self):
        """Test CLI displays version."""
        runner = CliRunner()
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "dh" in result.output
        assert "version" in result.output

    def test_cli_version_short_flag(self):
        """Test CLI displays version with -v flag."""
        runner = CliRunner()
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert "version" in result.output
