"""Tests for build commands."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import typer

from dh.commands import build


class TestBuildCommand:
    """Test suite for the build command."""
    
    def test_build_frontend_regular(self, mock_context, mock_run_command):
        """Test building frontend for production."""
        # Set context to frontend only
        mock_context.is_frontend = True
        mock_context.is_backend = False
        
        # Run build command
        build.build(docker=False)
        
        # Verify npm build was called
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args
        assert "npm run build" in call_args[0]
        assert call_args[1]["cwd"] == mock_context.frontend_path
    
    def test_build_backend_regular(self, mock_context, mock_run_command):
        """Test building backend for production."""
        # Set context to backend only
        mock_context.is_frontend = False
        mock_context.is_backend = True
        
        # Run build command
        build.build(docker=False)
        
        # Verify backend build was called
        mock_run_command.assert_called()
    
    def test_build_frontend_docker(self, mock_context, mock_run_command, mock_check_command_exists):
        """Test building frontend Docker image."""
        mock_context.is_frontend = True
        mock_context.is_backend = False
        mock_check_command_exists.return_value = True
        
        # Run build with docker flag
        build.build(docker=True)
        
        # Verify docker build was called
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args
        assert "docker build" in call_args[0]
        assert call_args[1]["cwd"] == mock_context.frontend_path
    
    def test_build_docker_not_installed(self, mock_context, mock_check_command_exists):
        """Test build fails gracefully when Docker is not installed."""
        mock_context.is_frontend = True
        mock_check_command_exists.return_value = False
        
        # Run build with docker flag should raise Exit
        with pytest.raises(typer.Exit) as exc_info:
            build.build(docker=True)
        
        assert exc_info.value.exit_code == 1
    
    def test_build_both_projects(self, mock_context, mock_run_command):
        """Test building both frontend and backend."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = True
        mock_context.has_backend = True
        
        # Run build command
        build.build(docker=False)
        
        # Verify both builds were called
        assert mock_run_command.call_count >= 2


class TestRunCommand:
    """Test suite for the run command."""
    
    def test_run_frontend_docker(self, mock_context, mock_run_command, mock_check_command_exists):
        """Test running frontend Docker container."""
        mock_context.is_frontend = True
        mock_context.is_backend = False
        mock_check_command_exists.return_value = True
        
        # Run the run command
        build.run()
        
        # Verify docker run was called
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args[0][0]
        assert "docker run" in call_args
        assert "-p 3000:3000" in call_args
    
    def test_run_backend_docker(self, mock_context, mock_run_command, mock_check_command_exists):
        """Test running backend Docker container."""
        mock_context.is_frontend = False
        mock_context.is_backend = True
        mock_check_command_exists.return_value = True
        
        # Run the run command
        build.run()
        
        # Verify docker run was called
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args[0][0]
        assert "docker run" in call_args
        assert "-p 8000:8000" in call_args
    
    def test_run_docker_not_installed(self, mock_context, mock_check_command_exists):
        """Test run fails gracefully when Docker is not installed."""
        mock_context.is_frontend = True
        mock_check_command_exists.return_value = False
        
        # Run should raise Exit
        with pytest.raises(typer.Exit) as exc_info:
            build.run()
        
        assert exc_info.value.exit_code == 1
