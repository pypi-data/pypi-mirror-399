"""Tests for compliance manifests commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


def setup_mock_client(mock_get_client):
    """Setup mock client for manifests tests."""
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_auth_client = Mock()
    mock_client.get_authenticated_client.return_value = mock_auth_client
    return mock_client, mock_auth_client


# Manifest Generate Tests


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_generate_success(mock_get_client):
    """Test successful manifest generation."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "manifest": {
            "id": "mfst-123",
            "version": "1.0",
            "status": "generated",
            "created_at": "2024-01-01T00:00:00Z",
            "frameworks": ["SOC2", "ISO27001"],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_generate") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "generate", "bundle-456"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_generate_with_frameworks(mock_get_client):
    """Test manifest generation with specific frameworks."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "manifest": {
            "id": "mfst-789",
            "status": "generated",
            "frameworks": ["HIPAA"],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_generate") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "manifest",
                "generate",
                "bundle-abc",
                "--frameworks",
                "HIPAA",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_generate_empty_response(mock_get_client):
    """Test manifest generation with empty response."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_generate") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "generate", "bundle-456"])

        assert result.exit_code == 0
        assert "failed" in result.output.lower()


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_generate_exception(mock_get_client):
    """Test manifest generation with exception."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Connection timeout")

    result = runner.invoke(app, ["compliance", "manifest", "generate", "bundle-456"])

    assert result.exit_code == 1
    assert "Connection timeout" in result.output


# Manifest Show Tests


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_show_success(mock_get_client):
    """Test successful manifest retrieval."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "manifest": {
            "id": "mfst-123",
            "bundle_id": "bundle-456",
            "version": "2.0",
            "status": "verified",
            "hash": "abc123def456ghi789jkl012mno345",
            "created_at": "2024-01-01T00:00:00Z",
            "frameworks": [
                {"name": "SOC2", "control_count": 50, "policy_count": 25},
                {"name": "PCI-DSS", "control_count": 40, "policy_count": 20},
            ],
            "controls": [{"id": "c1"}, {"id": "c2"}],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "show", "bundle-456"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_show_not_found(mock_get_client):
    """Test manifest retrieval when not found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "show", "bundle-999"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_show_simple_frameworks(mock_get_client):
    """Test manifest show with simple framework strings."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "manifest": {
            "id": "mfst-abc",
            "status": "generated",
            "frameworks": ["SOC2", "HIPAA"],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_get") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "show", "bundle-xyz"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_show_exception(mock_get_client):
    """Test manifest retrieval with exception."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Network error")

    result = runner.invoke(app, ["compliance", "manifest", "show", "bundle-456"])

    assert result.exit_code == 1
    assert "Network error" in result.output


# Manifest Verify Tests


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_verify_success(mock_get_client):
    """Test successful manifest verification."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "verification": {
            "valid": True,
            "hash_valid": True,
            "signature_valid": True,
            "verified_at": "2024-01-01T00:00:00Z",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_verify") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "verify", "mfst-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_verify_failed(mock_get_client):
    """Test manifest verification with failures."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "verification": {
            "valid": False,
            "hash_valid": False,
            "signature_valid": True,
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_verify") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "verify", "mfst-456"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_verify_empty_response(mock_get_client):
    """Test manifest verification with empty response."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.manifests.api_verify") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "manifest", "verify", "mfst-999"])

        assert result.exit_code == 0
        assert "failed" in result.output.lower()


@patch("iltero.commands.compliance.manifests.get_retry_client")
def test_manifest_verify_exception(mock_get_client):
    """Test manifest verification with exception."""
    mock_client, _ = setup_mock_client(mock_get_client)
    mock_client.get_authenticated_client.side_effect = Exception("Service unavailable")

    result = runner.invoke(app, ["compliance", "manifest", "verify", "mfst-123"])

    assert result.exit_code == 1
    assert "Service unavailable" in result.output
