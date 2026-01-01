"""Tests for prompt utility functions."""

from unittest.mock import patch

from dh.utils.prompts import prompt_email, prompt_text


class TestPromptText:
    """Test suite for text prompting."""

    @patch("dh.utils.prompts.Prompt.ask")
    def test_prompt_text_with_password(self, mock_ask):
        """Test prompt_text with password=True for sensitive input."""
        mock_ask.return_value = "secret123"

        result = prompt_text("Enter password", password=True)

        # Should pass password flag to Rich Prompt
        assert result == "secret123"
        mock_ask.assert_called_once()
        call_kwargs = mock_ask.call_args.kwargs
        assert call_kwargs["password"] is True

    @patch("dh.utils.prompts.Prompt.ask")
    def test_prompt_text_with_default(self, mock_ask):
        """Test prompt_text with default value."""
        mock_ask.return_value = "default_val"

        result = prompt_text("Enter value", default="default_val")

        # Should pass default to Rich Prompt
        assert result == "default_val"
        mock_ask.assert_called_once()
        call_kwargs = mock_ask.call_args.kwargs
        assert call_kwargs["default"] == "default_val"


class TestPromptEmail:
    """Test suite for email prompt validation."""

    @patch("dh.utils.prompts.prompt_text")
    def test_prompt_email_with_invalid_then_valid(self, mock_prompt_text):
        """Test prompt_email retries on invalid format."""
        # First call returns invalid, second returns valid
        mock_prompt_text.side_effect = [
            "not-an-email",
            "valid@example.com",
        ]

        result = prompt_email()

        # Should retry and return valid email
        assert result == "valid@example.com"
        assert mock_prompt_text.call_count == 2

    @patch("dh.utils.prompts.prompt_text")
    def test_prompt_email_with_valid_first_try(self, mock_prompt_text):
        """Test prompt_email accepts valid email immediately."""
        mock_prompt_text.return_value = "user@domain.com"

        result = prompt_email()

        # Should accept immediately
        assert result == "user@domain.com"
        assert mock_prompt_text.call_count == 1
