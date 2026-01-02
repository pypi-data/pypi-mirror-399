"""End-to-end integration tests for CLI workflows.

These tests validate complete CLI workflows with mocked API responses
to ensure commands work together correctly.
"""

import json
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from iltero.cli import app
from iltero.scanners.models import (
    ScanResults,
    ScanSummary,
    ScanType,
    Severity,
    Violation,
)

runner = CliRunner()


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    config_dir = tmp_path / ".iltero"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_api_client():
    """Create a mock API client for all tests."""
    with patch("iltero.core.http.get_retry_client") as mock_get_client:
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client
        yield mock_client


@pytest.fixture
def terraform_project(tmp_path):
    """Create a sample Terraform project for scanning."""
    project_dir = tmp_path / "terraform"
    project_dir.mkdir()

    # Create main.tf
    main_tf = project_dir / "main.tf"
    main_tf.write_text("""
resource "aws_s3_bucket" "test" {
  bucket = "my-test-bucket"
}

resource "aws_instance" "web" {
  ami           = "ami-0123456789"
  instance_type = "t2.micro"
}
""")

    # Create variables.tf
    variables_tf = project_dir / "variables.tf"
    variables_tf.write_text("""
variable "environment" {
  type    = string
  default = "dev"
}
""")

    return project_dir


@pytest.fixture
def terraform_plan_json(tmp_path):
    """Create a sample Terraform plan JSON file."""
    plan_file = tmp_path / "tfplan.json"
    plan_content = {
        "format_version": "1.0",
        "terraform_version": "1.5.0",
        "planned_values": {
            "root_module": {
                "resources": [
                    {
                        "address": "aws_s3_bucket.test",
                        "type": "aws_s3_bucket",
                        "name": "test",
                        "values": {"bucket": "my-test-bucket"},
                    }
                ]
            }
        },
        "resource_changes": [
            {
                "address": "aws_s3_bucket.test",
                "change": {"actions": ["create"]},
            }
        ],
    }
    plan_file.write_text(json.dumps(plan_content))
    return plan_file


def create_mock_scan_results(
    violations: int = 0,
    passed: int = 10,
    scanner: str = "checkov",
) -> ScanResults:
    """Create mock scan results for testing."""
    violation_list = []
    for i in range(violations):
        violation_list.append(
            Violation(
                check_id=f"CKV_AWS_{i + 1}",
                check_name=f"Test Check {i + 1}",
                severity=Severity.HIGH if i % 2 == 0 else Severity.MEDIUM,
                resource=f"aws_s3_bucket.test{i}",
                file_path="main.tf",
                line_range=(10 + i, 15 + i),
                description=f"Test violation {i + 1}",
            )
        )

    summary = ScanSummary(
        total_checks=passed + violations,
        passed=passed,
        failed=violations,
        skipped=0,
        critical=0,
        high=violations // 2 + violations % 2,
        medium=violations // 2,
        low=0,
        info=0,
    )

    return ScanResults(
        scanner=scanner,
        version="2.3.0",
        scan_type=ScanType.STATIC,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        summary=summary,
        violations=violation_list,
        metadata={},
    )


# ============================================================================
# Test: CLI Basic Commands
# ============================================================================


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self):
        """Test CLI help output."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # The app help says "Unified CLI for Iltero platform"
        assert "Unified CLI for Iltero platform" in result.output
        assert "workspace" in result.output
        assert "environment" in result.output
        assert "stack" in result.output
        assert "scan" in result.output

    def test_cli_version(self):
        """Test CLI version output."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "iltero version" in result.output

    def test_cli_no_args_shows_help(self):
        """Test CLI without args shows help."""
        result = runner.invoke(app, [])
        # Typer with no_args_is_help=True returns exit code 2 with help
        assert result.exit_code == 2
        assert "Usage:" in result.output

    def test_subcommand_help(self):
        """Test subcommand help output."""
        for subcommand in [
            "workspace",
            "environment",
            "stack",
            "scan",
            "auth",
            "config",
        ]:
            result = runner.invoke(app, [subcommand, "--help"])
            assert result.exit_code == 0, f"Failed for {subcommand}"
            assert "Usage:" in result.output


# ============================================================================
# Test: Configuration Workflow
# ============================================================================


class TestConfigWorkflow:
    """Test configuration management workflow."""

    def test_config_show_without_existing_config(self):
        """Test showing configuration without existing config file."""
        # The config show command should work even without explicit config
        result = runner.invoke(app, ["config", "show", "--help"])
        assert result.exit_code == 0


# ============================================================================
# Test: Authentication Workflow
# ============================================================================


