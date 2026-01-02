"""Scanner utility commands."""

from __future__ import annotations

import typer

from iltero.commands.scanner.check import scanner_check

app = typer.Typer(
    name="scanner",
    help="Scanner installation and diagnostics",
    no_args_is_help=True,
)

# Register commands
app.command("check")(scanner_check)

__all__ = [
    "app",
    "scanner_check",
]
