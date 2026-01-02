"""Compliance scans commands - list, show, submit."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from iltero.api_client.api.compliance_scans import get_scan as api_get
from iltero.api_client.api.compliance_scans import list_scans as api_list
from iltero.api_client.api.compliance_scans import (
    submit_scan_results as api_submit,
)
from iltero.api_client.models.scan_results_submission_schema import (
    ScanResultsSubmissionSchema,
)
from iltero.api_client.models.scan_results_submission_schema_scan_results import (
    ScanResultsSubmissionSchemaScanResults,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance scans management")
console = Console()

# Column definitions for scans table
SCAN_COLUMNS = [
    ("id", "ID"),
    ("stack_id", "Stack"),
    ("scan_type", "Type"),
    ("status", "Status"),
    ("score", "Score"),
    ("created_at", "Created"),
]

# Status color mapping
STATUS_COLORS = {
    "completed": "green",
    "passed": "green",
    "failed": "red",
    "in_progress": "yellow",
    "pending": "blue",
}


def list_scans(
    stack_id: str | None = typer.Option(
        None,
        "--stack-id",
        "-s",
        help="Filter by stack ID",
    ),
    scan_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by scan type (static, runtime, drift)",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by status (pending, in_progress, completed, failed)",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """List compliance scans.

    Retrieves compliance scan records. Use filters to find scans by stack,
    type, or status.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
            scan_type=scan_type,
            status=status,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No scans found matching criteria")
            return

        if output_format == "json":
            console.print_json(data=data)
            return

        table = create_table(
            *[col_name for _, col_name in SCAN_COLUMNS],
            title="Compliance Scans",
        )

        scans = data if isinstance(data, list) else [data]
        for scan in scans:
            row = []
            for col_key, _ in SCAN_COLUMNS:
                value = scan.get(col_key, "")
                if col_key == "status" and value:
                    color = STATUS_COLORS.get(value.lower(), "white")
                    value = f"[{color}]{value}[/]"
                elif col_key == "score" and value is not None:
                    score = float(value) if value else 0
                    color = "green" if score >= 80 else ("yellow" if score >= 60 else "red")
                    value = f"[{color}]{score:.1f}%[/]"
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(scans)} scan(s)")

    except Exception as e:
        print_error(f"Error listing scans: {e}")
        raise typer.Exit(1)


def show_scan(
    scan_id: str = typer.Argument(
        ...,
        help="Scan ID to show",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
) -> None:
    """Show detailed information about a scan.

    Retrieves complete scan details including results, violations found,
    and compliance score.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            scan_id=scan_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print(f"\n[bold]Scan:[/bold] {scan_id}")

        if stack_id := data.get("stack_id"):
            console.print(f"[bold]Stack:[/bold] {stack_id}")

        if scan_type := data.get("scan_type"):
            console.print(f"[bold]Type:[/bold] {scan_type}")

        if status := data.get("status"):
            color = STATUS_COLORS.get(status.lower(), "white")
            console.print(f"[bold]Status:[/bold] [{color}]{status}[/]")

        if score := data.get("score"):
            score_val = float(score)
            color = "green" if score_val >= 80 else ("yellow" if score_val >= 60 else "red")
            console.print(f"[bold]Score:[/bold] [{color}]{score_val:.1f}%[/]")

        if created := data.get("created_at"):
            console.print(f"[bold]Created:[/bold] {created}")

        if completed := data.get("completed_at"):
            console.print(f"[bold]Completed:[/bold] {completed}")

        # Show summary counts
        if summary := data.get("summary"):
            console.print("\n[bold]Summary:[/bold]")
            if passed := summary.get("passed"):
                console.print(f"  [green]Passed:[/green] {passed}")
            if failed := summary.get("failed"):
                console.print(f"  [red]Failed:[/red] {failed}")
            if skipped := summary.get("skipped"):
                console.print(f"  [yellow]Skipped:[/yellow] {skipped}")

        # Show violations if present
        if violations := data.get("violations"):
            console.print(f"\n[bold]Violations:[/bold] {len(violations)}")
            if violations and len(violations) > 0:
                table = create_table("Rule", "Resource", "Severity")
                for v in violations[:10]:
                    table.add_row(
                        str(v.get("rule_id", "-")),
                        str(v.get("resource_id", "-")),
                        str(v.get("severity", "-")),
                    )
                console.print(table)
                if len(violations) > 10:
                    console.print(f"  ... and {len(violations) - 10} more violations")

        console.print()

    except Exception as e:
        print_error(f"Error showing scan: {e}")
        raise typer.Exit(1)


def submit_scan(
    scan_id: str = typer.Argument(
        ...,
        help="Scan ID to submit results for",
    ),
    results_file: Path = typer.Option(
        ...,
        "--file",
        "-f",
        help="Path to JSON file with scan results",
        exists=True,
        readable=True,
    ),
    scanner_version: str | None = typer.Option(
        None,
        "--scanner-version",
        help="Version of scanner that produced results",
    ),
    pipeline_url: str | None = typer.Option(
        None,
        "--pipeline-url",
        help="URL to the CI/CD pipeline run",
    ),
    commit_sha: str | None = typer.Option(
        None,
        "--commit",
        help="Git commit SHA that was scanned",
    ),
    branch: str | None = typer.Option(
        None,
        "--branch",
        help="Git branch that was scanned",
    ),
) -> None:
    """Submit scan results from CI/CD pipeline.

    Uploads scan results from external scanners (Checkov, OPA, etc.) to
    complete a pending scan. The scan must exist and be in PENDING or
    IN_PROGRESS status.
    """
    try:
        # Load results from file
        with open(results_file) as f:
            raw_results = json.load(f)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build submission schema
        scan_results = ScanResultsSubmissionSchemaScanResults.from_dict(raw_results)
        body = ScanResultsSubmissionSchema(
            scan_results=scan_results,
            scanner_version=scanner_version,
            pipeline_url=pipeline_url,
            commit_sha=commit_sha,
            branch=branch,
        )

        response = api_submit.sync_detailed(
            scan_id=scan_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        console.print(f"\n[bold]Scan results submitted:[/bold] {scan_id}")

        if score := data.get("score"):
            score_val = float(score)
            color = "green" if score_val >= 80 else ("yellow" if score_val >= 60 else "red")
            console.print(f"[bold]Score:[/bold] [{color}]{score_val:.1f}%[/]")

        if status := data.get("status"):
            color = STATUS_COLORS.get(status.lower(), "white")
            console.print(f"[bold]Status:[/bold] [{color}]{status}[/]")

        if violations_count := data.get("violations_count"):
            console.print(f"[bold]Violations:[/bold] {violations_count}")

        print_success("Scan results submitted successfully")

    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in results file: {e}")
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error submitting scan results: {e}")
        raise typer.Exit(1)


# Register commands
app.command("list")(list_scans)
app.command("show")(show_scan)
app.command("submit")(submit_scan)
