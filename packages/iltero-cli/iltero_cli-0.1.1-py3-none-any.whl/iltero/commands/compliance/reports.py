"""Compliance reports commands - list, generate, export."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_stack_reporting import (
    export_report as api_export,
)
from iltero.api_client.api.compliance_stack_reporting import (
    generate_report as api_generate,
)
from iltero.api_client.api.compliance_stack_reporting import (
    list_reports as api_list,
)
from iltero.api_client.models.compliance_report_request_schema import (
    ComplianceReportRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance reports management")
console = Console()

# Column definitions for reports table
REPORT_COLUMNS = [
    ("id", "ID"),
    ("type", "Type"),
    ("status", "Status"),
    ("created_at", "Created"),
    ("frameworks", "Frameworks"),
]

# Status color mapping
STATUS_COLORS = {
    "completed": "green",
    "pending": "yellow",
    "failed": "red",
    "generating": "blue",
}


def list_reports(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    limit: int = typer.Option(10, help="Max reports"),
) -> None:
    """List compliance reports for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            limit=limit,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No reports found.")
            return

        reports = data.get("reports", [])
        if not reports:
            print_info("No reports found.")
            return

        table = create_table(*[col[1] for col in REPORT_COLUMNS], title="Reports")

        for report in reports:
            status = report.get("status", "unknown")
            status_color = STATUS_COLORS.get(status.lower(), "white")
            frameworks = report.get("frameworks", [])
            fw_str = ", ".join(frameworks) if frameworks else "-"

            table.add_row(
                report.get("id", "-"),
                report.get("type", "-"),
                f"[{status_color}]{status}[/{status_color}]",
                report.get("created_at", "-"),
                fw_str,
            )

        console.print(table)
    except Exception as e:
        print_error(f"Failed to list reports: {e}")
        raise typer.Exit(1) from e


def generate_report(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    report_type: str = typer.Option("summary", "--type", "-t", help="Type"),
    include_evidence: bool = typer.Option(False, "--include-evidence"),
    include_remediation: bool = typer.Option(True, "--include-remediation"),
    include_trends: bool = typer.Option(False, "--include-trends"),
    frameworks: str | None = typer.Option(None, "--frameworks", help="CSV"),
    format_: str = typer.Option("json", "--format", "-f", help="Format"),
) -> None:
    """Generate a compliance report for a stack."""
    try:
        framework_list = None
        if frameworks:
            framework_list = [f.strip() for f in frameworks.split(",")]

        body = ComplianceReportRequestSchema(
            stack_id=stack_id,
            report_type=report_type,
            include_evidence=include_evidence,
            include_remediation=include_remediation,
            include_trends=include_trends,
            frameworks=framework_list,
            format_=format_,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_generate.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to generate report.")
            return

        report = data.get("report", data)
        report_id = report.get("id", "N/A")
        print_success(f"Report generated: {report_id}")

        table = create_table("Field", "Value", title="Report Details")
        table.add_row("ID", report.get("id", "-"))
        table.add_row("Type", report.get("type", report_type))
        table.add_row("Status", report.get("status", "-"))
        table.add_row("Format", report.get("format", format_))
        table.add_row("Created At", report.get("created_at", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to generate report: {e}")
        raise typer.Exit(1) from e


def export_report(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    report_id: str = typer.Argument(..., help="Report identifier"),
    format_: str = typer.Option("PDF", "--format", "-f", help="Format"),
) -> None:
    """Export a compliance report in specified format."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_export.sync_detailed(
            stack_id=stack_id,
            report_id=report_id,
            client=auth_client,
            format_=format_,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to export report.")
            return

        export_info = data.get("export", data)
        print_success(f"Report exported as {format_}")

        if export_info.get("download_url"):
            url = export_info["download_url"]
            console.print(f"Download URL: [cyan]{url}[/cyan]")
        if export_info.get("file_path"):
            path = export_info["file_path"]
            console.print(f"File path: [cyan]{path}[/cyan]")
    except Exception as e:
        print_error(f"Failed to export report: {e}")
        raise typer.Exit(1) from e


app.command("list")(list_reports)
app.command("generate")(generate_report)
app.command("export")(export_report)
