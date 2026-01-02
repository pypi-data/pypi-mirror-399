"""Tests for compliance violations commands."""

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


# Violations List Tests


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_list_success(mock_get_client):
    """Test listing compliance violations."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "v-123",
            "policy_id": "pol-456",
            "severity": "high",
            "status": "open",
            "resource_type": "aws_s3_bucket",
            "resource_id": "my-bucket",
        }
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "violations", "list"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_list_with_filters(mock_get_client):
    """Test listing violations with filters."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = []
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "violations",
                "list",
                "--scan-id",
                "scan-123",
                "--status",
                "open",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_list_json_output(mock_get_client):
    """Test listing violations with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [{"id": "v-123", "status": "open"}]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "violations", "list", "--output", "json"],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_list_empty(mock_get_client):
    """Test listing violations when none found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "violations", "list"])

        assert result.exit_code == 0
        assert "No violations found" in result.output


# Violations Show Tests


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_show_success(mock_get_client):
    """Test showing violation details."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "v-123",
        "policy_id": "pol-456",
        "severity": "high",
        "status": "open",
        "resource_type": "aws_s3_bucket",
        "resource_id": "my-bucket",
        "description": "Public access enabled",
        "remediation_guidance": "Disable public access",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "violations", "show", "v-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_show_json_output(mock_get_client):
    """Test showing violation with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "v-123", "status": "open"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "violations", "show", "v-123", "--output", "json"],
        )

        assert result.exit_code == 0


# Violations Update Tests


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_update_success(mock_get_client):
    """Test updating violation status."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "v-123",
        "status": "acknowledged",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_update") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "violations",
                "update",
                "550e8400-e29b-41d4-a716-446655440000",
                "--status",
                "acknowledged",
            ],
        )

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_update_with_comment(mock_get_client):
    """Test updating violation with comment."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "v-123", "status": "resolved"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_update") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "violations",
                "update",
                "550e8400-e29b-41d4-a716-446655440000",
                "--status",
                "resolved",
                "--comment",
                "Fixed by upgrading",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.violations.get_retry_client")
def test_violations_update_with_remediation(mock_get_client):
    """Test updating violation with remediation creation."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "v-123",
        "status": "acknowledged",
        "remediation_id": "rem-456",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.violations.api_update") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "violations",
                "update",
                "550e8400-e29b-41d4-a716-446655440000",
                "--status",
                "acknowledged",
                "--create-remediation",
                "--remediation-type",
                "MANUAL",
            ],
        )

        assert result.exit_code == 0
