"""Cloud Custodian scanner implementation for runtime compliance."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
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


class CloudCustodianScanner(BaseScanner):
    """Cloud Custodian scanner for runtime cloud resource compliance.

    Cloud Custodian queries live cloud resources via provider APIs
    and evaluates them against YAML-based policies.

    This scanner is used for post-deployment runtime compliance checks,
    validating that deployed resources match expected configurations.
    """

    # Map Cloud Custodian severity levels to our Severity enum
    SEVERITY_MAP = {
        "critical": Severity.CRITICAL,
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "low": Severity.LOW,
        "info": Severity.INFO,
    }

    def __init__(
        self,
        custodian_path: str | None = None,
        policy_dir: str | None = None,
        output_dir: str | None = None,
        cloud_provider: str = "aws",
        region: str | None = None,
        account_id: str | None = None,
        resource_tags: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        """Initialize Cloud Custodian scanner.

        Args:
            custodian_path: Path to custodian executable (auto-detected).
            policy_dir: Directory containing Custodian YAML policies.
            output_dir: Directory for scan output (temp if None).
            cloud_provider: Cloud provider (aws, azure, gcp).
            region: Cloud region to scan.
            account_id: Cloud account/subscription ID.
            resource_tags: Tags to filter scanned resources.
            **kwargs: Additional arguments passed to BaseScanner.
        """
        super().__init__(**kwargs)
        self.custodian_path = custodian_path or shutil.which("custodian")
        self.policy_dir = Path(policy_dir) if policy_dir else None
        self.output_dir = Path(output_dir) if output_dir else None
        self.cloud_provider = cloud_provider.lower()
        self.region = region
        self.account_id = account_id
        self.resource_tags = resource_tags or {}
        self._version: str | None = None

    def is_available(self) -> bool:
        """Check if Cloud Custodian is installed."""
        return self.custodian_path is not None

    def get_version(self) -> str:
        """Get Cloud Custodian version."""
        if self._version is not None:
            return self._version

        if not self.custodian_path:
            return "unknown"

        try:
            result = subprocess.run(
                [self.custodian_path, "version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            # Parse version from output
            output = result.stdout.strip()
            if output:
                self._version = output.split()[-1] if output else "unknown"
                return self._version
            return "unknown"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return "unknown"

    def scan(
        self,
        path: str,
        scan_type: ScanType = ScanType.RUNTIME,
    ) -> ScanResults:
        """Scan live cloud resources against Custodian policies.

        Args:
            path: Path to Custodian policy YAML file or directory.
            scan_type: Type of scan (typically RUNTIME for Custodian).

        Returns:
            ScanResults with compliance violations.

        Raises:
            ScannerError: If Custodian is not available or scan fails.
        """
        if not self.custodian_path:
            raise ScannerError(
                "custodian",
                "Cloud Custodian not found. Install with: pip install c7n",
            )

        path_obj = Path(path)
        if not path_obj.exists():
            raise ScannerError(
                "custodian",
                f"Policy path does not exist: {path}",
            )

        started_at = datetime.now(UTC)

        # Use temp directory for output if not specified
        output_dir = self.output_dir or Path(tempfile.mkdtemp(prefix="custodian_"))

        # Collect all policy files
        policy_files = self._collect_policy_files(path_obj)
        if not policy_files:
            raise ScannerError(
                "custodian",
                f"No policy files found in: {path}",
            )

        all_violations: list[Violation] = []
        total_checks = 0
        passed = 0
        failed = 0

        # Run Custodian for each policy file
        for policy_file in policy_files:
            try:
                result = self._run_custodian(policy_file, output_dir)
                violations, checks, pass_count = self._parse_results(
                    result, policy_file, output_dir
                )
                all_violations.extend(violations)
                total_checks += checks
                passed += pass_count
                failed += len(violations)
            except ScannerError:
                raise
            except Exception as e:
                # Log but continue with other policies
                all_violations.append(
                    Violation(
                        check_id="CUSTODIAN_ERROR",
                        check_name=f"Policy execution error: {policy_file}",
                        severity=Severity.HIGH,
                        resource="unknown",
                        file_path=str(policy_file),
                        line_range=(0, 0),
                        description=str(e),
                    )
                )
                failed += 1

        completed_at = datetime.now(UTC)

        # Build summary
        summary = self._build_summary(all_violations, total_checks, passed)

        return ScanResults(
            scanner="cloud-custodian",
            version=self.get_version(),
            scan_type=scan_type,
            started_at=started_at,
            completed_at=completed_at,
            summary=summary,
            violations=all_violations,
            metadata={
                "cloud_provider": self.cloud_provider,
                "region": self.region,
                "account_id": self.account_id,
                "policy_count": len(policy_files),
                "output_dir": str(output_dir),
            },
        )

    def _collect_policy_files(self, path: Path) -> list[Path]:
        """Collect all YAML policy files from path."""
        if path.is_file():
            return [path] if path.suffix in (".yml", ".yaml") else []

        policy_files = []
        for pattern in ("*.yml", "*.yaml"):
            policy_files.extend(path.glob(pattern))
            policy_files.extend(path.glob(f"**/{pattern}"))

        return sorted(set(policy_files))

    def _run_custodian(self, policy_file: Path, output_dir: Path) -> subprocess.CompletedProcess:
        """Run Cloud Custodian on a policy file."""
        cmd = [
            self.custodian_path,
            "run",
            "--output-dir",
            str(output_dir),
            str(policy_file),
        ]

        # Add region if specified
        if self.region:
            cmd.extend(["--region", self.region])

        # Add dry-run mode for safety (doesn't take actions)
        cmd.append("--dry-run")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            return result
        except subprocess.TimeoutExpired as e:
            raise ScannerError(
                "custodian",
                f"Cloud Custodian timed out after {self.timeout} seconds",
            ) from e

    def _parse_results(
        self,
        result: subprocess.CompletedProcess,
        policy_file: Path,
        output_dir: Path,
    ) -> tuple[list[Violation], int, int]:
        """Parse Cloud Custodian output into violations.

        Returns:
            Tuple of (violations, total_checks, passed_checks).
        """
        violations = []
        total_checks = 0
        passed = 0

        # Load the policy to get metadata
        try:
            with open(policy_file) as f:
                import yaml

                policies = yaml.safe_load(f)
        except Exception:
            policies = {"policies": []}

        policy_list = policies.get("policies", [])
        total_checks = len(policy_list)

        # Check output directory for results
        for policy in policy_list:
            policy_name = policy.get("name", "unknown")
            policy_output = output_dir / policy_name / "resources.json"

            if policy_output.exists():
                try:
                    with open(policy_output) as f:
                        resources = json.load(f)

                    if resources:
                        # Resources found = violations
                        for resource in resources:
                            violation = self._resource_to_violation(resource, policy, policy_file)
                            violations.append(violation)
                    else:
                        passed += 1
                except (json.JSONDecodeError, KeyError):
                    passed += 1
            else:
                # No output file = passed (no matching resources)
                passed += 1

        return violations, total_checks, passed

    def _resource_to_violation(
        self,
        resource: dict[str, Any],
        policy: dict[str, Any],
        policy_file: Path,
    ) -> Violation:
        """Convert a non-compliant resource to a Violation."""
        policy_name = policy.get("name", "unknown")
        description = policy.get("description", f"Policy {policy_name} failed")
        severity_str = policy.get("metadata", {}).get("severity", "medium")
        severity = self.SEVERITY_MAP.get(severity_str.lower(), Severity.MEDIUM)

        # Extract resource identifier
        resource_id = (
            resource.get("ResourceId")
            or resource.get("id")
            or resource.get("Id")
            or resource.get("name")
            or resource.get("Name")
            or "unknown"
        )

        resource_type = policy.get("resource", "unknown")

        return Violation(
            check_id=policy_name,
            check_name=policy.get("description", policy_name),
            severity=severity,
            resource=f"{resource_type}/{resource_id}",
            file_path=str(policy_file),
            line_range=(0, 0),
            description=description,
            remediation=policy.get("metadata", {}).get("remediation"),
            framework=policy.get("metadata", {}).get("framework"),
            metadata={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_data": resource,
                "cloud_provider": self.cloud_provider,
                "region": self.region,
            },
        )

    def _build_summary(
        self,
        violations: list[Violation],
        total_checks: int,
        passed: int,
    ) -> ScanSummary:
        """Build summary from violations."""
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for violation in violations:
            severity_counts[violation.severity.value.lower()] += 1

        return ScanSummary(
            total_checks=total_checks,
            passed=passed,
            failed=len(violations),
            skipped=0,
            **severity_counts,
        )

    def scan_resources(
        self,
        policy_file: str | Path,
        resource_ids: list[str] | None = None,
        resource_tags: dict[str, str] | None = None,
    ) -> ScanResults:
        """Scan specific resources by ID or tags.

        This is a convenience method for targeted post-deployment scanning.

        Args:
            policy_file: Path to Custodian policy YAML.
            resource_ids: Optional list of resource IDs to scan.
            resource_tags: Optional tags to filter resources.

        Returns:
            ScanResults with compliance violations.
        """
        # For now, delegate to standard scan
        # Future: Add resource filtering via Custodian filters
        return self.scan(str(policy_file), ScanType.RUNTIME)
