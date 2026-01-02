"""Tests for stack remediation commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestRemediationPlan:
    """Tests for remediation plan command."""

    @patch("iltero.commands.stack.remediation.get_retry_client")
    @patch("iltero.commands.stack.remediation.api_plan")
    def test_plan_success(self, mock_api, mock_get_client):
        """Test creating remediation plan."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "plan": {
                "id": "plan-1",
                "stack_id": "stack-1",
                "status": "created",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            [
                "remediation",
                "plan",
                "stack-1",
                "--validation",
                "val-1",
            ],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.remediation.get_retry_client")
    def test_plan_error(self, mock_get_client):
        """Test plan handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            [
                "remediation",
                "plan",
                "stack-1",
                "--validation",
                "val-1",
            ],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRemediationApply:
    """Tests for remediation apply command."""

    @patch("iltero.commands.stack.remediation.get_retry_client")
    @patch("iltero.commands.stack.remediation.api_apply")
    def test_apply_success(self, mock_api, mock_get_client):
        """Test applying remediation."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "remediation": {
                "id": "remediation-1",
                "plan_id": "plan-1",
                "status": "applying",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["remediation", "apply", "stack-1", "--plan", "plan-1", "--force"],
        )

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.remediation.get_retry_client")
    def test_apply_error(self, mock_get_client):
        """Test apply handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            ["remediation", "apply", "stack-1", "--plan", "plan-1", "--force"],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRemediationStatus:
    """Tests for remediation status command."""

    @patch("iltero.commands.stack.remediation.get_retry_client")
    @patch("iltero.commands.stack.remediation.api_status")
    def test_status_success(self, mock_api, mock_get_client):
        """Test getting remediation status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "status": {
                "stack_id": "stack-1",
                "status": "completed",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["remediation", "status", "stack-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.remediation.get_retry_client")
    def test_status_error(self, mock_get_client):
        """Test status handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["remediation", "status", "stack-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRemediationHistory:
    """Tests for remediation history command."""

    @patch("iltero.commands.stack.remediation.get_retry_client")
    @patch("iltero.commands.stack.remediation.api_history")
    def test_history_success(self, mock_api, mock_get_client):
        """Test getting remediation history."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "remediations": [
                {
                    "id": "remediation-1",
                    "stack_id": "stack-1",
                    "status": "completed",
                }
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["remediation", "history", "stack-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.remediation.get_retry_client")
    @patch("iltero.commands.stack.remediation.api_history")
    def test_history_empty(self, mock_api, mock_get_client):
        """Test history when none exists."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"remediations": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["remediation", "history", "stack-1"])

        assert result.exit_code == 0

    @patch("iltero.commands.stack.remediation.get_retry_client")
    def test_history_error(self, mock_get_client):
        """Test history handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["remediation", "history", "stack-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output
