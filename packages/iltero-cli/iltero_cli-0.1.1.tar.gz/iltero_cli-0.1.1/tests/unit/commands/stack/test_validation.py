"""Tests for stack validation commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestValidationStatus:
    """Tests for validation status command."""

    @patch("iltero.commands.stack.validation.get_retry_client")
    @patch("iltero.commands.stack.validation.api_status")
    def test_status_success(self, mock_api, mock_get_client):
        """Test getting compliance status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "status": {
                "stack_id": "stack-1",
                "overall_status": "compliant",
                "violations": [],
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["validation", "status", "stack-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.validation.get_retry_client")
    @patch("iltero.commands.stack.validation.api_status")
    def test_status_with_violations(self, mock_api, mock_get_client):
        """Test compliance status with violations."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "status": {
                "stack_id": "stack-1",
                "overall_status": "non-compliant",
                "violations": [
                    {"policy": "encryption-required", "severity": "high"},
                ],
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["validation", "status", "stack-1"])

        assert result.exit_code == 0

    @patch("iltero.commands.stack.validation.get_retry_client")
    def test_status_error(self, mock_get_client):
        """Test status handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["validation", "status", "stack-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestValidationPostDeployment:
    """Tests for validation post-deployment command."""

    @patch("iltero.commands.stack.validation.get_retry_client")
    @patch("iltero.commands.stack.validation.api_post")
    def test_post_deployment_success(self, mock_api, mock_get_client):
        """Test post-deployment validation."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "validation": {
                "stack_id": "stack-1",
                "run_id": "run-1",
                "passed": True,
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["validation", "post-deployment", "stack-1"],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.validation.get_retry_client")
    @patch("iltero.commands.stack.validation.api_post")
    def test_post_deployment_failed(self, mock_api, mock_get_client):
        """Test post-deployment validation with failures."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "validation": {
                "stack_id": "stack-1",
                "passed": False,
                "failures": [{"check": "security-groups", "error": "Open to world"}],
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["validation", "post-deployment", "stack-1"],
        )

        assert result.exit_code == 0

    @patch("iltero.commands.stack.validation.get_retry_client")
    def test_post_deployment_error(self, mock_get_client):
        """Test post-deployment handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            ["validation", "post-deployment", "stack-1"],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output
