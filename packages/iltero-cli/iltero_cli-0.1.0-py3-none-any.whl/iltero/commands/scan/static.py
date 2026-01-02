"""Static scan command - pre-plan Terraform code scanning."""

from __future__ import annotations

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
    upload_results,
)
from iltero.core.exceptions import ScannerError
from iltero.scanners import ScanOrchestrator
from iltero.utils.output import print_error, print_info, print_warning


def scan_static(
    path: Path = typer.Argument(
        Path("."),
        help="Path to Terraform directory to scan",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    stack_id: str | None = typer.Option(
        None,
        "--stack-id",
        "-s",
        help="Stack ID for backend submission",
        envvar="ILTERO_STACK_ID",
    ),
    unit: str | None = typer.Option(
        None,
        "--unit",
        "-u",
        help="Unit name for multi-unit stacks",
    ),
    environment: str = typer.Option(
        "development",
        "--environment",
        "-e",
        help="Environment name",
        envvar="ILTERO_ENVIRONMENT",
    ),
    policy_sets: str | None = typer.Option(
        None,
        "--policy-sets",
        "-p",
        help="Comma-separated policy sets to apply",
        envvar="ILTERO_POLICY_SETS",
    ),
    frameworks: str | None = typer.Option(
        None,
        "--frameworks",
        help="Comma-separated compliance frameworks",
    ),
    parallel: bool = typer.Option(
        True,
        "--parallel/--no-parallel",
        help="Run checks in parallel",
    ),
    timeout: int = typer.Option(
        300,
        "--timeout",
        "-t",
        help="Scan timeout in seconds",
    ),
    fail_on: str = typer.Option(
        "critical",
        "--fail-on",
        help="Fail on severity: critical, high, medium, low, info",
    ),
    max_violations: int | None = typer.Option(
        None,
        "--max-violations",
        help="Maximum allowed violations",
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
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Run scan without uploading results",
    ),
    run_id: str | None = typer.Option(
        None,
        "--run-id",
        help="Existing Iltero run ID if continuing a run",
        envvar="ILTERO_RUN_ID",
    ),
    external_run_id: str | None = typer.Option(
        None,
        "--external-run-id",
        help="External CI/CD run ID (e.g., GitHub Actions run ID)",
        envvar="GITHUB_RUN_ID",
    ),
    external_run_url: str | None = typer.Option(
        None,
        "--external-run-url",
        help="URL to the CI/CD pipeline run",
        envvar="ILTERO_EXTERNAL_RUN_URL",
    ),
    external_checks_dir: Path | None = typer.Option(
        None,
        "--external-checks-dir",
        help="Directory with external Checkov checks",
    ),
):
    """Run static compliance scan on Terraform code.

    Scans Terraform files using Checkov for static analysis.
    Results can be saved locally and/or uploaded to Iltero backend.
    """
    try:
        # Parse options
        policy_list = policy_sets.split(",") if policy_sets else None
        framework_list = frameworks.split(",") if frameworks else None
        fail_severity = severity_from_string(fail_on)

        # Create orchestrator - static scan uses Checkov only
        ext_checks = str(external_checks_dir) if external_checks_dir else None
        orchestrator = ScanOrchestrator(
            checkov_enabled=True,
            opa_enabled=False,
            parallel=parallel,
            timeout=timeout,
            policy_sets=policy_list,
            frameworks=framework_list,
            external_checks_dir=ext_checks,
            console=console,
        )

        # Check available scanners
        if not orchestrator.available_scanners:
            print_error("No scanners available. Install checkov or opa.")
            raise typer.Exit(EXIT_SCANNER_ERROR)

        scanners = ", ".join(orchestrator.available_scanners)
        print_info(f"Running static scan on [cyan]{path}[/cyan] using [green]{scanners}[/green]")

        # Run scan
        results = orchestrator.scan_static(
            str(path),
            show_progress=output_format == "table",
        )

        # Display results
        if output_format == "table":
            print_scan_summary(results)
            print_violations(results)
        elif output_format == "json":
            console.print_json(data=results.to_dict())
        elif output_format in ("sarif", "junit"):
            # For these, we typically save to file
            if not output_file:
                msg = f"--output {output_format} typically requires "
                msg += "--output-file"
                print_warning(msg)
                console.print_json(data=results.to_dict())

        # Save to file if requested
        if output_file:
            save_results(results, output_file, output_format)

        # Upload to backend if not skipped
        if not skip_upload and not dry_run and stack_id:
            upload_results(
                results,
                stack_id,
                unit,
                environment,
                run_id=run_id,
                external_run_id=external_run_id,
                external_run_url=external_run_url,
            )

        # Check thresholds
        passed, message = orchestrator.check_thresholds(
            results,
            fail_on=fail_severity,
            max_violations=max_violations,
        )

        if not passed:
            print_error(message)
            raise typer.Exit(EXIT_SCAN_FAILED)

        from iltero.utils.output import print_success

        print_success(f"Scan completed with {results.summary.total_violations} violation(s)")

    except ScannerError as e:
        print_error(f"Scanner error: {e}")
        raise typer.Exit(EXIT_SCANNER_ERROR)
    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise typer.Exit(EXIT_CONFIG_ERROR)
