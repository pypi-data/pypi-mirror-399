"""JSON formatter for scan results.

Outputs scan results in JSON format, suitable for programmatic consumption,
API integration, and further processing by other tools.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from iltero.scanners.formatters.base import BaseFormatter

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


class JSONFormatter(BaseFormatter):
    """Format scan results as JSON."""

    def __init__(self, indent: int = 2, compact: bool = False) -> None:
        """Initialize JSON formatter.

        Args:
            indent: Number of spaces for indentation (default: 2).
            compact: If True, output compact JSON without indentation.
        """
        self._indent = None if compact else indent

    def format(self, results: ScanResults) -> str:
        """Convert ScanResults to JSON string.

        Args:
            results: The scan results to format.

        Returns:
            JSON string representation.
        """
        return json.dumps(results.to_dict(), indent=self._indent)

    def get_extension(self) -> str:
        """Return file extension for JSON format."""
        return ".json"

    @property
    def name(self) -> str:
        """Return the formatter name."""
        return "JSON"
