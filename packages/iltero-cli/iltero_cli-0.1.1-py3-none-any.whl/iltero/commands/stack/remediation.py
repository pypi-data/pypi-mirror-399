"""Stack remediation commands - plan, apply, status, history."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_stack_remediation import (
    apply_remediation as api_apply,
)
from iltero.api_client.api.compliance_stack_remediation import (
    create_policy_override as api_override,
)
from iltero.api_client.api.compliance_stack_remediation import (
    create_remediation_plan as api_plan,
)
from iltero.api_client.api.compliance_stack_remediation import (
    get_remediation_history as api_history,
)
from iltero.api_client.api.compliance_stack_remediation import (
    get_remediation_status as api_status,
)
from iltero.api_client.models.policy_override_request_schema import (
    PolicyOverrideRequestSchema,
)
from iltero.api_client.models.remediation_plan_request_schema import (
    RemediationPlanRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack remediation management")
console = Console()


def plan(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    validation_id: str = typer.Option(
        ..., "--validation", "-v", help="Validation ID with violations"
    ),
    auto_apply: bool = typer.Option(False, "--auto-apply", help="Auto-apply remediation"),
) -> None:
    """Create a remediation plan for a stack."""
    try:
        body = RemediationPlanRequestSchema(
            stack_id=stack_id,
            validation_id=validation_id,
            auto_apply=auto_apply,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_plan.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to create remediation plan.")
            return

        plan_data = data.get("plan", data)
        plan_id = plan_data.get("id", "N/A")

        print_success(f"Remediation plan created: {plan_id}")

        table = create_table("Field", "Value", title="Remediation Plan")
        table.add_row("ID", plan_data.get("id", "-"))
        table.add_row("Stack ID", stack_id)
        table.add_row("Status", plan_data.get("status", "-"))
        table.add_row("Actions", str(plan_data.get("action_count", "-")))
        table.add_row("Created At", plan_data.get("created_at", "-"))

        console.print(table)

        # Show actions summary
        actions = plan_data.get("actions", [])
        if actions:
            a_table = create_table("Action", "Resource", "Type")
            for action in actions[:10]:
                a_table.add_row(
                    action.get("action", "-"),
                    action.get("resource", "-"),
                    action.get("type", "-"),
                )
            console.print("\n[bold]Planned Actions[/bold]")
            console.print(a_table)
    except Exception as e:
        print_error(f"Failed to create remediation plan: {e}")
        raise typer.Exit(1) from e


def apply(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    plan_id: str = typer.Option(..., "--plan", "-p", help="Plan ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Force apply without confirmation"),
) -> None:
    """Apply a remediation plan."""
    try:
        if not force:
            confirm = typer.confirm(f"Apply remediation plan {plan_id}?", default=False)
            if not confirm:
                print_info("Operation cancelled.")
                return

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_apply.sync_detailed(
            stack_id=stack_id,
            plan_id=plan_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to apply remediation.")
            return

        execution = data.get("execution", data)
        print_success(f"Remediation applied: {plan_id}")

        table = create_table("Field", "Value", title="Execution Results")
        table.add_row("Status", execution.get("status", "-"))
        table.add_row("Actions Applied", str(execution.get("applied", "-")))
        table.add_row("Actions Failed", str(execution.get("failed", "-")))
        table.add_row("Duration", execution.get("duration", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to apply remediation: {e}")
        raise typer.Exit(1) from e


def status(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
) -> None:
    """Get remediation status for a stack."""
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
            print_info("No remediation status available.")
            return

        status_data = data.get("status", data)

        table = create_table("Field", "Value", title="Remediation Status")
        table.add_row("Stack ID", stack_id)
        table.add_row("Current Status", status_data.get("status", "-"))
        table.add_row("Last Plan ID", status_data.get("last_plan_id", "-"))
        table.add_row("Last Applied", status_data.get("last_applied", "-"))
        table.add_row("Pending Actions", str(status_data.get("pending", "-")))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to get remediation status: {e}")
        raise typer.Exit(1) from e


def history(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results"),
) -> None:
    """Show remediation history for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_history.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No remediation history found.")
            return

        entries = data.get("history", [])
        if not entries:
            print_info("No remediation history found.")
            return

        table = create_table("Plan ID", "Status", "Actions", "Applied At")
        for entry in entries[:limit]:
            table.add_row(
                entry.get("plan_id", "-"),
                entry.get("status", "-"),
                str(entry.get("action_count", "-")),
                entry.get("applied_at", "-")[:10] if entry.get("applied_at") else "-",
            )

        console.print(table)
        console.print(f"\nTotal entries: [cyan]{len(entries)}[/cyan]")
    except Exception as e:
        print_error(f"Failed to get remediation history: {e}")
        raise typer.Exit(1) from e


def override(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    policy_rule: str = typer.Option(..., "--rule", "-r", help="Policy rule to override"),
    reason: str = typer.Option(..., "--reason", help="Override reason"),
    duration: int = typer.Option(7, "--days", "-d", help="Override duration in days"),
) -> None:
    """Create a temporary policy override."""
    try:
        body = PolicyOverrideRequestSchema(
            stack_id=stack_id,
            policy_rule=policy_rule,
            override_reason=reason,
            expiration_days=duration,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_override.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to create override.")
            return

        override_data = data.get("override", data)
        override_id = override_data.get("id", "N/A")
        print_success(f"Override created: {override_id}")

        table = create_table("Field", "Value", title="Override Details")
        table.add_row("ID", override_data.get("id", "-"))
        table.add_row("Policy Rule", policy_rule)
        table.add_row("Duration", f"{duration} days")
        table.add_row("Expires At", override_data.get("expires_at", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to create override: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("plan")(plan)
app.command("apply")(apply)
app.command("status")(status)
app.command("history")(history)
app.command("override")(override)
