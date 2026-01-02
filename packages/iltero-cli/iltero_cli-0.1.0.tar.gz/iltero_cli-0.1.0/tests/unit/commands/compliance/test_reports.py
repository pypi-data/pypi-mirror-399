"""Tests for compliance reports commands."""

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


# Reports List Tests


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_list_success(mock_get_client):
    """Test listing compliance reports."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "reports": [
            {
                "id": "report-123",
                "type": "summary",
                "status": "completed",
                "created_at": "2025-01-01T00:00:00Z",
                "frameworks": ["SOC2", "HIPAA"],
            }
        ]
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "reports", "list", "stack-456"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_list_empty(mock_get_client):
    """Test listing reports when none exist."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"reports": []}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "reports", "list", "stack-456"])

        assert result.exit_code == 0
        assert "No reports found" in result.output


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_list_with_limit(mock_get_client):
    """Test listing reports with custom limit."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"reports": []}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_list") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "reports", "list", "stack-456", "--limit", "5"])

        assert result.exit_code == 0


# Reports Generate Tests


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_generate_success(mock_get_client):
    """Test generating a compliance report."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "report": {
            "id": "report-new-123",
            "type": "summary",
            "status": "generating",
            "created_at": "2025-01-01T00:00:00Z",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_generate") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "reports", "generate", "stack-456"])

        assert result.exit_code == 0
        assert "Report generated" in result.output


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_generate_with_options(mock_get_client):
    """Test generating report with all options."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "report": {"id": "report-123", "type": "detailed", "status": "pending"}
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_generate") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "reports",
                "generate",
                "stack-456",
                "--type",
                "detailed",
                "--include-evidence",
                "--include-trends",
                "--frameworks",
                "SOC2,HIPAA",
                "--format",
                "pdf",
            ],
        )

        assert result.exit_code == 0


# Reports Export Tests


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_export_success(mock_get_client):
    """Test exporting a compliance report."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "export": {
            "download_url": "https://example.com/report.pdf",
            "file_path": "/path/to/report.pdf",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_export") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "reports", "export", "stack-456", "report-123"],
        )

        assert result.exit_code == 0
        assert "exported" in result.output


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_export_with_format(mock_get_client):
    """Test exporting report with custom format."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"export": {"download_url": "http://test.com"}}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_export") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "reports",
                "export",
                "stack-456",
                "report-123",
                "--format",
                "CSV",
            ],
        )

        assert result.exit_code == 0
        assert "CSV" in result.output


@patch("iltero.commands.compliance.reports.get_retry_client")
def test_reports_export_no_url(mock_get_client):
    """Test export result without download URL."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"export": {}}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.reports.api_export") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["compliance", "reports", "export", "stack-456", "report-123"],
        )

        assert result.exit_code == 0
