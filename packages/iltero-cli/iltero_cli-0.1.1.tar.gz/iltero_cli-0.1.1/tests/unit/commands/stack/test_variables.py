"""Tests for stack variables commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestStackVariablesList:
    """Tests for stack variables list command."""

    @patch("iltero.commands.stack.variables.get_retry_client")
    @patch("iltero.commands.stack.variables.api_list")
    def test_list_variables_success(self, mock_api, mock_get_client) -> None:
        """Test listing stack variables."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "variables": [
                {
                    "key": "AWS_REGION",
                    "value": "us-east-1",
                    "category": "env",
                    "sensitive": False,
                    "description": "AWS region",
                },
                {
                    "key": "DB_PASSWORD",
                    "value": "secret123",
                    "category": "secret",
                    "sensitive": True,
                    "description": "Database password",
                },
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["variables", "list", "stack-123"])

        assert result.exit_code == 0
        assert "AWS_REGION" in result.output
        assert "us-east-1" in result.output
        assert "DB_PASSWORD" in result.output
        # Secret should be masked
        assert "secret123" not in result.output
        assert "********" in result.output

    @patch("iltero.commands.stack.variables.get_retry_client")
    @patch("iltero.commands.stack.variables.api_list")
    def test_list_variables_show_secrets(self, mock_api, mock_get_client) -> None:
        """Test listing variables with --show-secrets flag."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "variables": [
                {
                    "key": "API_KEY",
                    "value": "super-secret-key",
                    "category": "secret",
                    "sensitive": True,
                },
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["variables", "list", "stack-123", "--show-secrets"],
        )

        assert result.exit_code == 0
        assert "API_KEY" in result.output
        assert "super-secret-key" in result.output

    @patch("iltero.commands.stack.variables.get_retry_client")
    @patch("iltero.commands.stack.variables.api_list")
    def test_list_variables_empty(self, mock_api, mock_get_client) -> None:
        """Test listing when no variables exist."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"variables": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["variables", "list", "stack-123"])

        assert result.exit_code == 0
        assert "No variables found" in result.output

    @patch("iltero.commands.stack.variables.get_retry_client")
    @patch("iltero.commands.stack.variables.api_list")
    def test_list_variables_pagination(self, mock_api, mock_get_client) -> None:
        """Test pagination of variables."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        # Create 25 variables
        variables = [
            {
                "key": f"VAR_{i}",
                "value": f"value_{i}",
                "category": "env",
                "sensitive": False,
            }
            for i in range(25)
        ]
        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"variables": variables}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        # First page
        result = runner.invoke(
            app,
            ["variables", "list", "stack-123", "--per-page", "10"],
        )

        assert result.exit_code == 0
        assert "1-10" in result.output
        assert "25" in result.output
        assert "page 1/3" in result.output

    @patch("iltero.commands.stack.variables.get_retry_client")
    @patch("iltero.commands.stack.variables.api_list")
    def test_list_variables_filter_category(self, mock_api, mock_get_client) -> None:
        """Test filtering by category."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "variables": [
                {"key": "VAR1", "value": "v1", "category": "env"},
                {"key": "VAR2", "value": "v2", "category": "terraform"},
                {"key": "VAR3", "value": "v3", "category": "env"},
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["variables", "list", "stack-123", "--category", "terraform"],
        )

        assert result.exit_code == 0
        assert "VAR2" in result.output
        # VAR1 and VAR3 should not be shown
        assert "VAR1" not in result.output
        assert "VAR3" not in result.output

    @patch("iltero.commands.stack.variables.get_retry_client")
    def test_list_variables_error(self, mock_get_client) -> None:
        """Test error handling."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("API error")

        result = runner.invoke(app, ["variables", "list", "stack-123"])

        assert result.exit_code == 1
        assert "Failed to list variables" in result.output
