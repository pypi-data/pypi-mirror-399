"""Stack approval commands - list, show, request, approve, reject, cancel."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.stack_approvals import (
    approve_deployment as api_approve,
)
from iltero.api_client.api.stack_approvals import (
    cancel_approval as api_cancel,
)
from iltero.api_client.api.stack_approvals import (
    check_expired_approvals as api_expired,
)
from iltero.api_client.api.stack_approvals import (
    get_approval as api_get,
)
from iltero.api_client.api.stack_approvals import (
    get_compliance_analysis as api_compliance,
)
from iltero.api_client.api.stack_approvals import (
    get_run_approval as api_run,
)
from iltero.api_client.api.stack_approvals import (
    list_pending_approvals as api_list,
)
from iltero.api_client.api.stack_approvals import (
    reject_deployment as api_reject,
)
from iltero.api_client.api.stack_approvals import (
    request_deployment_approval as api_request,
)
from iltero.api_client.models.approval_request_schema import (
    ApprovalRequestSchema,
)
from iltero.api_client.models.approve_request_schema import (
    ApproveRequestSchema,
)
from iltero.api_client.models.reject_request_schema import (
    RejectRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack deployment approval management")
console = Console()


def list_approvals(
    stack_id: str | None = typer.Option(None, "--stack", "-s", help="Filter by stack ID"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max results"),
) -> None:
    """List pending approval requests."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No pending approvals found.")
            return

        approvals = data.get("approvals", [])
        if not approvals:
            print_info("No pending approvals found.")
            return

        table = create_table("ID", "Stack", "Status", "Requester", "Created")
        for approval in approvals[:limit]:
            table.add_row(
                approval.get("id", "-"),
                approval.get("stack_id", "-"),
                approval.get("status", "-"),
                approval.get("requester", "-"),
                approval.get("created_at", "-")[:10] if approval.get("created_at") else "-",
            )

        console.print(table)
        console.print(f"\nTotal: [cyan]{len(approvals)}[/cyan] pending")
    except Exception as e:
        print_error(f"Failed to list approvals: {e}")
        raise typer.Exit(1) from e


def show_approval(
    approval_id: str = typer.Argument(..., help="Approval request ID"),
) -> None:
    """Show details of an approval request."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            approval_id=approval_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Approval not found.")
            return

        approval = data.get("approval", data)

        table = create_table("Field", "Value", title="Approval Details")
        table.add_row("ID", approval.get("id", "-"))
        table.add_row("Stack ID", approval.get("stack_id", "-"))
        table.add_row("Run ID", approval.get("run_id", "-"))
        table.add_row("Status", approval.get("status", "-"))
        table.add_row("Requester", approval.get("requester", "-"))
        table.add_row("Approver", approval.get("approver", "-") or "-")
        table.add_row("Created At", approval.get("created_at", "-"))
        table.add_row("Expires At", approval.get("expires_at", "-"))

        console.print(table)

        # Show plan summary if available
        plan = approval.get("plan_summary")
        if plan:
            console.print("\n[bold]Plan Summary[/bold]")
            console.print(f"  Add: [green]{plan.get('add', 0)}[/green]")
            console.print(f"  Change: [yellow]{plan.get('change', 0)}[/yellow]")
            console.print(f"  Destroy: [red]{plan.get('destroy', 0)}[/red]")
    except Exception as e:
        print_error(f"Failed to get approval: {e}")
        raise typer.Exit(1) from e


def request_approval(
    run_id: str = typer.Argument(..., help="Run ID to request approval for"),
    reason: str = typer.Option("", "--reason", help="Reason for request"),
    priority: str = typer.Option(
        "MEDIUM",
        "--priority",
        "-p",
        help="Priority (LOW, MEDIUM, HIGH, CRITICAL)",
    ),
) -> None:
    """Request deployment approval for a stack run."""
    try:
        body = ApprovalRequestSchema(
            run_id=run_id,
            reason=reason,
            priority=priority,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_request.sync_detailed(
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to create approval request.")
            return

        approval = data.get("approval", data)
        approval_id = approval.get("id", "N/A")
        print_success(f"Approval requested: {approval_id}")
    except Exception as e:
        print_error(f"Failed to request approval: {e}")
        raise typer.Exit(1) from e


def approve(
    approval_id: str = typer.Argument(..., help="Approval request ID"),
    comment: str = typer.Option("", "--comment", "-c", help="Approval comment"),
) -> None:
    """Approve a deployment request."""
    try:
        body = ApproveRequestSchema(comment=comment)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_approve.sync_detailed(
            approval_id=approval_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Approval action failed.")
            return

        print_success(f"Deployment approved: {approval_id}")
    except Exception as e:
        print_error(f"Failed to approve: {e}")
        raise typer.Exit(1) from e


def reject(
    approval_id: str = typer.Argument(..., help="Approval request ID"),
    comment: str = typer.Option("", "--comment", "-c", help="Rejection comment"),
) -> None:
    """Reject a deployment request."""
    try:
        body = RejectRequestSchema(comment=comment)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_reject.sync_detailed(
            approval_id=approval_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Rejection action failed.")
            return

        print_success(f"Deployment rejected: {approval_id}")
    except Exception as e:
        print_error(f"Failed to reject: {e}")
        raise typer.Exit(1) from e


def cancel(
    approval_id: str = typer.Argument(..., help="Approval request ID"),
    reason: str = typer.Option("", "--reason", "-r", help="Cancellation reason"),
) -> None:
    """Cancel a pending approval request."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_cancel.sync_detailed(
            approval_id=approval_id,
            client=auth_client,
            reason=reason,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Cancel action failed.")
            return

        print_success(f"Approval cancelled: {approval_id}")
    except Exception as e:
        print_error(f"Failed to cancel approval: {e}")
        raise typer.Exit(1) from e


