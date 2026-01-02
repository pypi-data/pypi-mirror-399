"""Tests for compliance policy commands."""

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


# Policy List Tests


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_list_success(mock_get_client):
    """Test listing compliance policies."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "pol-123",
            "name": "S3 Encryption Policy",
            "severity": "high",
            "rule_id": "CKV_AWS_19",
            "policy_set_id": "ps-456",
            "active": True,
        }
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy", "list"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_list_with_filters(mock_get_client):
    """Test listing policies with filters."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = []
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "policy",
                "list",
                "--severity",
                "high",
                "--policy-set-id",
                "ps-456",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_list_json_output(mock_get_client):
    """Test listing policies with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [{"id": "pol-123", "name": "Test Policy"}]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "policy", "list", "--output", "json"],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_list_empty(mock_get_client):
    """Test listing policies when none found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy", "list"])

        assert result.exit_code == 0
        assert "No policies found" in result.output


# Policy Show Tests


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_show_success(mock_get_client):
    """Test showing policy details."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "pol-123",
        "name": "S3 Encryption Policy",
        "rule_id": "CKV_AWS_19",
        "severity": "high",
        "policy_set_id": "ps-456",
        "active": True,
        "description": "Ensure S3 buckets have encryption enabled",
        "compliance_frameworks": ["hipaa", "soc2"],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy", "show", "pol-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_show_json_output(mock_get_client):
    """Test showing policy with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "pol-123", "name": "Test Policy"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "policy", "show", "pol-123", "--output", "json"],
        )

        assert result.exit_code == 0


# Policy Violations Tests


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_violations_success(mock_get_client):
    """Test getting policy violation summary."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "policy_id": "pol-123",
        "total_violations": 5,
        "by_status": {"open": 3, "resolved": 2},
        "by_severity": {"high": 2, "medium": 3},
        "violations": [
            {"id": "v-1", "resource_id": "bucket-1", "status": "open"},
        ],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_violations") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy", "violations", "pol-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.policy.get_retry_client")
def test_policy_violations_json_output(mock_get_client):
    """Test getting policy violations with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"policy_id": "pol-123", "total_violations": 0}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy.api_violations") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "policy",
                "violations",
                "pol-123",
                "--output",
                "json",
            ],
        )

        assert result.exit_code == 0
