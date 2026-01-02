"""Shared utilities for environment commands."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Environment management")
console = Console()

# Column definitions for environment table output
ENVIRONMENT_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("key", "Key"),
    ("is_production", "Production"),
    ("is_default", "Default"),
    ("color", "Color"),
]
