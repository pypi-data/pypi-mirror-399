"""Environment CRUD operations."""

from __future__ import annotations

import typer

from iltero.api_client.api.environment_management import (
    create_environment as api_create_environment,
)
from iltero.api_client.api.environment_management import (
    delete_environment as api_delete_environment,
)
from iltero.api_client.api.environment_management import (
    get_environment as api_get_environment,
)
from iltero.api_client.api.environment_management import (
    list_environments as api_list_environments,
)
from iltero.api_client.api.environment_management import (
    update_environment as api_update_environment,
)
from iltero.api_client.models.environment_create_schema import (
    EnvironmentCreateSchema,
)
from iltero.api_client.models.environment_update_schema import (
    EnvironmentUpdateSchema,
)
from iltero.commands.environment.main import ENVIRONMENT_COLUMNS, console
from iltero.core.http import get_retry_client
from iltero.utils.output import (
    OutputFormat,
    confirm_action,
    format_output,
    print_detail,
    print_error,
    print_success,
)


def list_environments(
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    limit: int = typer.Option(10, "--limit", "-l", help="Results per page"),
    search: str | None = typer.Option(None, "--search", "-s", help="Search by name"),
    is_default: bool | None = typer.Option(None, "--default", help="Filter by default status"),
    is_production: bool | None = typer.Option(
        None, "--production", help="Filter by production status"
    ),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """List all environments."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list_environments.sync_detailed(
            client=auth_client,
            page=page,
            limit=limit,
            search=search,
            is_default=is_default,
            is_production=is_production,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data"):
            data = result.data
            if isinstance(data, list):
                environments = data
            elif hasattr(data, "items"):
                environments = data.items
            else:
                environments = [data] if data else []

            format_output(
                environments,
                format_type=output,
                title="Environments",
                columns=ENVIRONMENT_COLUMNS,
            )
        else:
            console.print("[dim]No environments found[/dim]")

    except Exception as e:
        print_error(f"Failed to list environments: {e}")
        raise typer.Exit(1)


def create_environment(
    name: str = typer.Argument(..., help="Environment name"),
    key: str | None = typer.Option(None, "--key", "-k", help="URL-friendly identifier"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Environment description"
    ),
    production: bool = typer.Option(False, "--production", help="Mark as production environment"),
    default: bool = typer.Option(False, "--default", help="Set as default environment"),
    color: str = typer.Option("#9ca3af", "--color", "-c", help="Color code for UI (hex)"),
    branch: str = typer.Option("main", "--branch", "-b", help="Git branch for deployments"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Create a new environment."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build request schema
        create_schema = EnvironmentCreateSchema(
            name=name,
            key=key,
            description=description,
            is_production=production,
            is_default=default,
            color=color,
            repo_ref_name=branch,
        )

        response = api_create_environment.sync_detailed(
            client=auth_client,
            body=create_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Environment '{name}' created successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Created Environment",
                    columns=ENVIRONMENT_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to create environment: {e}")
        raise typer.Exit(1)


def show_environment(
    environment_id: str = typer.Argument(..., help="Environment ID"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Show environment details."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get_environment.sync_detailed(
            client=auth_client,
            environment_id=environment_id,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data") and result.data:
            if output == OutputFormat.TABLE:
                # Detail view for single environment
                data = result.data
                if hasattr(data, "to_dict"):
                    data = data.to_dict()

                console.print("\n[bold]Environment Details[/bold]\n")
                for key_name, value in data.items():
                    print_detail(key_name.replace("_", " ").title(), value)
                console.print()
            else:
                format_output(result.data, format_type=output)
        else:
            print_error(f"Environment '{environment_id}' not found")
            raise typer.Exit(1)

    except Exception as e:
        print_error(f"Failed to get environment: {e}")
        raise typer.Exit(1)


def update_environment(
    environment_id: str = typer.Argument(..., help="Environment ID"),
    name: str | None = typer.Option(None, "--name", "-n", help="New name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    production: bool | None = typer.Option(
        None, "--production/--no-production", help="Set production status"
    ),
    default: bool | None = typer.Option(None, "--default/--no-default", help="Set default status"),
    color: str | None = typer.Option(None, "--color", "-c", help="Color code for UI (hex)"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Update environment settings."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build update schema with only provided fields
        update_schema = EnvironmentUpdateSchema(
            name=name,
            description=description,
            is_production=production,
            is_default=default,
            color=color,
        )

        response = api_update_environment.sync_detailed(
            client=auth_client,
            environment_id=environment_id,
            body=update_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Environment '{environment_id}' updated successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Updated Environment",
                    columns=ENVIRONMENT_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to update environment: {e}")
        raise typer.Exit(1)


def delete_environment(
    environment_id: str = typer.Argument(..., help="Environment ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete an environment."""
    try:
        if not force:
            if not confirm_action(
                f"Are you sure you want to delete environment '{environment_id}'?"
            ):
                console.print("[dim]Deletion cancelled[/dim]")
                raise typer.Exit(0)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_delete_environment.sync_detailed(
            client=auth_client,
            environment_id=environment_id,
        )

        client.handle_response(response)
        print_success(f"Environment '{environment_id}' deleted successfully")

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to delete environment: {e}")
        raise typer.Exit(1)
