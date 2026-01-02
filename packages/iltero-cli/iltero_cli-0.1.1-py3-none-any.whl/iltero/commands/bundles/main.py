"""Shared utilities and setup for bundles commands."""

from __future__ import annotations

import typer
from rich.console import Console

# Create Typer app
app = typer.Typer(help="Template bundle marketplace")
console = Console()

# Column definitions for bundle table output
BUNDLE_COLUMNS = [
    ("id", "ID"),
    ("name", "Name"),
    ("provider", "Provider"),
    ("industry", "Industry"),
    ("tier", "Tier"),
    ("compliance_frameworks", "Compliance"),
    ("marketplace_category", "Category"),
]
