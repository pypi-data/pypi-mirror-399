"""Stack CRUD operations."""

from __future__ import annotations

import typer

from iltero.api_client.api.stacks import create_stack as api_create_stack
from iltero.api_client.api.stacks import delete_stack as api_delete_stack
from iltero.api_client.api.stacks import get_stack as api_get_stack
from iltero.api_client.api.stacks import list_stacks as api_list_stacks
from iltero.api_client.api.stacks import update_stack as api_update_stack
from iltero.api_client.models.stack_create_schema import StackCreateSchema
from iltero.api_client.models.stack_update_schema import StackUpdateSchema
from iltero.api_client.models.terraform_backend_schema import (
    TerraformBackendSchema,
)
from iltero.commands.stack.main import STACK_COLUMNS, console
from iltero.core.http import get_retry_client
from iltero.utils.output import (
    OutputFormat,
    confirm_action,
    format_output,
    print_detail,
    print_error,
    print_success,
)


def list_stacks(
    search: str | None = typer.Option(None, "--search", "-s", help="Search by name"),
    active: bool | None = typer.Option(None, "--active", help="Filter by active status"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """List all stacks."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list_stacks.sync_detailed(
            client=auth_client,
            search=search,
            active=active,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data"):
            data = result.data
            if isinstance(data, list):
                stacks = data
            elif hasattr(data, "items"):
                stacks = data.items
            else:
                stacks = [data] if data else []

            format_output(
                stacks,
                format_type=output,
                title="Stacks",
                columns=STACK_COLUMNS,
            )
        else:
            console.print("[dim]No stacks found[/dim]")

    except Exception as e:
        print_error(f"Failed to list stacks: {e}")
        raise typer.Exit(1)


def create_stack(
    name: str = typer.Argument(..., help="Stack name"),
    backend_type: str = typer.Option(
        "s3", "--backend-type", "-b", help="Terraform backend type (s3, gcs, azurerm, local)"
    ),
    backend_bucket: str | None = typer.Option(
        None, "--backend-bucket", help="Backend bucket/container name"
    ),
    backend_key: str | None = typer.Option(
        None, "--backend-key", help="Backend state file key/path"
    ),
    backend_region: str | None = typer.Option(
        None, "--backend-region", help="Backend region (for S3)"
    ),
    description: str | None = typer.Option(None, "--description", "-d", help="Stack description"),
    template_id: str | None = typer.Option(None, "--template", "-t", help="Template bundle ID"),
    terraform_dir: str | None = typer.Option(
        None, "--terraform-dir", help="Terraform working directory"
    ),
    workspace_environment_ids: list[str] | None = typer.Option(
        None, "--env", "-e", help="Workspace environment IDs (can specify multiple)"
    ),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Create a new stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build terraform backend config
        backend_config: dict = {
            "type": backend_type,
        }
        if backend_bucket:
            backend_config["bucket"] = backend_bucket
        if backend_key:
            backend_config["key"] = backend_key
        if backend_region:
            backend_config["region"] = backend_region

        terraform_backend = TerraformBackendSchema.from_dict(backend_config)

        # Build request schema
        create_schema = StackCreateSchema(
            name=name,
            terraform_backend=terraform_backend,
            description=description,
            template_id=template_id,
            terraform_working_directory=terraform_dir,
            workspace_environment_ids=workspace_environment_ids,
        )

        response = api_create_stack.sync_detailed(
            client=auth_client,
            body=create_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Stack '{name}' created successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Created Stack",
                    columns=STACK_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to create stack: {e}")
        raise typer.Exit(1)


def show_stack(
    stack_id: str = typer.Argument(..., help="Stack ID"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Show stack details."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get_stack.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
        )

        result = client.handle_response(response)

        if result and hasattr(result, "data") and result.data:
            if output == OutputFormat.TABLE:
                # Detail view for single stack
                data = result.data
                if hasattr(data, "to_dict"):
                    data = data.to_dict()

                console.print("\n[bold]Stack Details[/bold]\n")
                for key, value in data.items():
                    print_detail(key.replace("_", " ").title(), value)
                console.print()
            else:
                format_output(result.data, format_type=output)
        else:
            print_error(f"Stack '{stack_id}' not found")
            raise typer.Exit(1)

    except Exception as e:
        print_error(f"Failed to get stack: {e}")
        raise typer.Exit(1)


def update_stack(
    stack_id: str = typer.Argument(..., help="Stack ID"),
    name: str | None = typer.Option(None, "--name", "-n", help="New name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    active: bool | None = typer.Option(None, "--active/--inactive", help="Set active status"),
    output: OutputFormat = typer.Option(OutputFormat.TABLE, "--output", "-o", help="Output format"),
):
    """Update stack settings."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Build update schema with only provided fields
        update_schema = StackUpdateSchema(
            name=name,
            description=description,
            is_active=active,
        )

        response = api_update_stack.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
            body=update_schema,
        )

        result = client.handle_response(response)

        if result:
            print_success(f"Stack '{stack_id}' updated successfully")
            if hasattr(result, "data") and result.data:
                format_output(
                    result.data,
                    format_type=output,
                    title="Updated Stack",
                    columns=STACK_COLUMNS,
                )

    except Exception as e:
        print_error(f"Failed to update stack: {e}")
        raise typer.Exit(1)


def delete_stack(
    stack_id: str = typer.Argument(..., help="Stack ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Delete a stack."""
    try:
        if not force:
            if not confirm_action(f"Are you sure you want to delete stack '{stack_id}'?"):
                console.print("[dim]Deletion cancelled[/dim]")
                raise typer.Exit(0)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_delete_stack.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
        )

        client.handle_response(response)
        print_success(f"Stack '{stack_id}' deleted successfully")

    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to delete stack: {e}")
        raise typer.Exit(1)
