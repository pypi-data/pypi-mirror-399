"""Rich table formatter for scan results.

Outputs scan results as formatted tables using the Rich library,
suitable for terminal display with colors and styling.
"""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from iltero.scanners.formatters.base import BaseFormatter
from iltero.scanners.models import Severity
from iltero.utils.tables import create_table

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


class TableFormatter(BaseFormatter):
    """Format scan results as Rich tables for terminal display."""

    SEVERITY_COLORS = {
        Severity.CRITICAL: "red",
        Severity.HIGH: "orange1",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "blue",
        Severity.INFO: "dim",
    }

    def __init__(
        self,
        max_violations: int = 20,
        show_summary: bool = True,
        show_violations: bool = True,
    ) -> None:
        """Initialize Table formatter.

        Args:
            max_violations: Maximum violations to display (default: 20).
            show_summary: Whether to show summary table (default: True).
            show_violations: Whether to show violations table (default: True).
        """
        self._max_violations = max_violations
        self._show_summary = show_summary
        self._show_violations = show_violations

    def format(self, results: ScanResults) -> str:
        """Convert ScanResults to Rich table string.

        Args:
            results: The scan results to format.

        Returns:
            Formatted table string.
        """
        # Use StringIO to capture console output
        output = StringIO()
        console = Console(file=output, force_terminal=True)

        if self._show_summary:
            summary_table = self._build_summary_table(results)
            console.print(summary_table)
            console.print()

            # Violations by severity
            if results.summary.total_violations > 0:
                severity_table = self._build_severity_table(results)
                console.print(severity_table)
                console.print()

        if self._show_violations and results.violations:
            violations_table = self._build_violations_table(results)
            console.print(violations_table)

            if len(results.violations) > self._max_violations:
                console.print(
                    f"\n[dim]Showing {self._max_violations} of "
                    f"{len(results.violations)} violations.[/dim]"
                )

        return output.getvalue()

    def _build_summary_table(self, results: ScanResults) -> Table:
        """Build summary statistics table.

        Args:
            results: The scan results.

        Returns:
            Rich Table with summary stats.
        """
        table = create_table("Metric", "Value", title="Scan Summary", show_header=False)
        table.columns[0].style = "cyan"
        table.columns[1].style = "green"

        table.add_row("Scanner", results.scanner)
        table.add_row("Version", results.version)
        table.add_row("Duration", f"{results.duration_seconds:.2f}s")
        table.add_row("Total Checks", str(results.summary.total_checks))
        table.add_row("Passed", f"[green]{results.summary.passed}[/green]")
        table.add_row("Failed", f"[red]{results.summary.failed}[/red]")
        table.add_row("Skipped", str(results.summary.skipped))

        return table

    def _build_severity_table(self, results: ScanResults) -> Table:
        """Build violations by severity table.

        Args:
            results: The scan results.

        Returns:
            Rich Table with severity breakdown.
        """
        table = create_table("Severity", "Count", title="Violations by Severity")
        table.columns[0].style = "bold"
        table.columns[1].justify = "right"

        summary = results.summary

        if summary.critical > 0:
            table.add_row("[red]CRITICAL[/red]", str(summary.critical))
        if summary.high > 0:
            table.add_row("[orange1]HIGH[/orange1]", str(summary.high))
        if summary.medium > 0:
            table.add_row("[yellow]MEDIUM[/yellow]", str(summary.medium))
        if summary.low > 0:
            table.add_row("[blue]LOW[/blue]", str(summary.low))
        if summary.info > 0:
            table.add_row("[dim]INFO[/dim]", str(summary.info))

        return table

    def _build_violations_table(self, results: ScanResults) -> Table:
        """Build violations detail table.

        Args:
            results: The scan results.

        Returns:
            Rich Table with violation details.
        """
        violations = results.violations[: self._max_violations]

        table = create_table(
            "Check ID",
            "Severity",
            "Resource",
            "File",
            "Description",
            title=f"Violations ({len(results.violations)} total)",
            show_lines=True,
        )
        table.columns[0].style = "cyan"
        table.columns[0].width = 15
        table.columns[1].width = 10
        table.columns[2].style = "green"
        table.columns[2].width = 30
        table.columns[3].style = "blue"
        table.columns[3].width = 25
        table.columns[4].width = 40

        for v in violations:
            color = self.SEVERITY_COLORS.get(v.severity, "white")
            desc = v.description
            if len(desc) > 40:
                desc = desc[:37] + "..."

            table.add_row(
                v.check_id,
                f"[{color}]{v.severity.value}[/{color}]",
                v.resource,
                f"{v.file_path}:{v.line_range[0]}",
                desc,
            )

        return table

    def get_extension(self) -> str:
        """Return file extension for table format."""
        return ".txt"

    @property
    def name(self) -> str:
        """Return the formatter name."""
        return "Table"
