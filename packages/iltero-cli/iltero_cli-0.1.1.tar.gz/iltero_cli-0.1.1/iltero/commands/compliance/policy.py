"""Compliance policy commands - list, show, violations (read-only)."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_policies import list_policies as api_list
from iltero.api_client.api.compliance_policies import (
    policy_get_policy_965bc6dd as api_get,
)
from iltero.api_client.api.compliance_policies import (
    policy_get_policy_violations_b215dff8 as api_violations,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance policies management")
console = Console()

# Column definitions for policies table
POLICY_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("severity", "Severity"),
    ("rule_id", "Rule ID"),
    ("policy_set_id", "Policy Set"),
    ("active", "Active"),
]


def list_policies(
    policy_set_id: str | None = typer.Option(
        None,
        "--policy-set-id",
        "-p",
        help="Filter by policy set ID",
    ),
    severity: str | None = typer.Option(
        None,
        "--severity",
        "-s",
        help="Filter by severity (critical, high, medium, low)",
    ),
    rule_id_pattern: str | None = typer.Option(
        None,
        "--rule-id",
        "-r",
        help="Filter by rule ID pattern",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """List compliance policies.

    Retrieves individual compliance policies. Use filters to find
    policies by set, severity, or rule ID pattern.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            policy_set_id=policy_set_id,
            severity=severity,
            rule_id_pattern=rule_id_pattern,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No policies found matching criteria")
            return

        if output_format == "json":
            console.print_json(data=data)
            return

        table = create_table(
            *[col_name for _, col_name in POLICY_COLUMNS],
            title="Compliance Policies",
        )

        policies = data if isinstance(data, list) else [data]
        for policy in policies:
            row = []
            for col_key, _ in POLICY_COLUMNS:
                value = policy.get(col_key, "")
                if col_key == "active":
                    value = "✓" if value else "✗"
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(policies)} policy(ies)")

    except Exception as e:
        print_error(f"Error listing policies: {e}")
        raise typer.Exit(1)


def show_policy(
    policy_id: str = typer.Argument(
        ...,
        help="Policy ID to show",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Show detailed information about a policy.

    Retrieves complete policy configuration including rule definitions,
    severity, and compliance framework mappings.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            policy_id=policy_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Policy:[/bold] {data.get('name', policy_id)}")
        console.print(f"[bold]ID:[/bold] {data.get('id', policy_id)}")

        if rule_id := data.get("rule_id"):
            console.print(f"[bold]Rule ID:[/bold] {rule_id}")

        if severity := data.get("severity"):
            severity_color = {
                "critical": "red",
                "high": "bright_red",
                "medium": "yellow",
                "low": "blue",
            }.get(severity.lower(), "white")
            console.print(f"[bold]Severity:[/bold] [{severity_color}]{severity}[/]")

        if policy_set := data.get("policy_set_id"):
            console.print(f"[bold]Policy Set:[/bold] {policy_set}")

        active = data.get("active", False)
        active_status = "[green]Active[/]" if active else "[red]Inactive[/]"
        console.print(f"[bold]Status:[/bold] {active_status}")

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

        if remediation := data.get("remediation_guidance"):
            console.print("\n[bold]Remediation Guidance:[/bold]")
            console.print(f"  {remediation}")

        console.print()

    except Exception as e:
        print_error(f"Error showing policy: {e}")
        raise typer.Exit(1)


def policy_violations(
    policy_id: str = typer.Argument(
        ...,
        help="Policy ID to get violations for",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Get violation summary for a policy.

    Retrieves a summary of all violations associated with a specific policy,
    including counts by status and severity.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_violations.sync_detailed(
            policy_id=policy_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Violations for Policy:[/bold] {policy_id}")

        if total := data.get("total_violations"):
            console.print(f"[bold]Total Violations:[/bold] {total}")

        if by_status := data.get("by_status"):
            console.print("\n[bold]By Status:[/bold]")
            for status, count in by_status.items():
                console.print(f"  • {status}: {count}")

        if by_severity := data.get("by_severity"):
            console.print("\n[bold]By Severity:[/bold]")
            for severity, count in by_severity.items():
                console.print(f"  • {severity}: {count}")

        if violations := data.get("violations"):
            console.print("\n[bold]Recent Violations:[/bold]")
            table = create_table("ID", "Resource", "Status", "Created")
            for v in violations[:10]:
                table.add_row(
                    str(v.get("id", "-")),
                    str(v.get("resource_id", "-")),
                    str(v.get("status", "-")),
                    str(v.get("created_at", "-")),
                )
            console.print(table)

        console.print()

    except Exception as e:
        print_error(f"Error getting policy violations: {e}")
        raise typer.Exit(1)


# Register commands
app.command("list")(list_policies)
app.command("show")(show_policy)
app.command("violations")(policy_violations)
