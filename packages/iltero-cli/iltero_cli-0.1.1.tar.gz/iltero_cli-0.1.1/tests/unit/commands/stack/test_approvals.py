"""Tests for stack approvals commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestApprovalsList:
    """Tests for approvals list command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_list")
    def test_list_pending_approvals_success(self, mock_api, mock_get_client):
        """Test listing pending approvals successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "approvals": [
                {
                    "id": "approval-1",
                    "stack_id": "stack-1",
                    "status": "pending",
                    "requester": "user@example.com",
                    "created_at": "2024-01-01T00:00:00Z",
                },
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "list"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_list")
    def test_list_approvals_empty(self, mock_api, mock_get_client):
        """Test listing approvals when none pending."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"approvals": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "list"])

        assert result.exit_code == 0
        assert "No pending approvals" in result.output

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_list_approvals_error(self, mock_get_client):
        """Test list approvals handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Auth failed")

        result = runner.invoke(app, ["approvals", "list"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsShow:
    """Tests for approvals show command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_get")
    def test_show_approval_success(self, mock_api, mock_get_client):
        """Test showing approval details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "approval": {
                "id": "approval-1",
                "stack_id": "stack-1",
                "status": "pending",
                "requester": "user@example.com",
                "created_at": "2024-01-01T00:00:00Z",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "show", "approval-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_show_approval_error(self, mock_get_client):
        """Test show approval handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Not found")

        result = runner.invoke(app, ["approvals", "show", "nonexistent"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsRequest:
    """Tests for approvals request command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_request")
    def test_request_approval_success(self, mock_api, mock_get_client):
        """Test requesting deployment approval."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "approval": {
                "id": "approval-new",
                "stack_id": "stack-1",
                "status": "pending",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["approvals", "request", "run-123"],
        )

        assert result.exit_code == 0
        assert "Approval requested" in result.output

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_request_approval_error(self, mock_get_client):
        """Test request approval handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            ["approvals", "request", "run-123"],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsApprove:
    """Tests for approvals approve command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_approve")
    def test_approve_success(self, mock_api, mock_get_client):
        """Test approving deployment."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"approval": {"id": "approval-1", "status": "approved"}}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["approvals", "approve", "approval-1"],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_approve_error(self, mock_get_client):
        """Test approve handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Not authorized")

        result = runner.invoke(app, ["approvals", "approve", "approval-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsReject:
    """Tests for approvals reject command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_reject")
    def test_reject_success(self, mock_api, mock_get_client):
        """Test rejecting deployment."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"approval": {"id": "approval-1", "status": "rejected"}}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["approvals", "reject", "approval-1", "--comment", "Security concerns"],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_reject_error(self, mock_get_client):
        """Test reject handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Not authorized")

        result = runner.invoke(
            app,
            ["approvals", "reject", "approval-1", "--comment", "Issues"],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsCancel:
    """Tests for approvals cancel command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_cancel")
    def test_cancel_success(self, mock_api, mock_get_client):
        """Test canceling approval request."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"approval": {"id": "approval-1", "status": "cancelled"}}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "cancel", "approval-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_cancel_error(self, mock_get_client):
        """Test cancel handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Cannot cancel")

        result = runner.invoke(app, ["approvals", "cancel", "approval-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsCompliance:
    """Tests for approvals compliance command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_compliance")
    def test_compliance_success(self, mock_api, mock_get_client):
        """Test getting compliance analysis."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "analysis": {
                "approval_id": "approval-1",
                "compliant": True,
                "violations": [],
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "compliance", "run-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_compliance_error(self, mock_get_client):
        """Test compliance handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Not found")

        result = runner.invoke(app, ["approvals", "compliance", "run-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsRun:
    """Tests for approvals run command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_run")
    def test_run_approval_success(self, mock_api, mock_get_client):
        """Test getting run approval."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "approval": {
                "run_id": "run-1",
                "approval_required": True,
                "status": "pending",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "run", "run-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_run_approval_error(self, mock_get_client):
        """Test run approval handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Not found")

        result = runner.invoke(app, ["approvals", "run", "run-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestApprovalsExpired:
    """Tests for approvals expired command."""

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_expired")
    def test_check_expired_success(self, mock_api, mock_get_client):
        """Test checking expired approvals."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "expired_approvals": [{"id": "approval-1", "expired_at": "2024-01-01T00:00:00Z"}]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "expired"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.approvals.get_retry_client")
    @patch("iltero.commands.stack.approvals.api_expired")
    def test_check_expired_none(self, mock_api, mock_get_client):
        """Test checking when no expired approvals."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"expired_approvals": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["approvals", "expired"])

        assert result.exit_code == 0

    @patch("iltero.commands.stack.approvals.get_retry_client")
    def test_check_expired_error(self, mock_get_client):
        """Test expired check handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["approvals", "expired"])

        assert result.exit_code == 1
        assert "Failed" in result.output
