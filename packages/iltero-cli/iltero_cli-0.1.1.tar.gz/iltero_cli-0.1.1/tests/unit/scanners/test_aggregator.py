"""Tests for ResultAggregator."""

from datetime import UTC, datetime

import pytest

from iltero.scanners.aggregator import ResultAggregator
from iltero.scanners.models import (
    ScanResults,
    ScanSummary,
    ScanType,
    Severity,
    Violation,
)


class TestResultAggregator:
    """Test ResultAggregator."""

    def test_merge_empty_list_raises_error(self):
        """Test merging empty list raises error."""
        with pytest.raises(ValueError, match="No results to merge"):
            ResultAggregator.merge([])

    def test_merge_single_result(self):
        """Test merging a single result returns it."""
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
            check_id="V1",
            check_name="Test",
            severity=Severity.HIGH,
            resource="resource",
            file_path="file.tf",
            line_range=(1, 1),
            description="Test",
        )

        result = ScanResults(
            scanner="checkov",
            version="1.0",
            scan_type=ScanType.STATIC,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            summary=summary,
            violations=[violation],
        )

        merged = ResultAggregator.merge([result])
        assert merged.scanner == "combined"
        assert len(merged.violations) == 1

    def test_merge_multiple_results(self):
        """Test merging multiple scanner results."""
        now = datetime.now(UTC)

        # First scanner result
        summary1 = ScanSummary(
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

        violation1 = Violation(
            check_id="V1",
            check_name="Test1",
            severity=Severity.CRITICAL,
            resource="resource1",
            file_path="file1.tf",
            line_range=(1, 1),
            description="Test1",
        )

        result1 = ScanResults(
            scanner="checkov",
            version="1.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary1,
            violations=[violation1],
        )

        # Second scanner result
        summary2 = ScanSummary(
            total_checks=5,
            passed=3,
            failed=2,
            skipped=0,
            critical=0,
            high=1,
            medium=1,
            low=0,
            info=0,
        )

        violation2 = Violation(
            check_id="V2",
            check_name="Test2",
            severity=Severity.HIGH,
            resource="resource2",
            file_path="file2.tf",
            line_range=(2, 2),
            description="Test2",
        )

        result2 = ScanResults(
            scanner="opa",
            version="0.50.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary2,
            violations=[violation2],
        )

        # Merge results
        merged = ResultAggregator.merge([result1, result2])

        assert merged.scanner == "combined"
        assert merged.summary.total_checks == 15
        assert merged.summary.passed == 11
        assert merged.summary.failed == 2  # Unique violations
        assert len(merged.violations) == 2

    def test_deduplication_same_check_and_resource(self):
        """Test violations are deduplicated by check_id + resource."""
        now = datetime.now(UTC)

        # Create two results with the same violation
        violation = Violation(
            check_id="V1",
            check_name="Test",
            severity=Severity.HIGH,
            resource="resource1",
            file_path="file.tf",
            line_range=(1, 1),
            description="Test",
        )

        summary = ScanSummary(
            total_checks=5,
            passed=4,
            failed=1,
            skipped=0,
            critical=0,
            high=1,
            medium=0,
            low=0,
            info=0,
        )

        result1 = ScanResults(
            scanner="scanner1",
            version="1.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[violation],
        )

        result2 = ScanResults(
            scanner="scanner2",
            version="2.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[violation],
        )

        merged = ResultAggregator.merge([result1, result2])

        # Should have only 1 violation after deduplication
        assert len(merged.violations) == 1
        assert merged.summary.failed == 1

    def test_filter_by_severity(self):
        """Test filtering violations by severity."""
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
                severity=Severity.MEDIUM,
                resource="r3",
                file_path="f3",
                line_range=(3, 3),
                description="medium",
            ),
            Violation(
                check_id="V4",
                check_name="V4",
                severity=Severity.LOW,
                resource="r4",
                file_path="f4",
                line_range=(4, 4),
                description="low",
            ),
        ]

        summary = ScanSummary(
            total_checks=10,
            passed=6,
            failed=4,
            skipped=0,
            critical=1,
            high=1,
            medium=1,
            low=1,
            info=0,
        )

        results = ScanResults(
            scanner="test",
            version="1.0",
            scan_type=ScanType.STATIC,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            summary=summary,
            violations=violations,
        )

        # Filter to HIGH and above
        filtered = ResultAggregator.filter_by_severity(results, Severity.HIGH)

        assert len(filtered.violations) == 2
        assert filtered.summary.failed == 2
        assert filtered.summary.critical == 1
        assert filtered.summary.high == 1
        assert filtered.summary.medium == 0

    def test_filter_by_critical_only(self):
        """Test filtering to critical only."""
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
        ]

        summary = ScanSummary(
            total_checks=5,
            passed=3,
            failed=2,
            skipped=0,
            critical=1,
            high=1,
            medium=0,
            low=0,
            info=0,
        )

        results = ScanResults(
            scanner="test",
            version="1.0",
            scan_type=ScanType.STATIC,
            started_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            summary=summary,
            violations=violations,
        )

        filtered = ResultAggregator.filter_by_severity(
            results,
            Severity.CRITICAL,
        )

        assert len(filtered.violations) == 1
        assert filtered.violations[0].severity == Severity.CRITICAL
