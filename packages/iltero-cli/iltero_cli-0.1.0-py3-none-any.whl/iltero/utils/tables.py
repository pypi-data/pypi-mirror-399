"""Centralized table styling for consistent CLI output."""

from __future__ import annotations

from rich.box import MINIMAL
from rich.table import Table

# Global table configuration - modify here to change all tables
TABLE_BOX_STYLE = MINIMAL
TABLE_HEADER_STYLE = "bold"
TABLE_SHOW_HEADER = True


def create_table(
    *columns: str,
    title: str | None = None,
    show_header: bool | None = None,
    header_style: str | None = None,
    **kwargs,
) -> Table:
    """Create a consistently styled table.

    Args:
        *columns: Column names to add to the table.
        title: Optional table title.
        show_header: Override default show_header setting.
        header_style: Override default header style.
        **kwargs: Additional arguments passed to Table constructor.

    Returns:
        A Rich Table with consistent styling.

    Example:
        table = create_table("Name", "Status", "Version")
        table.add_row("Checkov", "Installed", "2.5.0")
        console.print(table)
    """
    if show_header is None:
        show_header = TABLE_SHOW_HEADER
    table = Table(
        title=title,
        box=TABLE_BOX_STYLE,
        show_header=show_header,
        header_style=header_style or TABLE_HEADER_STYLE,
        **kwargs,
    )

    for column in columns:
        table.add_column(column)

    return table
