"""Tests for compliance remediation commands."""

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


# Remediation List Tests


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_list_success(mock_get_client):
    """Test listing remediations."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "rem-123",
            "violation_id": "vio-456",
            "action_type": "AUTOMATIC",
            "status": "pending",
            "created_at": "2025-01-01T00:00:00Z",
        }
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "remediation", "list"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_list_with_filters(mock_get_client):
    """Test listing remediations with filters."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = []
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "remediation",
                "list",
                "--violation-id",
                "vio-456",
                "--status",
                "pending",
                "--type",
                "AUTOMATIC",
                "--limit",
                "50",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_list_json_output(mock_get_client):
    """Test listing remediations with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [{"id": "rem-123", "status": "pending"}]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "remediation", "list", "--output", "json"],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_list_empty(mock_get_client):
    """Test listing remediations when none found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "remediation", "list"])

        assert result.exit_code == 0
        assert "No remediations found" in result.stdout


# Remediation Show Tests


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_show_success(mock_get_client):
    """Test showing remediation details."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "rem-123",
        "violation_id": "vio-456",
        "action_type": "AUTOMATIC",
        "status": "completed",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:05:00Z",
        "executed_at": "2025-01-01T00:05:00Z",
        "details": "Apply S3 encryption fix",
        "result": "Successfully applied encryption",
        "affected_resources": ["s3://bucket-1", "s3://bucket-2"],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "remediation", "show", "rem-123"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_show_json_output(mock_get_client):
    """Test showing remediation with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "rem-123", "status": "pending"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "remediation", "show", "rem-123", "--output", "json"],
        )

        assert result.exit_code == 0


# Remediation Create Tests


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_create_success(mock_get_client):
    """Test creating a remediation."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "rem-new",
        "violation_id": "vio-456",
        "action_type": "MANUAL",
        "status": "pending",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_create") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "remediation",
                "create",
                "--violation-id",
                "vio-456",
                "--type",
                "MANUAL",
                "--details",
                "Manual fix required",
            ],
        )

        assert result.exit_code == 0
        assert "created" in result.stdout.lower()


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_create_automatic(mock_get_client):
    """Test creating an automatic remediation."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "rem-new",
        "action_type": "AUTOMATIC",
        "status": "pending",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_create") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "remediation",
                "create",
                "--violation-id",
                "vio-456",
                "--type",
                "AUTOMATIC",
            ],
        )

        assert result.exit_code == 0


def test_remediation_create_invalid_type():
    """Test creating remediation with invalid type."""
    result = runner.invoke(
        app,
        [
            "compliance",
            "remediation",
            "create",
            "--violation-id",
            "vio-456",
            "--type",
            "INVALID",
        ],
    )

    assert result.exit_code == 1
    assert "Invalid action type" in result.stdout


# Remediation Update Tests


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_update_success(mock_get_client):
    """Test updating remediation status."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "rem-123",
        "status": "completed",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_update") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "remediation",
                "update",
                "rem-123",
                "--status",
                "completed",
                "--details",
                "Fix verified",
            ],
        )

        assert result.exit_code == 0
        assert "updated" in result.stdout.lower()


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_update_json_output(mock_get_client):
    """Test updating remediation with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "rem-123", "status": "in_progress"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_update") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "remediation",
                "update",
                "rem-123",
                "--status",
                "in_progress",
                "--output",
                "json",
            ],
        )

        assert result.exit_code == 0


# Remediation Execute Tests


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_execute_success(mock_get_client):
    """Test executing a remediation."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "rem-123",
        "status": "completed",
        "result": "Remediation applied successfully",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_execute") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "remediation", "execute", "rem-123", "--yes"],
        )

        assert result.exit_code == 0
        assert "executed" in result.stdout.lower()


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_execute_json_output(mock_get_client):
    """Test executing remediation with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "rem-123", "status": "completed"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.remediation.api_execute") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "remediation",
                "execute",
                "rem-123",
                "--yes",
                "--output",
                "json",
            ],
        )

        assert result.exit_code == 0


def test_remediation_execute_requires_confirmation():
    """Test execute requires confirmation without --yes."""
    result = runner.invoke(
        app,
        ["compliance", "remediation", "execute", "rem-123"],
        input="n\n",  # Respond 'no' to confirmation
    )

    assert result.exit_code == 1  # Aborted


@patch("iltero.commands.compliance.remediation.get_retry_client")
def test_remediation_execute_error(mock_get_client):
    """Test execute handles errors."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Auth failed")

    result = runner.invoke(
        app,
        ["compliance", "remediation", "execute", "rem-123", "--yes"],
    )

    assert result.exit_code == 1
    assert "Error" in result.stdout
