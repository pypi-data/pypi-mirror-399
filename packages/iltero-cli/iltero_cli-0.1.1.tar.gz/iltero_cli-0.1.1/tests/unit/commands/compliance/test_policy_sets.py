"""Tests for compliance policy sets commands."""

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


# Policy Sets List Tests


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_list_success(mock_get_client):
    """Test listing compliance policy sets."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "ps-123",
            "name": "AWS Security Best Practices",
            "source_type": "builtin",
            "policy_count": 50,
            "active": True,
        }
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy-sets", "list"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_list_with_filters(mock_get_client):
    """Test listing policy sets with filters."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = []
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "policy-sets",
                "list",
                "--source-type",
                "builtin",
                "--active",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_list_json_output(mock_get_client):
    """Test listing policy sets with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [{"id": "ps-123", "name": "Test Set"}]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "policy-sets", "list", "--output", "json"],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_list_empty(mock_get_client):
    """Test listing policy sets when none found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy-sets", "list"])

        assert result.exit_code == 0
        assert "No policy sets found" in result.output


# Policy Sets Show Tests


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_show_success(mock_get_client):
    """Test showing policy set details."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "ps-123",
        "name": "AWS Security Best Practices",
        "source_type": "builtin",
        "active": True,
        "policy_count": 50,
        "description": "Comprehensive AWS security checks",
        "compliance_frameworks": ["hipaa", "soc2", "pci-dss"],
        "policies": [
            {"id": "pol-1", "name": "S3 Encryption", "severity": "high"},
        ],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "policy-sets", "show", "ps-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_show_json_output(mock_get_client):
    """Test showing policy set with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "ps-123", "name": "Test Set"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "policy-sets",
                "show",
                "ps-123",
                "--output",
                "json",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.policy_sets.get_retry_client")
def test_policy_sets_list_inactive(mock_get_client):
    """Test listing inactive policy sets."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [{"id": "ps-456", "name": "Deprecated Set", "active": False}]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.policy_sets.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "policy-sets", "list", "--inactive"],
        )

        assert result.exit_code == 0
