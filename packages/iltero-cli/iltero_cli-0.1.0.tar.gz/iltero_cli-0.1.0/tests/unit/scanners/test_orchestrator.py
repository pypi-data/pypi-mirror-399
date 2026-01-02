"""Tests for ScanOrchestrator."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from iltero.core.exceptions import ScannerError
from iltero.scanners.checkov import CheckovScanner
from iltero.scanners.models import (
    ScanResults,
    ScanSummary,
    ScanType,
    Severity,
    Violation,
)
from iltero.scanners.opa import OPAScanner
from iltero.scanners.orchestrator import ScanOrchestrator


def create_violation(
    check_id: str,
    severity: Severity,
    description: str = "Test violation",
) -> Violation:
    """Helper to create a Violation with all required fields."""
    return Violation(
        check_id=check_id,
        check_name=f"Test Check {check_id}",
        severity=severity,
        resource="test_resource.example",
        file_path="main.tf",
        line_range=(10, 15),
        description=description,
    )


def create_scan_results(
    violations: list[Violation] | None = None,
    scanner: str = "checkov",
) -> ScanResults:
    """Helper to create ScanResults with all required fields."""
    if violations is None:
        violations = []

    summary = ScanSummary(
        total_checks=10,
        passed=10 - len(violations),
        failed=len(violations),
        skipped=0,
        critical=sum(1 for v in violations if v.severity == Severity.CRITICAL),
        high=sum(1 for v in violations if v.severity == Severity.HIGH),
        medium=sum(1 for v in violations if v.severity == Severity.MEDIUM),
        low=sum(1 for v in violations if v.severity == Severity.LOW),
        info=sum(1 for v in violations if v.severity == Severity.INFO),
    )

    return ScanResults(
        scanner=scanner,
        version="1.0.0",
        scan_type=ScanType.STATIC,
        started_at=datetime.now(UTC),
        completed_at=datetime.now(UTC),
        summary=summary,
        violations=violations,
    )


@pytest.fixture
def mock_checkov_scanner():
    """Create a mock Checkov scanner."""
    scanner = MagicMock(spec=CheckovScanner)
    scanner.is_available.return_value = True
    return scanner


@pytest.fixture
def mock_opa_scanner():
    """Create a mock OPA scanner."""
    scanner = MagicMock(spec=OPAScanner)
    scanner.is_available.return_value = True
    return scanner


@pytest.fixture
def sample_scan_results():
    """Create sample scan results."""
    return create_scan_results(
        violations=[
            create_violation("CKV_AWS_1", Severity.HIGH, "Test violation 1"),
            create_violation("CKV_AWS_2", Severity.MEDIUM, "Test violation 2"),
            create_violation("CKV_AWS_3", Severity.LOW, "Test violation 3"),
        ]
    )


class TestScanOrchestratorInit:
    """Tests for ScanOrchestrator initialization."""

    def test_init_with_defaults(self):
        """Test initialization with default settings."""
        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            assert orchestrator.checkov_enabled is True
            assert orchestrator.opa_enabled is False
            assert orchestrator.parallel is True
            assert orchestrator.timeout == 300
            assert orchestrator.policy_sets == []
            assert orchestrator.frameworks == []

    def test_init_with_custom_settings(self):
        """Test initialization with custom settings."""
        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator(
                checkov_enabled=False,
                opa_enabled=True,
                parallel=False,
                timeout=600,
                policy_sets=["cis", "soc2"],
                frameworks=["AWS", "GCP"],
                opa_policy_dir="/path/to/policies",
            )
            assert orchestrator.checkov_enabled is False
            assert orchestrator.opa_enabled is True
            assert orchestrator.parallel is False
            assert orchestrator.timeout == 600
            assert orchestrator.policy_sets == ["cis", "soc2"]
            assert orchestrator.frameworks == ["AWS", "GCP"]

    def test_init_adds_checkov_when_available(self):
        """Test Checkov scanner is added when available."""
        with patch.object(CheckovScanner, "is_available", return_value=True):
            orchestrator = ScanOrchestrator(checkov_enabled=True)
            assert "CheckovScanner" in orchestrator.available_scanners

    def test_init_skips_checkov_when_unavailable(self):
        """Test Checkov scanner skipped when unavailable."""
        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator(checkov_enabled=True)
            assert "CheckovScanner" not in orchestrator.available_scanners

    def test_init_adds_opa_when_available(self):
        """Test OPA scanner is added when available."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=False),
            patch.object(OPAScanner, "is_available", return_value=True),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=False,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
            )
            assert "OPAScanner" in orchestrator.available_scanners


