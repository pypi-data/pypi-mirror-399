"""Tests for stack drift commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestDriftSchedule:
    """Tests for drift schedule command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_schedule")
    def test_schedule_drift_success(self, mock_api, mock_get_client):
        """Test scheduling drift detection."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "detection": {
                "id": "detection-1",
                "stack_id": "stack-1",
                "status": "scheduled",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "schedule", "stack-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_schedule_drift_error(self, mock_get_client):
        """Test schedule drift handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "schedule", "stack-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestDriftStart:
    """Tests for drift start command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_start")
    def test_start_drift_success(self, mock_api, mock_get_client):
        """Test starting drift detection."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "detection": {
                "id": "detection-1",
                "status": "running",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "start", "detection-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_start_drift_error(self, mock_get_client):
        """Test start drift handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "start", "detection-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestDriftShow:
    """Tests for drift show command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_get")
    def test_show_drift_success(self, mock_api, mock_get_client):
        """Test showing drift detection details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "detection": {
                "id": "detection-1",
                "stack_id": "stack-1",
                "status": "completed",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "show", "detection-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_show_drift_error(self, mock_get_client):
        """Test show drift handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "show", "detection-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestDriftLatest:
    """Tests for drift latest command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_latest")
    def test_latest_drift_success(self, mock_api, mock_get_client):
        """Test getting latest drift detection."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "detection": {
                "id": "detection-latest",
                "stack_id": "stack-1",
                "status": "completed",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "latest", "stack-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_latest_drift_error(self, mock_get_client):
        """Test latest drift handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "latest", "stack-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestDriftPending:
    """Tests for drift pending command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_pending")
    def test_pending_success(self, mock_api, mock_get_client):
        """Test listing pending drift detections."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "detections": [{"id": "detection-1", "stack_id": "stack-1", "status": "pending"}]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "pending"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_pending")
    def test_pending_empty(self, mock_api, mock_get_client):
        """Test listing pending detections when none exist."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"detections": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "pending"])

        assert result.exit_code == 0

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_pending_error(self, mock_get_client):
        """Test pending handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "pending"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestDriftRemediated:
    """Tests for drift remediated command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_remediated")
    def test_remediated_success(self, mock_api, mock_get_client):
        """Test marking drift as remediated."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "detection": {
                "id": "detection-1",
                "status": "remediated",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "remediated", "detection-1", "--run", "run-123"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_remediated_error(self, mock_get_client):
        """Test remediated handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "remediated", "detection-1", "--run", "run-123"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestDriftPeriodic:
    """Tests for drift periodic command."""

    @patch("iltero.commands.stack.drift.get_retry_client")
    @patch("iltero.commands.stack.drift.api_periodic")
    def test_periodic_success(self, mock_api, mock_get_client):
        """Test scheduling periodic drift detection."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "schedule": {
                "stack_id": "stack-1",
                "interval": "daily",
                "enabled": True,
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["drift", "periodic", "stack-1", "--interval", "24"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.drift.get_retry_client")
    def test_periodic_error(self, mock_get_client):
        """Test periodic handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["drift", "periodic", "stack-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output
