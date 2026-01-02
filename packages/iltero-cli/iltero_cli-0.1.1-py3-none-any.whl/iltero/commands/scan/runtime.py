"""Runtime scan command - post-apply cloud resource scanning."""

from __future__ import annotations

import time
from pathlib import Path

import typer

from iltero.commands.scan.main import (
    EXIT_CONFIG_ERROR,
    EXIT_SCAN_FAILED,
    EXIT_SCANNER_ERROR,
    console,
    print_scan_summary,
    print_violations,
    save_results,
    severity_from_string,
    upload_apply_results,
)
from iltero.core.exceptions import ScannerError
from iltero.scanners import CloudCustodianScanner
from iltero.utils.output import print_error, print_info, print_success


def scan_runtime(
    policy_path: Path = typer.Argument(
        ...,
        help="Path to Cloud Custodian policy YAML file or directory",
        exists=True,
    ),
    run_id: str = typer.Option(
        ...,
        "--run-id",
        help="Run ID from previous phases (required)",
        envvar="ILTERO_RUN_ID",
    ),
    cloud_provider: str = typer.Option(
        "aws",
        "--cloud-provider",
        "-c",
        help="Cloud provider: aws, azure, gcp",
    ),
    region: str | None = typer.Option(
        None,
        "--region",
        "-r",
        help="Cloud region to scan",
        envvar="AWS_REGION",
    ),
    wait: int = typer.Option(
        0,
        "--wait",
        "-w",
        help="Seconds to wait before scanning (for resource provisioning)",
    ),
    timeout: int = typer.Option(
        600,
        "--timeout",
        "-t",
        help="Scan timeout in seconds",
    ),
    fail_on: str = typer.Option(
        "critical",
        "--fail-on",
        help="Fail on severity: critical, high, medium, low, info",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json, sarif, junit",
    ),
    output_file: Path | None = typer.Option(
        None,
        "--output-file",
        "-f",
        help="Save results to file",
    ),
    skip_upload: bool = typer.Option(
        False,
        "--skip-upload",
        help="Skip uploading results to backend",
    ),
    schedule_drift: bool = typer.Option(
        False,
        "--schedule-drift",
        help="Schedule drift detection after scan",
    ),
    dry_run: bool = typer.Option(
        True,
        "--dry-run/--no-dry-run",
        help="Run in dry-run mode (no actions taken)",
    ),
):
    """Run runtime compliance scan on live cloud resources.

    Scans deployed cloud resources using Cloud Custodian policies.
    This command is typically run after terraform apply to validate
    that deployed resources meet compliance requirements.

    Requires Cloud Custodian installed: pip install c7n

    Example:
        # Wait 30s for resources to provision, then scan
        iltero scan runtime policies/ --run-id $RUN_ID --wait 30

        # Scan and schedule drift detection
        iltero scan runtime policies/ --run-id $RUN_ID --schedule-drift
    """
    try:
        fail_severity = severity_from_string(fail_on)

        # Wait for resources to provision if requested
        if wait > 0:
            print_info(f"Waiting {wait} seconds for resources to provision...")
            time.sleep(wait)

        # Initialize Cloud Custodian scanner
        scanner = CloudCustodianScanner(
            policy_dir=str(policy_path),
            cloud_provider=cloud_provider,
            region=region,
            timeout=timeout,
        )

        if not scanner.is_available():
            print_error("Cloud Custodian not available. Install with: pip install c7n")
            raise typer.Exit(EXIT_SCANNER_ERROR)

        print_info(
            f"Running runtime scan on [cyan]{policy_path}[/cyan] "
            f"({cloud_provider.upper()}"
            f"{f', {region}' if region else ''})"
        )

        if dry_run:
            print_info("[yellow]Dry-run mode:[/yellow] No actions taken")

        # Run scan
        results = scanner.scan(str(policy_path))

        # Display results
        if output_format == "table":
            print_scan_summary(results)
            print_violations(results)
        elif output_format == "json":
            console.print_json(data=results.to_dict())

        # Save to file if requested
        if output_file:
            save_results(results, output_file, output_format)

        # Upload to backend if not skipped
        if not skip_upload:
            # Determine success based on violations
            has_blocking = results.summary.critical > 0 or results.summary.high > 0

            # Build apply results with scan data
            apply_results = {
                "runtime_scan": results.to_dict(),
                "cloud_provider": cloud_provider,
                "region": region,
                "dry_run": dry_run,
            }

            upload_apply_results(
                run_id=run_id,
                success=not has_blocking,
                apply_results=apply_results,
                schedule_drift_detection=schedule_drift,
            )

        # Check thresholds
        passed = _check_thresholds(results, fail_severity)

        if not passed:
            print_error(
                f"Runtime scan failed: "
                f"{results.summary.critical} critical, "
                f"{results.summary.high} high violations"
            )
            raise typer.Exit(EXIT_SCAN_FAILED)

        print_success(f"Runtime scan completed: {results.summary.total_violations} violation(s)")

        if schedule_drift and not skip_upload:
            print_info("Drift detection scheduled")

    except ScannerError as e:
        print_error(f"Scanner error: {e}")
        raise typer.Exit(EXIT_SCANNER_ERROR)
    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise typer.Exit(EXIT_CONFIG_ERROR)


def _check_thresholds(
    results,
    fail_severity,
) -> bool:
    """Check if results pass severity thresholds."""
    from iltero.scanners.models import Severity

    severity_order = [
        Severity.CRITICAL,
        Severity.HIGH,
        Severity.MEDIUM,
        Severity.LOW,
        Severity.INFO,
    ]

    # Get index of fail_severity
    try:
        threshold_idx = severity_order.index(fail_severity)
    except ValueError:
        threshold_idx = 0  # Default to CRITICAL

    # Check all severities at or above threshold
    for i, severity in enumerate(severity_order):
        if i > threshold_idx:
            break

        count = getattr(results.summary, severity.value.lower(), 0)
        if count > 0:
            return False

    return True
