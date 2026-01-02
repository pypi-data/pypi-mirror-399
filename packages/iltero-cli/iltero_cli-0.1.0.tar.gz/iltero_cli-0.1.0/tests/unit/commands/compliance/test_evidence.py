"""Tests for compliance evidence commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


def setup_mock_client(mock_get_client):
    """Setup mock client for evidence tests."""
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_auth_client = Mock()
    mock_client.get_authenticated_client.return_value = mock_auth_client
    return mock_client, mock_auth_client


# Evidence Collect Tests


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_collect_success(mock_get_client):
    """Test successful evidence collection."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "evidence": {
            "id": "evd-123",
            "status": "collected",
            "created_at": "2024-01-01T00:00:00Z",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.evidence.api_collect") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "evidence", "collect", "stack-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_collect_with_options(mock_get_client):
    """Test evidence collection with all options."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "evidence": {
            "id": "evd-456",
            "status": "collected",
            "created_at": "2024-01-01T00:00:00Z",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.evidence.api_collect") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "evidence",
                "collect",
                "stack-123",
                "--types",
                "logs,config",
                "--reason",
                "audit",
                "--compress",
                "--encrypt",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_collect_empty_response(mock_get_client):
    """Test evidence collection with empty response."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.evidence.api_collect") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "evidence", "collect", "stack-123"])

        assert result.exit_code == 0
        assert "failed" in result.output.lower()


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_collect_exception(mock_get_client):
    """Test evidence collection with exception."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Connection failed")

    result = runner.invoke(app, ["compliance", "evidence", "collect", "stack-123"])

    assert result.exit_code == 1
    assert "Connection failed" in result.output


# Evidence Show Tests


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_show_success(mock_get_client):
    """Test successful evidence retrieval."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "evidence": {
            "id": "evd-123",
            "stack_id": "stack-456",
            "status": "collected",
            "collection_reason": "audit",
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z",
            "evidence_types": [
                {"type": "logs", "status": "collected", "size": "10MB"},
                {"type": "config", "status": "collected", "size": "5MB"},
            ],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.evidence.api_retrieve") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "evidence", "show", "stack-456", "evd-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_show_not_found(mock_get_client):
    """Test evidence retrieval when not found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.evidence.api_retrieve") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "evidence", "show", "stack-456", "evd-999"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_show_simple_types(mock_get_client):
    """Test evidence show with simple string types."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "evidence": {
            "id": "evd-789",
            "status": "collected",
            "evidence_types": ["logs", "config", "state"],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.evidence.api_retrieve") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "evidence", "show", "stack-abc", "evd-789"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.evidence.get_retry_client")
def test_evidence_show_exception(mock_get_client):
    """Test evidence retrieval with exception."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Network error")

    result = runner.invoke(app, ["compliance", "evidence", "show", "stack-456", "evd-123"])

    assert result.exit_code == 1
    assert "Network error" in result.output
