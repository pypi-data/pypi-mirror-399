"""Compliance policy sets commands - list, show (read-only)."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_policies import (
    get_policy_set as api_get,
)
from iltero.api_client.api.compliance_policies import (
    list_policy_sets as api_list,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance policy sets management")
console = Console()

# Column definitions for policy sets table
POLICY_SET_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("source_type", "Source"),
    ("policy_count", "Policies"),
    ("active", "Active"),
]


def list_policy_sets(
    source_type: str | None = typer.Option(
        None,
        "--source-type",
        "-s",
        help="Filter by source type (builtin, custom, marketplace)",
    ),
    active: bool | None = typer.Option(
        None,
        "--active/--inactive",
        "-a/-i",
        help="Filter by active status",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """List compliance policy sets.

    Retrieves available compliance policy sets. Policy sets define the
    rules and checks applied during scans. Filter by source type or
    active status to find specific sets.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            source_type=source_type,
            active=active,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No policy sets found matching criteria")
            return

        if output_format == "json":
            console.print_json(data=data)
            return

        table = create_table(
            *[col_name for _, col_name in POLICY_SET_COLUMNS],
            title="Compliance Policy Sets",
        )

        policy_sets = data if isinstance(data, list) else [data]
        for ps in policy_sets:
            row = []
            for col_key, _ in POLICY_SET_COLUMNS:
                value = ps.get(col_key, "")
                if col_key == "active":
                    value = "✓" if value else "✗"
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(policy_sets)} policy set(s)")

    except Exception as e:
        print_error(f"Error listing policy sets: {e}")
        raise typer.Exit(1)


def show_policy_set(
    policy_set_id: str = typer.Argument(
        ...,
        help="Policy set ID to show",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Show detailed information about a policy set.

    Retrieves complete policy set configuration including all policies
    within the set, their severities, and compliance framework mappings.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            policy_set_id=policy_set_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        ps_name = data.get("name", policy_set_id)
        console.print(f"\n[bold]Policy Set:[/bold] {ps_name}")
        console.print(f"[bold]ID:[/bold] {data.get('id', policy_set_id)}")

        if source_type := data.get("source_type"):
            console.print(f"[bold]Source Type:[/bold] {source_type}")

        active = data.get("active", False)
        active_status = "[green]Active[/]" if active else "[red]Inactive[/]"
        console.print(f"[bold]Status:[/bold] {active_status}")

        if policy_count := data.get("policy_count"):
            console.print(f"[bold]Policy Count:[/bold] {policy_count}")

        if description := data.get("description"):
            console.print("\n[bold]Description:[/bold]")
            console.print(f"  {description}")

        if frameworks := data.get("compliance_frameworks"):
            console.print("\n[bold]Compliance Frameworks:[/bold]")
            if isinstance(frameworks, list):
                for fw in frameworks:
                    console.print(f"  • {fw}")
            else:
                console.print(f"  {frameworks}")

        if policies := data.get("policies"):
            console.print("\n[bold]Policies:[/bold]")
            table = create_table("ID", "Name", "Severity", "Active")
            for p in policies:
                active_icon = "✓" if p.get("active", False) else "✗"
                table.add_row(
                    str(p.get("id", "-")),
                    str(p.get("name", "-")),
                    str(p.get("severity", "-")),
                    active_icon,
                )
            console.print(table)

        console.print()

    except Exception as e:
        print_error(f"Error showing policy set: {e}")
        raise typer.Exit(1)


# Register commands
app.command("list")(list_policy_sets)
app.command("show")(show_policy_set)
