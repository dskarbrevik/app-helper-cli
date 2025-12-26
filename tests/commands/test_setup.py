"""Tests for setup commands."""

import pytest
import typer

from dh.commands import setup


class TestSetupCommand:
    """Test suite for the setup command."""
    
    def test_setup_detects_projects(self, mock_context, mock_check_command_exists, mock_check_tool_version, mock_prompts):
        """Test that setup detects frontend and backend projects."""
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "1.0.0"
        
        # Mock all required tools exist
        # Run setup
        try:
            setup.setup()
        except typer.Exit:
            # Setup may exit after completion or prompt cancellation
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
    
    def test_setup_missing_tools(self, mock_context, mock_check_command_exists, monkeypatch):
        """Test setup warns about missing tools."""
        # Mock some tools missing
        def mock_check_exists(cmd):
            return cmd in ["node", "npm"]  # Docker and supabase missing
        
        mock_check_command_exists.side_effect = mock_check_exists
        
        # Run setup - should warn but not fail
        try:
            setup.setup()
        except typer.Exit:
            pass
        
        assert mock_check_command_exists.called
    
    def test_setup_checks_required_tools_frontend(self, mock_context, mock_check_command_exists, mock_check_tool_version):
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
    
    def test_setup_checks_required_tools_backend(self, mock_context, mock_check_command_exists, mock_check_tool_version):
        """Test that setup checks for required backend tools."""
        mock_context.has_frontend = False
        mock_context.has_backend = True
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "3.11.0"
        
        try:
            setup.setup()
        except (typer.Exit, Exception):
            pass
        
        # Verify Python and uv were checked
        calls = [call[0][0] for call in mock_check_command_exists.call_args_list]
        assert "python3" in calls or "python" in calls


class TestInstallCommand:
    """Test suite for the install command."""
    
    def test_install_frontend_dependencies(self, mock_context, mock_run_command):
        """Test installing frontend dependencies."""
        mock_context.is_frontend = True
        mock_context.is_backend = False
        
        # Run install
        setup.install()
        
        # Verify npm install was called
        mock_run_command.assert_called_once()
        assert "npm install" in mock_run_command.call_args[0]
        assert mock_run_command.call_args[1]["cwd"] == mock_context.frontend_path
    
    def test_install_backend_dependencies(self, mock_context, mock_run_command):
        """Test installing backend dependencies."""
        mock_context.is_frontend = False
        mock_context.is_backend = True
        
        # Run install
        setup.install()
        
        # Verify uv sync was called
        mock_run_command.assert_called_once()
        assert "uv sync" in mock_run_command.call_args[0][0]
        assert mock_run_command.call_args[1]["cwd"] == mock_context.backend_path
    
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
        """Test install fails when no projects are available."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = False
        mock_context.has_backend = False
        
        # Should raise Exit
        with pytest.raises(typer.Exit) as exc_info:
            setup.install()
        
        assert exc_info.value.exit_code == 1
