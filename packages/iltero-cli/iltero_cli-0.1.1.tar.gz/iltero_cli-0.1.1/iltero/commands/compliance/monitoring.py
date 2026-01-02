"""Compliance monitoring commands - status, alerts, ack."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_stack_monitoring import (
    acknowledge_alert as api_ack,
)
from iltero.api_client.api.compliance_stack_monitoring import (
    get_alerts as api_alerts,
)
from iltero.api_client.api.compliance_stack_monitoring import (
    get_monitoring_status as api_status,
)
from iltero.api_client.models.alert_acknowledgment_request_schema import (
    AlertAcknowledgmentRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance monitoring management")
console = Console()

# Severity color mapping
SEVERITY_COLORS = {
    "critical": "red",
    "high": "bright_red",
    "medium": "yellow",
    "low": "blue",
    "info": "white",
}

# Status color mapping
STATUS_COLORS = {
    "active": "green",
    "paused": "yellow",
    "error": "red",
}


def status(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
) -> None:
    """Get monitoring status for a stack."""
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
            print_info("No monitoring data found.")
            return

        status_data = data.get("monitoring", data)

        table = create_table("Field", "Value", title="Monitoring Status")

        enabled = status_data.get("enabled", status_data.get("is_enabled"))
        if enabled is not None:
            if enabled:
                enabled_str = "[green]Enabled[/green]"
            else:
                enabled_str = "[red]Disabled[/red]"
            table.add_row("Status", enabled_str)

        table.add_row("Stack ID", status_data.get("stack_id", "-"))
        table.add_row("Last Check", status_data.get("last_check", "-"))
        table.add_row("Check Interval", status_data.get("check_interval", "-"))
        alerts_count = status_data.get("active_alerts", "-")
        table.add_row("Active Alerts", str(alerts_count))
        checks = status_data.get("total_checks", "-")
        table.add_row("Total Checks", str(checks))

        console.print(table)

        # Show configured monitors if available
        monitors = status_data.get("monitors", [])
        if monitors:
            mon_table = create_table("Type", "Status", "Last Run")
            for monitor in monitors:
                mon_status = monitor.get("status", "unknown")
                color = STATUS_COLORS.get(mon_status.lower(), "white")
                mon_table.add_row(
                    monitor.get("type", "-"),
                    f"[{color}]{mon_status}[/{color}]",
                    monitor.get("last_run", "-"),
                )
            console.print(mon_table)
    except Exception as e:
        print_error(f"Failed to get monitoring status: {e}")
        raise typer.Exit(1) from e


def alerts(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    filter_status: str | None = typer.Option("ACTIVE", "--status", "-s", help="Filter by status"),
) -> None:
    """Get compliance alerts for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_alerts.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            status=filter_status,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No alerts found.")
            return

        alerts_list = data.get("alerts", [])
        if not alerts_list:
            status_str = filter_status.lower() if filter_status else ""
            print_info(f"No {status_str} alerts found.")
            return

        table = create_table(
            "ID",
            "Severity",
            "Type",
            "Message",
            "Created At",
            title="Compliance Alerts",
        )

        for alert in alerts_list:
            severity = alert.get("severity", "unknown").lower()
            color = SEVERITY_COLORS.get(severity, "white")

            message = alert.get("message", "-")
            if len(message) > 50:
                message = message[:47] + "..."

            table.add_row(
                alert.get("id", "-"),
                f"[{color}]{severity.upper()}[/{color}]",
                alert.get("type", "-"),
                message,
                alert.get("created_at", "-"),
            )

        console.print(table)
    except Exception as e:
        print_error(f"Failed to get alerts: {e}")
        raise typer.Exit(1) from e


def ack(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    alert_id: str = typer.Argument(..., help="Alert identifier"),
    note: str | None = typer.Option(None, "--note", "-n", help="Note"),
    action: str | None = typer.Option(None, "--action", "-a", help="Action"),
    assign_to: str | None = typer.Option(None, "--assign", help="User ID"),
) -> None:
    """Acknowledge a compliance alert."""
    try:
        body = AlertAcknowledgmentRequestSchema(
            stack_id=stack_id,
            acknowledgment_note=note,
            action_taken=action,
            assign_to=assign_to,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_ack.sync_detailed(
            stack_id=stack_id,
            alert_id=alert_id,
            client=auth_client,
            body=body,
        )

        client.handle_response(response)
        print_success(f"Alert {alert_id} acknowledged")

        if note:
            console.print(f"  Note: {note}")
        if action:
            console.print(f"  Action: {action}")
        if assign_to:
            console.print(f"  Assigned to: {assign_to}")
    except Exception as e:
        print_error(f"Failed to acknowledge alert: {e}")
        raise typer.Exit(1) from e


app.command("status")(status)
app.command("alerts")(alerts)
app.command("ack")(ack)
