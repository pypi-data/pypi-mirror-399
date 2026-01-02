"""Stack variables commands - read-only list with secret masking."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.stacks_variables import (
    list_stack_variables as api_list,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack variables (read-only)")
console = Console()

# Secret value mask
SECRET_MASK = "********"


def _mask_value(value: str | None, is_secret: bool) -> str:
    """Mask secret values for display."""
    if is_secret:
        return SECRET_MASK
    return value or "-"


@app.command("list")
def list_variables(
    stack_id: str = typer.Argument(..., help="Stack ID to list variables for"),
    show_secrets: bool = typer.Option(
        False,
        "--show-secrets",
        help="Show secret values (requires appropriate permissions)",
    ),
    page: int = typer.Option(1, "--page", "-p", help="Page number (1-indexed)"),
    per_page: int = typer.Option(20, "--per-page", "-n", help="Items per page"),
    category: str | None = typer.Option(
        None,
        "--category",
        "-c",
        help="Filter by category (env, terraform, secret)",
    ),
) -> None:
    """List variables for a stack.

    Displays stack variables in a paginated table. Secret values are
    masked by default for security. Use --show-secrets to reveal them
    (requires appropriate permissions).

    Example:
        iltero stack variables list abc123
        iltero stack variables list abc123 --page 2 --per-page 10
        iltero stack variables list abc123 --category terraform
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_list.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info(f"No variables found for stack '{stack_id}'.")
            return

        variables = data.get("variables", [])
        if not variables:
            print_info(f"No variables found for stack '{stack_id}'.")
            return

        # Filter by category if specified
        if category:
            variables = [v for v in variables if v.get("category", "").lower() == category.lower()]
            if not variables:
                print_info(f"No variables found with category '{category}'.")
                return

        # Calculate pagination
        total = len(variables)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total)

        if start_idx >= total:
            print_info(f"Page {page} is out of range. Total pages: {total_pages}")
            return

        paginated = variables[start_idx:end_idx]

        # Create table
        table = create_table("Key", "Value", "Category", "Sensitive", "Description")

        for var in paginated:
            key = var.get("key", "-")
            is_secret = var.get("sensitive", False) or var.get("is_secret", False)
            raw_value = var.get("value", "")

            # Mask value if secret and not showing secrets
            if is_secret and not show_secrets:
                display_value = SECRET_MASK
            else:
                display_value = str(raw_value) if raw_value else "-"

            # Truncate long values
            if len(display_value) > 50:
                display_value = display_value[:47] + "..."

            category_val = var.get("category", "-")
            sensitive_display = "[red]Yes[/red]" if is_secret else "No"
            description = var.get("description", "-") or "-"

            # Truncate long descriptions
            if len(description) > 40:
                description = description[:37] + "..."

            table.add_row(
                key,
                display_value,
                category_val,
                sensitive_display,
                description,
            )

        console.print(table)

        # Pagination info
        console.print(
            f"\nShowing [cyan]{start_idx + 1}-{end_idx}[/cyan] of "
            f"[cyan]{total}[/cyan] variables "
            f"(page [cyan]{page}/{total_pages}[/cyan])"
        )

        if total_pages > 1:
            if page < total_pages:
                console.print(f"[dim]Use --page {page + 1} to see more[/dim]")

        # Security note if secrets present
        secret_count = sum(
            1 for v in variables if v.get("sensitive", False) or v.get("is_secret", False)
        )
        if secret_count > 0 and not show_secrets:
            console.print(
                f"\n[dim]{secret_count} sensitive variable(s) masked. "
                "Use --show-secrets to reveal.[/dim]"
            )

    except Exception as e:
        print_error(f"Failed to list variables: {e}")
        raise typer.Exit(1) from e
