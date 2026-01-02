"""OPA (Open Policy Agent) scanner implementation."""

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


class OPAScanner(BaseScanner):
    """OPA scanner implementation for Terraform plan evaluation."""

    def __init__(
        self,
        opa_path: str | None = None,
        policy_dir: str | None = None,
        data_dir: str | None = None,
        query: str = "data.terraform.deny",
        **kwargs: Any,
    ):
        """Initialize OPA scanner.

        Args:
            opa_path: Path to opa executable (auto-detected if None).
            policy_dir: Directory containing Rego policies.
            data_dir: Directory containing data files for policies.
            query: OPA query to evaluate (default: data.terraform.deny).
            **kwargs: Additional arguments passed to BaseScanner.
        """
        super().__init__(**kwargs)
        self.opa_path = opa_path or shutil.which("opa")
        self.policy_dir = Path(policy_dir) if policy_dir else None
        self.data_dir = Path(data_dir) if data_dir else None
        self.query = query
        self._version: str | None = None

    def is_available(self) -> bool:
        """Check if OPA is installed."""
        return self.opa_path is not None

    def get_version(self) -> str:
        """Get OPA version."""
        if self._version is not None:
            return self._version

        if not self.opa_path:
            return "unknown"

        try:
            result = subprocess.run(
                [self.opa_path, "version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            # Parse version from output
            for line in result.stdout.split("\n"):
                if line.startswith("Version:"):
                    self._version = line.split(":")[1].strip()
                    return self._version
            return "unknown"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "unknown"

    def scan(
        self,
        path: str,
        scan_type: ScanType = ScanType.EVALUATION,
    ) -> ScanResults:
        """Evaluate Terraform plan against OPA policies.

        Args:
            path: Path to Terraform plan JSON file.
            scan_type: Type of scan (typically EVALUATION for OPA).

        Returns:
            ScanResults with policy violations.

        Raises:
            ScannerError: If OPA is not available or evaluation fails.
        """
        if not self.opa_path:
            raise ScannerError(
                "opa",
                "OPA not found. Install from: https://www.openpolicyagent.org/",
            )

        if not self.policy_dir or not self.policy_dir.exists():
            raise ScannerError(
                "opa",
                f"Policy directory not found: {self.policy_dir}",
            )

        path_obj = Path(path)
        if not path_obj.exists():
            raise ScannerError("opa", f"Plan file does not exist: {path}")

        started_at = datetime.now(UTC)

        # Build OPA command
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
                "opa",
                f"OPA evaluation timed out after {self.timeout} seconds",
            ) from e

        completed_at = datetime.now(UTC)

        # OPA returns 0 even if there are violations
        if result.returncode != 0:
            raise ScannerError(
                "opa",
                f"OPA failed with exit code {result.returncode}: {result.stderr}",
            )

        # Parse JSON output
        try:
            raw_results = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise ScannerError(
                "opa",
                f"Failed to parse OPA output: {e}",
            ) from e

        # Normalize results
        return self._normalize_results(
            raw_results,
            scan_type,
            started_at,
            completed_at,
        )

    def _build_command(self, plan_file: str) -> list[str]:
        """Build OPA command with options."""
        cmd = [
            self.opa_path,
            "eval",
            "--data",
            str(self.policy_dir),
            "--input",
            plan_file,
            "--format",
            "json",
            self.query,
        ]

        # Add data directory if specified
        if self.data_dir and self.data_dir.exists():
            cmd.extend(["--data", str(self.data_dir)])

        return cmd

    def _normalize_results(
        self,
        raw_results: dict[str, Any],
        scan_type: ScanType,
        started_at: datetime,
        completed_at: datetime,
    ) -> ScanResults:
        """Normalize OPA output to ScanResults."""
        violations = []

        # Extract violations from OPA result
        # OPA returns: {"result": [{"expressions": [{"value": [...]}]}]}
        opa_violations = self._extract_violations(raw_results)

        for v in opa_violations:
            # Handle different violation formats
            if isinstance(v, str):
                # Simple string violation
                violation = Violation(
                    check_id="OPA_CUSTOM",
                    check_name=v,
                    severity=Severity.MEDIUM,
                    resource="unknown",
                    file_path="plan.json",
                    line_range=(0, 0),
                    description=v,
                )
            elif isinstance(v, dict):
                # Structured violation
                severity_str = v.get("severity", "MEDIUM")
                try:
                    severity = Severity[severity_str.upper()]
                except (KeyError, AttributeError):
                    severity = Severity.MEDIUM

                violation = Violation(
                    check_id=v.get("policy_id", v.get("id", "OPA_CUSTOM")),
                    check_name=v.get("policy_name", v.get("name", "")),
                    severity=severity,
                    resource=v.get("resource", ""),
                    file_path=v.get("file", "plan.json"),
                    line_range=(v.get("line", 0), v.get("line", 0)),
                    description=v.get("message", v.get("msg", "")),
                    remediation=v.get("remediation", ""),
                    framework=v.get("framework", ""),
                    metadata=v.get("metadata", {}),
                )
            else:
                continue

            violations.append(violation)

        # Calculate summary
        summary = ScanSummary(
            total_checks=len(opa_violations) if opa_violations else 0,
            passed=0,  # OPA only returns failures
            failed=len(violations),
            skipped=0,
            critical=sum(1 for v in violations if v.severity == Severity.CRITICAL),
            high=sum(1 for v in violations if v.severity == Severity.HIGH),
            medium=sum(1 for v in violations if v.severity == Severity.MEDIUM),
            low=sum(1 for v in violations if v.severity == Severity.LOW),
            info=sum(1 for v in violations if v.severity == Severity.INFO),
        )

        return ScanResults(
            scanner="opa",
            version=self.get_version(),
            scan_type=scan_type,
            started_at=started_at,
            completed_at=completed_at,
            summary=summary,
            violations=violations,
            metadata={
                "policy_dir": (str(self.policy_dir) if self.policy_dir else None),
                "policy_sets": self.policy_sets,
                "query": self.query,
            },
        )

    def _extract_violations(
        self,
        raw_results: dict[str, Any],
    ) -> list[Any]:
        """Extract violations from OPA output.

        Handles various OPA output formats.
        """
        # Standard OPA eval format
        result = raw_results.get("result", [])
        if not result:
            return []

        # Navigate nested structure
        first_result = result[0] if result else {}
        expressions = first_result.get("expressions", [])
        if not expressions:
            return []

        # Get the value from the first expression
        value = expressions[0].get("value", [])

        # Value can be a list of violations or a single violation
        if isinstance(value, list):
            return value
        elif isinstance(value, dict):
            return [value]
        elif isinstance(value, bool):
            # Boolean result means no violations if False
            return []

        return []
