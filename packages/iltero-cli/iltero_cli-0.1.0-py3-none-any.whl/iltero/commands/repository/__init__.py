"""Repository management commands."""

from __future__ import annotations

import typer

app = typer.Typer(help="Repository management")

# Import submodules to register commands
from iltero.commands.repository import main  # noqa: F401, E402
