"""Base scanner interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import ScanResults, ScanType


class BaseScanner(ABC):
    """Base class for all scanners."""

    def __init__(
        self,
        parallel: bool = True,
        timeout: int = 300,
        policy_sets: list[str] | None = None,
        frameworks: list[str] | None = None,
    ):
        """Initialize scanner.

        Args:
            parallel: Run checks in parallel for speed.
            timeout: Maximum scan duration in seconds.
            policy_sets: List of policy set names to apply.
            frameworks: List of compliance frameworks to check.
        """
        self.parallel = parallel
        self.timeout = timeout
        self.policy_sets = policy_sets or []
        self.frameworks = frameworks or []

    @abstractmethod
    def scan(
        self,
        path: str,
        scan_type: ScanType = ScanType.STATIC,
    ) -> ScanResults:
        """Run scan on the given path.

        Args:
            path: Path to scan (directory or file).
            scan_type: Type of scan to run.

        Returns:
            ScanResults object with all findings.
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """Get scanner tool version."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if scanner is installed and available."""
        pass

    def validate_prerequisites(self) -> tuple[bool, str | None]:
        """Validate scanner prerequisites.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if not self.is_available():
            return False, f"{self.__class__.__name__} is not installed"
        return True, None