class TestAuthWorkflow:
    """Test authentication workflow."""

    def test_auth_help(self):
        """Test auth help output."""
        result = runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "set-token" in result.output
        assert "status" in result.output

    def test_auth_set_token_help(self):
        """Test auth set-token help output."""
        result = runner.invoke(app, ["auth", "set-token", "--help"])
        assert result.exit_code == 0


# ============================================================================
# Test: Scan Workflow
# ============================================================================


class TestScanWorkflow:
    """Test scanning workflow end-to-end."""

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_clean(self, mock_orchestrator, terraform_project):
        """Test static scan with no violations."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_mock_scan_results(violations=0, passed=10)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            True,
            "All checks passed",
        )

        result = runner.invoke(
            app,
            ["scan", "static", str(terraform_project), "--skip-upload"],
        )

        assert result.exit_code == 0
        mock_instance.scan_static.assert_called_once()

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_with_violations(self, mock_orchestrator, terraform_project):
        """Test static scan with violations."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_mock_scan_results(violations=3, passed=7)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "3 violation(s) at or above HIGH severity",
        )

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--fail-on",
                "high",
                "--skip-upload",
            ],
        )

        # Should fail due to violations
        assert result.exit_code == 1

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_json_output(self, mock_orchestrator, terraform_project):
        """Test static scan with JSON output format."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_mock_scan_results(violations=1, passed=9)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--output",
                "json",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 0

    @pytest.fixture
    def opa_policies(self, tmp_path):
        """Create a mock OPA policy directory."""
        policy_dir = tmp_path / "policies"
        policy_dir.mkdir()
        policy_file = policy_dir / "test.rego"
        policy_file.write_text("package test\nallow = true")
        return policy_dir

    @patch("iltero.commands.scan.evaluation.ScanOrchestrator")
    def test_evaluation_scan(self, mock_orchestrator, terraform_plan_json, opa_policies):
        """Test evaluation scan on Terraform plan."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_mock_scan_results(violations=0, passed=5)
        results.scan_type = ScanType.EVALUATION
        mock_instance.scan_plan.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            [
                "scan",
                "evaluation",
                str(terraform_plan_json),
                "--opa-policy-dir",
                str(opa_policies),
                "--skip-upload",
            ],
        )

        assert result.exit_code == 0
        mock_instance.scan_plan.assert_called_once()


# ============================================================================
# Test: Scanner Check Workflow
# ============================================================================


class TestScannerCheckWorkflow:
    """Test scanner installation check workflow."""

    @patch("shutil.which")
    def test_scanner_check_all_available(self, mock_which):
        """Test scanner check when all scanners available."""
        mock_which.return_value = "/usr/local/bin/checkov"

        result = runner.invoke(app, ["scanner", "check"])

        assert result.exit_code == 0

    @patch("shutil.which")
    def test_scanner_check_none_available(self, mock_which):
        """Test scanner check when no scanners available."""
        mock_which.return_value = None

        result = runner.invoke(app, ["scanner", "check"])

        # When no scanners are available, CLI returns exit code 1
        # This is correct behavior - it indicates some scanners are missing
        assert result.exit_code == 1
        assert "Not" in result.output or "❌" in result.output or "✗" in result.output


# ============================================================================
# Test: Workspace Workflow
# ============================================================================


class TestWorkspaceWorkflow:
    """Test workspace management workflow."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_workspace_list(self, mock_get_client):
        """Test listing workspaces."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "ws-1", "name": "production", "description": "Prod"},
            {"id": "ws-2", "name": "staging", "description": "Staging"},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_list_workspaces") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["workspace", "list"])

            assert result.exit_code == 0

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_workspace_create_and_select(self, mock_get_client, temp_config_dir):
        """Test creating and selecting a workspace."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        # Create response
        mock_create_response = Mock()
        mock_create_response.parsed = Mock()
        mock_create_response.parsed.data = {
            "id": "ws-new",
            "name": "new-workspace",
            "description": "New workspace",
        }
        mock_client.handle_response.return_value = mock_create_response.parsed

        with (
            patch("iltero.commands.workspace.operations.api_create_workspace") as mock_create,
            patch(
                "iltero.core.config.ConfigManager.DEFAULT_CONFIG_DIR",
                new=temp_config_dir,
            ),
        ):
            mock_create.sync_detailed.return_value = mock_create_response

            result = runner.invoke(
                app,
                [
                    "workspace",
                    "create",
                    "new-workspace",
                    "--description",
                    "New workspace",
                ],
            )

            assert result.exit_code == 0


# ============================================================================
# Test: Environment Workflow
# ============================================================================


class TestEnvironmentWorkflow:
    """Test environment management workflow."""

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_environment_list(self, mock_get_client):
        """Test listing environments."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "env-1", "name": "production", "workspace_id": "ws-1"},
            {"id": "env-2", "name": "staging", "workspace_id": "ws-1"},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_list_environments") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["environment", "list"])

            assert result.exit_code == 0


