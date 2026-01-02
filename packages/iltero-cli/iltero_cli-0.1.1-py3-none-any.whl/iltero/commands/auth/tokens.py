"""Token management commands - set, show, clear."""

from __future__ import annotations

import typer
from rich.prompt import Prompt

from iltero.cli import get_auth
from iltero.commands.auth.main import console


def set_token(
    token: str = typer.Option(
        None,
        "--token",
        "-t",
        help="API token (if not provided, will prompt)",
    ),
):
    """
    Store API token in system keyring.

    Get your token from the Iltero web UI or backend admin panel.
    """
    auth = get_auth()

    if not token:
        token = Prompt.ask("Enter your API token", password=True)

    auth.set_token(token)
    console.print("[green]✓[/green] Token stored successfully in keyring")
    console.print("[dim]You can now use other iltero commands[/dim]")


def show_token(
    reveal: bool = typer.Option(
        False,
        "--reveal",
        help="Show full token (default: masked)",
    ),
):
    """Show current API token."""
    auth = get_auth()

    try:
        token = auth.get_token()
        if reveal:
            console.print(f"Token: {token}")
        else:
            # Show only first and last 8 characters
            masked = f"{token[:8]}...{token[-8:]}"
            console.print(f"Token: {masked}")
            console.print("[dim]Use --reveal to show full token[/dim]")
    except Exception as e:
        console.print(f"[red]No token found:[/red] {e}")
        console.print("[dim]Run 'iltero auth set-token' to configure[/dim]")


def clear_token(
    confirm: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation",
    ),
):
    """Remove API token from keyring."""
    if not confirm:
        confirmed = typer.confirm("Are you sure you want to clear the stored token?")
        if not confirmed:
            console.print("Operation cancelled")
            raise typer.Exit(0)

    auth = get_auth()
    auth.clear_token()
    console.print("[green]✓[/green] Token cleared from keyring")
