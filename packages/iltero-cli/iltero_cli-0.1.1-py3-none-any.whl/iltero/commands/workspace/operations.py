"""Workspace CRUD operations."""

from __future__ import annotations

import typer

from iltero.api_client.api.workspaces import (
    create_workspace as api_create_workspace,
)
from iltero.api_client.api.workspaces import (
    delete_workspace as api_delete_workspace,
)
from iltero.api_client.api.workspaces import get_workspace as api_get_workspace
from iltero.api_client.api.workspaces import (
    list_workspaces as api_list_workspaces,
)
from iltero.api_client.api.workspaces import (
    update_workspace as api_update_workspace,
)
from iltero.api_client.models.workspace_create_schema import (
    WorkspaceCreateSchema,
)
from iltero.api_client.models.workspace_update_schema import (
    WorkspaceUpdateSchema,
)
from iltero.commands.workspace.main import WORKSPACE_COLUMNS, console
from iltero.core.http import get_retry_client
from iltero.utils.output import (
    OutputFormat,
    confirm_action,
    format_output,
    print_detail,
    print_error,
    print_success,
)


def list_workspaces(
    environment_id: str | None = typer.Option(
        None, "--environment", "-e", help="Filter by environment ID"
    ),
    name: str | None = typer.Option(None, "--name", "-n", help="Filter by workspace name"),
    active: bool | None = typer.Option(None, "--active", help="Filter by active status"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """List all workspaces."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list_workspaces.sync_detailed(
            client=auth_client,
            environment_id=environment_id,
            name=name,
            active=active,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data"):
            data = result.data
            if isinstance(data, list):
                workspaces = data
            elif hasattr(data, "items"):
                workspaces = data.items
            else:
                workspaces = [data] if data else []

            format_output(
                workspaces,
                format_type=output,
                title="Workspaces",
                columns=WORKSPACE_COLUMNS,
            )
        else:
            console.print("[dim]No workspaces found[/dim]")

    except Exception as e:
        print_error(f"Failed to list workspaces: {e}")
        raise typer.Exit(1)


def create_workspace(
    name: str = typer.Argument(..., help="Workspace name"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Workspace description"
    ),
    slug: str | None = typer.Option(None, "--slug", "-s", help="URL-friendly workspace slug"),
    environment_ids: list[str] | None = typer.Option(
        None,
        "--environment",
        "-e",
        help="Environment IDs (can specify multiple)",
    ),
    default_environment_id: str | None = typer.Option(
        None, "--default-environment", help="Default environment ID"
    ),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Create a new workspace."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build request schema
        create_schema = WorkspaceCreateSchema(
            name=name,
            description=description,
            slug=slug,
            environment_ids=environment_ids,
            default_environment_id=default_environment_id,
        )

        response = api_create_workspace.sync_detailed(
            client=auth_client,
            body=create_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Workspace '{name}' created successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Created Workspace",
                    columns=WORKSPACE_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to create workspace: {e}")
        raise typer.Exit(1)


def show_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Show workspace details."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get_workspace.sync_detailed(
            client=auth_client,
            workspace_id=workspace_id,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data") and result.data:
            if output == OutputFormat.TABLE:
                # Detail view for single workspace
                data = result.data
                if hasattr(data, "to_dict"):
                    data = data.to_dict()

                console.print("\n[bold]Workspace Details[/bold]\n")
                for key, value in data.items():
                    print_detail(key.replace("_", " ").title(), value)
                console.print()
            else:
                format_output(result.data, format_type=output)
        else:
            print_error(f"Workspace '{workspace_id}' not found")
            raise typer.Exit(1)

    except Exception as e:
        print_error(f"Failed to get workspace: {e}")
        raise typer.Exit(1)


def update_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID"),
    name: str | None = typer.Option(None, "--name", "-n", help="New name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    active: bool | None = typer.Option(None, "--active/--inactive", help="Set active status"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Update workspace settings."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build update schema with only provided fields
        update_schema = WorkspaceUpdateSchema(
            name=name,
            description=description,
            is_active=active,
        )

        response = api_update_workspace.sync_detailed(
            client=auth_client,
            workspace_id=workspace_id,
            body=update_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Workspace '{workspace_id}' updated successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Updated Workspace",
                    columns=WORKSPACE_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to update workspace: {e}")
        raise typer.Exit(1)


def delete_workspace(
    workspace_id: str = typer.Argument(..., help="Workspace ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete a workspace."""
    try:
        if not force:
            if not confirm_action(f"Are you sure you want to delete workspace '{workspace_id}'?"):
                console.print("[dim]Deletion cancelled[/dim]")
                raise typer.Exit(0)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_delete_workspace.sync_detailed(
            client=auth_client,
            workspace_id=workspace_id,
        )

        client.handle_response(response)
        print_success(f"Workspace '{workspace_id}' deleted successfully")

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to delete workspace: {e}")
        raise typer.Exit(1)