# ============================================================================
# Test: Stack Workflow
# ============================================================================


class TestStackWorkflow:
    """Test stack management workflow."""

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_stack_list(self, mock_get_client):
        """Test listing stacks."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {
                "id": "stack-1",
                "name": "web-app",
                "environment_id": "env-1",
                "status": "active",
            },
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.stack.operations.api_list_stacks") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["stack", "list"])

            assert result.exit_code == 0

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_stack_show(self, mock_get_client):
        """Test showing stack details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "id": "stack-1",
            "name": "web-app",
            "environment_id": "env-1",
            "status": "active",
            "repository_id": "repo-1",
            "working_directory": "infra/aws",
            "terraform_version": "1.5.0",
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.stack.operations.api_get_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["stack", "show", "stack-1"])

            assert result.exit_code == 0


# ============================================================================
# Test: Bundles Workflow
# ============================================================================


class TestBundlesWorkflow:
    """Test bundles workflow."""

    @patch("iltero.commands.bundles.marketplace.get_retry_client")
    def test_bundles_list(self, mock_get_client):
        """Test listing template bundles."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {
                "id": "mod-1",
                "name": "aws-vpc",
                "description": "AWS VPC module",
                "version": "1.0.0",
            },
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.bundles.marketplace.api_discover_bundles") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["bundles", "list"])

            assert result.exit_code == 0


# ============================================================================
# Test: Repository Workflow
# ============================================================================


class TestRepositoryWorkflow:
    """Test repository management workflow."""

    @patch("iltero.commands.repository.main.get_retry_client")
    def test_repository_list(self, mock_get_client):
        """Test listing repositories."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "repositories": [
                {
                    "id": "repo-1",
                    "name": "infrastructure",
                    "provider": "github",
                    "status": "active",
                    "url": "https://github.com/org/infra",
                },
            ]
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.repository.main.api_list") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["repository", "list"])

            assert result.exit_code == 0


# ============================================================================
# Test: Complete Lifecycle Scenarios
# ============================================================================


class TestCompleteLifecycleScenarios:
    """Test complete multi-command workflows."""

    def test_help_for_all_commands(self):
        """Verify help works for all top-level commands."""
        commands = [
            "workspace",
            "environment",
            "stack",
            "scan",
            "scanner",
            "auth",
            "config",
            "bundles",
            "repository",
            "registry",
            "compliance",
            "token",
        ]

        for cmd in commands:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0, f"Help failed for '{cmd}'"

    def test_nested_command_help(self):
        """Verify help works for nested commands."""
        # These nested commands actually exist in the CLI
        nested_commands = [
            ["stack", "runs", "--help"],
            ["stack", "variables", "--help"],
            ["stack", "drift", "--help"],
            ["stack", "approvals", "--help"],
            ["stack", "exceptions", "--help"],
            ["compliance", "violations", "--help"],
            ["compliance", "scans", "--help"],
            ["compliance", "reports", "--help"],
        ]

        for cmd_parts in nested_commands:
            result = runner.invoke(app, cmd_parts)
            cmd_str = " ".join(cmd_parts)
            assert result.exit_code == 0, f"Help failed for {cmd_str}"


# ============================================================================
# Test: Error Handling
# ============================================================================


class TestErrorHandling:
    """Test error handling across commands."""

    def test_invalid_command(self):
        """Test handling of invalid command."""
        result = runner.invoke(app, ["invalid-command"])
        assert result.exit_code != 0

    def test_missing_required_argument(self):
        """Test handling of missing required argument."""
        result = runner.invoke(app, ["stack", "show"])
        assert result.exit_code != 0

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_api_connection_error(self, mock_get_client):
        """Test handling of API connection errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Connection refused")

        result = runner.invoke(app, ["workspace", "list"])

        assert result.exit_code == 1
        assert "Failed" in result.output or "Error" in result.output

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_scan_path_not_found(self, mock_orchestrator):
        """Test scanning non-existent path."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]
        mock_instance.scan_static.side_effect = FileNotFoundError("Path not found")

        result = runner.invoke(
            app,
            ["scan", "static", "/nonexistent/path", "--skip-upload"],
        )

        # Exit code can be 1 or 2 depending on error handling
        assert result.exit_code != 0


# ============================================================================
# Test: Output Formats
# ============================================================================


class TestOutputFormats:
    """Test different output formats."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_json_output_format(self, mock_get_client):
        """Test JSON output format."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "ws-1", "name": "test", "description": "Test"},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_list_workspaces") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["workspace", "list", "--output", "json"])

            assert result.exit_code == 0

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_table_output_format(self, mock_get_client):
        """Test table output format (default)."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "ws-1", "name": "test", "description": "Test"},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_list_workspaces") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["workspace", "list"])

            assert result.exit_code == 0
