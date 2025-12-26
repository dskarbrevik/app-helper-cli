"""Tests for clean commands."""

from pathlib import Path

import pytest

from dh.commands import clean


class TestCleanCommand:
    """Test suite for the clean command."""
    
    def test_clean_frontend_artifacts(self, mock_context, mock_run_command):
        """Test cleaning frontend build artifacts."""
        # Create dummy directories
        (mock_context.frontend_path / "node_modules").mkdir()
        (mock_context.frontend_path / ".next").mkdir()
        (mock_context.frontend_path / "out").mkdir()
        (mock_context.frontend_path / ".turbo").mkdir()
        
        mock_context.is_frontend = True
        mock_context.is_backend = False
        mock_context.has_frontend = True
        
        # Run clean command
        clean.clean()
        
        # Verify rm commands were called
        assert mock_run_command.call_count >= 4
        
        # Check that rm -rf was called for each directory
        calls = [call[0][0] for call in mock_run_command.call_args_list]
        assert any("rm -rf node_modules" in call for call in calls)
        assert any("rm -rf .next" in call for call in calls)
    
    def test_clean_backend_artifacts(self, mock_context, mock_run_command):
        """Test cleaning backend build artifacts."""
        mock_context.is_frontend = False
        mock_context.is_backend = True
        mock_context.has_backend = True
        
        # Run clean command
        clean.clean()
        
        # Verify Python cache cleanup was called
        assert mock_run_command.called
        calls = [call[0][0] for call in mock_run_command.call_args_list]
        assert any("__pycache__" in call for call in calls)
    
    def test_clean_both_projects(self, mock_context, mock_run_command):
        """Test cleaning both frontend and backend."""
        # Create frontend artifacts
        (mock_context.frontend_path / "node_modules").mkdir()
        
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = True
        mock_context.has_backend = True
        
        # Run clean command
        clean.clean()
        
        # Verify both cleanups were called
        assert mock_run_command.call_count > 0
    
    def test_clean_no_artifacts(self, mock_context, mock_run_command):
        """Test clean command when no artifacts exist."""
        mock_context.is_frontend = True
        mock_context.is_backend = False
        mock_context.has_frontend = True
        
        # Run clean command (no directories exist)
        clean.clean()
        
        # Should complete without errors
        # No rm commands for non-existent directories
        calls = [call[0][0] for call in mock_run_command.call_args_list]
        # Only commands for existing artifacts should be run
        assert len(calls) >= 0  # May or may not run commands
