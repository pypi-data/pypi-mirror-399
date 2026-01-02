"""Authentication status command."""

from __future__ import annotations

from iltero.cli import get_auth, get_config
from iltero.commands.auth.main import console


def status():
    """Show authentication status."""
    auth = get_auth()
    config = get_config()

    console.print("[bold]Authentication Status[/bold]")
    console.print()

    # Check token availability
    has_token = auth.has_token()
    if has_token:
        console.print("[green]✓[/green] Token: Available")
        token = auth.get_token()
        token_type = token.split("_")[1] if "_" in token else "unknown"
        token_type_names = {
            "p": "Pipeline",
            "u": "Personal",
            "s": "Service",
            "r": "Registry",
        }
        console.print(f"  Type: {token_type_names.get(token_type, 'Unknown')}")
    else:
        console.print("[red]✗[/red] Token: Not configured")
        console.print("  [dim]Run 'iltero auth set-token' to configure[/dim]")

    console.print()
    console.print(f"API URL: {config.get_api_url()}")
