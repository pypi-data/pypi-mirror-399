"""Compliance violations commands - list, show, update."""

from __future__ import annotations

from uuid import UUID

import typer
from rich.console import Console

from iltero.api_client.api.compliance_violations import (
    get_violation as api_get,
)
from iltero.api_client.api.compliance_violations import (
    list_violations as api_list,
)
from iltero.api_client.api.compliance_violations import (
    update_violation as api_update,
)
from iltero.api_client.models.violation_update_schema import (
    ViolationUpdateSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance violations management")
console = Console()

# Column definitions for violations table
VIOLATION_COLUMNS = [
    ("id", "ID"),
    ("policy_id", "Policy"),
    ("severity", "Severity"),
    ("status", "Status"),
    ("resource_type", "Resource Type"),
    ("resource_id", "Resource ID"),
]


def list_violations(
    scan_id: str | None = typer.Option(
        None,
        "--scan-id",
        "-s",
        help="Filter by scan ID",
    ),
    stack_id: str | None = typer.Option(
        None,
        "--stack-id",
        help="Filter by stack ID",
    ),
    policy_id: str | None = typer.Option(
        None,
        "--policy-id",
        "-p",
        help="Filter by policy ID",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by status (open, acknowledged, resolved)",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """List compliance violations.

    Retrieves violations found during compliance scans. Use filters to
    find specific violations by scan, stack, policy, or status.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            scan_id=scan_id,
            stack_id=stack_id,
            policy_id=policy_id,
            status=status,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No violations found matching criteria")
            return

        if output_format == "json":
            console.print_json(data=data)
            return

        table = create_table(
            *[col_name for _, col_name in VIOLATION_COLUMNS],
            title="Compliance Violations",
        )

        violations = data if isinstance(data, list) else [data]
        for violation in violations:
            row = []
            for col_key, _ in VIOLATION_COLUMNS:
                value = violation.get(col_key, "")
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(violations)} violation(s)")

    except Exception as e:
        print_error(f"Error listing violations: {e}")
        raise typer.Exit(1)


def show_violation(
    violation_id: str = typer.Argument(
        ...,
        help="Violation ID to show",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Show detailed information about a violation.

    Retrieves full violation context including affected resources,
    policy details, and available remediation options.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            violation_id=violation_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Violation:[/bold] {data.get('id', violation_id)}")

        if policy := data.get("policy_id"):
            console.print(f"[bold]Policy:[/bold] {policy}")

        if severity := data.get("severity"):
            severity_color = {
                "critical": "red",
                "high": "bright_red",
                "medium": "yellow",
                "low": "blue",
            }.get(severity.lower(), "white")
            console.print(f"[bold]Severity:[/bold] [{severity_color}]{severity}[/]")

        if status := data.get("status"):
            console.print(f"[bold]Status:[/bold] {status}")

        if resource_type := data.get("resource_type"):
            console.print(f"[bold]Resource Type:[/bold] {resource_type}")

        if resource_id := data.get("resource_id"):
            console.print(f"[bold]Resource ID:[/bold] {resource_id}")

        if description := data.get("description"):
            console.print("\n[bold]Description:[/bold]")
            console.print(f"  {description}")

        if remediation := data.get("remediation_guidance"):
            console.print("\n[bold]Remediation Guidance:[/bold]")
            console.print(f"  {remediation}")

        if scan_id := data.get("scan_id"):
            console.print(f"\n[bold]Scan ID:[/bold] {scan_id}")

        if created := data.get("created_at"):
            console.print(f"[bold]Created:[/bold] {created}")

        console.print()

    except Exception as e:
        print_error(f"Error showing violation: {e}")
        raise typer.Exit(1)


def update_violation(
    violation_id: str = typer.Argument(
        ...,
        help="Violation ID to update",
    ),
    status: str = typer.Option(
        ...,
        "--status",
        "-s",
        help="New status (open, acknowledged, resolved, false_positive)",
    ),
    comment: str | None = typer.Option(
        None,
        "--comment",
        "-c",
        help="Comment explaining the status change",
    ),
    create_remediation: bool = typer.Option(
        False,
        "--create-remediation",
        "-r",
        help="Create a remediation action for this violation",
    ),
    remediation_type: str | None = typer.Option(
        None,
        "--remediation-type",
        help="Type of remediation (MANUAL or AUTOMATIC)",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Update a violation's status.

    Use this command to acknowledge violations, mark them as resolved,
    or flag them as false positives. Comments are recorded for audit trail.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        body = ViolationUpdateSchema(
            status=status,
            comment=comment,
            create_remediation=create_remediation,
            remediation_type=remediation_type,
        )

        response = api_update.sync_detailed(
            violation_id=UUID(violation_id),
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        print_success(f"Violation {violation_id} updated to status: {status}")

        if create_remediation and data.get("remediation_id"):
            print_info(f"Remediation created: {data.get('remediation_id')}")

    except Exception as e:
        print_error(f"Error updating violation: {e}")
        raise typer.Exit(1)


# Register commands
app.command("list")(list_violations)
app.command("show")(show_violation)
app.command("update")(update_violation)
