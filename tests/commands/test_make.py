"""Tests for make commands."""

from unittest.mock import patch

import pytest
import typer

from dh.commands import make


class TestMakeRequirementsCommand:
    """Test suite for the make requirements command."""

    def test_make_requirements_success(self, mock_context, mock_run_command):
        """Test generating requirements.txt successfully."""
        mock_context.is_backend = True
        mock_context.is_frontend = False

        with patch("dh.commands.make.check_command_exists", return_value=True):
            # Run make requirements command
            make.requirements()

            # Verify uv export was called with correct arguments
            mock_run_command.assert_called_once()
            call_args = mock_run_command.call_args
            assert "uv export" in call_args[0][0]
            assert "--no-dev" in call_args[0][0]
            assert "--no-hashes" in call_args[0][0]
            assert "--output-file requirements.txt" in call_args[0][0]
            assert call_args[1]["cwd"] == mock_context.backend_path

    def test_make_requirements_no_backend(self, mock_context, mock_run_command):
        """Test make requirements fails when no backend project exists."""
        mock_context.is_backend = False
        mock_context.has_backend = False

        with patch("dh.commands.make.check_command_exists", return_value=True):
            # Should raise Exit due to no backend
            with pytest.raises(typer.Exit) as exc_info:
                make.requirements()

            assert exc_info.value.exit_code == 1
            mock_run_command.assert_not_called()

    def test_make_requirements_uv_not_installed(self, mock_context):
        """Test make requirements fails gracefully when uv is not installed."""
        mock_context.is_backend = True

        with patch("dh.commands.make.check_command_exists", return_value=False):
            # Should raise Exit due to missing uv
            with pytest.raises(typer.Exit) as exc_info:
                make.requirements()

            assert exc_info.value.exit_code == 1


class TestMakeEnvCommand:
    """Test suite for the make env command."""

    def test_make_env_frontend_creates_file(self, mock_context):
        """Test creating frontend .env file."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        # Ensure no .env exists
        env_path = mock_context.frontend_path / ".env"
        if env_path.exists():
            env_path.unlink()

        make.env(target="frontend", force=False)

        # Verify .env was created
        assert env_path.exists()

        # Verify it contains expected variables
        content = env_path.read_text()
        assert "NEXT_PUBLIC_SUPABASE_URL" in content
        assert "NEXT_PUBLIC_SUPABASE_KEY" in content
        assert "NEXT_PUBLIC_API_URL" in content
        assert "SUPABASE_SECRET_KEY" in content
        assert "SUPABASE_DB_PASSWORD" in content
        assert "SUPABASE_TEST_EMAIL" in content
        assert "SUPABASE_TEST_PASSWORD" in content

    def test_make_env_backend_creates_file(self, mock_context):
        """Test creating backend .env file."""
        mock_context.is_frontend = False
        mock_context.is_backend = True

        # Ensure no .env exists
        env_path = mock_context.backend_path / ".env"
        if env_path.exists():
            env_path.unlink()

        make.env(target="backend", force=False)

        # Verify .env was created
        assert env_path.exists()

        # Verify it contains expected variables
        content = env_path.read_text()
        assert "SUPABASE_URL" in content
        assert "SUPABASE_KEY" in content

    def test_make_env_preserves_existing_values(self, mock_context):
        """Test that existing .env values are preserved."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        env_path = mock_context.frontend_path / ".env"

        # Create existing .env with a value
        env_path.write_text("NEXT_PUBLIC_SUPABASE_URL=https://existing.supabase.co\n")

        make.env(target="frontend", force=False)

        # Verify existing value was preserved (exact line should still be there)
        content = env_path.read_text()
        assert "NEXT_PUBLIC_SUPABASE_URL=https://existing.supabase.co" in content
        # Verify new variables were added
        assert "NEXT_PUBLIC_SUPABASE_KEY" in content

    def test_make_env_preserves_custom_variables(self, mock_context):
        """Test that custom variables not in template are preserved."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        env_path = mock_context.frontend_path / ".env"

        # Create existing .env with custom variables
        original_content = """# My custom config
