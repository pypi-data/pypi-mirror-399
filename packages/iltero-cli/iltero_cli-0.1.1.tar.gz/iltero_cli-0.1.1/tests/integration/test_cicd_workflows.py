"""CI/CD pipeline integration tests.

These tests validate webhook integration and CI/CD workflow scenarios.
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
def terraform_project(tmp_path):
    """Create a sample Terraform project for scanning."""
    project_dir = tmp_path / "terraform"
    project_dir.mkdir()

    main_tf = project_dir / "main.tf"
    main_tf.write_text("""
resource "aws_s3_bucket" "data" {
  bucket = "company-data-bucket"

  tags = {
    Environment = "production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}
""")
    return project_dir


@pytest.fixture
def terraform_plan_json(tmp_path):
    """Create a sample Terraform plan JSON file."""
    plan_file = tmp_path / "tfplan.json"
    plan_content = {
        "format_version": "1.2",
        "terraform_version": "1.5.7",
        "planned_values": {
            "root_module": {
                "resources": [
                    {
                        "address": "aws_s3_bucket.data",
                        "type": "aws_s3_bucket",
                        "name": "data",
                        "provider_name": "registry.terraform.io/hashicorp/aws",
                        "values": {
                            "bucket": "company-data-bucket",
                            "tags": {"Environment": "production", "ManagedBy": "Terraform"},
                        },
                    }
                ]
            }
        },
        "resource_changes": [
            {
                "address": "aws_s3_bucket.data",
                "mode": "managed",
                "type": "aws_s3_bucket",
                "name": "data",
                "change": {
                    "actions": ["create"],
                    "before": None,
                    "after": {
                        "bucket": "company-data-bucket",
                        "tags": {"Environment": "production", "ManagedBy": "Terraform"},
                    },
                },
            }
        ],
    }
    plan_file.write_text(json.dumps(plan_content, indent=2))
    return plan_file


def create_clean_scan_results() -> ScanResults:
    """Create scan results with no violations."""
    summary = ScanSummary(
        total_checks=15,
        passed=15,
        failed=0,
        skipped=0,
        critical=0,
        high=0,
        medium=0,
        low=0,
        info=0,
    )

    return ScanResults(
        scanner="checkov",
        version="3.0.0",
        scan_type=ScanType.STATIC,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        summary=summary,
        violations=[],
        metadata={"framework": "terraform"},
    )


def create_failing_scan_results(
    critical: int = 0,
    high: int = 0,
    medium: int = 0,
) -> ScanResults:
    """Create scan results with violations."""
    violations = []

    for i in range(critical):
        violations.append(
            Violation(
                check_id=f"CKV_AWS_CRIT_{i + 1}",
                check_name=f"Critical Check {i + 1}",
                severity=Severity.CRITICAL,
                resource=f"aws_s3_bucket.critical{i}",
                file_path="main.tf",
                line_range=(10, 15),
                description="Critical security issue",
            )
        )

    for i in range(high):
        violations.append(
            Violation(
                check_id=f"CKV_AWS_HIGH_{i + 1}",
                check_name=f"High Check {i + 1}",
                severity=Severity.HIGH,
                resource=f"aws_s3_bucket.high{i}",
                file_path="main.tf",
                line_range=(20, 25),
                description="High severity issue",
            )
        )

    for i in range(medium):
        violations.append(
            Violation(
                check_id=f"CKV_AWS_MED_{i + 1}",
                check_name=f"Medium Check {i + 1}",
                severity=Severity.MEDIUM,
                resource=f"aws_s3_bucket.medium{i}",
                file_path="main.tf",
                line_range=(30, 35),
                description="Medium severity issue",
            )
        )

    summary = ScanSummary(
        total_checks=15 + len(violations),
        passed=15,
        failed=len(violations),
        skipped=0,
        critical=critical,
        high=high,
        medium=medium,
        low=0,
        info=0,
    )

    return ScanResults(
        scanner="checkov",
        version="3.0.0",
        scan_type=ScanType.STATIC,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        summary=summary,
        violations=violations,
        metadata={"framework": "terraform"},
    )


# ============================================================================
# Test: Validate Phase (Pre-Plan Scanning)
# ============================================================================


class TestValidatePhase:
    """Test validate phase workflow - runs before terraform plan."""

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_validate_phase_passes(self, mock_orchestrator, terraform_project):
        """Test validate phase when all checks pass."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_clean_scan_results()
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "All checks passed")

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

        assert result.exit_code == 0
        mock_instance.scan_static.assert_called_once()

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_validate_phase_fails_on_critical(self, mock_orchestrator, terraform_project):
        """Test validate phase fails when critical violations found."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(critical=2)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "2 violation(s) at or above CRITICAL severity",
        )

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--fail-on",
                "critical",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 1

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_validate_phase_with_webhook_submission(self, mock_orchestrator, terraform_project):
        """Test validate phase with webhook submission."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_clean_scan_results()
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            mock_auth = Mock()
            mock_client.get_authenticated_client.return_value = mock_auth

            mock_response = Mock()
            mock_response.parsed = Mock()
            mock_response.parsed.data = {"id": "scan-123", "status": "completed"}
            mock_client.handle_response.return_value = mock_response.parsed

            with patch("iltero.commands.scan.main.webhook_validation_phase") as mock_submit:
                mock_submit.sync_detailed.return_value = mock_response

                result = runner.invoke(
                    app,
                    [
                        "scan",
                        "static",
                        str(terraform_project),
                        "--stack-id",
                        "stack-123",
                    ],
                )

                # Should attempt to submit results
                assert result.exit_code == 0


# ============================================================================
# Test: Plan Phase (Post-Plan Evaluation)
# ============================================================================


class TestPlanPhase:
    """Test plan phase workflow - evaluates terraform plan output."""

    @pytest.fixture
    def opa_policies(self, tmp_path):
        """Create a mock OPA policy directory."""
        policy_dir = tmp_path / "policies"
        policy_dir.mkdir()
        # Create a minimal policy file
        policy_file = policy_dir / "test.rego"
        policy_file.write_text("package test\nallow = true")
        return policy_dir

    @patch("iltero.commands.scan.evaluation.ScanOrchestrator")
    def test_plan_phase_passes(self, mock_orchestrator, terraform_plan_json, opa_policies):
        """Test plan phase when evaluation passes."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_clean_scan_results()
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

    @patch("iltero.commands.scan.evaluation.ScanOrchestrator")
    def test_plan_phase_fails_on_high(self, mock_orchestrator, terraform_plan_json, opa_policies):
        """Test plan phase fails when high severity violations found."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(high=3)
        results.scan_type = ScanType.EVALUATION
        mock_instance.scan_plan.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "3 violation(s) at or above HIGH severity",
        )

        result = runner.invoke(
            app,
            [
                "scan",
                "evaluation",
                str(terraform_plan_json),
                "--opa-policy-dir",
                str(opa_policies),
                "--fail-on",
                "high",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 1


# ============================================================================
# Test: Apply Phase (Post-Deployment)
# ============================================================================


class TestApplyPhase:
    """Test apply phase workflow - runs after terraform apply."""

    @pytest.fixture
    def custodian_policies(self, tmp_path):
        """Create a mock Cloud Custodian policy directory."""
        policy_dir = tmp_path / "custodian"
        policy_dir.mkdir()
        policy_file = policy_dir / "policy.yaml"
        policy_file.write_text("policies: []")
        return policy_dir

    @patch("iltero.commands.scan.runtime.CloudCustodianScanner")
    def test_apply_phase_runtime_scan(self, mock_scanner_class, custodian_policies):
        """Test apply phase runs runtime scan."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.is_available.return_value = True

        results = create_clean_scan_results()
        results.scan_type = ScanType.RUNTIME
        mock_scanner.scan_runtime.return_value = results

        runner.invoke(
            app,
            [
                "scan",
                "runtime",
                str(custodian_policies),
                "--run-id",
                "run-123",
                "--skip-upload",
            ],
        )

        # Should attempt to run the scan
        assert mock_scanner_class.called


# ============================================================================
# Test: CI/CD Exit Codes
# ============================================================================


class TestCICDExitCodes:
    """Test CI/CD-friendly exit codes."""

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_exit_code_0_on_success(self, mock_orchestrator, terraform_project):
        """Test exit code 0 when scan passes."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_clean_scan_results()
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            ["scan", "static", str(terraform_project), "--skip-upload"],
        )

        assert result.exit_code == 0

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_exit_code_1_on_policy_failure(self, mock_orchestrator, terraform_project):
        """Test exit code 1 when policy check fails."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(high=1)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "Policy violations found",
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

        assert result.exit_code == 1

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_exit_code_1_on_error(self, mock_orchestrator, terraform_project):
        """Test exit code non-zero on scanner error."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]
        mock_instance.scan_static.side_effect = RuntimeError("Scanner crashed")

        result = runner.invoke(
            app,
            ["scan", "static", str(terraform_project), "--skip-upload"],
        )

        # Scanner error should result in non-zero exit code
        assert result.exit_code != 0


# ============================================================================
# Test: Output Formats for CI/CD
# ============================================================================


class TestCICDOutputFormats:
    """Test CI/CD-friendly output formats."""

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_json_output_for_parsing(self, mock_orchestrator, terraform_project):
        """Test JSON output can be parsed by CI tools."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(high=2, medium=3)
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

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_sarif_output_for_github(self, mock_orchestrator, terraform_project):
        """Test SARIF output for GitHub Security."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(high=1)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--output",
                "sarif",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 0

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_junit_output_for_jenkins(self, mock_orchestrator, terraform_project):
        """Test JUnit output for Jenkins/CI servers."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(medium=2)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--output",
                "junit",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 0


# ============================================================================
# Test: Threshold Configuration
# ============================================================================


class TestThresholdConfiguration:
    """Test configurable failure thresholds."""

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_fail_on_critical_only(self, mock_orchestrator, terraform_project):
        """Test only failing on critical violations."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        # Has high violations but no critical
        results = create_failing_scan_results(high=5)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--fail-on",
                "critical",
                "--skip-upload",
            ],
        )

        # Should pass because no critical violations
        assert result.exit_code == 0

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_fail_on_medium_and_above(self, mock_orchestrator, terraform_project):
        """Test failing on medium and above violations."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(medium=3)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "3 violation(s) at or above MEDIUM severity",
        )

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--fail-on",
                "medium",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 1

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_max_violations_threshold(self, mock_orchestrator, terraform_project):
        """Test maximum violations threshold."""
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        results = create_failing_scan_results(medium=10)
        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "10 violations exceeds maximum of 5",
        )

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--max-violations",
                "5",
                "--skip-upload",
            ],
        )

        assert result.exit_code == 1


# ============================================================================
# Test: Pipeline Scenarios
# ============================================================================


class TestPipelineScenarios:
    """Test realistic pipeline scenarios."""

    @pytest.fixture
    def opa_policies(self, tmp_path):
        """Create a mock OPA policy directory."""
        policy_dir = tmp_path / "policies"
        policy_dir.mkdir()
        policy_file = policy_dir / "test.rego"
        policy_file.write_text("package test\nallow = true")
        return policy_dir

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    @patch("iltero.commands.scan.evaluation.ScanOrchestrator")
    def test_github_actions_workflow(
        self,
        mock_eval_orchestrator,
        mock_static_orchestrator,
        terraform_project,
        terraform_plan_json,
        opa_policies,
    ):
        """Simulate GitHub Actions workflow."""
        # Setup static scan mock
        static_instance = Mock()
        mock_static_orchestrator.return_value = static_instance
        static_instance.available_scanners = ["checkov"]

        static_results = create_clean_scan_results()
        static_instance.scan_static.return_value = static_results
        static_instance.check_thresholds.return_value = (True, "")

        # 1. Run static scan (validate phase)
        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_project),
                "--fail-on",
                "high",
                "--output",
                "sarif",
                "--skip-upload",
            ],
        )
        assert result.exit_code == 0

        # Setup evaluation scan mock
        eval_instance = Mock()
        mock_eval_orchestrator.return_value = eval_instance
        eval_instance.available_scanners = ["checkov"]

        eval_results = create_clean_scan_results()
        eval_results.scan_type = ScanType.EVALUATION
        eval_instance.scan_plan.return_value = eval_results
        eval_instance.check_thresholds.return_value = (True, "")

        # 2. Run plan evaluation (plan phase)
        result = runner.invoke(
            app,
            [
                "scan",
                "evaluation",
                str(terraform_plan_json),
                "--opa-policy-dir",
                str(opa_policies),
                "--fail-on",
                "high",
                "--skip-upload",
            ],
        )
        assert result.exit_code == 0

    @patch("shutil.which")
    def test_scanner_availability_check(self, mock_which):
        """Test scanner availability check in CI."""
        mock_which.return_value = "/usr/local/bin/checkov"

        result = runner.invoke(
            app,
            ["scanner", "check"],
        )

        assert result.exit_code == 0
