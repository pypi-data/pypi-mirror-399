"""Scan orchestrator for running multiple scanners."""

from __future__ import annotations

import concurrent.futures

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from iltero.core.exceptions import ScannerError

from .aggregator import ResultAggregator
from .base import BaseScanner
from .checkov import CheckovScanner
from .models import ScanResults, ScanType, Severity
from .opa import OPAScanner


class ScanOrchestrator:
    """Orchestrates running multiple scanners in parallel."""

    def __init__(
        self,
        checkov_enabled: bool = True,
        opa_enabled: bool = False,
        parallel: bool = True,
        timeout: int = 300,
        policy_sets: list[str] | None = None,
        frameworks: list[str] | None = None,
        external_checks_dir: str | None = None,
        opa_policy_dir: str | None = None,
        console: Console | None = None,
    ):
        """Initialize scan orchestrator.

        Args:
            checkov_enabled: Enable Checkov scanner.
            opa_enabled: Enable OPA scanner (requires policy_dir).
            parallel: Run scanners in parallel.
            timeout: Maximum scan timeout in seconds.
            policy_sets: Policy sets to apply.
            frameworks: Compliance frameworks to check.
            external_checks_dir: Directory with external Checkov checks.
            opa_policy_dir: Directory containing OPA policies.
            console: Rich console for output.
        """
        self.checkov_enabled = checkov_enabled
        self.opa_enabled = opa_enabled
        self.parallel = parallel
        self.timeout = timeout
        self.policy_sets = policy_sets or []
        self.frameworks = frameworks or []
        self.external_checks_dir = external_checks_dir
        self.opa_policy_dir = opa_policy_dir
        self.console = console or Console()

        self._scanners: list[BaseScanner] = []
        self._initialize_scanners()

    def _initialize_scanners(self) -> None:
        """Initialize enabled scanners."""
        if self.checkov_enabled:
            scanner = CheckovScanner(
                parallel=self.parallel,
                timeout=self.timeout,
                policy_sets=self.policy_sets,
                frameworks=self.frameworks,
                external_checks_dir=self.external_checks_dir,
            )
            if scanner.is_available():
                self._scanners.append(scanner)
            else:
                self.console.print("[yellow]Warning:[/yellow] Checkov not available")

        if self.opa_enabled and self.opa_policy_dir:
            scanner = OPAScanner(
                parallel=self.parallel,
                timeout=self.timeout,
                policy_sets=self.policy_sets,
                policy_dir=self.opa_policy_dir,
            )
            if scanner.is_available():
                self._scanners.append(scanner)
            else:
                self.console.print("[yellow]Warning:[/yellow] OPA not available")

    @property
    def available_scanners(self) -> list[str]:
        """Get list of available scanner names."""
        return [s.__class__.__name__ for s in self._scanners]

    def scan_static(
        self,
        path: str,
        show_progress: bool = True,
    ) -> ScanResults:
        """Run static analysis on Terraform code.

        Args:
            path: Path to Terraform directory.
            show_progress: Show progress indicator.

        Returns:
            Aggregated scan results.

        Raises:
            ScannerError: If no scanners available or all fail.
        """
        return self._run_scan(
            path=path,
            scan_type=ScanType.STATIC,
            show_progress=show_progress,
        )

    def scan_plan(
        self,
        plan_file: str,
        show_progress: bool = True,
    ) -> ScanResults:
        """Run policy evaluation on Terraform plan.

        Args:
            plan_file: Path to Terraform plan JSON file.
            show_progress: Show progress indicator.

        Returns:
            Aggregated scan results.

        Raises:
            ScannerError: If no scanners available or all fail.
        """
        return self._run_scan(
            path=plan_file,
            scan_type=ScanType.EVALUATION,
            show_progress=show_progress,
        )

    def _run_scan(
        self,
        path: str,
        scan_type: ScanType,
        show_progress: bool,
    ) -> ScanResults:
        """Run scan with all enabled scanners.

        Args:
            path: Path to scan.
            scan_type: Type of scan.
            show_progress: Show progress indicator.

        Returns:
            Aggregated scan results.
        """
        if not self._scanners:
            raise ScannerError("orchestrator", "No scanners available")

        # Filter scanners by scan type
        compatible_scanners = self._get_compatible_scanners(scan_type)
        if not compatible_scanners:
            raise ScannerError(
                "orchestrator",
                f"No scanners compatible with {scan_type.value} scan type",
            )

        results: list[ScanResults] = []
        errors: list[tuple[str, Exception]] = []

        if self.parallel and len(compatible_scanners) > 1:
            results, errors = self._run_parallel(
                compatible_scanners,
                path,
                scan_type,
                show_progress,
            )
        else:
            results, errors = self._run_sequential(
                compatible_scanners,
                path,
                scan_type,
                show_progress,
            )

        # Handle errors
        if errors and not results:
            # All scanners failed
            error_msgs = [f"{name}: {err}" for name, err in errors]
            raise ScannerError(
                "orchestrator",
                "All scanners failed:\n" + "\n".join(error_msgs),
            )
        elif errors:
            # Some scanners failed
            for name, err in errors:
                self.console.print(f"[yellow]Warning:[/yellow] {name} failed: {err}")

        # Aggregate results
        if len(results) == 1:
            return results[0]
        return ResultAggregator.merge(results)

    def _get_compatible_scanners(
        self,
        scan_type: ScanType,
    ) -> list[BaseScanner]:
        """Get scanners compatible with the scan type."""
        compatible = []
        for scanner in self._scanners:
            if scan_type == ScanType.STATIC:
                # Static analysis: Checkov
                if isinstance(scanner, CheckovScanner):
                    compatible.append(scanner)
            elif scan_type == ScanType.EVALUATION:
                # Plan evaluation: OPA (and Checkov can do some)
                if isinstance(scanner, OPAScanner | CheckovScanner):
                    compatible.append(scanner)
        return compatible

    def _run_parallel(
        self,
        scanners: list[BaseScanner],
        path: str,
        scan_type: ScanType,
        show_progress: bool,
    ) -> tuple[list[ScanResults], list[tuple[str, Exception]]]:
        """Run scanners in parallel."""
        results: list[ScanResults] = []
        errors: list[tuple[str, Exception]] = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(scanners)) as executor:
            # Submit all scanner tasks
            future_to_scanner = {
                executor.submit(scanner.scan, path, scan_type): scanner for scanner in scanners
            }

            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    task = progress.add_task(
                        f"Running {len(scanners)} scanner(s)...",
                        total=len(scanners),
                    )

                    for future in concurrent.futures.as_completed(future_to_scanner):
                        scanner = future_to_scanner[future]
                        scanner_name = scanner.__class__.__name__
                        try:
                            result = future.result()
                            results.append(result)
                        except Exception as e:
                            errors.append((scanner_name, e))

                        progress.advance(task)
            else:
                for future in concurrent.futures.as_completed(future_to_scanner):
                    scanner = future_to_scanner[future]
                    scanner_name = scanner.__class__.__name__
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        errors.append((scanner_name, e))

        return results, errors

    def _run_sequential(
        self,
        scanners: list[BaseScanner],
        path: str,
        scan_type: ScanType,
        show_progress: bool,
    ) -> tuple[list[ScanResults], list[tuple[str, Exception]]]:
        """Run scanners sequentially."""
        results: list[ScanResults] = []
        errors: list[tuple[str, Exception]] = []

        for scanner in scanners:
            scanner_name = scanner.__class__.__name__

            if show_progress:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                ) as progress:
                    progress.add_task(f"Running {scanner_name}...", total=None)
                    try:
                        result = scanner.scan(path, scan_type)
                        results.append(result)
                    except Exception as e:
                        errors.append((scanner_name, e))
            else:
                try:
                    result = scanner.scan(path, scan_type)
                    results.append(result)
                except Exception as e:
                    errors.append((scanner_name, e))

        return results, errors

    def check_thresholds(
        self,
        results: ScanResults,
        fail_on: Severity = Severity.CRITICAL,
        max_violations: int | None = None,
    ) -> tuple[bool, str]:
        """Check if results exceed thresholds.

        Args:
            results: Scan results to check.
            fail_on: Minimum severity to cause failure.
            max_violations: Maximum total violations allowed.

        Returns:
            Tuple of (passed, message).
        """
        violations_by_severity = results.get_violations_by_severity()

        # Check severity threshold
        severity_checks = {
            Severity.CRITICAL: violations_by_severity["critical"],
            Severity.HIGH: (violations_by_severity["critical"] + violations_by_severity["high"]),
            Severity.MEDIUM: (
                violations_by_severity["critical"]
                + violations_by_severity["high"]
                + violations_by_severity["medium"]
            ),
            Severity.LOW: (
                violations_by_severity["critical"]
                + violations_by_severity["high"]
                + violations_by_severity["medium"]
                + violations_by_severity["low"]
            ),
            Severity.INFO: results.summary.total_violations,
        }

        threshold_violations = severity_checks.get(fail_on, 0)
        if threshold_violations > 0:
            return False, (
                f"Found {threshold_violations} violation(s) at {fail_on.value} severity or above"
            )

        # Check max violations
        if max_violations is not None:
            total = results.summary.total_violations
            if total > max_violations:
                return False, (f"Found {total} violations, exceeds maximum of {max_violations}")

        return True, "All checks passed"
