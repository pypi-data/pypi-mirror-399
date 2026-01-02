"""Stack drift detection commands - schedule, start, show, list, remediate."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.stack_drift_detection import (
    analyze_drift_impact as api_impact,
)
from iltero.api_client.api.stack_drift_detection import (
    complete_drift_detection as api_complete,
)
from iltero.api_client.api.stack_drift_detection import (
    fail_drift_detection as api_fail,
)
from iltero.api_client.api.stack_drift_detection import (
    get_drift_detection as api_get,
)
from iltero.api_client.api.stack_drift_detection import (
    get_latest_drift as api_latest,
)
from iltero.api_client.api.stack_drift_detection import (
    get_pending_detections as api_pending,
)
from iltero.api_client.api.stack_drift_detection import (
    mark_drift_remediated as api_remediated,
)
from iltero.api_client.api.stack_drift_detection import (
    schedule_drift_detection as api_schedule,
)
from iltero.api_client.api.stack_drift_detection import (
    schedule_periodic_drift as api_periodic,
)
from iltero.api_client.api.stack_drift_detection import (
    start_drift_detection as api_start,
)
from iltero.api_client.models.drift_detection_result_schema import (
    DriftDetectionResultSchema,
)
from iltero.api_client.models.drift_detection_result_schema_drift_summary import (  # noqa: E501
    DriftDetectionResultSchemaDriftSummary,
)
from iltero.api_client.models.drift_remediation_request_schema import (
    DriftRemediationRequestSchema,
)
from iltero.api_client.models.schedule_drift_detection_schema import (
    ScheduleDriftDetectionSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack drift detection management")
console = Console()


def schedule(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
) -> None:
    """Schedule a drift detection for a stack."""
    try:
        body = ScheduleDriftDetectionSchema(
            stack_id=stack_id,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_schedule.sync_detailed(
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to schedule drift detection.")
            return

        detection = data.get("detection", data)
        detection_id = detection.get("id", "N/A")
        print_success(f"Drift detection scheduled: {detection_id}")

        table = create_table("Field", "Value", title="Detection Details")
        table.add_row("ID", detection.get("id", "-"))
        table.add_row("Stack ID", stack_id)
        table.add_row("Status", detection.get("status", "-"))
        table.add_row("Scheduled For", detection.get("scheduled_for", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to schedule drift detection: {e}")
        raise typer.Exit(1) from e


def periodic(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    interval_hours: int = typer.Option(24, "--interval", "-i", help="Interval in hours"),
) -> None:
    """Configure periodic drift detection for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_periodic.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            interval_hours=interval_hours,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to configure periodic drift detection.")
            return

        print_success(f"Periodic drift detection configured ({interval_hours}h)")
    except Exception as e:
        print_error(f"Failed to configure periodic detection: {e}")
        raise typer.Exit(1) from e


def start(
    detection_id: str = typer.Argument(..., help="Detection ID"),
    run_id: str | None = typer.Option(None, "--run", "-r", help="Associated run ID"),
) -> None:
    """Start a scheduled drift detection."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_start.sync_detailed(
            detection_id=detection_id,
            client=auth_client,
            run_id=run_id,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to start drift detection.")
            return

        print_success(f"Drift detection started: {detection_id}")
    except Exception as e:
        print_error(f"Failed to start detection: {e}")
        raise typer.Exit(1) from e


def show(
    detection_id: str = typer.Argument(..., help="Detection ID"),
) -> None:
    """Show details of a drift detection."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            detection_id=detection_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Detection not found.")
            return

        detection = data.get("detection", data)

        table = create_table("Field", "Value", title="Drift Detection")
        table.add_row("ID", detection.get("id", "-"))
        table.add_row("Stack ID", detection.get("stack_id", "-"))
        table.add_row("Status", detection.get("status", "-"))
        table.add_row("Drift Detected", str(detection.get("drift_detected")))
        table.add_row("Started At", detection.get("started_at", "-"))
        table.add_row("Completed At", detection.get("completed_at", "-") or "-")

        console.print(table)

        # Show drift summary if available
        summary = detection.get("drift_summary")
        if summary:
            console.print("\n[bold]Drift Summary[/bold]")
            console.print(f"  Resources Changed: {summary.get('changed', 0)}")
            console.print(f"  Resources Added: {summary.get('added', 0)}")
            console.print(f"  Resources Deleted: {summary.get('deleted', 0)}")
    except Exception as e:
        print_error(f"Failed to get detection: {e}")
        raise typer.Exit(1) from e