class TestScanOrchestratorScan:
    """Tests for scan operations."""

    def test_scan_static_no_scanners_raises_error(self):
        """Test static scan with no available scanners."""
        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator(checkov_enabled=True, opa_enabled=False)
            with pytest.raises(ScannerError, match="No scanners available"):
                orchestrator.scan_static("/path/to/terraform")

    def test_scan_plan_no_scanners_raises_error(self):
        """Test plan scan with no available scanners."""
        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator(checkov_enabled=True, opa_enabled=False)
            with pytest.raises(ScannerError, match="No scanners available"):
                orchestrator.scan_plan("/path/to/plan.json")

    def test_scan_static_with_checkov(self, sample_scan_results):
        """Test static scan with Checkov scanner."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=sample_scan_results),
        ):
            orchestrator = ScanOrchestrator(checkov_enabled=True)
            results = orchestrator.scan_static("/path/to/terraform", show_progress=False)
            assert results.summary.total_violations == 3

    def test_scan_plan_with_checkov(self, sample_scan_results):
        """Test plan scan with Checkov scanner."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=sample_scan_results),
        ):
            orchestrator = ScanOrchestrator(checkov_enabled=True)
            results = orchestrator.scan_plan("/path/to/plan.json", show_progress=False)
            assert results.summary.total_violations == 3


class TestScanOrchestratorThresholds:
    """Tests for threshold checking."""

    def test_check_thresholds_passes_with_no_violations(self):
        """Test threshold check passes with no violations."""
        results = create_scan_results(violations=[])

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(results)
            assert passed is True
            assert message == "All checks passed"

    def test_check_thresholds_fails_on_critical(self):
        """Test threshold check fails on critical violations."""
        results = create_scan_results(
            violations=[
                create_violation("CKV_AWS_1", Severity.CRITICAL, "Critical"),
            ]
        )

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(results, fail_on=Severity.CRITICAL)
            assert passed is False
            assert "1 violation(s)" in message
            assert "critical" in message.lower()

    def test_check_thresholds_fails_on_high(self):
        """Test threshold check fails on high and critical violations."""
        results = create_scan_results(
            violations=[
                create_violation("CKV_AWS_1", Severity.HIGH, "High issue"),
                create_violation("CKV_AWS_2", Severity.MEDIUM, "Med issue"),
            ]
        )

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(results, fail_on=Severity.HIGH)
            assert passed is False
            assert "1 violation(s)" in message

    def test_check_thresholds_max_violations_exceeded(self):
        """Test threshold check fails when max violations exceeded."""
        results = create_scan_results(
            violations=[
                create_violation(f"CKV_AWS_{i}", Severity.INFO, f"Info {i}") for i in range(5)
            ]
        )

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(
                results, fail_on=Severity.CRITICAL, max_violations=3
            )
            assert passed is False
            assert "5 violations" in message
            assert "exceeds maximum of 3" in message

    def test_check_thresholds_max_violations_not_exceeded(self):
        """Test threshold check passes when under max violations."""
        results = create_scan_results(
            violations=[
                create_violation(f"CKV_AWS_{i}", Severity.INFO, f"Info {i}") for i in range(2)
            ]
        )

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(
                results, fail_on=Severity.CRITICAL, max_violations=5
            )
            assert passed is True
            assert message == "All checks passed"

    def test_check_thresholds_medium_severity(self):
        """Test threshold check with medium severity."""
        results = create_scan_results(
            violations=[
                create_violation("CKV_1", Severity.HIGH, "High"),
                create_violation("CKV_2", Severity.MEDIUM, "Medium"),
                create_violation("CKV_3", Severity.LOW, "Low"),
            ]
        )

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(results, fail_on=Severity.MEDIUM)
            assert passed is False
            # HIGH + MEDIUM = 2 violations
            assert "2 violation(s)" in message

    def test_check_thresholds_low_severity(self):
        """Test threshold check with low severity includes all."""
        results = create_scan_results(
            violations=[
                create_violation("CKV_1", Severity.MEDIUM, "Medium"),
                create_violation("CKV_2", Severity.LOW, "Low"),
                create_violation("CKV_3", Severity.INFO, "Info"),
            ]
        )

        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator()
            passed, message = orchestrator.check_thresholds(results, fail_on=Severity.LOW)
            assert passed is False
            # MEDIUM + LOW = 2
            assert "2 violation(s)" in message


