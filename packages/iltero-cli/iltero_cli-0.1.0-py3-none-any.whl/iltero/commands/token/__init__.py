"""Token management commands."""

from __future__ import annotations

from iltero.commands.token.main import app, console
from iltero.commands.token.operations import create_token, list_tokens

# Register commands
app.command("list")(list_tokens)
app.command("create")(create_token)

__all__ = [
    "app",
    "console",
    "list_tokens",
    "create_token",
]
