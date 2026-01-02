"""Shared utilities for workspace commands."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Workspace management")
console = Console()

# Column definitions for workspace table output
WORKSPACE_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("description", "Description"),
    ("slug", "Slug"),
    ("active", "Active"),
]
