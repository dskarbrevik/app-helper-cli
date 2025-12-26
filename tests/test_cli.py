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
    
    def test_build_command_exists(self):
        """Test build command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["build", "--help"])
        
        assert result.exit_code == 0
        assert "Build" in result.output or "build" in result.output
    
    def test_clean_command_exists(self):
        """Test clean command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["clean", "--help"])
        
        assert result.exit_code == 0
        assert "clean" in result.output.lower()
    
    def test_dev_command_exists(self):
        """Test dev command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["dev", "--help"])
        
        assert result.exit_code == 0
        assert "dev" in result.output.lower()
    
    def test_setup_command_exists(self):
        """Test setup command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["setup", "--help"])
        
        assert result.exit_code == 0
        assert "setup" in result.output.lower()
    
    def test_validate_command_exists(self):
        """Test validate command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["validate", "--help"])
        
        assert result.exit_code == 0
        assert "validate" in result.output.lower()
    
    def test_db_subcommand_exists(self):
        """Test db subcommand group is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["db", "--help"])
        
        assert result.exit_code == 0
        assert "db" in result.output.lower() or "database" in result.output.lower()
    
    def test_lint_command_exists(self):
        """Test lint command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["lint", "--help"])
        
        assert result.exit_code == 0
        assert "lint" in result.output.lower()
    
    def test_format_command_exists(self):
        """Test format command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["format", "--help"])
        
        assert result.exit_code == 0
        assert "format" in result.output.lower()
    
    def test_test_command_exists(self):
        """Test test command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["test", "--help"])
        
        assert result.exit_code == 0
        assert "test" in result.output.lower()
    
    def test_run_command_exists(self):
        """Test run command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["run", "--help"])
        
        assert result.exit_code == 0
        assert "run" in result.output.lower()
    
    def test_install_command_exists(self):
        """Test install command is registered."""
        runner = CliRunner()
        result = runner.invoke(app, ["install", "--help"])
        
        assert result.exit_code == 0
        assert "install" in result.output.lower()
