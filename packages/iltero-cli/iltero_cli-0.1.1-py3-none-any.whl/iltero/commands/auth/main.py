"""Shared utilities for auth commands."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Authentication management")
console = Console()