class TestScanOrchestratorRunModes:
    """Tests for parallel/sequential execution."""

    def test_sequential_execution_when_parallel_disabled(self, sample_scan_results):
        """Test sequential execution when parallel is False."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=sample_scan_results),
        ):
            orchestrator = ScanOrchestrator(checkov_enabled=True, parallel=False)
            results = orchestrator.scan_static("/path/to/terraform", show_progress=False)
            assert results.summary.total_violations == 3

    def test_scanner_error_handling(self):
        """Test handling of scanner errors."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", side_effect=Exception("Scanner failed")),
        ):
            orchestrator = ScanOrchestrator(checkov_enabled=True)
            with pytest.raises(ScannerError, match="All scanners failed"):
                orchestrator.scan_static("/path/to/terraform", show_progress=False)

    def test_parallel_execution_multiple_scanners(self):
        """Test parallel execution with multiple scanners."""
        checkov_results = create_scan_results(
            violations=[
                create_violation("CKV_1", Severity.HIGH, "Checkov violation"),
            ],
            scanner="checkov",
        )
        opa_results = create_scan_results(
            violations=[
                create_violation("OPA_1", Severity.MEDIUM, "OPA violation"),
            ],
            scanner="opa",
        )

        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=checkov_results),
            patch.object(OPAScanner, "is_available", return_value=True),
            patch.object(OPAScanner, "scan", return_value=opa_results),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=True,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
                parallel=True,
            )
            results = orchestrator.scan_plan("/path/to/plan.json", show_progress=False)
            # Results from both scanners should be merged
            assert results.summary.total_violations == 2

    def test_sequential_execution_multiple_scanners(self):
        """Test sequential execution with multiple scanners."""
        checkov_results = create_scan_results(
            violations=[
                create_violation("CKV_1", Severity.HIGH, "Checkov"),
            ],
            scanner="checkov",
        )
        opa_results = create_scan_results(
            violations=[
                create_violation("OPA_1", Severity.LOW, "OPA"),
            ],
            scanner="opa",
        )

        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=checkov_results),
            patch.object(OPAScanner, "is_available", return_value=True),
            patch.object(OPAScanner, "scan", return_value=opa_results),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=True,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
                parallel=False,
            )
            results = orchestrator.scan_plan("/path/to/plan.json", show_progress=False)
            assert results.summary.total_violations == 2

    def test_partial_scanner_failure_parallel(self):
        """Test partial failure in parallel mode."""
        checkov_results = create_scan_results(
            violations=[
                create_violation("CKV_1", Severity.HIGH, "Checkov"),
            ],
            scanner="checkov",
        )

        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=checkov_results),
            patch.object(OPAScanner, "is_available", return_value=True),
            patch.object(OPAScanner, "scan", side_effect=Exception("OPA failed")),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=True,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
                parallel=True,
            )
            # Should not raise, should return partial results
            results = orchestrator.scan_plan("/path/to/plan.json", show_progress=False)
            assert results.summary.total_violations == 1

    def test_partial_scanner_failure_sequential(self):
        """Test partial failure in sequential mode."""
        checkov_results = create_scan_results(
            violations=[
                create_violation("CKV_1", Severity.CRITICAL, "Critical"),
            ],
            scanner="checkov",
        )

        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=checkov_results),
            patch.object(OPAScanner, "is_available", return_value=True),
            patch.object(OPAScanner, "scan", side_effect=Exception("OPA error")),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=True,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
                parallel=False,
            )
            results = orchestrator.scan_plan("/path/to/plan.json", show_progress=False)
            assert results.summary.total_violations == 1

    def test_show_progress_parallel(self, sample_scan_results):
        """Test parallel execution with progress display."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=sample_scan_results),
            patch("iltero.scanners.orchestrator.Progress") as mock_progress,
        ):
            # Setup progress context manager mock
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
            mock_progress.return_value.__exit__ = MagicMock(return_value=None)
            mock_progress_instance.add_task.return_value = 1

            orchestrator = ScanOrchestrator(checkov_enabled=True, parallel=True)
            results = orchestrator.scan_static("/path/to/terraform", show_progress=True)
            assert results.summary.total_violations == 3
            mock_progress_instance.add_task.assert_called()

    def test_show_progress_sequential(self, sample_scan_results):
        """Test sequential execution with progress display."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", return_value=sample_scan_results),
            patch("iltero.scanners.orchestrator.Progress") as mock_progress,
        ):
            mock_progress_instance = MagicMock()
            mock_progress.return_value.__enter__ = MagicMock(return_value=mock_progress_instance)
            mock_progress.return_value.__exit__ = MagicMock(return_value=None)

            orchestrator = ScanOrchestrator(checkov_enabled=True, parallel=False)
            results = orchestrator.scan_static("/path/to/terraform", show_progress=True)
            assert results.summary.total_violations == 3
            mock_progress_instance.add_task.assert_called()

    def test_all_scanners_fail_raises_error(self):
        """Test that error is raised when all scanners fail."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(CheckovScanner, "scan", side_effect=Exception("Checkov failed")),
            patch.object(OPAScanner, "is_available", return_value=True),
            patch.object(OPAScanner, "scan", side_effect=Exception("OPA failed")),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=True,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
                parallel=True,
            )
            with pytest.raises(ScannerError, match="All scanners failed"):
                orchestrator.scan_plan("/path/to/plan.json", show_progress=False)


class TestScanOrchestratorAvailableScanners:
    """Tests for available_scanners property."""

    def test_available_scanners_empty_when_none(self):
        """Test available_scanners is empty when no scanners available."""
        with patch.object(CheckovScanner, "is_available", return_value=False):
            orchestrator = ScanOrchestrator(checkov_enabled=True, opa_enabled=False)
            assert orchestrator.available_scanners == []

    def test_available_scanners_with_multiple(self):
        """Test available_scanners with multiple scanners."""
        with (
            patch.object(CheckovScanner, "is_available", return_value=True),
            patch.object(OPAScanner, "is_available", return_value=True),
        ):
            orchestrator = ScanOrchestrator(
                checkov_enabled=True,
                opa_enabled=True,
                opa_policy_dir="/path/to/policies",
            )
            scanners = orchestrator.available_scanners
            assert "CheckovScanner" in scanners
            assert "OPAScanner" in scanners
