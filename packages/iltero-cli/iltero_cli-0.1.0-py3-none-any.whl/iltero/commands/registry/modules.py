"""Module management commands - CRUD operations."""

from __future__ import annotations

import typer

from iltero.api_client.api.ia_c_module_registry import (
    create_registry_module as api_create_module,
)
from iltero.api_client.api.ia_c_module_registry import (
    delete_registry_module as api_delete_module,
)
from iltero.api_client.api.ia_c_module_registry import (
    get_registry_module as api_get_module,
)
from iltero.api_client.api.ia_c_module_registry import (
    list_registry_modules as api_list_modules,
)
from iltero.api_client.api.ia_c_module_registry import (
    update_registry_module as api_update_module,
)
from iltero.api_client.models.registry_module_create_schema import (
    RegistryModuleCreateSchema,
)
from iltero.api_client.models.registry_module_update_schema import (
    RegistryModuleUpdateSchema,
)
from iltero.commands.registry.main import MODULE_COLUMNS, console
from iltero.core.http import get_retry_client
from iltero.utils.output import (
    OutputFormat,
    confirm_action,
    format_output,
    print_detail,
    print_error,
    print_success,
)


def list_modules(
    tool: str | None = typer.Option(
        None,
        "--tool",
        "-t",
        help="Filter by tool (terraform, opentofu)",
    ),
    namespace: str | None = typer.Option(None, "--namespace", "-n", help="Filter by namespace"),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Filter by provider (aws, azure, gcp)",
    ),
    name: str | None = typer.Option(None, "--name", help="Filter by module name"),
    active: bool | None = typer.Option(None, "--active/--inactive", help="Filter by active status"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """List modules in the registry."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list_modules.sync_detailed(
            client=auth_client,
            tool=tool,
            namespace=namespace,
            provider=provider,
            name=name,
            active=active,
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

            format_output(
                modules,
                format_type=output,
                title="Registry Modules",
                columns=MODULE_COLUMNS,
            )
        else:
            console.print("[dim]No modules found[/dim]")

    except Exception as e:
        print_error(f"Failed to list modules: {e}")
        raise typer.Exit(1)


def create_module(
    name: str = typer.Argument(..., help="Module name"),
    namespace: str = typer.Option(..., "--namespace", "-n", help="Module namespace (required)"),
    provider: str = typer.Option(
        ...,
        "--provider",
        "-p",
        help="Cloud provider: aws, azure, gcp (required)",
    ),
    tool: str = typer.Option(
        "terraform",
        "--tool",
        "-t",
        help="IaC tool: terraform, opentofu",
    ),
    description: str | None = typer.Option(None, "--description", "-d", help="Module description"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Create a new module in the registry."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build request schema
        create_schema = RegistryModuleCreateSchema(
            name=name,
            namespace=namespace,
            provider=provider,
            tool=tool,
            description=description,
        )

        response = api_create_module.sync_detailed(
            client=auth_client,
            body=create_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Module '{namespace}/{name}/{provider}' created")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Created Module",
                    columns=MODULE_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to create module: {e}")
        raise typer.Exit(1)


def show_module(
    module_id: str = typer.Argument(..., help="Module ID"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Show module details."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get_module.sync_detailed(
            client=auth_client,
            module_id=module_id,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data") and result.data:
            if output == OutputFormat.TABLE:
                # Detail view for single module
                data = result.data
                if hasattr(data, "to_dict"):
                    data = data.to_dict()

                console.print("\n[bold]Module Details[/bold]\n")
                for key, value in data.items():
                    print_detail(key.replace("_", " ").title(), value)
                console.print()
            else:
                format_output(result.data, format_type=output)
        else:
            print_error(f"Module '{module_id}' not found")
            raise typer.Exit(1)

    except Exception as e:
        print_error(f"Failed to get module: {e}")
        raise typer.Exit(1)


def update_module(
    module_id: str = typer.Argument(..., help="Module ID"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    active: bool | None = typer.Option(None, "--active/--inactive", help="Set active status"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Update module settings."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build update schema with only provided fields
        update_schema = RegistryModuleUpdateSchema(
            description=description,
            is_active=active,
        )

        response = api_update_module.sync_detailed(
            client=auth_client,
            module_id=module_id,
            body=update_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Module '{module_id}' updated successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Updated Module",
                    columns=MODULE_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to update module: {e}")
        raise typer.Exit(1)


def delete_module(
    module_id: str = typer.Argument(..., help="Module ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete a module from the registry."""
    try:
        if not force:
            if not confirm_action(f"Are you sure you want to delete module '{module_id}'?"):
                console.print("[dim]Deletion cancelled[/dim]")
                raise typer.Exit(0)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_delete_module.sync_detailed(
            client=auth_client,
            module_id=module_id,
        )

        client.handle_response(response)
        print_success(f"Module '{module_id}' deleted successfully")

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to delete module: {e}")
        raise typer.Exit(1)
