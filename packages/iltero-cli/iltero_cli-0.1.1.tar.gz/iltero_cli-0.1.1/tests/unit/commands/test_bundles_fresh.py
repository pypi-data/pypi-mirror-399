"""Tests for bundles commands."""

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


def test_bundles_list_success():
    """Test listing template bundles."""
    mock_response = Mock()
    mock_response.status_code = 200
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

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "list"])

            assert result.exit_code == 0
            assert "HIPAA" in result.stdout
            assert "bundle" in result.stdout.lower()
            assert "Found 1 bundle(s)" in result.stdout


def test_bundles_list_with_filters():
    """Test listing bundles with filters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = []

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ) as mock_api:
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "list",
                    "--industry",
                    "healthcare",
                    "--provider",
                    "aws",
                    "--compliance",
                    "hipaa",
                ],
            )

            assert result.exit_code == 0
            mock_api.assert_called_once()
            call_kwargs = mock_api.call_args.kwargs
            assert call_kwargs["industry"] == "healthcare"
            assert call_kwargs["provider"] == "aws"
            assert call_kwargs["compliance_frameworks"] == "hipaa"


def test_bundles_list_json_output():
    """Test listing bundles with JSON output."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "bundle-123",
            "name": "Test Bundle",
        }
    ]

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "list", "--output", "json"])

            assert result.exit_code == 0
            assert "bundle-123" in result.stdout


def test_bundles_list_no_results():
    """Test listing bundles with no results."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = None

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "list"])

            assert result.exit_code == 0
        assert "No bundles found" in result.stdout


def test_bundles_list_api_error():
    """Test listing bundles with API error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.parsed = None

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = None
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "list"])

            assert result.exit_code == 1
            assert "Error listing bundles" in result.stdout


def test_bundles_show_success():
    """Test showing bundle details."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "bundle-123",
        "name": "Healthcare Bundle",
        "description": "Complete HIPAA-compliant infrastructure",
        "provider": "aws",
        "industry": "healthcare",
        "tier": "enterprise",
        "compliance_frameworks": ["hipaa", "soc2"],
        "marketplace_category": "Healthcare",
        "infrastructure_units": ["vpc", "rds", "s3"],
    }

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_get_bundle.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "show", "bundle-123"])

            assert result.exit_code == 0
            assert "Healthcare Bundle" in result.stdout
            assert "bundle-123" in result.stdout
            assert "HIPAA-compliant" in result.stdout


def test_bundles_show_json_output():
    """Test showing bundle with JSON output."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"id": "bundle-123", "name": "Test"}

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_get_bundle.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "show", "bundle-123", "--output", "json"])

            assert result.exit_code == 0
            assert "bundle-123" in result.stdout


def test_bundles_show_not_found():
    """Test showing non-existent bundle."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.parsed = None

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = None
        with patch(
            "iltero.commands.bundles.marketplace.api_get_bundle.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "show", "not-found"])

            assert result.exit_code == 1
            assert "Error showing bundle" in result.stdout


def test_bundles_search_success():
    """Test searching bundles."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "bundle-1",
            "name": "Healthcare HIPAA Bundle",
            "description": "HIPAA compliance",
            "marketplace_category": "Healthcare",
            "provider": "aws",
            "industry": "healthcare",
            "tier": "enterprise",
            "compliance_frameworks": ["hipaa"],
        },
        {
            "id": "bundle-2",
            "name": "Finance Bundle",
            "description": "Financial services",
            "marketplace_category": "Finance",
            "provider": "aws",
            "industry": "finance",
            "tier": "standard",
            "compliance_frameworks": ["pci-dss"],
        },
    ]

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "search", "healthcare"])

            assert result.exit_code == 0
            # Rich table truncates long names, so check for bundle-1 ID instead
            assert "bundle-1" in result.stdout
            assert "bundle-2" not in result.stdout  # Filtered out


def test_bundles_search_with_filters():
    """Test searching bundles with additional filters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = []

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ) as mock_api:
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "search",
                    "hipaa",
                    "--industry",
                    "healthcare",
                    "--provider",
                    "aws",
                ],
            )

            assert result.exit_code == 0
            mock_api.assert_called_once()


def test_bundles_search_no_results():
    """Test searching bundles with no matches."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "bundle-1",
            "name": "Test Bundle",
            "description": "Testing",
            "marketplace_category": "Other",
        }
    ]

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "search", "nonexistent"])

            assert result.exit_code == 0
            assert "No bundles found" in result.stdout


