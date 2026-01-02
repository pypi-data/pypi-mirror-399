"""Result aggregation for multiple scanners."""

from __future__ import annotations

from .models import ScanResults, ScanSummary, Severity, Violation


class ResultAggregator:
    """Aggregates results from multiple scanners."""

    @staticmethod
    def merge(results_list: list[ScanResults]) -> ScanResults:
        """Merge multiple ScanResults into one.

        Args:
            results_list: List of ScanResults from different scanners.

        Returns:
            Merged ScanResults with deduplicated violations.

        Raises:
            ValueError: If no results to merge.
        """
        if not results_list:
            raise ValueError("No results to merge")

        # Use first result as template
        first = results_list[0]

        # Merge violations from all scanners
        all_violations: list[Violation] = []
        for result in results_list:
            all_violations.extend(result.violations)

        # Deduplicate violations (same check_id + resource)
        unique_violations = ResultAggregator._deduplicate(all_violations)

        # Recalculate summary
        merged_summary = ScanSummary(
            total_checks=sum(r.summary.total_checks for r in results_list),
            passed=sum(r.summary.passed for r in results_list),
            failed=len(unique_violations),
            skipped=sum(r.summary.skipped for r in results_list),
            critical=sum(1 for v in unique_violations if v.severity == Severity.CRITICAL),
            high=sum(1 for v in unique_violations if v.severity == Severity.HIGH),
            medium=sum(1 for v in unique_violations if v.severity == Severity.MEDIUM),
            low=sum(1 for v in unique_violations if v.severity == Severity.LOW),
            info=sum(1 for v in unique_violations if v.severity == Severity.INFO),
        )

        # Build scanner info
        scanner_names = [r.scanner for r in results_list]
        scanner_versions = {r.scanner: r.version for r in results_list}

        version_str = ", ".join(f"{r.scanner}:{r.version}" for r in results_list)

        return ScanResults(
            scanner="combined",
            version=version_str,
            scan_type=first.scan_type,
            started_at=min(r.started_at for r in results_list),
            completed_at=max(r.completed_at for r in results_list),
            summary=merged_summary,
            violations=unique_violations,
            metadata={
                "scanners": scanner_names,
                "scanner_versions": scanner_versions,
            },
        )

    @staticmethod
    def _deduplicate(violations: list[Violation]) -> list[Violation]:
        """Deduplicate violations based on check_id + resource.

        When duplicates are found, keeps the one with higher severity.
        """
        seen: dict[tuple[str, str], Violation] = {}

        for v in violations:
            key = (v.check_id, v.resource)
            if key not in seen:
                seen[key] = v
            else:
                # Keep the one with higher severity
                existing = seen[key]
                if ResultAggregator._severity_rank(v.severity) > ResultAggregator._severity_rank(
                    existing.severity
                ):
                    seen[key] = v

        return list(seen.values())

    @staticmethod
    def _severity_rank(severity: Severity) -> int:
        """Get numeric rank for severity comparison."""
        ranks = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }
        return ranks.get(severity, 0)

    @staticmethod
    def filter_by_severity(
        results: ScanResults,
        min_severity: Severity,
    ) -> ScanResults:
        """Filter violations by minimum severity.

        Args:
            results: Original scan results.
            min_severity: Minimum severity to include.

        Returns:
            New ScanResults with filtered violations.
        """
        min_rank = ResultAggregator._severity_rank(min_severity)

        filtered_violations = [
            v for v in results.violations if ResultAggregator._severity_rank(v.severity) >= min_rank
        ]

        # Recalculate summary for filtered violations
        filtered_summary = ScanSummary(
            total_checks=results.summary.total_checks,
            passed=results.summary.passed,
            failed=len(filtered_violations),
            skipped=results.summary.skipped,
            critical=sum(1 for v in filtered_violations if v.severity == Severity.CRITICAL),
            high=sum(1 for v in filtered_violations if v.severity == Severity.HIGH),
            medium=sum(1 for v in filtered_violations if v.severity == Severity.MEDIUM),
            low=sum(1 for v in filtered_violations if v.severity == Severity.LOW),
            info=sum(1 for v in filtered_violations if v.severity == Severity.INFO),
        )

        return ScanResults(
            scanner=results.scanner,
            version=results.version,
            scan_type=results.scan_type,
            started_at=results.started_at,
            completed_at=results.completed_at,
            summary=filtered_summary,
            violations=filtered_violations,
            metadata={
                **results.metadata,
                "filtered_min_severity": min_severity.value,
            },
        )
