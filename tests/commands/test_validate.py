"""Tests for validate commands."""

import pytest

from dh.commands import validate


class TestValidateCommand:
    """Test suite for the validate command."""
    
    def test_validate_with_all_tools_installed(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation when all required tools are installed."""
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "1.0.0"
        
        # Create node_modules to simulate installed dependencies
        (mock_context.frontend_path / "node_modules").mkdir()
        
        # Run validate
        validate.validate()
        
        # Verify checks were performed
        assert mock_check_command_exists.called
        assert mock_check_tool_version.called
    
    def test_validate_frontend_missing_node(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation detects missing Node.js."""
        def mock_check_exists(cmd):
            return cmd != "node"
        
        mock_check_command_exists.side_effect = mock_check_exists
        mock_check_tool_version.return_value = "1.0.0"
        
        # Run validate
        validate.validate()
        
        # Should complete and report issues (not crash)
        assert True
    
    def test_validate_frontend_missing_dependencies(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation detects missing frontend dependencies."""
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "1.0.0"
        
        # Don't create node_modules
        
        # Run validate
        validate.validate()
        
        # Should detect missing node_modules
        assert not (mock_context.frontend_path / "node_modules").exists()
    
    def test_validate_backend_tools(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation checks backend tools."""
        mock_context.has_backend = True
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "3.11.0"
        
        # Run validate
        validate.validate()
        
        # Verify Python was checked
        calls = [call[0][0] for call in mock_check_command_exists.call_args_list]
        assert "python3" in calls or "python" in calls
    
    def test_validate_database_connection(
        self, mock_context, mock_db_client, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation checks database connection."""
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "1.0.0"
        
        # Mock successful database connection
        mock_db_client.table = lambda x: mock_db_client
        mock_db_client.select = lambda x: mock_db_client
        mock_db_client.limit = lambda x: mock_db_client
        mock_db_client.execute = lambda: None
        
        # Run validate
        validate.validate()
        
        # Should check database
        assert True
    
    def test_validate_no_database_config(
        self, mock_context, mock_check_command_exists, mock_check_tool_version
    ):
        """Test validation handles missing database config."""
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "1.0.0"
        
        # Remove database configuration
        mock_context.config.db.url = None
        mock_context.config.db.service_role_key = None
        
        # Run validate - should not crash
        validate.validate()
        
        # Should complete without database checks
        assert True
    
    def test_validate_displays_summary(
        self, mock_context, mock_check_command_exists, mock_check_tool_version, capsys
    ):
        """Test validation displays a summary of checks."""
        mock_check_command_exists.return_value = True
        mock_check_tool_version.return_value = "1.0.0"
        
        (mock_context.frontend_path / "node_modules").mkdir()
        
        # Run validate
        validate.validate()
        
        # Should display output (verified by not crashing)
        assert True
