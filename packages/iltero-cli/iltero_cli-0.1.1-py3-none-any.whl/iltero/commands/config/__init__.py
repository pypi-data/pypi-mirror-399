"""Configuration management commands."""

from __future__ import annotations

import typer

app = typer.Typer(help="CLI configuration management")

# Import submodules to register commands
from iltero.commands.config import main  # noqa: F401, E402
