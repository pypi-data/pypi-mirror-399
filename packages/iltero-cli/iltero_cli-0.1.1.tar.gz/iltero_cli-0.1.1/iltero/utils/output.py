"""Output formatting utilities for CLI commands."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

import yaml
from rich.console import Console
from rich.panel import Panel

from iltero.utils.tables import create_table

console = Console()


class OutputFormat(str, Enum):
    """Supported output formats."""

    TABLE = "table"
    JSON = "json"
    YAML = "yaml"


def format_output(
    data: Any,
    format_type: OutputFormat = OutputFormat.TABLE,
    title: str | None = None,
    columns: list[tuple[str, str]] | None = None,
) -> None:
    """Format and print data in the specified format.

    Args:
        data: Data to format (list of dicts, dict, or any JSON-serializable)
        format_type: Output format (table, json, yaml)
        title: Title for table output
        columns: List of (key, header) tuples for table columns
    """
    if format_type == OutputFormat.JSON:
        print_json(data)
    elif format_type == OutputFormat.YAML:
        print_yaml(data)
    else:
        print_table(data, title=title, columns=columns)


def print_json(data: Any) -> None:
    """Print data as formatted JSON."""
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    elif isinstance(data, list):
        data = [item.to_dict() if hasattr(item, "to_dict") else item for item in data]

    console.print_json(json.dumps(data, indent=2, default=str))


def print_yaml(data: Any) -> None:
    """Print data as YAML."""
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    elif isinstance(data, list):
        data = [item.to_dict() if hasattr(item, "to_dict") else item for item in data]

    yaml_str = yaml.safe_dump(data, default_flow_style=False, sort_keys=False)
    console.print(yaml_str)


def print_table(
    data: Any,
    title: str | None = None,
    columns: list[tuple[str, str]] | None = None,
) -> None:
    """Print data as a Rich table.

    Args:
        data: List of dicts or single dict to display
        title: Table title
        columns: List of (key, header) tuples defining columns
    """
    # Handle single item as list
    if isinstance(data, dict):
        data = [data]

    if not data:
        console.print("[dim]No data to display[/dim]")
        return

    # Convert model objects to dicts
    rows = []
    for item in data:
        if hasattr(item, "to_dict"):
            rows.append(item.to_dict())
        elif hasattr(item, "__dict__"):
            rows.append(vars(item))
        else:
            rows.append(item)

    # Auto-detect columns if not provided
    if columns is None and rows:
        columns = [(k, k.replace("_", " ").title()) for k in rows[0].keys()]

    # Create table with column headers
    headers = [header for _, header in columns or []]
    table = create_table(*headers, title=title)

    # Add rows
    for row in rows:
        values = []
        for key, _ in columns or []:
            value = row.get(key, "")
            values.append(format_cell_value(value))
        table.add_row(*values)

    console.print(table)


def format_cell_value(value: Any) -> str:
    """Format a cell value for table display."""
    if value is None:
        return "[dim]—[/dim]"
    if isinstance(value, bool):
        return "[green]✓[/green]" if value else "[red]✗[/red]"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "[dim]—[/dim]"
    if isinstance(value, dict):
        return json.dumps(value, default=str)
    return str(value)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[red]✗[/red] {message}", style="red")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def print_detail(label: str, value: Any) -> None:
    """Print a label-value pair."""
    formatted_value = format_cell_value(value)
    console.print(f"  [bold]{label}:[/bold] {formatted_value}")


def print_panel(content: str, title: str | None = None, style: str = "blue") -> None:
    """Print content in a panel."""
    console.print(Panel(content, title=title, border_style=style))


def confirm_action(message: str, default: bool = False) -> bool:
    """Prompt for confirmation."""
    from rich.prompt import Confirm

    return Confirm.ask(message, default=default)