def test_bundles_validate_success():
    """Test validating bundle compliance."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "status": "passed",
        "controls_passed": 50,
        "controls_failed": 0,
    }

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_validate_compliance.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "validate",
                    "bundle-123",
                    "--frameworks",
                    "hipaa,soc2",
                ],
            )

            assert result.exit_code == 0
            assert "passed" in result.stdout
            assert "Controls Passed" in result.stdout


def test_bundles_validate_with_violations():
    """Test validating bundle with compliance violations."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "status": "failed",
        "violations": ["Missing encryption", "No MFA"],
        "controls_passed": 45,
        "controls_failed": 5,
    }

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_validate_compliance.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "validate", "bundle-123"])

            assert result.exit_code == 0
            assert "failed" in result.stdout
            assert "Violations" in result.stdout


def test_bundles_validate_api_error():
    """Test validating bundle with API error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.parsed = None

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = None
        with patch(
            "iltero.commands.bundles.marketplace.api_validate_compliance.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "validate", "bundle-123"])

            assert result.exit_code == 1
            assert "Error validating bundle" in result.stdout


# Integration Commands Tests


def test_bundles_bootstrap_success():
    """Test bootstrapping stack with bundle."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "task_id": "task-456",
        "status": "pending",
    }

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_bootstrap.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "bootstrap",
                    "bundle-123",
                    "--stack-id",
                    "stack-789",
                    "--cloud-provider",
                    "aws",
                    "--aws-region",
                    "us-east-1",
                    "--aws-role-arn",
                    "arn:aws:iam::123456789012:role/test",
                    "--aws-plan-bucket",
                    "test-bucket",
                    "--backend-type",
                    "s3",
                    "--backend-bucket",
                    "tfstate-bucket",
                    "--backend-region",
                    "us-east-1",
                ],
            )

            assert result.exit_code == 0
            assert "Bootstrap Initiated" in result.stdout
            assert "task-456" in result.stdout
            assert "stack-789" in result.stdout


def test_bundles_bootstrap_with_compliance():
    """Test bootstrapping with full configuration."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"task_id": "task-456"}

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_bootstrap.sync_detailed",
            return_value=mock_response,
        ) as mock_api:
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "bootstrap",
                    "bundle-123",
                    "--stack-id",
                    "stack-789",
                    "--cloud-provider",
                    "aws",
                    "--aws-region",
                    "us-east-1",
                    "--aws-role-arn",
                    "arn:aws:iam::123456789012:role/test",
                    "--aws-plan-bucket",
                    "test-bucket",
                    "--backend-type",
                    "s3",
                    "--backend-bucket",
                    "tfstate-bucket",
                    "--backend-region",
                    "us-east-1",
                ],
            )

            assert result.exit_code == 0
            mock_api.assert_called_once()


def test_bundles_bootstrap_missing_stack_id():
    """Test bootstrap without required stack-id."""
    result = runner.invoke(app, ["bundles", "bootstrap", "bundle-123"])

    assert result.exit_code == 2  # Missing required option


def test_bundles_bootstrap_api_error():
    """Test bootstrap with API error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.parsed = None

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = None
        with patch(
            "iltero.commands.bundles.integration.api_bootstrap.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "bootstrap",
                    "bundle-123",
                    "--stack-id",
                    "stack-789",
                    "--cloud-provider",
                    "aws",
                    "--aws-region",
                    "us-east-1",
                    "--aws-role-arn",
                    "arn:aws:iam::123456789012:role/test",
                    "--aws-plan-bucket",
                    "test-bucket",
                    "--backend-type",
                    "s3",
                    "--backend-bucket",
                    "tfstate-bucket",
                    "--backend-region",
                    "us-east-1",
                ],
            )

            assert result.exit_code == 1
            assert "Error" in result.stdout or "Failed" in result.stdout


def test_bundles_bootstrap_status_success():
    """Test checking bootstrap status."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "status": "in_progress",
        "progress": 45,
        "completed_steps": ["validation", "setup"],
        "current_step": "deployment",
    }

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_bootstrap_status.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "bootstrap-status",
                    "task-456",
                    "--stack-id",
                    "stack-789",
                ],
            )

            assert result.exit_code == 0
            assert "in_progress" in result.stdout
            assert "45%" in result.stdout
            assert "deployment" in result.stdout


def test_bundles_bootstrap_status_completed():
    """Test bootstrap status when completed."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "status": "completed",
        "progress": 100,
    }

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_bootstrap_status.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "bootstrap-status",
                    "task-456",
                    "--stack-id",
                    "stack-789",
                ],
            )

            assert result.exit_code == 0
            assert "completed" in result.stdout


