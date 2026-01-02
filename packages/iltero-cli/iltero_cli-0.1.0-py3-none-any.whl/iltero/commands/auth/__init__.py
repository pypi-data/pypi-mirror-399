"""Authentication commands."""

from __future__ import annotations

from iltero.commands.auth.main import app, console
from iltero.commands.auth.status_cmd import status
from iltero.commands.auth.tokens import clear_token, set_token, show_token

# Register commands
app.command("set-token")(set_token)
app.command("show-token")(show_token)
app.command("clear-token")(clear_token)
app.command("status")(status)

__all__ = [
    "app",
    "console",
    "set_token",
    "show_token",
    "clear_token",
    "status",
]
