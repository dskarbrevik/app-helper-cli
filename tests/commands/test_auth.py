"""Tests for authentication commands."""

from unittest.mock import MagicMock, patch

import pytest
import typer

from dh.commands import auth


class TestAuthTokenCommand:
    """Test suite for the auth token command."""

    def test_auth_token_success(self, mock_context):
        """Test successful token retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-jwt-token-12345",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
        }

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.return_value = mock_response

            # Should complete without error
            auth.token(
                email="test@example.com",
                password="password123",
                export=False,
            )

            # Verify the request was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "auth/v1/token" in call_args[0][0]
            assert call_args[1]["json"]["email"] == "test@example.com"
            assert call_args[1]["json"]["password"] == "password123"

    def test_auth_token_export_mode(self, mock_context, capsys):
        """Test token export mode prints export command."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-jwt-token-12345",
            "refresh_token": "test-refresh-token",
            "expires_in": 3600,
        }

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.return_value = mock_response

            auth.token(
                email="test@example.com",
                password="password123",
                export=True,
            )

            # Check that export command was printed
            captured = capsys.readouterr()
            assert "export SUPABASE_ACCESS_TOKEN_JWT=" in captured.out
            assert "test-jwt-token-12345" in captured.out

    def test_auth_token_invalid_credentials(self, mock_context):
        """Test token request with invalid credentials."""
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.return_value = mock_response

            with pytest.raises(typer.Exit):
                auth.token(
                    email="test@example.com",
                    password="wrong-password",
                    export=False,
                )

    def test_auth_token_bad_request(self, mock_context):
        """Test token request with bad request response."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Invalid login credentials",
        }

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.return_value = mock_response

            with pytest.raises(typer.Exit):
                auth.token(
                    email="test@example.com",
                    password="password123",
                    export=False,
                )

    def test_auth_token_no_supabase_url(self, tmp_path, monkeypatch):
        """Test token request when Supabase URL is not configured."""
        from dh.utils.config import Config, DatabaseConfig

        class MockContextNoConfig:
            def __init__(self):
                self.workspace_root = tmp_path
                self.frontend_path = tmp_path / "fe"
                self.backend_path = tmp_path / "be"
                self.has_frontend = True
                self.has_backend = True
                self.config = Config(db=DatabaseConfig())  # Empty config

        monkeypatch.setattr(
            "dh.commands.auth.get_context", lambda: MockContextNoConfig()
        )

        with pytest.raises(typer.Exit):
            auth.token(
                email="test@example.com",
                password="password123",
                export=False,
            )

    def test_auth_token_uses_env_vars(self, mock_context):
        """Test that token command uses environment variables."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test-jwt-token",
            "expires_in": 3600,
        }

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.return_value = mock_response
            with patch.dict(
                "os.environ",
                {
                    "SUPABASE_TEST_EMAIL": "env@example.com",
                    "SUPABASE_TEST_PASSWORD": "env-password",
                },
            ):
                # Call without explicit email/password
                auth.token(email=None, password=None, export=False)

                # Verify env vars were used
                call_args = mock_post.call_args
                assert call_args[1]["json"]["email"] == "env@example.com"
                assert call_args[1]["json"]["password"] == "env-password"

    def test_auth_token_connection_error(self, mock_context):
        """Test token request when connection fails."""
        import requests

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError()

            with pytest.raises(typer.Exit):
                auth.token(
                    email="test@example.com",
                    password="password123",
                    export=False,
                )

    def test_auth_token_timeout(self, mock_context):
        """Test token request when request times out."""
        import requests

        with patch("dh.commands.auth.requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()

            with pytest.raises(typer.Exit):
                auth.token(
                    email="test@example.com",
                    password="password123",
                    export=False,
                )
