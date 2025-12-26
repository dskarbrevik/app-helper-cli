"""Tests for database commands."""

import pytest
import typer
from unittest.mock import patch

from dh.commands import db


class TestDBSetupCommand:
    """Test suite for the db setup command."""

    def test_db_setup_with_frontend_migrations(
        self, mock_context, mock_db_client, mock_run_command
    ):
        """Test database setup with frontend migrations."""
        # Create migrations directory
        migrations_dir = mock_context.frontend_path / "supabase" / "migrations"
        migrations_dir.mkdir(parents=True)

        # Create a sample migration file
        migration_file = migrations_dir / "20231225_init.sql"
        migration_file.write_text("CREATE TABLE test (id INT);")

        # Mock the db connection to succeed
        with patch("dh.commands.db.create_db_client") as mock_create:
            mock_client = mock_db_client
            mock_client.test_connection.return_value = True
            mock_create.return_value = mock_client

            # Run db setup - should attempt to apply migrations
            try:
                db.setup()
            except typer.Exit:
                # May exit after attempting migrations
                pass

            # Verify that database client was created
            assert mock_create.called

    def test_db_setup_no_migrations(self, mock_context, mock_db_client):
        """Test db setup when no migrations directory exists."""
        # Run db setup without migrations should fail
        with pytest.raises(typer.Exit) as exc_info:
            db.setup()

        # Verify it exits with error code
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


# Note: migrate, reset, and seed commands don't exist yet
# These tests are placeholders for future functionality


class TestDBStatusCommand:
    """Test suite for the db status command."""

    def test_db_status(self, mock_context, mock_db_client):
        """Test checking database status."""
        # Mock the database client creation
        with patch("dh.commands.db.create_db_client") as mock_create:
            mock_client = mock_db_client
            mock_client.test_connection.return_value = True
            mock_create.return_value = mock_client

            try:
                db.status()
            except typer.Exit:
                pass

            # Verify that we attempted to check the connection
            assert mock_create.called or mock_client.test_connection.called
