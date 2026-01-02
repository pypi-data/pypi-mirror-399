"""Tests for bundles commands - Fixed version."""

from __future__ import annotations

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


def setup_mock_client(mock_get_client):
    """Setup mock client for bundles tests."""
    mock_client = Mock()
    mock_get_client.return_value = mock_client
    mock_auth_client = Mock()
    mock_client.get_authenticated_client.return_value = mock_auth_client
    return mock_client, mock_auth_client


# Marketplace Commands Tests


@patch("iltero.commands.bundles.marketplace.get_retry_client")
def test_bundles_list_success(mock_get_client):
    """Test listing template bundles."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "bundle-123",
            "name": "Healthcare HIPAA Bundle",
            "provider": "aws",
            "industry": "healthcare",
            "tier": "enterprise",
            "compliance_frameworks": ["hipaa", "soc2"],
            "marketplace_category": "Healthcare",
        }
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.marketplace.api_discover_bundles") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["bundles", "list"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.bundles.marketplace.get_retry_client")
def test_bundles_show_success(mock_get_client):
    """Test showing bundle details."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "bundle-123",
        "name": "Healthcare HIPAA Bundle",
        "description": "Complete HIPAA-compliant infrastructure",
        "provider": "aws",
        "infrastructure_units": ["vpc", "ecs"],
        "uic_contracts": ["data-flow-validation"],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.marketplace.api_get_bundle") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["bundles", "show", "bundle-123"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.bundles.marketplace.get_retry_client")
def test_bundles_search_success(mock_get_client):
    """Test searching bundles."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {"id": "b1", "name": "HIPAA Bundle"},
        {"id": "b2", "name": "Healthcare Bundle"},
    ]
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.marketplace.api_discover_bundles") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["bundles", "search", "hipaa"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.bundles.marketplace.get_retry_client")
def test_bundles_validate_success(mock_get_client):
    """Test validating bundle compliance."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "bundle_id": "bundle-123",
        "status": "compliant",
        "violations": [],
        "warnings": [],
        "passed_controls": 50,
    }
    # handle_response returns the parsed response object
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.marketplace.api_validate_compliance") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["bundles", "validate", "bundle-123", "--frameworks", "hipaa"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


# Integration Commands Tests


@patch("iltero.commands.bundles.integration.get_retry_client")
def test_bundles_bootstrap_success(mock_get_client):
    """Test bootstrapping a bundle."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "task_id": "task-123",
        "status": "initiated",
        "message": "Bootstrap started",
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.integration.api_bootstrap") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            [
                "bundles",
                "bootstrap",
                "bundle-123",
                "--stack-id",
                "stack-456",
                "--cloud-provider",
                "aws",
                "--aws-region",
                "us-east-1",
                "--aws-role-arn",
                "arn:aws:iam::123456789012:role/TestRole",
                "--aws-plan-bucket",
                "test-plans",
                "--backend-type",
                "s3",
                "--backend-bucket",
                "test-state",
                "--backend-region",
                "us-east-1",
            ],
        )

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()
        # Verify the request was built with proper schemas
        call_args = mock_api.sync_detailed.call_args
        assert call_args is not None
        request_body = call_args.kwargs["body"]
        assert request_body.stack_id == "stack-456"
        assert request_body.template_bundle_id == "bundle-123"
        assert request_body.cloud_config.aws_region == "us-east-1"
        assert request_body.terraform_backend.type_ == "s3"
        assert request_body.terraform_backend.config.bucket == "test-state"


@patch("iltero.commands.bundles.integration.get_retry_client")
def test_bundles_bootstrap_status_success(mock_get_client):
    """Test checking bootstrap status."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "task_id": "task-123",
        "status": "in_progress",
        "progress": 50,
        "completed_steps": ["validate", "prepare"],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.integration.api_bootstrap_status") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(
            app,
            ["bundles", "bootstrap-status", "task-123", "--stack-id", "stack-456"],
        )

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.bundles.integration.get_retry_client")
def test_bundles_analyze_success(mock_get_client):
    """Test analyzing a bundle."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "pattern_type": "microservices",
        "uic_coordination": "enabled",
        "infrastructure_units": ["vpc", "ecs", "rds"],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.integration.api_analyze") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["bundles", "analyze", "--stack-id", "stack-789"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()


@patch("iltero.commands.bundles.integration.get_retry_client")
def test_bundles_dependencies_success(mock_get_client):
    """Test showing dependencies."""
    mock_client, _ = setup_mock_client(mock_get_client)

    mock_response = Mock()
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "dependencies": [
            {"from": "vpc", "to": "ecs", "type": "network"},
            {"from": "ecs", "to": "rds", "type": "data"},
        ],
        "data_flows": ["vpc→ecs", "ecs→rds"],
    }
    mock_client.handle_response.return_value = mock_response.parsed

    with patch("iltero.commands.bundles.integration.api_dependencies") as mock_api:
        mock_api.sync_detailed.return_value = mock_response

        result = runner.invoke(app, ["bundles", "dependencies", "--stack-id", "stack-789"])

        assert result.exit_code == 0
        mock_client.get_authenticated_client.assert_called_once()
