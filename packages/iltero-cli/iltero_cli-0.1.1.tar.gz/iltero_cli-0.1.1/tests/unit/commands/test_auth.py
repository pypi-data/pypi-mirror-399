"""Tests for auth token commands."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from iltero.cli import app
from iltero.core.exceptions import AuthenticationError

runner = CliRunner()


class TestSetTokenCommand:
    """Tests for `iltero auth set-token` command."""

    def test_set_token_with_option(self):
        """Test setting token via --token option."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "set-token", "--token", "itk_p_test123"])

            assert result.exit_code == 0
            mock_auth.set_token.assert_called_once_with("itk_p_test123")
            assert "Token stored successfully" in result.output

    def test_set_token_with_prompt(self):
        """Test setting token via interactive prompt."""
        with (
            patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth,
            patch("iltero.commands.auth.tokens.Prompt.ask") as mock_prompt,
        ):
            mock_auth = MagicMock()
            mock_get_auth.return_value = mock_auth
            mock_prompt.return_value = "itk_u_prompt_token"

            result = runner.invoke(app, ["auth", "set-token"])

            assert result.exit_code == 0
            mock_auth.set_token.assert_called_once_with("itk_u_prompt_token")


class TestShowTokenCommand:
    """Tests for `iltero auth show-token` command."""

    def test_show_token_masked(self):
        """Test showing masked token."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_auth.get_token.return_value = "itk_p_1234567890abcdef"
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "show-token"])

            assert result.exit_code == 0
            # Should show first and last 8 chars
            assert "itk_p_12" in result.output
            assert "90abcdef" in result.output
            assert "..." in result.output

    def test_show_token_revealed(self):
        """Test showing full token with --reveal."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_auth.get_token.return_value = "itk_p_fulltoken123"
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "show-token", "--reveal"])

            assert result.exit_code == 0
            assert "itk_p_fulltoken123" in result.output

    def test_show_token_not_found(self):
        """Test showing token when not configured."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_auth.get_token.side_effect = AuthenticationError("No API token found")
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "show-token"])

            assert "No token found" in result.output


class TestClearTokenCommand:
    """Tests for `iltero auth clear-token` command."""

    def test_clear_token_with_confirmation(self):
        """Test clearing token with --yes flag."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "clear-token", "--yes"])

            assert result.exit_code == 0
            mock_auth.clear_token.assert_called_once()
            assert "Token cleared" in result.output

    def test_clear_token_cancelled(self):
        """Test cancelling token clear."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "clear-token"], input="n\n")

            assert result.exit_code == 0
            mock_auth.clear_token.assert_not_called()
            assert "cancelled" in result.output.lower()

    def test_clear_token_confirmed_interactively(self):
        """Test clearing token with interactive confirmation."""
        with patch("iltero.commands.auth.tokens.get_auth") as mock_get_auth:
            mock_auth = MagicMock()
            mock_get_auth.return_value = mock_auth

            result = runner.invoke(app, ["auth", "clear-token"], input="y\n")

            assert result.exit_code == 0
            mock_auth.clear_token.assert_called_once()
