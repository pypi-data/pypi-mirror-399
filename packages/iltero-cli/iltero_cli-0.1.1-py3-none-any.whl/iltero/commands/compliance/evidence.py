"""Compliance evidence commands - collect, show."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_stack_evidence import (
    collect_evidence as api_collect,
)
from iltero.api_client.api.compliance_stack_evidence import (
    retrieve_evidence as api_retrieve,
)
from iltero.api_client.models.evidence_collection_request_schema import (
    EvidenceCollectionRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance evidence management")
console = Console()

# Evidence type options
EVIDENCE_TYPES = [
    "config",
    "logs",
    "state",
    "metrics",
    "audit",
]


def collect(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    evidence_types: str = typer.Option(
        "config,state", "--types", "-t", help="Evidence types (CSV)"
    ),
    reason: str = typer.Option("manual", "--reason", "-r", help="Collection reason"),
    compress: bool = typer.Option(True, "--compress/--no-compress"),
    encrypt: bool = typer.Option(True, "--encrypt/--no-encrypt"),
    retention_days: int | None = typer.Option(None, "--retention", help="Retention days override"),
) -> None:
    """Collect compliance evidence for a stack."""
    try:
        types_list = [t.strip() for t in evidence_types.split(",")]

        body = EvidenceCollectionRequestSchema(
            stack_id=stack_id,
            evidence_types=types_list,
            collection_reason=reason,
            compress=compress,
            encrypt=encrypt,
            retention_override_days=retention_days,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_collect.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Evidence collection failed.")
            return

        evidence = data.get("evidence", data)
        evidence_id = evidence.get("id", "N/A")
        print_success(f"Evidence collected: {evidence_id}")

        table = create_table("Field", "Value", title="Evidence Details")
        table.add_row("ID", evidence.get("id", "-"))
        table.add_row("Stack ID", stack_id)
        table.add_row("Types", ", ".join(types_list))
        table.add_row("Reason", reason)
        table.add_row("Compressed", str(compress))
        table.add_row("Encrypted", str(encrypt))
        table.add_row("Status", evidence.get("status", "-"))
        table.add_row("Created At", evidence.get("created_at", "-"))

        console.print(table)
    except Exception as e:
        print_error(f"Failed to collect evidence: {e}")
        raise typer.Exit(1) from e


def show(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    evidence_id: str = typer.Argument(..., help="Evidence identifier"),
) -> None:
    """Show details of collected evidence."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_retrieve.sync_detailed(
            stack_id=stack_id,
            evidence_id=evidence_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Evidence not found.")
            return

        evidence = data.get("evidence", data)

        table = create_table("Field", "Value", title="Evidence Details")
        table.add_row("ID", evidence.get("id", "-"))
        table.add_row("Stack ID", evidence.get("stack_id", stack_id))
        table.add_row("Status", evidence.get("status", "-"))
        table.add_row("Reason", evidence.get("collection_reason", "-"))
        table.add_row("Created At", evidence.get("created_at", "-"))
        table.add_row("Expires At", evidence.get("expires_at", "-"))

        console.print(table)

        # Show evidence types if available
        types = evidence.get("evidence_types", [])
        if types:
            types_table = create_table("Type", "Status", "Size")
            for ev_type in types:
                if isinstance(ev_type, dict):
                    types_table.add_row(
                        ev_type.get("type", "-"),
                        ev_type.get("status", "-"),
                        ev_type.get("size", "-"),
                    )
                else:
                    types_table.add_row(str(ev_type), "-", "-")
            console.print(types_table)
    except Exception as e:
        print_error(f"Failed to retrieve evidence: {e}")
        raise typer.Exit(1) from e


app.command("collect")(collect)
app.command("show")(show)
