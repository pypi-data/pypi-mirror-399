"""Tests for stack exceptions commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestExceptionsRequest:
    """Tests for exceptions request command."""

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_request")
    def test_request_exception_success(self, mock_api, mock_get_client):
        """Test requesting policy exception."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "exception": {
                "id": "exception-1",
                "stack_id": "stack-1",
                "policy_id": "policy-1",
                "status": "pending",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            [
                "exceptions",
                "request",
                "stack-1",
                "--scope",
                "rule-1,rule-2",
                "--reason",
                "Temporary exemption needed",
                "--mitigation",
                "Additional monitoring",
            ],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    def test_request_exception_error(self, mock_get_client):
        """Test request exception handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            [
                "exceptions",
                "request",
                "stack-1",
                "--scope",
                "rule-1",
                "--reason",
                "Test",
                "--mitigation",
                "Monitoring",
            ],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestExceptionsApprove:
    """Tests for exceptions approve command."""

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_approve")
    def test_approve_exception_success(self, mock_api, mock_get_client):
        """Test approving policy exception."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "exception": {
                "id": "exception-1",
                "status": "approved",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            [
                "exceptions",
                "approve",
                "exc-ref-1",
                "--approver",
                "infosec-1",
                "--expiry",
                "2024-12-31",
            ],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    def test_approve_exception_error(self, mock_get_client):
        """Test approve exception handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Not authorized")

        result = runner.invoke(
            app,
            [
                "exceptions",
                "approve",
                "exc-ref-1",
                "--approver",
                "infosec-1",
                "--expiry",
                "2024-12-31",
            ],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestExceptionsList:
    """Tests for exceptions list command."""

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_active")
    def test_list_exceptions_success(self, mock_api, mock_get_client):
        """Test listing active exceptions."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "exceptions": [
                {
                    "id": "exception-1",
                    "stack_id": "stack-1",
                    "policy_id": "policy-1",
                    "status": "active",
                }
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["exceptions", "list"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_active")
    def test_list_exceptions_empty(self, mock_api, mock_get_client):
        """Test listing exceptions when none active."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"exceptions": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["exceptions", "list"])

        assert result.exit_code == 0

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    def test_list_exceptions_error(self, mock_get_client):
        """Test list exceptions handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["exceptions", "list"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestExceptionsExpiring:
    """Tests for exceptions expiring command."""

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_expiring")
    def test_expiring_success(self, mock_api, mock_get_client):
        """Test listing expiring exceptions."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "exceptions": [
                {
                    "id": "exception-1",
                    "expires_at": "2024-01-15T00:00:00Z",
                }
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["exceptions", "expiring"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_expiring")
    def test_expiring_none(self, mock_api, mock_get_client):
        """Test expiring when none expiring soon."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"exceptions": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["exceptions", "expiring"])

        assert result.exit_code == 0

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    def test_expiring_error(self, mock_get_client):
        """Test expiring handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["exceptions", "expiring"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestExceptionsRevoke:
    """Tests for exceptions revoke command."""

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    @patch("iltero.commands.stack.exceptions.api_revoke")
    def test_revoke_success(self, mock_api, mock_get_client):
        """Test revoking exception."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "exception": {
                "id": "exception-1",
                "status": "revoked",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            [
                "exceptions",
                "revoke",
                "stack-1",
                "--reason",
                "No longer needed",
            ],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.exceptions.get_retry_client")
    def test_revoke_error(self, mock_get_client):
        """Test revoke handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            ["exceptions", "revoke", "stack-1", "--reason", "Test"],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output
