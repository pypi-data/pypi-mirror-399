"""Checkov scanner implementation."""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from iltero.core.exceptions import ScannerError
from iltero.scanners.base import BaseScanner
from iltero.scanners.models import (
    ScanResults,
    ScanSummary,
    ScanType,
    Severity,
    Violation,
)


class CheckovScanner(BaseScanner):
    """Checkov scanner implementation for static Terraform analysis."""

    SEVERITY_MAP = {
        "CRITICAL": Severity.CRITICAL,
        "HIGH": Severity.HIGH,
        "MEDIUM": Severity.MEDIUM,
        "LOW": Severity.LOW,
        "INFO": Severity.INFO,
    }

    def __init__(
        self,
        checkov_path: str | None = None,
        external_checks_dir: str | None = None,
        **kwargs: Any,
    ):
        """Initialize Checkov scanner.

        Args:
            checkov_path: Path to checkov executable (auto-detected if None).
            external_checks_dir: Directory with external/custom checks.
            **kwargs: Additional arguments passed to BaseScanner.
        """
        super().__init__(**kwargs)
        self.checkov_path = checkov_path or shutil.which("checkov")
        self.external_checks_dir = external_checks_dir
        self._version: str | None = None

    def is_available(self) -> bool:
        """Check if Checkov is installed."""
        return self.checkov_path is not None

    def get_version(self) -> str:
        """Get Checkov version."""
        if self._version is not None:
            return self._version

        if not self.checkov_path:
            return "unknown"

        try:
            result = subprocess.run(
                [self.checkov_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            # Parse version from output (e.g., "2.5.24")
            self._version = result.stdout.strip().split()[-1]
            return self._version
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "unknown"

    def scan(
        self,
        path: str,
        scan_type: ScanType = ScanType.STATIC,
    ) -> ScanResults:
        """Run Checkov scan on Terraform directory.

        Args:
            path: Path to Terraform code directory.
            scan_type: Type of scan (typically STATIC for Checkov).

        Returns:
            ScanResults with normalized violations.

        Raises:
            ScannerError: If Checkov is not available or scan fails.
        """
        if not self.checkov_path:
            raise ScannerError(
                "checkov",
                "Checkov not found. Install with: pip install checkov",
            )

        path_obj = Path(path)
        if not path_obj.exists():
            raise ScannerError("checkov", f"Path does not exist: {path}")

        started_at = datetime.now(UTC)

        # Build Checkov command
        cmd = self._build_command(path)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise ScannerError(
                "checkov",
                f"Checkov scan timed out after {self.timeout} seconds",
            ) from e

        completed_at = datetime.now(UTC)

        # Checkov exits with 1 if violations found (not an error)
        if result.returncode not in [0, 1]:
            raise ScannerError(
                "checkov",
                f"Checkov failed with exit code {result.returncode}: {result.stderr}",
            )

        # Parse JSON output
        try:
            raw_results = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ScannerError(
                "checkov",
                f"Failed to parse Checkov output: {e}",
            ) from e

        # Normalize to our format
        return self._normalize_results(
            raw_results,
            scan_type,
            started_at,
            completed_at,
        )

    def _build_command(self, path: str) -> list[str]:
        """Build Checkov command with options."""
        cmd = [
            self.checkov_path,
            "--directory",
            path,
            "--framework",
            "terraform",
            "--output",
            "json",
            "--quiet",
            "--compact",
        ]

        # Add external checks directory if specified
        if self.external_checks_dir:
            cmd.extend(["--external-checks-dir", self.external_checks_dir])

        # Add framework filters if specified
        if self.frameworks:
            for framework in self.frameworks:
                cmd.extend(["--framework", framework])

        return cmd

    def _normalize_results(
        self,
        raw_results: dict[str, Any] | list[dict[str, Any]],
        scan_type: ScanType,
        started_at: datetime,
        completed_at: datetime,
    ) -> ScanResults:
        """Normalize Checkov output to ScanResults."""
        violations: list[Violation] = []
        summary_data = {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        # Checkov can return multiple result sets (one per framework)
        # Handle both list and dict formats
        if isinstance(raw_results, list):
            results_list: list[dict[str, Any]] = raw_results
        else:
            results_list = [raw_results]

        for result_set in results_list:
            # Extract check results
            check_type = result_set.get("check_type", "terraform")

            # Update summary from passed/failed/skipped counts
            passed_checks = result_set.get("passed", 0)
            failed_checks = result_set.get("failed", 0)
            skipped_checks = result_set.get("skipped", 0)

            summary_data["passed"] += passed_checks
            summary_data["failed"] += failed_checks
            summary_data["skipped"] += skipped_checks
            summary_data["total_checks"] += passed_checks + failed_checks + skipped_checks

            # Process failed checks
            results_section = result_set.get("results", {})
            failed_check_list = results_section.get("failed_checks", [])

            for check in failed_check_list:
                severity = self._map_severity(
                    check.get("check_result", {}).get("severity", "MEDIUM")
                )

                # Extract line range safely
                line_range = check.get("file_line_range", [0, 0])
                if not isinstance(line_range, list) or len(line_range) < 2:
                    line_range = [0, 0]

                violation = Violation(
                    check_id=check.get("check_id", ""),
                    check_name=check.get("check_name", ""),
                    severity=severity,
                    resource=check.get("resource", ""),
                    file_path=check.get("file_path", ""),
                    line_range=(line_range[0], line_range[1]),
                    description=check.get("check_name", ""),
                    remediation=check.get("guideline", ""),
                    framework=check.get("check_class", check_type),
                    metadata={
                        "bc_id": check.get("bc_check_id"),
                        "resource_type": check.get("resource_type"),
                        "evaluations": check.get("evaluations"),
                    },
                )

                violations.append(violation)

                # Update severity counts
                severity_key = severity.value.lower()
                summary_data[severity_key] += 1

        summary = ScanSummary(**summary_data)

        return ScanResults(
            scanner="checkov",
            version=self.get_version(),
            scan_type=scan_type,
            started_at=started_at,
            completed_at=completed_at,
            summary=summary,
            violations=violations,
            metadata={
                "frameworks": self.frameworks,
                "policy_sets": self.policy_sets,
                "external_checks_dir": self.external_checks_dir,
            },
        )

    def _map_severity(self, checkov_severity: str) -> Severity:
        """Map Checkov severity to our Severity enum."""
        if isinstance(checkov_severity, str):
            return self.SEVERITY_MAP.get(
                checkov_severity.upper(),
                Severity.MEDIUM,
            )
        return Severity.MEDIUM
