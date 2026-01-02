"""Registry template commands - list and show templates."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.onboarding import (
    onboarding_get_template_bundles_42b6e9a1 as api_list_templates,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info
from iltero.utils.tables import create_table

console = Console()

templates_app = typer.Typer(help="Template bundle management")


def list_templates(
    provider: str = typer.Option(
        "aws", "--provider", "-p", help="Cloud provider (aws, azure, gcp)"
    ),
    framework: str | None = typer.Option(None, "--framework", "-f", help="Framework filter"),
    industry: str | None = typer.Option(None, "--industry", "-i", help="Industry filter"),
) -> None:
    """List available template bundles."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list_templates.sync_detailed(
            client=auth_client,
            provider=provider,
            framework=framework,
            industry=industry,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No templates found.")
            return

        templates = data.get("bundles", data.get("templates", []))
        if not templates:
            print_info("No templates found.")
            return

        table = create_table("ID", "Name", "Provider", "Framework", "Industry")
        for t in templates:
            table.add_row(
                t.get("id", "-"),
                t.get("name", "-"),
                t.get("provider", "-"),
                t.get("framework", "-"),
                t.get("industry", "-"),
            )

        console.print(table)
        console.print(f"\nTotal: [cyan]{len(templates)}[/cyan] templates")
    except Exception as e:
        print_error(f"Failed to list templates: {e}")
        raise typer.Exit(1) from e


def show_template(
    template_id: str = typer.Argument(..., help="Template bundle ID"),
) -> None:
    """Show template bundle details."""
    try:
        # Use list with provider to find the template
        # The API doesn't have a direct get endpoint
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Try each provider to find template
        for provider in ["aws", "azure", "gcp"]:
            response = api_list_templates.sync_detailed(
                client=auth_client,
                provider=provider,
            )

            result = client.handle_response(response)
            data = result.data

            if data:
                templates = data.get("bundles", data.get("templates", []))
                for t in templates:
                    if t.get("id") == template_id:
                        _display_template(t)
                        return

        print_info(f"Template not found: {template_id}")
    except Exception as e:
        print_error(f"Failed to get template: {e}")
        raise typer.Exit(1) from e


def _display_template(template: dict) -> None:
    """Display template details."""
    table = create_table("Field", "Value", title="Template Details")
    table.add_row("ID", template.get("id", "-"))
    table.add_row("Name", template.get("name", "-"))
    table.add_row("Description", template.get("description", "-"))
    table.add_row("Provider", template.get("provider", "-"))
    table.add_row("Framework", template.get("framework", "-"))
    table.add_row("Industry", template.get("industry", "-"))
    table.add_row("Version", template.get("version", "-"))

    console.print(table)

    # Show modules if available
    modules = template.get("modules", [])
    if modules:
        console.print("\n[bold]Included Modules[/bold]")
        m_table = create_table("Module", "Version", "Description")
        for m in modules:
            m_table.add_row(
                m.get("name", "-"),
                m.get("version", "-"),
                m.get("description", "-")[:40] + "..."
                if len(m.get("description", "")) > 40
                else m.get("description", "-"),
            )
        console.print(m_table)


# Register commands
templates_app.command("list")(list_templates)
templates_app.command("show")(show_template)
