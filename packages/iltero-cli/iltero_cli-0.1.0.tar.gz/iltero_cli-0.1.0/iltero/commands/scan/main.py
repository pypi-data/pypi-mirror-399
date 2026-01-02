"""Shared utilities and setup for scan commands."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks import (
    webhook_apply_phase,
    webhook_plan_phase,
    webhook_validation_phase,
)
from iltero.api_client.iltero_api_client.models import (
    ApplyPhaseSchema,
    PlanPhaseSchema,
    ValidatePhaseSchema,
)
from iltero.api_client.iltero_api_client.models.apply_phase_schema_apply_results import (  # noqa: E501
    ApplyPhaseSchemaApplyResults,
)
from iltero.api_client.iltero_api_client.models.plan_phase_schema_compliance_results_type_0 import (  # noqa: E501
    PlanPhaseSchemaComplianceResultsType0,
)
from iltero.api_client.iltero_api_client.models.plan_phase_schema_plan_results import (  # noqa: E501
    PlanPhaseSchemaPlanResults,
)
from iltero.api_client.iltero_api_client.models.plan_phase_schema_plan_summary_type_0 import (  # noqa: E501
    PlanPhaseSchemaPlanSummaryType0,
)
from iltero.api_client.iltero_api_client.models.validate_phase_schema_compliance_scan_type_0 import (  # noqa: E501
    ValidatePhaseSchemaComplianceScanType0,
)
from iltero.core.http import get_retry_client
from iltero.scanners import ScanResults, Severity
from iltero.scanners.formatters import (
    JSONFormatter,
    JUnitFormatter,
    SARIFFormatter,
)
from iltero.utils.cicd import detect_cicd_context
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

# Create main app
app = typer.Typer(help="Compliance scanning operations")
console = Console()

# Exit codes
EXIT_SUCCESS = 0
EXIT_SCAN_FAILED = 1
EXIT_CONFIG_ERROR = 2
EXIT_API_ERROR = 3
EXIT_SCANNER_ERROR = 4


def severity_from_string(value: str) -> Severity:
    """Convert string to Severity enum."""
    try:
        return Severity[value.upper()]
    except KeyError:
        return Severity.CRITICAL


def print_scan_summary(results: ScanResults) -> None:
    """Print scan summary to console."""
    summary = results.summary

    # Create summary table
    table = create_table("Metric", "Value", title="Scan Summary", show_header=False)
    table.columns[0].style = "cyan"
    table.columns[1].style = "green"

    table.add_row("Scanner", results.scanner)
    table.add_row("Version", results.version)
    table.add_row("Duration", f"{results.duration_seconds:.2f}s")
    table.add_row("Total Checks", str(summary.total_checks))
    table.add_row("Passed", f"[green]{summary.passed}[/green]")
    table.add_row("Failed", f"[red]{summary.failed}[/red]")
    table.add_row("Skipped", str(summary.skipped))

    console.print(table)
    console.print()

    # Violations by severity
    if summary.total_violations > 0:
        violations_table = create_table("Severity", "Count", title="Violations by Severity")
        violations_table.columns[0].style = "bold"
        violations_table.columns[1].justify = "right"

        if summary.critical > 0:
            violations_table.add_row(
                "[red]CRITICAL[/red]",
                str(summary.critical),
            )
        if summary.high > 0:
            violations_table.add_row(
                "[orange1]HIGH[/orange1]",
                str(summary.high),
            )
        if summary.medium > 0:
            violations_table.add_row(
                "[yellow]MEDIUM[/yellow]",
                str(summary.medium),
            )
        if summary.low > 0:
            violations_table.add_row(
                "[blue]LOW[/blue]",
                str(summary.low),
            )
        if summary.info > 0:
            violations_table.add_row(
                "[dim]INFO[/dim]",
                str(summary.info),
            )

        console.print(violations_table)
        console.print()


def print_violations(
    results: ScanResults,
    max_display: int = 20,
) -> None:
    """Print violation details to console."""
    violations = results.violations
    if not violations:
        print_success("No violations found!")
        return

    # Limit display
    display_violations = violations[:max_display]

    table = create_table(
        "Check ID",
        "Severity",
        "Resource",
        "File",
        "Description",
        title=f"Violations ({len(violations)} total)",
        show_lines=True,
    )
    table.columns[0].style = "cyan"
    table.columns[0].width = 15
    table.columns[1].width = 10
    table.columns[2].style = "green"
    table.columns[2].width = 30
    table.columns[3].style = "blue"
    table.columns[3].width = 25
    table.columns[4].width = 40

    severity_colors = {
        Severity.CRITICAL: "red",
        Severity.HIGH: "orange1",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "blue",
        Severity.INFO: "dim",
    }

    for v in display_violations:
        color = severity_colors.get(v.severity, "white")
        desc = v.description
        if len(desc) > 40:
            desc = desc[:40] + "..."
        table.add_row(
            v.check_id,
            f"[{color}]{v.severity.value}[/{color}]",
            v.resource,
            f"{v.file_path}:{v.line_range[0]}",
            desc,
        )

    console.print(table)

    if len(violations) > max_display:
        print_info(
            f"Showing {max_display} of {len(violations)} violations. "
            "Use --output json for full results."
        )


def save_results(
    results: ScanResults,
    output_file,
    output_format: str,
) -> None:
    """Save results to file.

    Args:
        results: The scan results to save.
        output_file: Path to the output file.
        output_format: Format to use (json, sarif, junit).
    """
    output_path = Path(output_file)

    # Select formatter based on format
    if output_format == "json":
        formatter = JSONFormatter()
    elif output_format == "sarif":
        formatter = SARIFFormatter()
    elif output_format == "junit":
        formatter = JUnitFormatter()
    else:
        formatter = JSONFormatter()

    output_path.write_text(formatter.format(results))
    print_success(f"Results saved to {output_path}")


def upload_results(
    results: ScanResults,
    stack_id: str,
    unit: str | None,
    environment: str,
    run_id: str | None = None,
    external_run_id: str | None = None,
    external_run_url: str | None = None,
) -> bool:
    """Upload scan results to backend via webhook.

    Submits compliance scan results to the Iltero backend using the
    validation phase webhook endpoint.

    Args:
        results: The scan results to upload.
        stack_id: The stack ID to associate results with.
        unit: Optional unit name for multi-unit stacks.
        environment: Environment name (e.g., 'development', 'production').
        run_id: Optional existing Iltero run ID if continuing a run.
        external_run_id: Optional external CI/CD run ID (e.g., GitHub run ID).
        external_run_url: Optional URL to the CI/CD pipeline run.

    Returns:
        True if upload succeeded, False otherwise.
    """
    print_info(f"Uploading results to backend for stack [cyan]{stack_id}[/cyan]...")

    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Convert scan results to dict for compliance_scan field
        scan_data = results.to_dict()
        # Add metadata
        scan_data["environment"] = environment
        if unit:
            scan_data["unit"] = unit

        # Create compliance scan object
        compliance_scan = ValidatePhaseSchemaComplianceScanType0()
        for key, value in scan_data.items():
            compliance_scan[key] = value

        # Determine success based on violations
        # No critical/high violations = success
        has_blocking_violations = results.summary.critical > 0 or results.summary.high > 0

        # Detect CI/CD context for audit trail
        cicd_context = detect_cicd_context()

        # Build webhook payload
        payload = ValidatePhaseSchema(
            stack_id=stack_id,
            success=not has_blocking_violations,
            run_id=run_id,
            external_run_id=external_run_id,
            external_run_url=external_run_url,
            compliance_scan=compliance_scan,
            cicd_context=cicd_context,
        )

        response = webhook_validation_phase.sync_detailed(
            client=auth_client,  # type: ignore[arg-type]
            body=payload,
        )

        result = client.handle_response(response)  # type: ignore[arg-type]

        if result:
            print_success("Scan results uploaded successfully")
            return True
        else:
            print_error("Failed to upload scan results")
            return False

    except Exception as e:
        print_error(f"Error uploading results: {e}")
        return False


def upload_plan_results(
    run_id: str,
    success: bool,
    plan_results: dict | None = None,
    plan_summary: dict | None = None,
    plan_url: str | None = None,
    compliance_results: ScanResults | None = None,
) -> bool:
    """Upload plan phase results to backend via webhook.

    Submits Terraform plan results and optional OPA policy evaluation
    to the Iltero backend using the plan phase webhook endpoint.

    Args:
        run_id: The run ID from the validation phase (required).
        success: Whether the plan succeeded.
        plan_results: Optional Terraform plan output dict.
        plan_summary: Optional resource changes summary dict.
        plan_url: Optional URL to stored plan file.
        compliance_results: Optional OPA evaluation ScanResults.

    Returns:
        True if upload succeeded, False otherwise.
    """
    print_info(f"Uploading plan results for run [cyan]{run_id}[/cyan]...")

    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build plan_results object if provided
        plan_results_obj = None
        if plan_results:
            plan_results_obj = PlanPhaseSchemaPlanResults()
            for key, value in plan_results.items():
                plan_results_obj[key] = value

        # Build plan_summary object if provided
        plan_summary_obj = None
        if plan_summary:
            plan_summary_obj = PlanPhaseSchemaPlanSummaryType0()
            for key, value in plan_summary.items():
                plan_summary_obj[key] = value

        # Build compliance_results object if provided
        compliance_obj = None
        if compliance_results:
            scan_data = compliance_results.to_dict()
            compliance_obj = PlanPhaseSchemaComplianceResultsType0()
            for key, value in scan_data.items():
                compliance_obj[key] = value

        # Build webhook payload
        payload = PlanPhaseSchema(
            run_id=run_id,
            success=success,
            plan_results=plan_results_obj,
            plan_summary=plan_summary_obj,
            plan_url=plan_url,
            compliance_results=compliance_obj,
        )

        response = webhook_plan_phase.sync_detailed(
            client=auth_client,  # type: ignore[arg-type]
            body=payload,
        )

        result = client.handle_response(response)  # type: ignore[arg-type]

        if result:
            print_success("Plan results uploaded successfully")
            return True
        else:
            print_error("Failed to upload plan results")
            return False

    except Exception as e:
        print_error(f"Error uploading plan results: {e}")
        return False


def upload_apply_results(
    run_id: str,
    success: bool,
    apply_results: dict | None = None,
    schedule_drift_detection: bool = False,
) -> bool:
    """Upload apply phase results to backend via webhook.

    Submits Terraform apply results to the Iltero backend using the
    apply phase webhook endpoint. Optionally schedules drift detection.

    Args:
        run_id: The run ID from previous phases (required).
        success: Whether the apply succeeded.
        apply_results: Optional Terraform apply output dict.
        schedule_drift_detection: Whether to schedule drift detection.

    Returns:
        True if upload succeeded, False otherwise.
    """
    print_info(f"Uploading apply results for run [cyan]{run_id}[/cyan]...")

    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build apply_results object if provided
        apply_results_obj = None
        if apply_results:
            apply_results_obj = ApplyPhaseSchemaApplyResults()
            for key, value in apply_results.items():
                apply_results_obj[key] = value

        # Build webhook payload
        payload = ApplyPhaseSchema(
            run_id=run_id,
            success=success,
            apply_results=apply_results_obj,
            schedule_drift_detection=schedule_drift_detection,
        )

        response = webhook_apply_phase.sync_detailed(
            client=auth_client,  # type: ignore[arg-type]
            body=payload,
        )

        result = client.handle_response(response)  # type: ignore[arg-type]

        if result:
            msg = "Apply results uploaded successfully"
            if schedule_drift_detection:
                msg += " (drift detection scheduled)"
            print_success(msg)
            return True
        else:
            print_error("Failed to upload apply results")
            return False

    except Exception as e:
        print_error(f"Error uploading apply results: {e}")
        return False
