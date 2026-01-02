"""Compliance remediation commands - list, show, create, update, execute."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_remediation import (
    create_remediation as api_create,
)
from iltero.api_client.api.compliance_remediation import (
    execute_remediation as api_execute,
)
from iltero.api_client.api.compliance_remediation import (
    get_remediation as api_get,
)
from iltero.api_client.api.compliance_remediation import (
    list_remediations as api_list,
)
from iltero.api_client.api.compliance_remediation import (
    update_remediation as api_update,
)
from iltero.api_client.models.remediation_create_schema import (
    RemediationCreateSchema,
)
from iltero.api_client.models.remediation_update_schema import (
    RemediationUpdateSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance remediation management")
console = Console()

# Column definitions for remediations table
REMEDIATION_COLUMNS = [
    ("id", "ID"),
    ("violation_id", "Violation"),
    ("action_type", "Type"),
    ("status", "Status"),
    ("created_at", "Created"),
]

# Status color mapping
STATUS_COLORS = {
    "pending": "blue",
    "in_progress": "yellow",
    "completed": "green",
    "failed": "red",
    "cancelled": "dim",
}

# Action type display
ACTION_TYPES = {
    "MANUAL": "Manual",
    "AUTOMATIC": "Automatic",
    "manual": "Manual",
    "automatic": "Automatic",
}


def list_remediations(
    violation_id: str | None = typer.Option(
        None,
        "--violation-id",
        "-v",
        help="Filter by violation ID",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Filter by status (pending, in_progress, completed, failed)",
    ),
    action_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by action type (MANUAL, AUTOMATIC)",
    ),
    limit: int = typer.Option(
        100,
        "--limit",
        "-l",
        help="Maximum number of results",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """List remediation actions.

    Retrieves remediation actions for compliance violations. Use filters
    to find remediations by violation, status, or type.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            violation_id=violation_id,
            status=status,
            action_type=action_type,
            limit=limit,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No remediations found matching criteria")
            return

        if output_format == "json":
            console.print_json(data=data)
            return

        table = create_table(
            *[col_name for _, col_name in REMEDIATION_COLUMNS],
            title="Remediation Actions",
        )

        remediations = data if isinstance(data, list) else [data]
        for rem in remediations:
            row = []
            for col_key, _ in REMEDIATION_COLUMNS:
                value = rem.get(col_key, "")
                if col_key == "status" and value:
                    color = STATUS_COLORS.get(value.lower(), "white")
                    value = f"[{color}]{value}[/]"
                elif col_key == "action_type" and value:
                    value = ACTION_TYPES.get(value, value)
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(remediations)} remediation(s)")

    except Exception as e:
        print_error(f"Error listing remediations: {e}")
        raise typer.Exit(1)


