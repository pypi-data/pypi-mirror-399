"""Module search command."""

from __future__ import annotations

import typer

from iltero.api_client.api.ia_c_module_registry import (
    list_registry_modules as api_list_modules,
)
from iltero.commands.registry.main import MODULE_COLUMNS, console
from iltero.core.http import get_retry_client
from iltero.utils.output import OutputFormat, format_output, print_error


def search_modules(
    query: str = typer.Argument(..., help="Search query"),
    tool: str | None = typer.Option(None, "--tool", "-t", help="Filter by tool"),
    provider: str | None = typer.Option(None, "--provider", "-p", help="Filter by provider"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Search modules in the registry."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Use list with name filter for searching
        response = api_list_modules.sync_detailed(
            client=auth_client,
            tool=tool,
            provider=provider,
            name=query,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data"):
            data = result.data
            if isinstance(data, list):
                modules = data
            elif hasattr(data, "items"):
                modules = data.items
            else:
                modules = [data] if data else []

            if modules:
                format_output(
                    modules,
                    format_type=output,
                    title=f"Search Results for '{query}'",
                    columns=MODULE_COLUMNS,
                )
            else:
                console.print(f"[dim]No modules found matching '{query}'[/dim]")
        else:
            console.print(f"[dim]No modules found matching '{query}'[/dim]")

    except Exception as e:
        print_error(f"Failed to search modules: {e}")
        raise typer.Exit(1)
