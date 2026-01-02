"""Stack policy exception commands - request, approve, list, show, revoke."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.stacks_policy_exceptions import (
    approve_policy_exception as api_approve,
)
from iltero.api_client.api.stacks_policy_exceptions import (
    policyexception_get_exception_status_36e4b9d0 as api_status,
)
from iltero.api_client.api.stacks_policy_exceptions import (
    policyexception_list_active_exceptions_b8970be2 as api_active,
)
from iltero.api_client.api.stacks_policy_exceptions import (
    policyexception_list_expiring_exceptions_1cd8bb99 as api_expiring,
)
from iltero.api_client.api.stacks_policy_exceptions import (
    policyexception_revoke_exception_17e24fa2 as api_revoke,
)
from iltero.api_client.api.stacks_policy_exceptions import (
    request_policy_exception as api_request,
)
from iltero.api_client.models.policy_exception_approval_schema import (
    PolicyExceptionApprovalSchema,
)
from iltero.api_client.models.policy_exception_request_schema import (
    PolicyExceptionRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack policy exception management")
console = Console()


def request_exception(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    scope: str = typer.Option(
        ..., "--scope", "-s", help="Rules/checks to exempt (comma-separated)"
    ),
    reason: str = typer.Option(..., "--reason", "-r", help="Justification for exception"),
    mitigation: str = typer.Option(..., "--mitigation", "-m", help="How risks will be mitigated"),
    duration_days: int = typer.Option(30, "--days", "-d", help="Exception duration in days"),
) -> None:
    """Request a policy exception for a stack."""
    try:
        scope_list = [s.strip() for s in scope.split(",")]
        body = PolicyExceptionRequestSchema(
            stack_id=stack_id,
            justification=reason,
            scope=scope_list,
            duration_days=duration_days,
            risk_mitigation=mitigation,
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
            print_info("Failed to create exception request.")
            return

        exception = data.get("exception", data)
        exception_id = exception.get("id", "N/A")
        print_success(f"Exception requested: {exception_id}")

        table = create_table("Field", "Value", title="Exception Details")
        table.add_row("ID", exception.get("id", "-"))
        table.add_row("Stack ID", stack_id)
        table.add_row("Scope", ", ".join(scope_list))
        table.add_row("Status", exception.get("status", "-"))
        table.add_row("Expires", exception.get("expires_at", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to request exception: {e}")
        raise typer.Exit(1) from e


def approve_exception(
    exception_ref: str = typer.Argument(..., help="Exception reference ID"),
    approver_id: str = typer.Option(..., "--approver", "-a", help="InfoSec approver ID"),
    expiry_date: str = typer.Option(..., "--expiry", "-e", help="Expiry date (ISO format)"),
    notes: str = typer.Option("", "--notes", "-n", help="Approval notes"),
) -> None:
    """Approve a policy exception request."""
    try:
        body = PolicyExceptionApprovalSchema(
            exception_ref=exception_ref,
            approved=True,
            approver_id=approver_id,
            expiry_date=expiry_date,
            notes=notes if notes else None,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_approve.sync_detailed(
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Approval action failed.")
            return

        print_success(f"Exception approved: {exception_ref}")
    except Exception as e:
        print_error(f"Failed to approve exception: {e}")
        raise typer.Exit(1) from e


def list_active(
    limit: int = typer.Option(20, "--limit", "-l", help="Max results"),
) -> None:
    """List active policy exceptions."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_active.sync_detailed(
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No active exceptions found.")
            return

        exceptions = data.get("exceptions", [])
        if not exceptions:
            print_info("No active exceptions found.")
            return

        table = create_table("ID", "Stack", "Policy", "Expires", "Approver")
        for exc in exceptions[:limit]:
            table.add_row(
                exc.get("id", "-"),
                exc.get("stack_id", "-"),
                exc.get("policy_id", "-"),
                exc.get("expires_at", "-")[:10] if exc.get("expires_at") else "-",
                exc.get("approved_by", "-"),
            )

        console.print(table)
        console.print(f"\nTotal active: [cyan]{len(exceptions)}[/cyan]")
    except Exception as e:
        print_error(f"Failed to list exceptions: {e}")
        raise typer.Exit(1) from e


def show_status(
    stack_id: str = typer.Argument(..., help="Stack ID"),
) -> None:
    """Show status of policy exceptions for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_status.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Exception not found.")
            return

        exception = data.get("exception", data)

        table = create_table("Field", "Value", title="Exception Status")
        table.add_row("ID", exception.get("id", "-"))
        table.add_row("Stack ID", exception.get("stack_id", "-"))
        table.add_row("Policy ID", exception.get("policy_id", "-"))
        table.add_row("Status", exception.get("status", "-"))
        table.add_row("Requested By", exception.get("requested_by", "-"))
        table.add_row("Approved By", exception.get("approved_by", "-") or "-")
        table.add_row("Created At", exception.get("created_at", "-"))
        table.add_row("Expires At", exception.get("expires_at", "-"))
        table.add_row("Justification", exception.get("justification", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to get exception status: {e}")
        raise typer.Exit(1) from e


def list_expiring(
    days: int = typer.Option(7, "--days", "-d", help="Days until expiration"),
) -> None:
    """List policy exceptions expiring soon."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_expiring.sync_detailed(
            client=auth_client,
            days=days,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No expiring exceptions found.")
            return

        exceptions = data.get("exceptions", [])
        if not exceptions:
            print_info(f"No exceptions expiring within {days} days.")
            return

        table = create_table("ID", "Stack", "Policy", "Expires In")
        for exc in exceptions:
            table.add_row(
                exc.get("id", "-"),
                exc.get("stack_id", "-"),
                exc.get("policy_id", "-"),
                exc.get("expires_in", "-"),
            )

        console.print(table)
        console.print(
            f"\n[yellow]⚠ {len(exceptions)} exceptions expiring within {days} days[/yellow]"
        )
    except Exception as e:
        print_error(f"Failed to list expiring exceptions: {e}")
        raise typer.Exit(1) from e


def revoke(
    stack_id: str = typer.Argument(..., help="Stack ID"),
    reason: str = typer.Option(..., "--reason", "-r", help="Revocation reason"),
) -> None:
    """Revoke an active policy exception."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_revoke.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            reason=reason,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Revocation failed.")
            return

        print_success(f"Exception revoked for stack: {stack_id}")
    except Exception as e:
        print_error(f"Failed to revoke exception: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("request")(request_exception)
app.command("approve")(approve_exception)
app.command("list")(list_active)
app.command("show")(show_status)
app.command("expiring")(list_expiring)
app.command("revoke")(revoke)
