"""Repository commands - list, show, create, sync, initialize."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.repositories import (
    create_repository as api_create,
)
from iltero.api_client.api.repositories import (
    get_repository as api_get,
)
from iltero.api_client.api.repositories import (
    initialize_repository as api_initialize,
)
from iltero.api_client.api.repositories import (
    repository_list_repositories_e8da9bbf as api_list,
)
from iltero.api_client.api.repositories import (
    repository_sync_repository_a2bff0df as api_sync,
)
from iltero.api_client.models.repository_config_schema import (
    RepositoryConfigSchema,
)
from iltero.api_client.models.repository_create_schema import (
    RepositoryCreateSchema,
)
from iltero.api_client.models.repository_initialize_request_schema import (
    RepositoryInitializeRequestSchema,
)
from iltero.commands.repository import app
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

console = Console()


def list_repositories(
    provider: str | None = typer.Option(
        None, "--provider", "-p", help="Filter by provider (github, gitlab)"
    ),
    status: str | None = typer.Option(None, "--status", "-s", help="Filter by status"),
    active: bool | None = typer.Option(None, "--active/--inactive", help="Filter by active status"),
) -> None:
    """List repositories."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            client=auth_client,
            provider=provider,
            status=status,
            active=active,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No repositories found.")
            return

        repos = data.get("repositories", [])
        if not repos:
            print_info("No repositories found.")
            return

        table = create_table("ID", "Name", "Provider", "Status", "URL")
        for repo in repos:
            table.add_row(
                repo.get("id", "-"),
                repo.get("name", "-"),
                repo.get("provider", "-"),
                repo.get("status", "-"),
                repo.get("url", "-")[:40] + "..."
                if len(repo.get("url", "")) > 40
                else repo.get("url", "-"),
            )

        console.print(table)
        console.print(f"\nTotal: [cyan]{len(repos)}[/cyan] repositories")
    except Exception as e:
        print_error(f"Failed to list repositories: {e}")
        raise typer.Exit(1) from e


def show_repository(
    repository_id: str = typer.Argument(..., help="Repository ID"),
) -> None:
    """Show repository details."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            repository_id=repository_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Repository not found.")
            return

        repo = data.get("repository", data)

        table = create_table("Field", "Value", title="Repository Details")
        table.add_row("ID", repo.get("id", "-"))
        table.add_row("Name", repo.get("name", "-"))
        table.add_row("Provider", repo.get("provider", "-"))
        table.add_row("URL", repo.get("url", "-"))
        table.add_row("Status", repo.get("status", "-"))
        table.add_row("Active", str(repo.get("active", "-")))
        table.add_row("Visibility", repo.get("visibility", "-"))
        table.add_row("Default Branch", repo.get("default_branch", "-"))
        table.add_row("Created At", repo.get("created_at", "-"))

        console.print(table)

        # Show compliance settings if available
        compliance = repo.get("compliance_settings")
        if compliance:
            console.print("\n[bold]Compliance Settings[/bold]")
            console.print(f"  Scanning: {'Enabled' if compliance.get('scanning') else 'Disabled'}")
            console.print(
                f"  Monitoring: {'Enabled' if compliance.get('monitoring') else 'Disabled'}"
            )
    except Exception as e:
        print_error(f"Failed to get repository: {e}")
        raise typer.Exit(1) from e


def create_repository(
    name: str = typer.Argument(..., help="Repository name"),
    url: str = typer.Option(..., "--url", "-u", help="Repository URL"),
    provider: str = typer.Option("github", "--provider", "-p", help="Git provider"),
    visibility: str = typer.Option("private", "--visibility", "-v", help="Visibility"),
    description: str | None = typer.Option(None, "--description", "-d", help="Description"),
) -> None:
    """Create a new repository."""
    try:
        config = RepositoryConfigSchema()
        body = RepositoryCreateSchema(
            name=name,
            url=url,
            provider=provider,
            option="existing",
            config=config,
            visibility=visibility,
            description=description,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_create.sync_detailed(
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to create repository.")
            return

        repo = data.get("repository", data)
        repo_id = repo.get("id", "N/A")
        print_success(f"Repository created: {repo_id}")

        table = create_table("Field", "Value", title="New Repository")
        table.add_row("ID", repo.get("id", "-"))
        table.add_row("Name", name)
        table.add_row("URL", url)
        table.add_row("Provider", provider)

        console.print(table)
    except Exception as e:
        print_error(f"Failed to create repository: {e}")
        raise typer.Exit(1) from e


def sync_repository(
    repository_id: str = typer.Argument(..., help="Repository ID"),
    status: str = typer.Option("start", "--status", "-s", help="Sync status (start, complete)"),
) -> None:
    """Sync repository status."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_sync.sync_detailed(
            repository_id=repository_id,
            status=status,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to sync repository.")
            return

        print_success(f"Repository sync {status}: {repository_id}")
    except Exception as e:
        print_error(f"Failed to sync repository: {e}")
        raise typer.Exit(1) from e


def initialize_repository(
    repository_id: str = typer.Argument(..., help="Repository ID"),
    workspace_id: str | None = typer.Option(None, "--workspace", "-w", help="Workspace ID"),
) -> None:
    """Initialize repository CI/CD."""
    try:
        body = RepositoryInitializeRequestSchema(workspace_id=workspace_id)

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_initialize.sync_detailed(
            repository_id=repository_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to initialize repository.")
            return

        pr_url = data.get("pr_url")
        if pr_url:
            console.print(f"\n[bold]Pull Request Created:[/bold] {pr_url}")
            console.print("\n[yellow]Merge the PR to complete initialization.[/yellow]")
        else:
            print_success(f"Repository initialized: {repository_id}")
    except Exception as e:
        print_error(f"Failed to initialize repository: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("list")(list_repositories)
app.command("show")(show_repository)
app.command("create")(create_repository)
app.command("sync")(sync_repository)
app.command("init")(initialize_repository)