def compliance(
    run_id: str = typer.Argument(..., help="Run ID"),
) -> None:
    """Show compliance analysis for a run's approval request."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_compliance.sync_detailed(
            run_id=run_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No compliance analysis available.")
            return

        analysis = data.get("compliance", data)

        table = create_table("Field", "Value", title="Compliance Analysis")
        table.add_row("Status", analysis.get("status", "-"))
        table.add_row("Score", str(analysis.get("score", "-")))
        table.add_row("Violations", str(analysis.get("violation_count", "-")))
        table.add_row("Warnings", str(analysis.get("warning_count", "-")))

        console.print(table)

        # Show violations if any
        violations = analysis.get("violations", [])
        if violations:
            v_table = create_table("Policy", "Severity", "Resource")
            for v in violations[:10]:
                v_table.add_row(
                    v.get("policy_id", "-"),
                    v.get("severity", "-"),
                    v.get("resource", "-"),
                )
            console.print("\n[bold]Violations[/bold]")
            console.print(v_table)
    except Exception as e:
        print_error(f"Failed to get compliance analysis: {e}")
        raise typer.Exit(1) from e


def run_approval(
    run_id: str = typer.Argument(..., help="Run ID"),
) -> None:
    """Get approval status for a specific run."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_run.sync_detailed(
            run_id=run_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No approval found for this run.")
            return

        approval = data.get("approval", data)

        table = create_table("Field", "Value", title="Run Approval Status")
        table.add_row("Approval ID", approval.get("id", "-"))
        table.add_row("Run ID", run_id)
        table.add_row("Status", approval.get("status", "-"))
        table.add_row("Approver", approval.get("approver", "-") or "-")
        table.add_row("Approved At", approval.get("approved_at", "-") or "-")

        console.print(table)
    except Exception as e:
        print_error(f"Failed to get run approval: {e}")
        raise typer.Exit(1) from e


def expired() -> None:
    """Check and expire pending approval requests."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_expired.sync_detailed(
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No expired approvals processed.")
            return

        count = data.get("expired_count", 0)
        print_success(f"Processed {count} expired approval(s)")
    except Exception as e:
        print_error(f"Failed to list expired approvals: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("list")(list_approvals)
app.command("show")(show_approval)
app.command("request")(request_approval)
app.command("approve")(approve)
app.command("reject")(reject)
app.command("cancel")(cancel)
app.command("compliance")(compliance)
app.command("run")(run_approval)
app.command("expired")(expired)
