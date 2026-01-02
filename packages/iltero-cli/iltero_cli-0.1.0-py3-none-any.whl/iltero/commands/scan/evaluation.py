"""Policy evaluation command - post-plan Terraform scanning."""

from __future__ import annotations

import json
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
    upload_plan_results,
)
from iltero.core.exceptions import ScannerError
from iltero.scanners import ScanOrchestrator
from iltero.utils.output import print_error, print_info, print_success


def _extract_plan_summary(plan_file: Path) -> dict | None:
    """Extract resource change summary from Terraform plan JSON."""
    try:
        with open(plan_file) as f:
            plan_data = json.load(f)

        resource_changes = plan_data.get("resource_changes", [])
        summary = {"create": 0, "update": 0, "delete": 0, "replace": 0}

        for change in resource_changes:
            actions = change.get("change", {}).get("actions", [])
            if "create" in actions:
                summary["create"] += 1
            if "update" in actions:
                summary["update"] += 1
            if "delete" in actions:
                summary["delete"] += 1
            if "replace" in actions or ("delete" in actions and "create" in actions):
                summary["replace"] += 1

        return summary
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def scan_evaluation(
    plan_file: Path = typer.Argument(
        ...,
        help="Path to Terraform plan JSON file",
        exists=True,
        dir_okay=False,
        file_okay=True,
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
    opa_policy_dir: Path = typer.Option(
        ...,
        "--opa-policy-dir",
        help="Directory containing OPA policies (required)",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    run_id: str | None = typer.Option(
        None,
        "--run-id",
        help="Run ID from validation phase (required for upload)",
        envvar="ILTERO_RUN_ID",
    ),
    plan_url: str | None = typer.Option(
        None,
        "--plan-url",
        help="URL to stored plan file (optional)",
    ),
):
    """Run policy evaluation on Terraform plan.

    Evaluates a Terraform plan JSON file against OPA policies.
    First generate plan JSON: terraform show -json plan.tfplan > plan.json

    This command calls the plan phase webhook to continue a deployment run.
    The --run-id should be the run ID returned from the static scan phase.
    """
    try:
        # Parse options
        policy_list = policy_sets.split(",") if policy_sets else None
        fail_severity = severity_from_string(fail_on)

        # Create orchestrator with OPA only
        orchestrator = ScanOrchestrator(
            checkov_enabled=False,
            opa_enabled=True,
            parallel=False,
            timeout=timeout,
            policy_sets=policy_list,
            opa_policy_dir=str(opa_policy_dir),
            console=console,
        )

        if not orchestrator.available_scanners:
            print_error("OPA not available. Install from openpolicyagent.org")
            raise typer.Exit(EXIT_SCANNER_ERROR)

        print_info(f"Running policy evaluation on [cyan]{plan_file}[/cyan]")

        # Run scan
        results = orchestrator.scan_plan(
            str(plan_file),
            show_progress=output_format == "table",
        )

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
        if not skip_upload and run_id:
            # Extract plan summary for backend
            plan_summary = _extract_plan_summary(plan_file)

            # Determine success based on violations
            has_blocking = results.summary.critical > 0 or results.summary.high > 0

            upload_plan_results(
                run_id=run_id,
                success=not has_blocking,
                plan_summary=plan_summary,
                plan_url=plan_url,
                compliance_results=results,
            )
        elif not skip_upload and not run_id:
            print_info(
                "Skipping upload: --run-id required for plan webhook. "
                "Use --skip-upload to suppress this message."
            )

        # Check thresholds
        passed, message = orchestrator.check_thresholds(
            results,
            fail_on=fail_severity,
        )

        if not passed:
            print_error(message)
            raise typer.Exit(EXIT_SCAN_FAILED)

        print_success("Policy evaluation completed")

    except ScannerError as e:
        print_error(f"Scanner error: {e}")
        raise typer.Exit(EXIT_SCANNER_ERROR)
    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        raise typer.Exit(EXIT_CONFIG_ERROR)
