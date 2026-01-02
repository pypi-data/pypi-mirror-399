"""Tests for compliance scans commands."""

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


# Scans List Tests


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_list_success(mock_get_client):
    """Test listing compliance scans."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "scan-123",
            "stack_id": "stack-456",
            "scan_type": "static",
            "status": "completed",
            "score": 85.5,
            "created_at": "2025-01-01T00:00:00Z",
        }
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "scans", "list"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_list_with_filters(mock_get_client):
    """Test listing scans with filters."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = []
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "scans",
                "list",
                "--stack-id",
                "stack-456",
                "--type",
                "static",
                "--status",
                "completed",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_list_json_output(mock_get_client):
    """Test listing scans with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [{"id": "scan-123", "status": "completed"}]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "scans", "list", "--output", "json"],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_list_empty(mock_get_client):
    """Test listing scans when none found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "scans", "list"])

        assert result.exit_code == 0
        assert "No scans found" in result.stdout


# Scans Show Tests


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_show_success(mock_get_client):
    """Test showing scan details."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "scan-123",
        "stack_id": "stack-456",
        "scan_type": "static",
        "status": "completed",
        "score": 85.5,
        "created_at": "2025-01-01T00:00:00Z",
        "completed_at": "2025-01-01T00:05:00Z",
        "summary": {
            "passed": 45,
            "failed": 5,
            "skipped": 2,
        },
        "violations": [{"rule_id": "CKV_AWS_1", "resource_id": "s3-bucket", "severity": "high"}],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "scans", "show", "scan-123"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_show_json_output(mock_get_client):
    """Test showing scan with JSON output."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "scan-123", "status": "completed"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "scans", "show", "scan-123", "--output", "json"],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_show_error(mock_get_client):
    """Test show scan handles errors."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Auth failed")

    result = runner.invoke(app, ["compliance", "scans", "show", "scan-123"])

    assert result.exit_code == 1
    assert "Error" in result.stdout


# Scans Submit Tests


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_submit_success(mock_get_client, tmp_path):
    """Test submitting scan results."""
    mock_client, _ = setup_mock_client(mock_get_client)

    # Create a temp results file
    results_file = tmp_path / "results.json"
    results_file.write_text('{"passed": 10, "failed": 2}')

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "scan-123",
        "status": "completed",
        "score": 83.3,
        "violations_count": 2,
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_submit") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "scans",
                "submit",
                "scan-123",
                "--file",
                str(results_file),
            ],
        )

        assert result.exit_code == 0
        assert "submitted" in result.stdout.lower()


@patch("iltero.commands.compliance.scans.get_retry_client")
def test_scans_submit_with_metadata(mock_get_client, tmp_path):
    """Test submitting scan results with metadata."""
    mock_client, _ = setup_mock_client(mock_get_client)

    results_file = tmp_path / "results.json"
    results_file.write_text('{"passed": 10, "failed": 0}')

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "scan-123", "status": "completed"}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.scans.api_submit") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "scans",
                "submit",
                "scan-123",
                "--file",
                str(results_file),
                "--scanner-version",
                "2.5.0",
                "--pipeline-url",
                "https://ci.example.com/123",
                "--commit",
                "abc123",
                "--branch",
                "main",
            ],
        )

        assert result.exit_code == 0


def test_scans_submit_invalid_json(tmp_path):
    """Test submit with invalid JSON file."""
    results_file = tmp_path / "invalid.json"
    results_file.write_text("not valid json {")

    result = runner.invoke(
        app,
        [
            "compliance",
            "scans",
            "submit",
            "scan-123",
            "--file",
            str(results_file),
        ],
    )

    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout


def test_scans_submit_missing_file():
    """Test submit with missing file."""
    result = runner.invoke(
        app,
        [
            "compliance",
            "scans",
            "submit",
            "scan-123",
            "--file",
            "/nonexistent/file.json",
        ],
    )

    assert result.exit_code == 2  # Typer validation error