def show_remediation(
    remediation_id: str = typer.Argument(
        ...,
        help="Remediation ID to show",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Show detailed information about a remediation.

    Retrieves complete remediation details including status, affected
    resources, and execution history.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            remediation_id=remediation_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Remediation:[/bold] {remediation_id}")

        if violation_id := data.get("violation_id"):
            console.print(f"[bold]Violation:[/bold] {violation_id}")

        if action_type := data.get("action_type"):
            display_type = ACTION_TYPES.get(action_type, action_type)
            console.print(f"[bold]Type:[/bold] {display_type}")

        if status := data.get("status"):
            color = STATUS_COLORS.get(status.lower(), "white")
            console.print(f"[bold]Status:[/bold] [{color}]{status}[/]")

        if created := data.get("created_at"):
            console.print(f"[bold]Created:[/bold] {created}")

        if updated := data.get("updated_at"):
            console.print(f"[bold]Updated:[/bold] {updated}")

        if executed := data.get("executed_at"):
            console.print(f"[bold]Executed:[/bold] {executed}")

        if details := data.get("details"):
            console.print("\n[bold]Details:[/bold]")
            console.print(f"  {details}")

        if result_details := data.get("result"):
            console.print("\n[bold]Result:[/bold]")
            console.print(f"  {result_details}")

        # Show affected resources if present
        if resources := data.get("affected_resources"):
            console.print(f"\n[bold]Affected Resources:[/bold] {len(resources)}")
            for res in resources[:5]:
                console.print(f"  • {res}")
            if len(resources) > 5:
                console.print(f"  ... and {len(resources) - 5} more")

        console.print()

    except Exception as e:
        print_error(f"Error showing remediation: {e}")
        raise typer.Exit(1)


def create_remediation(
    violation_id: str = typer.Option(
        ...,
        "--violation-id",
        "-v",
        help="ID of the violation to remediate",
    ),
    action_type: str = typer.Option(
        ...,
        "--type",
        "-t",
        help="Type of remediation action (MANUAL or AUTOMATIC)",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        "-d",
        help="Details or description of the remediation action",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Create a remediation action.

    Creates a remediation action for a compliance violation. Supports
    both manual and automatic remediation workflows.
    """
    # Validate action type
    valid_types = ["MANUAL", "AUTOMATIC", "manual", "automatic"]
    if action_type not in valid_types:
        print_error(f"Invalid action type. Must be one of: {valid_types}")
        raise typer.Exit(1)

    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        body = RemediationCreateSchema(
            violation_id=violation_id,
            action_type=action_type.upper(),
            details=details,
        )

        response = api_create.sync_detailed(
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        rem_id = data.get("id", "unknown")
        console.print(f"\n[bold]Remediation created:[/bold] {rem_id}")

        if status := data.get("status"):
            color = STATUS_COLORS.get(status.lower(), "white")
            console.print(f"[bold]Status:[/bold] [{color}]{status}[/]")

        print_success("Remediation action created successfully")

    except Exception as e:
        print_error(f"Error creating remediation: {e}")
        raise typer.Exit(1)


def update_remediation(
    remediation_id: str = typer.Argument(
        ...,
        help="Remediation ID to update",
    ),
    status: str = typer.Option(
        ...,
        "--status",
        "-s",
        help="New status (pending, in_progress, completed, failed, cancelled)",
    ),
    details: str | None = typer.Option(
        None,
        "--details",
        "-d",
        help="Additional details about the status update",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Update remediation status.

    Updates the status of a remediation action. Use this to track
    progress or mark remediation as completed.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        body = RemediationUpdateSchema(
            status=status,
            details=details,
        )

        response = api_update.sync_detailed(
            remediation_id=remediation_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Remediation updated:[/bold] {remediation_id}")

        if new_status := data.get("status"):
            color = STATUS_COLORS.get(new_status.lower(), "white")
            console.print(f"[bold]Status:[/bold] [{color}]{new_status}[/]")

        print_success("Remediation updated successfully")

    except Exception as e:
        print_error(f"Error updating remediation: {e}")
        raise typer.Exit(1)


def execute_remediation(
    remediation_id: str = typer.Argument(
        ...,
        help="Remediation ID to execute",
    ),
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompt",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Execute a remediation action.

    Triggers execution of a remediation action. For automatic remediations,
    this starts the fix workflow. For manual remediations, this marks them
    as completed.

    Note: Execution may require elevated permissions.
    """
    if not confirm:
        typer.confirm(
            f"Execute remediation {remediation_id}? This action may modify resources.",
            abort=True,
        )

    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_execute.sync_detailed(
            remediation_id=remediation_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Remediation executed:[/bold] {remediation_id}")

        if status := data.get("status"):
            color = STATUS_COLORS.get(status.lower(), "white")
            console.print(f"[bold]Status:[/bold] [{color}]{status}[/]")

        if result_msg := data.get("result"):
            console.print(f"[bold]Result:[/bold] {result_msg}")

        print_success("Remediation executed successfully")

    except Exception as e:
        print_error(f"Error executing remediation: {e}")
        raise typer.Exit(1)


# Register commands
app.command("list")(list_remediations)
app.command("show")(show_remediation)
app.command("create")(create_remediation)
app.command("update")(update_remediation)
app.command("execute")(execute_remediation)
