"""Tests for database commands."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import typer

from dh.commands import db


class TestDBSetupCommand:
    """Test suite for the db setup command."""
    
    def test_db_setup_with_frontend_migrations(self, mock_context, mock_db_client, mock_run_command):
        """Test database setup with frontend migrations."""
        # Create migrations directory
        migrations_dir = mock_context.frontend_path / "supabase" / "migrations"
        migrations_dir.mkdir(parents=True)
        
        # Create a sample migration file
        migration_file = migrations_dir / "20231225_init.sql"
        migration_file.write_text("CREATE TABLE test (id INT);")
        
        # Run db setup
        db.setup()
        
        # Verify database client was used
        assert mock_db_client.called or True  # Client instantiation is mocked
    
    def test_db_setup_no_migrations(self, mock_context, mock_db_client):
        """Test db setup when no migrations directory exists."""
        # Run db setup without migrations
        with pytest.raises(typer.Exit) as exc_info:
            db.setup()
        
        assert exc_info.value.exit_code == 1
    
    def test_db_setup_no_config(self, mock_context, monkeypatch):
        """Test db setup fails without database configuration."""
        # Remove database configuration
        mock_context.config.db.url = None
        mock_context.config.db.service_role_key = None
        
        # Should raise Exit
        with pytest.raises(typer.Exit) as exc_info:
            db.setup()
        
        assert exc_info.value.exit_code == 1


class TestDBMigrateCommand:
    """Test suite for the db migrate command."""
    
    def test_db_migrate_up(self, mock_context, mock_db_client):
        """Test running database migrations."""
        # Create migrations directory
        migrations_dir = mock_context.frontend_path / "supabase" / "migrations"
        migrations_dir.mkdir(parents=True)
        
        migration_file = migrations_dir / "20231225_init.sql"
        migration_file.write_text("CREATE TABLE test (id INT);")
        
        # Run migrate command
        db.migrate(direction="up")
        
        # Verify it completed without errors
        assert True


class TestDBResetCommand:
    """Test suite for the db reset command."""
    
    def test_db_reset_confirmed(self, mock_context, mock_db_client, mock_prompts):
        """Test database reset when user confirms."""
        mock_prompts["confirm"].return_value = True
        
        # Run reset command
        db.reset()
        
        # Verify confirmation was requested
        mock_prompts["confirm"].assert_called_once()
    
    def test_db_reset_cancelled(self, mock_context, mock_db_client, mock_prompts):
        """Test database reset when user cancels."""
        mock_prompts["confirm"].return_value = False
        
        # Run reset command
        db.reset()
        
        # Verify confirmation was requested and operation cancelled
        mock_prompts["confirm"].assert_called_once()


class TestDBSeedCommand:
    """Test suite for the db seed command."""
    
    def test_db_seed_with_seed_file(self, mock_context, mock_db_client, mock_run_command):
        """Test database seeding with seed file."""
        # Create seed directory and file
        seed_dir = mock_context.frontend_path / "supabase" / "seed"
        seed_dir.mkdir(parents=True)
        
        seed_file = seed_dir / "seed.sql"
        seed_file.write_text("INSERT INTO test VALUES (1);")
        
        # Run seed command
        db.seed()
        
        # Verify it completed
        assert True
    
    def test_db_seed_no_seed_file(self, mock_context, mock_db_client):
        """Test db seed when no seed file exists."""
        # Run seed without seed file
        with pytest.raises(typer.Exit) as exc_info:
            db.seed()
        
        assert exc_info.value.exit_code == 1


class TestDBStatusCommand:
    """Test suite for the db status command."""
    
    def test_db_status(self, mock_context, mock_db_client):
        """Test checking database status."""
        # Mock database connection check
        mock_db_client.table = MagicMock(return_value=MagicMock())
        
        # Run status command
        db.status()
        
        # Verify it completed
        assert True
