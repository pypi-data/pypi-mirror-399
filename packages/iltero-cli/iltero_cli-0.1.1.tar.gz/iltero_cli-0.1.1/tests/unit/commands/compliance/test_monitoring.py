"""Tests for compliance monitoring commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


def setup_mock_client(mock_get_client):
    """Setup mock client for compliance tests."""
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_auth_client = Mock()
    mock_client.get_authenticated_client.return_value = mock_auth_client
    return mock_client, mock_auth_client


# Status Tests


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_status_success(mock_get_client):
    """Test getting monitoring status."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "monitoring": {
            "enabled": True,
            "stack_id": "stack-456",
            "last_check": "2025-01-01T00:00:00Z",
            "check_interval": "1h",
            "active_alerts": 2,
            "total_checks": 100,
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_status") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "status", "stack-456"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_status_disabled(mock_get_client):
    """Test status when monitoring is disabled."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"monitoring": {"enabled": False, "stack_id": "stack-456"}}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_status") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "status", "stack-456"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_status_with_monitors(mock_get_client):
    """Test status with configured monitors."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "monitoring": {
            "enabled": True,
            "monitors": [
                {"type": "drift", "status": "active", "last_run": "1h ago"},
                {"type": "policy", "status": "paused", "last_run": "2h ago"},
            ],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_status") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "status", "stack-456"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_status_empty(mock_get_client):
    """Test status when no data available."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_status") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "status", "stack-456"])

        assert result.exit_code == 0


# Alerts Tests


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_alerts_success(mock_get_client):
    """Test getting compliance alerts."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "alerts": [
            {
                "id": "alert-123",
                "severity": "high",
                "type": "drift",
                "message": "Configuration drift detected",
                "created_at": "2025-01-01T00:00:00Z",
            }
        ]
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_alerts") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "alerts", "stack-456"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_alerts_empty(mock_get_client):
    """Test alerts when none exist."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"alerts": []}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_alerts") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "alerts", "stack-456"])

        assert result.exit_code == 0
        assert "No" in result.output and "alerts" in result.output


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_alerts_with_status_filter(mock_get_client):
    """Test alerts with status filter."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"alerts": []}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_alerts") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "monitoring",
                "alerts",
                "stack-456",
                "--status",
                "RESOLVED",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_alerts_long_message(mock_get_client):
    """Test alerts with long message truncation."""
    mock_client, _ = setup_mock_client(mock_get_client)

    long_message = "A" * 100  # Very long message
    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "alerts": [
            {
                "id": "alert-123",
                "severity": "medium",
                "type": "policy",
                "message": long_message,
                "created_at": "2025-01-01T00:00:00Z",
            }
        ]
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_alerts") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "monitoring", "alerts", "stack-456"])

        assert result.exit_code == 0


# Acknowledge Tests


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_ack_success(mock_get_client):
    """Test acknowledging an alert."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"acknowledged": True}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_ack") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "monitoring",
                "ack",
                "stack-456",
                "alert-123",
            ],
        )

        assert result.exit_code == 0
        assert "acknowledged" in result.output


@patch("iltero.commands.compliance.monitoring.get_retry_client")
def test_monitoring_ack_with_options(mock_get_client):
    """Test acknowledging with note and action."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"acknowledged": True}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.monitoring.api_ack") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "monitoring",
                "ack",
                "stack-456",
                "alert-123",
                "--note",
                "Investigating issue",
                "--action",
                "Will fix config",
                "--assign",
                "user-789",
            ],
        )

        assert result.exit_code == 0
        assert "acknowledged" in result.output
        assert "Investigating" in result.output
        assert "fix config" in result.output
        assert "user-789" in result.output
