"""Stack runs commands - list and show run details."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel

from iltero.api_client.api.stacks_runs import (
    get_stack_run as api_get,
)
from iltero.api_client.api.stacks_runs import (
    list_stack_runs as api_list,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack run history and details")
console = Console()

# Status colors for run states
STATUS_COLORS = {
    "pending": "yellow",
    "running": "blue",
    "success": "green",
    "succeeded": "green",
    "completed": "green",
    "failed": "red",
    "error": "red",
    "cancelled": "dim",
    "canceled": "dim",
    "queued": "cyan",
}


def _format_status(status: str | None) -> str:
    """Format status with color."""
    if not status:
        return "-"
    color = STATUS_COLORS.get(status.lower(), "white")
    return f"[{color}]{status}[/{color}]"


def _format_duration(seconds: int | float | None) -> str:
    """Format duration in human-readable form."""
    if seconds is None:
        return "-"
    try:
        secs = int(seconds)
        if secs < 60:
            return f"{secs}s"
        elif secs < 3600:
            mins = secs // 60
            remaining = secs % 60
            return f"{mins}m {remaining}s"
        else:
            hours = secs // 3600
            mins = (secs % 3600) // 60
            return f"{hours}h {mins}m"
    except (TypeError, ValueError):
        return "-"


@app.command("list")
def list_runs(
    stack_id: str = typer.Argument(..., help="Stack ID to list runs for"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of runs to display"),
    status: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
) -> None:
    """List recent runs for a stack.

    Displays deployment history with status, duration, and trigger info.
    Results are ordered by creation time, most recent first.

    Example:
        iltero stack runs list abc123
        iltero stack runs list abc123 --limit 10
        iltero stack runs list abc123 --status failed
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            limit=min(limit, 100),  # API max
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info(f"No runs found for stack '{stack_id}'.")
            return

        runs = data.get("runs", [])
        if not runs:
            print_info(f"No runs found for stack '{stack_id}'.")
            return

        # Filter by status if specified
        if status:
            runs = [r for r in runs if r.get("status", "").lower() == status.lower()]
            if not runs:
                print_info(f"No runs found with status '{status}'.")
                return

        # Limit results
        runs = runs[:limit]

        table = create_table("ID", "Status", "Type", "Trigger", "Duration", "Created")

        for run in runs:
            run_id = run.get("id", "-")
            run_status = _format_status(run.get("status"))
            run_type = run.get("type", run.get("run_type", "-"))
            trigger = run.get("trigger", run.get("triggered_by", "-"))
            duration = _format_duration(run.get("duration_seconds"))
            created = run.get("created_at", "-")
            if created and created != "-":
                created = created[:16].replace("T", " ")

            table.add_row(
                run_id[:12] if run_id != "-" else "-",
                run_status,
                run_type,
                trigger,
                duration,
                created,
            )

        console.print(table)
        console.print(f"\nShowing [cyan]{len(runs)}[/cyan] most recent runs")

    except Exception as e:
        print_error(f"Failed to list runs: {e}")
        raise typer.Exit(1) from e


@app.command("show")
def show_run(
    stack_id: str = typer.Argument(..., help="Stack ID"),
    run_id: str = typer.Argument(..., help="Run ID to show details for"),
) -> None:
    """Show detailed information about a specific run.

    Displays run status, outputs, logs, and resource changes.

    Example:
        iltero stack runs show abc123 run-xyz789
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            stack_id=stack_id,
            run_id=run_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_error(f"Run '{run_id}' not found.")
            raise typer.Exit(1)

        run = data.get("run", data)

        # Header panel
        status = run.get("status", "unknown")
        status_display = _format_status(status)
        title = f"Run {run_id[:12]} - {status_display}"

        # Build details
        details = []
        details.append(f"[bold]Stack:[/bold] {run.get('stack_id', '-')}")
        details.append(f"[bold]Type:[/bold] {run.get('type', '-')}")
        details.append(f"[bold]Status:[/bold] {status_display}")

        trigger = run.get("trigger", run.get("triggered_by", "-"))
        details.append(f"[bold]Trigger:[/bold] {trigger}")

        created = run.get("created_at", "-")
        if created and created != "-":
            created = created[:19].replace("T", " ")
        details.append(f"[bold]Created:[/bold] {created}")

        started = run.get("started_at", "-")
        if started and started != "-":
            started = started[:19].replace("T", " ")
        details.append(f"[bold]Started:[/bold] {started}")

        finished = run.get("finished_at", run.get("completed_at", "-"))
        if finished and finished != "-":
            finished = finished[:19].replace("T", " ")
        details.append(f"[bold]Finished:[/bold] {finished}")

        duration = _format_duration(run.get("duration_seconds"))
        details.append(f"[bold]Duration:[/bold] {duration}")

        console.print(Panel("\n".join(details), title=title))

        # Resource changes if available
        changes = run.get("resource_changes", run.get("changes", {}))
        if changes:
            console.print("\n[bold]Resource Changes:[/bold]")
            add = changes.get("add", changes.get("to_add", 0))
            change = changes.get("change", changes.get("to_change", 0))
            destroy = changes.get("destroy", changes.get("to_destroy", 0))
            console.print(
                f"  [green]+{add}[/green] to add, "
                f"[yellow]~{change}[/yellow] to change, "
                f"[red]-{destroy}[/red] to destroy"
            )

        # Outputs if available
        outputs = run.get("outputs", {})
        if outputs:
            console.print("\n[bold]Outputs:[/bold]")
            for key, value in outputs.items():
                val_str = str(value)
                if len(val_str) > 60:
                    val_str = val_str[:57] + "..."
                console.print(f"  {key}: [cyan]{val_str}[/cyan]")

        # Error message if failed
        if status.lower() in ("failed", "error"):
            error_msg = run.get("error", run.get("error_message", ""))
            if error_msg:
                console.print("\n[bold red]Error:[/bold red]")
                console.print(f"  {error_msg}")

        # Logs hint
        logs_url = run.get("logs_url", "")
        if logs_url:
            console.print(f"\n[dim]Logs: {logs_url}[/dim]")
        else:
            console.print("\n[dim]Use the web UI to view detailed logs[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to get run details: {e}")
        raise typer.Exit(1) from e
