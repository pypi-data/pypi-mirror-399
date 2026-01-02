"""Tests for compliance assessment commands."""

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


# Summary Tests


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_summary_success(mock_get_client):
    """Test getting compliance summary."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "summary": {
            "overall_score": 85,
            "status": "compliant",
            "total_policies": 50,
            "compliant_count": 45,
            "violation_count": 5,
            "last_assessment": "2025-01-01T00:00:00Z",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_summary") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "summary", "stack-456"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_summary_with_frameworks(mock_get_client):
    """Test summary with framework breakdown."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "summary": {
            "overall_score": 90,
            "status": "compliant",
            "frameworks": [
                {"name": "SOC2", "score": 92, "status": "compliant"},
                {"name": "HIPAA", "score": 88, "status": "compliant"},
            ],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_summary") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "summary", "stack-456"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_summary_low_score(mock_get_client):
    """Test summary with low compliance score."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "summary": {
            "overall_score": 45,
            "status": "non-compliant",
            "violation_count": 25,
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_summary") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "summary", "stack-456"])

        assert result.exit_code == 0


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_summary_empty(mock_get_client):
    """Test summary when no data available."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_summary") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "summary", "stack-456"])

        assert result.exit_code == 0


# Full Assessment Tests


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_full_success(mock_get_client):
    """Test performing full assessment."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "assessment": {
            "overall_score": 88,
            "status": "completed",
            "policies_evaluated": 50,
            "violations_found": 6,
            "evidence_collected": 120,
            "duration": "5m 30s",
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_full") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "full", "stack-456"])

        assert result.exit_code == 0
        assert "completed" in result.output.lower()


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_full_with_options(mock_get_client):
    """Test full assessment with all options."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"assessment": {"overall_score": 75, "status": "completed"}}
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_full") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "compliance",
                "assessment",
                "full",
                "stack-456",
                "--no-validation",
                "--evidence",
                "--no-monitoring",
                "--mode",
                "QUICK",
                "--auto-remediate",
                "--frameworks",
                "SOC2,PCI",
            ],
        )

        assert result.exit_code == 0


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_full_with_violations(mock_get_client):
    """Test full assessment with violations found."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "assessment": {
            "overall_score": 60,
            "status": "completed",
            "violations": [
                {"id": "v1", "policy": "policy-1"},
                {"id": "v2", "policy": "policy-2"},
            ],
        }
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_full") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "full", "stack-456"])

        assert result.exit_code == 0
        assert "2 violation" in result.output


@patch("iltero.commands.compliance.assessment.get_retry_client")
def test_assessment_full_no_data(mock_get_client):
    """Test full assessment when it fails."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = None
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.compliance.assessment.api_full") as api:
        api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["compliance", "assessment", "full", "stack-456"])

        assert result.exit_code == 0
