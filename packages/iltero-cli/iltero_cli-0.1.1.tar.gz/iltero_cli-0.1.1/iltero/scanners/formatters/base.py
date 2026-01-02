"""Base formatter interface for scan results."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


class BaseFormatter(ABC):
    """Abstract base class for output formatters.

    All formatters must implement the format() method to convert
    ScanResults into their specific output format.
    """

    @abstractmethod
    def format(self, results: ScanResults) -> str:
        """Format scan results to string output.

        Args:
            results: The scan results to format.

        Returns:
            Formatted string representation of the results.
        """
        pass

    @abstractmethod
    def get_extension(self) -> str:
        """Return file extension for this format.

        Returns:
            File extension including the dot (e.g., '.sarif', '.xml').
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the formatter name.

        Returns:
            Human-readable name of the format.
        """
        pass
