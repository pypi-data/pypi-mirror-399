"""Shared utilities and setup for registry commands."""

from __future__ import annotations

import typer
from rich.console import Console

# Create main app
app = typer.Typer(help="Module registry management")
console = Console()

# Column definitions for registry module table output
MODULE_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("namespace", "Namespace"),
    ("provider", "Provider"),
    ("tool", "Tool"),
    ("active", "Active"),
]
