"""Shared utilities for token commands."""

from __future__ import annotations

import typer
from rich.console import Console

app = typer.Typer(help="Token operations")
console = Console()