CUSTOM_VAR=my-custom-value
MY_API_KEY=secret123
NEXT_PUBLIC_SUPABASE_URL=https://existing.supabase.co
"""
        env_path.write_text(original_content)

        make.env(target="frontend", force=False)

        # Verify all custom content is preserved
        content = env_path.read_text()
        assert "CUSTOM_VAR=my-custom-value" in content
        assert "MY_API_KEY=secret123" in content
        assert "# My custom config" in content
        # Verify new variables were added
        assert "NEXT_PUBLIC_SUPABASE_KEY" in content

    def test_make_env_force_overwrites_values(self, mock_context):
        """Test that --force overwrites existing values."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        env_path = mock_context.frontend_path / ".env"

        # Create existing .env with a value
        env_path.write_text("NEXT_PUBLIC_SUPABASE_URL=https://existing.supabase.co\n")

        make.env(target="frontend", force=True)

        # Verify value was overwritten with empty value
        content = env_path.read_text()
        assert "https://existing.supabase.co" not in content
        assert "NEXT_PUBLIC_SUPABASE_URL=\n" in content

    def test_make_env_auto_detect_frontend(self, mock_context):
        """Test auto-detection when in frontend directory."""
        mock_context.is_frontend = True
        mock_context.is_backend = False
        mock_context.has_backend = False

        env_path = mock_context.frontend_path / ".env"
        if env_path.exists():
            env_path.unlink()

        # Run without target - should auto-detect frontend
        make.env(target=None, force=False)

        assert env_path.exists()
        content = env_path.read_text()
        assert "NEXT_PUBLIC_SUPABASE_URL" in content

    def test_make_env_auto_detect_backend(self, mock_context):
        """Test auto-detection when in backend directory."""
        mock_context.is_frontend = False
        mock_context.is_backend = True
        mock_context.has_frontend = False

        env_path = mock_context.backend_path / ".env"
        if env_path.exists():
            env_path.unlink()

        # Run without target - should auto-detect backend
        make.env(target=None, force=False)

        assert env_path.exists()
        content = env_path.read_text()
        assert "SUPABASE_URL" in content

    def test_make_env_all_creates_both(self, mock_context):
        """Test creating both frontend and backend .env files."""
        fe_env_path = mock_context.frontend_path / ".env"
        be_env_path = mock_context.backend_path / ".env"

        # Ensure no .env files exist
        if fe_env_path.exists():
            fe_env_path.unlink()
        if be_env_path.exists():
            be_env_path.unlink()

        make.env(target="all", force=False)

        # Verify both files were created
        assert fe_env_path.exists()
        assert be_env_path.exists()

        # Verify correct content in each
        fe_content = fe_env_path.read_text()
        be_content = be_env_path.read_text()

        assert "NEXT_PUBLIC_SUPABASE_URL" in fe_content
        assert "SUPABASE_URL" in be_content

    def test_make_env_ambiguous_context_fails(self, mock_context):
        """Test that ambiguous context without target fails."""
        mock_context.is_frontend = False
        mock_context.is_backend = False

        # Run without target when both exist - should fail
        with pytest.raises(typer.Exit) as exc_info:
            make.env(target=None, force=False)

        assert exc_info.value.exit_code == 1

    def test_make_env_no_project_fails(self, mock_context):
        """Test that running without any project fails."""
        mock_context.is_frontend = False
        mock_context.is_backend = False
        mock_context.has_frontend = False
        mock_context.has_backend = False

        with pytest.raises(typer.Exit) as exc_info:
            make.env(target=None, force=False)

        assert exc_info.value.exit_code == 1

    def test_make_env_frontend_target_no_frontend_fails(self, mock_context):
        """Test that frontend target without frontend project fails."""
        mock_context.has_frontend = False

        with pytest.raises(typer.Exit) as exc_info:
            make.env(target="frontend", force=False)

        assert exc_info.value.exit_code == 1

    def test_make_env_backend_target_no_backend_fails(self, mock_context):
        """Test that backend target without backend project fails."""
        mock_context.has_backend = False

        with pytest.raises(typer.Exit) as exc_info:
            make.env(target="backend", force=False)

        assert exc_info.value.exit_code == 1

    def test_make_env_has_section_comments(self, mock_context):
        """Test that .env file has organized section comments."""
        mock_context.is_frontend = True
        mock_context.is_backend = False

        env_path = mock_context.frontend_path / ".env"
        if env_path.exists():
            env_path.unlink()

        make.env(target="frontend", force=False)

        content = env_path.read_text()
        assert "For Vercel Deployment" in content
        assert "For DevHand CLI Only" in content
        assert "For Testing" in content