def test_bundles_bootstrap_status_failed():
    """Test bootstrap status when failed."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "status": "failed",
        "error": "Validation failed",
    }

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_bootstrap_status.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "bootstrap-status",
                    "task-456",
                    "--stack-id",
                    "stack-789",
                ],
            )

            assert result.exit_code == 0
            assert "failed" in result.stdout
            assert "Validation failed" in result.stdout


def test_bundles_analyze_success():
    """Test analyzing bundle pattern."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "pattern_type": "multi-tier",
        "uic_coordination_status": "active",
        "infrastructure_units": ["vpc", "rds", "s3"],
        "compliance_config": {"frameworks": ["hipaa"]},
    }

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_analyze.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "analyze", "--stack-id", "stack-789"])

            assert result.exit_code == 0
            assert "multi-tier" in result.stdout
            assert "active" in result.stdout
            assert "vpc" in result.stdout


def test_bundles_analyze_json_output():
    """Test analyzing bundle with JSON output."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"pattern_type": "simple"}

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_analyze.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                ["bundles", "analyze", "--stack-id", "stack-789", "--output", "json"],
            )

            assert result.exit_code == 0
            assert "simple" in result.stdout


def test_bundles_analyze_api_error():
    """Test analyze with API error."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.parsed = None

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = None
        with patch(
            "iltero.commands.bundles.integration.api_analyze.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "analyze", "--stack-id", "stack-789"])

            assert result.exit_code == 1
            assert "Error analyzing bundle" in result.stdout


def test_bundles_dependencies_success():
    """Test showing bundle dependencies."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "dependency_graph": [
            {"from": "vpc", "to": "rds", "via": "subnet"},
            {"from": "rds", "to": "s3", "via": "backup"},
        ],
        "uic_contracts": ["vpc-rds-contract", "rds-s3-contract"],
    }

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_dependencies.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "dependencies", "--stack-id", "stack-789"])

            assert result.exit_code == 0
            assert "vpc → rds" in result.stdout
            assert "rds → s3" in result.stdout
            assert "UIC Contracts" in result.stdout


def test_bundles_dependencies_json_output():
    """Test dependencies with JSON output."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {"dependency_graph": []}

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.integration.api_dependencies.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(
                app,
                [
                    "bundles",
                    "dependencies",
                    "--stack-id",
                    "stack-789",
                    "--output",
                    "json",
                ],
            )

            assert result.exit_code == 0


def test_bundles_dependencies_api_error():
    """Test dependencies with API error."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.parsed = None

    with patch("iltero.commands.bundles.integration.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = None
        with patch(
            "iltero.commands.bundles.integration.api_dependencies.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "dependencies", "--stack-id", "stack-789"])

            assert result.exit_code == 1
            assert "Error getting dependencies" in result.stdout


# Additional edge cases


def test_bundles_list_handles_list_values():
    """Test that list values in responses are formatted correctly."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = [
        {
            "id": "bundle-123",
            "name": "Test",
            "provider": "aws",
            "industry": "healthcare",
            "tier": "enterprise",
            "compliance_frameworks": ["hipaa", "soc2", "pci-dss"],
            "marketplace_category": "Healthcare",
        }
    ]

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "list"])

            assert result.exit_code == 0
            # Rich table wraps long lists, check individual items
            assert "hipaa" in result.stdout
            assert "soc2" in result.stdout
            assert "pci-dss" in result.stdout


def test_bundles_show_handles_missing_fields():
    """Test showing bundle with missing optional fields."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.parsed = Mock()
    mock_response.parsed.data = {
        "id": "bundle-123",
        "name": "Minimal Bundle",
        # Missing most optional fields
    }

    with patch("iltero.commands.bundles.marketplace.get_retry_client") as mock_get_client:
        mock_client, _ = setup_mock_client(mock_get_client)
        mock_client.handle_response.return_value = mock_response.parsed
        with patch(
            "iltero.commands.bundles.marketplace.api_get_bundle.sync_detailed",
            return_value=mock_response,
        ):
            result = runner.invoke(app, ["bundles", "show", "bundle-123"])

            assert result.exit_code == 0
            assert "Minimal Bundle" in result.stdout


def test_bundles_exception_handling():
    """Test that exceptions are caught and handled properly."""
    with patch(
        "iltero.commands.bundles.marketplace.api_discover_bundles.sync_detailed",
        side_effect=Exception("Network error"),
    ):
        result = runner.invoke(app, ["bundles", "list"])

        assert result.exit_code == 1
        assert "Error listing bundles" in result.stdout
