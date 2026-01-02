"""Tests for scanner models."""

from datetime import UTC, datetime

from iltero.scanners.models import (
    ScanResults,
    ScanSummary,
    ScanType,
    Severity,
    Violation,
)


class TestSeverity:
    """Test Severity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert Severity.CRITICAL.value == "critical"
        assert Severity.HIGH.value == "high"
        assert Severity.MEDIUM.value == "medium"
        assert Severity.LOW.value == "low"
        assert Severity.INFO.value == "info"

    def test_severity_ordering(self):
        """Test severity can be compared."""
        assert Severity.CRITICAL != Severity.HIGH
        assert Severity.HIGH != Severity.MEDIUM


class TestScanType:
    """Test ScanType enum."""

    def test_scan_type_values(self):
        """Test scan type enum values."""
        assert ScanType.STATIC.value == "static"
        assert ScanType.EVALUATION.value == "evaluation"
        assert ScanType.RUNTIME.value == "runtime"


class TestViolation:
    """Test Violation model."""

    def test_create_violation(self):
        """Test creating a violation."""
        violation = Violation(
            check_id="CKV_AWS_1",
            check_name="Ensure S3 bucket has encryption",
            severity=Severity.HIGH,
            resource="aws_s3_bucket.example",
            file_path="main.tf",
            line_range=(10, 15),
            description="S3 bucket is not encrypted",
        )

        assert violation.check_id == "CKV_AWS_1"
        assert violation.severity == Severity.HIGH
        assert violation.line_range == (10, 15)

    def test_violation_optional_fields(self):
        """Test violation with optional fields."""
        violation = Violation(
            check_id="TEST_1",
            check_name="Test",
            severity=Severity.MEDIUM,
            resource="resource",
            file_path="file.tf",
            line_range=(1, 1),
            description="Test",
            remediation="Fix it",
            framework="terraform",
            metadata={"key": "value"},
        )

        assert violation.remediation == "Fix it"
        assert violation.framework == "terraform"
        assert violation.metadata == {"key": "value"}


class TestScanSummary:
    """Test ScanSummary model."""

    def test_create_summary(self):
        """Test creating a scan summary."""
        summary = ScanSummary(
            total_checks=100,
            passed=80,
            failed=15,
            skipped=5,
            critical=2,
            high=5,
            medium=6,
            low=2,
            info=0,
        )

        assert summary.total_checks == 100
        assert summary.passed == 80
        assert summary.failed == 15
        assert summary.total_violations == 15

    def test_summary_total_violations(self):
        """Test total_violations calculation."""
        summary = ScanSummary(
            total_checks=50,
            passed=30,
            failed=20,
            skipped=0,
            critical=5,
            high=8,
            medium=4,
            low=2,
            info=1,
        )

        assert summary.total_violations == 20


class TestScanResults:
    """Test ScanResults model."""

    def test_create_scan_results(self):
        """Test creating scan results."""
        started_at = datetime.now(UTC)
        completed_at = datetime.now(UTC)

        summary = ScanSummary(
            total_checks=10,
            passed=8,
            failed=2,
            skipped=0,
            critical=1,
            high=1,
            medium=0,
            low=0,
            info=0,
        )

        violation = Violation(
            check_id="TEST_1",
            check_name="Test",
            severity=Severity.HIGH,
            resource="resource",
            file_path="file.tf",
            line_range=(1, 1),
            description="Test violation",
        )

        results = ScanResults(
            scanner="checkov",
            version="2.5.0",
            scan_type=ScanType.STATIC,
            started_at=started_at,
            completed_at=completed_at,
            summary=summary,
            violations=[violation],
        )

        assert results.scanner == "checkov"
        assert results.version == "2.5.0"
        assert results.scan_type == ScanType.STATIC
        assert len(results.violations) == 1
        assert results.summary.failed == 2

    def test_get_violations_by_severity(self):
        """Test grouping violations by severity."""
        summary = ScanSummary(
            total_checks=10,
            passed=5,
            failed=3,  # 3 violations total
            skipped=2,
            critical=1,
            high=2,
            medium=0,  # No medium violations
            low=0,
            info=0,
        )

        violations = [
            Violation(
                check_id="V1",
                check_name="V1",
                severity=Severity.CRITICAL,
                resource="r1",
                file_path="f1",
                line_range=(1, 1),
                description="critical",
            ),
            Violation(
                check_id="V2",
                check_name="V2",
                severity=Severity.HIGH,
                resource="r2",
                file_path="f2",
                line_range=(2, 2),
                description="high",
            ),
            Violation(
                check_id="V3",
                check_name="V3",
                severity=Severity.HIGH,
                resource="r3",
                file_path="f3",
                line_range=(3, 3),
                description="high2",
            ),
        ]

        results = ScanResults(
            scanner="test",
            version="1.0",
            scan_type=ScanType.STATIC,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            summary=summary,
            violations=violations,
        )

        by_severity = results.get_violations_by_severity()
        assert by_severity["critical"] == 1
        assert by_severity["high"] == 2
        assert by_severity["medium"] == 0