def latest(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
) -> None:
    """Get the latest drift detection for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_latest.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No drift detection found for this stack.")
            return

        detection = data.get("detection", data)

        drift_status = detection.get("drift_detected")
        if drift_status:
            console.print("[red]⚠ Drift detected[/red]")
        else:
            console.print("[green]✓ No drift detected[/green]")

        table = create_table("Field", "Value", title="Latest Detection")
        table.add_row("ID", detection.get("id", "-"))
        table.add_row("Status", detection.get("status", "-"))
        table.add_row("Completed At", detection.get("completed_at", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to get latest detection: {e}")
        raise typer.Exit(1) from e


def pending() -> None:
    """List pending drift detections."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_pending.sync_detailed(
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No pending detections found.")
            return

        detections = data.get("detections", [])
        if not detections:
            print_info("No pending detections found.")
            return

        table = create_table("ID", "Stack", "Status", "Scheduled")
        for d in detections:
            table.add_row(
                d.get("id", "-"),
                d.get("stack_id", "-"),
                d.get("status", "-"),
                d.get("scheduled_for", "-"),
            )

        console.print(table)
    except Exception as e:
        print_error(f"Failed to list pending detections: {e}")
        raise typer.Exit(1) from e


def impact(
    detection_id: str = typer.Argument(..., help="Detection ID"),
) -> None:
    """Analyze the impact of detected drift."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_impact.sync_detailed(
            detection_id=detection_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No impact analysis available.")
            return

        analysis = data.get("impact", data)

        table = create_table("Field", "Value", title="Impact Analysis")
        table.add_row("Severity", analysis.get("severity", "-"))
        table.add_row("Risk Score", str(analysis.get("risk_score", "-")))
        table.add_row("Affected Resources", str(analysis.get("affected", "-")))
        table.add_row("Recommendation", analysis.get("recommendation", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to analyze impact: {e}")
        raise typer.Exit(1) from e


def complete(
    detection_id: str = typer.Argument(..., help="Detection ID"),
    drift_found: bool = typer.Option(False, "--drift/--no-drift", help="Whether drift was found"),
) -> None:
    """Mark a drift detection as complete."""
    try:
        # Create body with required fields
        body = DriftDetectionResultSchema(
            drift_detected=drift_found,
            drift_summary=DriftDetectionResultSchemaDriftSummary(),
            drifted_resources=[],
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_complete.sync_detailed(
            detection_id=detection_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to complete detection.")
            return

        print_success(f"Detection completed: {detection_id}")
    except Exception as e:
        print_error(f"Failed to complete detection: {e}")
        raise typer.Exit(1) from e


def fail(
    detection_id: str = typer.Argument(..., help="Detection ID"),
    reason: str = typer.Option(..., "--reason", "-r", help="Failure reason"),
) -> None:
    """Mark a drift detection as failed."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_fail.sync_detailed(
            detection_id=detection_id,
            client=auth_client,
            error_message=reason,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to mark detection as failed.")
            return

        print_success(f"Detection marked as failed: {detection_id}")
    except Exception as e:
        print_error(f"Failed to mark detection failed: {e}")
        raise typer.Exit(1) from e


def remediated(
    detection_id: str = typer.Argument(..., help="Detection ID"),
    run_id: str = typer.Option(..., "--run", "-r", help="Remediation run ID"),
) -> None:
    """Mark drift as remediated."""
    try:
        body = DriftRemediationRequestSchema(remediation_run_id=run_id)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_remediated.sync_detailed(
            detection_id=detection_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to mark as remediated.")
            return

        print_success(f"Drift marked as remediated: {detection_id}")
    except Exception as e:
        print_error(f"Failed to mark remediated: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("schedule")(schedule)
app.command("periodic")(periodic)
app.command("start")(start)
app.command("show")(show)
app.command("latest")(latest)
app.command("pending")(pending)
app.command("impact")(impact)
app.command("complete")(complete)
app.command("fail")(fail)
app.command("remediated")(remediated)
