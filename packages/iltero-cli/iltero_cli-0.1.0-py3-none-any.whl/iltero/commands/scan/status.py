"""Scan status commands - view scan details and history."""

from __future__ import annotations

import typer

from iltero.api_client.api.compliance_scans import get_scan as api_get_scan
from iltero.api_client.api.compliance_scans import list_scans as api_list_scans
from iltero.commands.scan.main import EXIT_API_ERROR, console
from iltero.core.http import get_retry_client
from iltero.utils.output import OutputFormat, print_error
from iltero.utils.tables import create_table


def scan_status(
    scan_id: str = typer.Argument(
        ...,
        help="Scan ID to check status",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        help="Output format",
    ),
):
    """Get status and details of a compliance scan."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get_scan.sync_detailed(
            scan_id=scan_id,
            client=auth_client,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data") and result.data:
            data = result.data
            if hasattr(data, "to_dict"):
                data = data.to_dict()

            if output == OutputFormat.TABLE:
                # Display scan details as table
                table = create_table(
                    "Field",
                    "Value",
                    title="Scan Details",
                    show_header=False,
                )
                table.columns[0].style = "cyan"

                for key, value in data.items():
                    table.add_row(key.replace("_", " ").title(), str(value))

                console.print(table)
            elif output == OutputFormat.JSON:
                console.print_json(data=data)
            elif output == OutputFormat.YAML:
                import yaml

                console.print(yaml.dump(data, default_flow_style=False))
        else:
            print_error(f"Scan '{scan_id}' not found")
            raise typer.Exit(EXIT_API_ERROR)

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to get scan status: {e}")
        raise typer.Exit(EXIT_API_ERROR)


def scan_list(
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
        help="Filter by scan type: STATIC, EVALUATION",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        help="Filter by status: PENDING, COMPLETED, FAILED",
    ),
    output: OutputFormat = typer.Option(
        OutputFormat.TABLE,
        "--output",
        "-o",
        help="Output format",
    ),
):
    """List compliance scans."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list_scans.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
            scan_type=scan_type,
            status=status,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data"):
            data = result.data
            if isinstance(data, list):
                scans = data
            elif hasattr(data, "items"):
                scans = data.items
            else:
                scans = [data] if data else []

            if output == OutputFormat.TABLE:
                table = create_table(
                    "ID",
                    "Type",
                    "Status",
                    "Stack",
                    "Violations",
                    "Created",
                    title="Compliance Scans",
                )
                table.columns[0].style = "cyan"

                for scan in scans:
                    if hasattr(scan, "to_dict"):
                        scan = scan.to_dict()
                    table.add_row(
                        str(scan.get("id", "")),
                        scan.get("scan_type", ""),
                        scan.get("status", ""),
                        str(scan.get("stack_id", "")),
                        str(scan.get("violations_count", 0)),
                        str(scan.get("created_at", ""))[:19],
                    )

                console.print(table)
            elif output == OutputFormat.JSON:
                json_data = [s.to_dict() if hasattr(s, "to_dict") else s for s in scans]
                console.print_json(data=json_data)
        else:
            console.print("[dim]No scans found[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to list scans: {e}")
        raise typer.Exit(EXIT_API_ERROR)
