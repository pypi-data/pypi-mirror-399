"""Shared utilities for stack commands."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Stack management")
console = Console()

# Column definitions for stack table output
STACK_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("description", "Description"),
    ("active", "Active"),
    ("template_id", "Template"),
]
