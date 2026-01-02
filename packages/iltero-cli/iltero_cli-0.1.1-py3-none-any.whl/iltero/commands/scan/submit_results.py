"""Submit scan results command."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import typer

from iltero.commands.scan.main import EXIT_API_ERROR, EXIT_CONFIG_ERROR, console
from iltero.services import (
    ComplianceScanOrchestrator,
    ScanResultsSubmitter,
)
from iltero.utils.output import print_error, print_info, print_success

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


def submit_results(
    scan_id: str = typer.Argument(
        ...,
        help="Scan ID to submit results for",
    ),
    results_file: Path = typer.Argument(
        ...,
        help="Path to JSON results file",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    stack_id: str | None = typer.Option(
        None,
        "--stack-id",
        "-s",
        help="Stack ID (for loading run context)",
        envvar="ILTERO_STACK_ID",
    ),
    run_id: str | None = typer.Option(
        None,
        "--run-id",
        help="Local run ID to load provenance from",
        envvar="ILTERO_RUN_ID",
    ),
    scanner_version: str | None = typer.Option(
        None,
        "--scanner-version",
        help="Version of scanner that produced results",
    ),
    pipeline_url: str | None = typer.Option(
        None,
        "--pipeline-url",
        help="URL to CI/CD pipeline run",
        envvar="ILTERO_EXTERNAL_RUN_URL",
    ),
    commit_sha: str | None = typer.Option(
        None,
        "--commit-sha",
        help="Git commit SHA that was scanned",
        envvar="GITHUB_SHA",
    ),
    branch: str | None = typer.Option(
        None,
        "--branch",
        help="Git branch that was scanned",
        envvar="GITHUB_REF_NAME",
    ),
):
    """Submit scan results with policy resolution provenance.

    Submits previously generated scan results to the compliance API.
    If a stack ID and run ID are provided, policy resolution provenance
    will be loaded and included in the submission.

    Example:
        iltero scan submit-results abc123 results.json --stack-id my-stack
    """
    import json

    try:
        # Load results from file
        print_info(f"Loading results from [cyan]{results_file}[/cyan]...")

        with open(results_file) as f:
            results_data = json.load(f)

        # Parse into ScanResults
        # Handle various formats
        if "scanner" in results_data:
            # Direct ScanResults format
            scan_results = _parse_scan_results(results_data)
        elif "passed_checks" in results_data or "failed_checks" in results_data:
            # Checkov format
            scan_results = _parse_checkov_results(results_data)
        else:
            print_error("Unrecognized results file format")
            raise typer.Exit(EXIT_CONFIG_ERROR)

        # Try to load provenance from run context
        provenance = None
        if stack_id and run_id:
            print_info(f"Loading run context for [cyan]{stack_id}/{run_id}[/cyan]...")
            orchestrator = ComplianceScanOrchestrator()
            context = orchestrator.load_existing_run(stack_id, run_id)
            if context:
                provenance = context.provenance
                print_info("Policy resolution provenance loaded")

        # Submit results
        print_info(f"Submitting results for scan [cyan]{scan_id}[/cyan]...")

        submitter = ScanResultsSubmitter()
        response = submitter.submit_results(
            scan_id=scan_id,
            scan_results=scan_results,
            policy_resolution=provenance,
            scanner_version=scanner_version,
            pipeline_url=pipeline_url,
            commit_sha=commit_sha,
            branch=branch,
        )

        print_success("Results submitted successfully")

        # Show response summary
        if response:
            console.print(f"[dim]Response: {response}[/dim]")

    except typer.Exit:
        raise
    except FileNotFoundError:
        print_error(f"Results file not found: {results_file}")
        raise typer.Exit(EXIT_CONFIG_ERROR)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in results file: {e}")
        raise typer.Exit(EXIT_CONFIG_ERROR)
    except Exception as e:
        print_error(f"Error submitting results: {e}")
        raise typer.Exit(EXIT_API_ERROR)


def _parse_scan_results(data: dict) -> ScanResults:
    """Parse ScanResults from dict format."""
    from datetime import datetime

    from iltero.scanners.models import (
        ScanResults,
        ScanSummary,
        ScanType,
        Severity,
        Violation,
    )

    violations = []
    for v in data.get("violations", []):
        violations.append(
            Violation(
                check_id=v.get("check_id", ""),
                check_name=v.get("check_name", ""),
                severity=Severity[v.get("severity", "INFO").upper()],
                resource=v.get("resource", ""),
                file_path=v.get("file_path", ""),
                line_range=tuple(v.get("line_range", [0, 0])),
                description=v.get("description", ""),
                remediation=v.get("remediation"),
                framework=v.get("framework"),
                metadata=v.get("metadata", {}),
            )
        )

    summary_data = data.get("summary", {})
    summary = ScanSummary(
        total_checks=summary_data.get("total_checks", 0),
        passed=summary_data.get("passed", 0),
        failed=summary_data.get("failed", 0),
        skipped=summary_data.get("skipped", 0),
        critical=summary_data.get("critical", 0),
        high=summary_data.get("high", 0),
        medium=summary_data.get("medium", 0),
        low=summary_data.get("low", 0),
        info=summary_data.get("info", 0),
    )

    return ScanResults(
        scanner=data.get("scanner", "unknown"),
        version=data.get("version", "0.0.0"),
        scan_type=ScanType(data.get("scan_type", "static")),
        started_at=datetime.fromisoformat(data.get("started_at", datetime.now().isoformat())),
        completed_at=datetime.fromisoformat(data.get("completed_at", datetime.now().isoformat())),
        summary=summary,
        violations=violations,
        metadata=data.get("metadata", {}),
    )


def _parse_checkov_results(data: dict) -> ScanResults:
    """Parse ScanResults from Checkov output format."""
    from datetime import datetime

    from iltero.scanners.models import (
        ScanResults,
        ScanSummary,
        ScanType,
        Severity,
        Violation,
    )

    # Extract violations from failed_checks
    violations = []
    for check in data.get("failed_checks", []):
        # Map Checkov severity
        severity_map = {
            "CRITICAL": Severity.CRITICAL,
            "HIGH": Severity.HIGH,
            "MEDIUM": Severity.MEDIUM,
            "LOW": Severity.LOW,
            "INFO": Severity.INFO,
        }
        sev = severity_map.get(check.get("severity", "").upper(), Severity.INFO)

        # Extract line range safely
        line_range_raw = check.get("file_line_range", [0, 0])
        end_line = line_range_raw[1] if len(line_range_raw) > 1 else 0

        violations.append(
            Violation(
                check_id=check.get("check_id", ""),
                check_name=check.get("check", {}).get("name", check.get("check_id", "")),
                severity=sev,
                resource=check.get("resource", ""),
                file_path=check.get("file_path", ""),
                line_range=(line_range_raw[0], end_line),
                description=check.get("description", ""),
                remediation=check.get("guideline"),
                framework=check.get("bc_check_id"),
                metadata=check.get("evaluations", {}),
            )
        )

    # Build summary
    passed_count = len(data.get("passed_checks", []))
    failed_count = len(data.get("failed_checks", []))
    skipped_count = len(data.get("skipped_checks", []))

    # Count by severity
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for v in violations:
        severity_counts[v.severity.value] += 1

    summary = ScanSummary(
        total_checks=passed_count + failed_count + skipped_count,
        passed=passed_count,
        failed=failed_count,
        skipped=skipped_count,
        critical=severity_counts["critical"],
        high=severity_counts["high"],
        medium=severity_counts["medium"],
        low=severity_counts["low"],
        info=severity_counts["info"],
    )

    return ScanResults(
        scanner="checkov",
        version=data.get("check_type", "unknown"),
        scan_type=ScanType.STATIC,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        summary=summary,
        violations=violations,
        metadata={
            "check_type": data.get("check_type"),
            "parsing_errors": data.get("parsing_errors", []),
        },
    )
