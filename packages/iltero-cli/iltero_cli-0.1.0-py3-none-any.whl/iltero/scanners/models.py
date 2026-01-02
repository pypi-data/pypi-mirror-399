"""Scanner data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ScanType(str, Enum):
    """Type of scan being performed."""

    STATIC = "static"  # Pre-plan static analysis (Checkov on .tf files)
    EVALUATION = "evaluation"  # Post-plan policy evaluation (OPA on plan JSON)
    RUNTIME = "runtime"  # Runtime infrastructure scan


class Severity(str, Enum):
    """Severity levels for violations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Violation:
    """Represents a single compliance violation."""

    check_id: str  # e.g., "CKV_AWS_1"
    check_name: str  # e.g., "Ensure S3 bucket encryption"
    severity: Severity
    resource: str  # e.g., "aws_s3_bucket.data"
    file_path: str  # e.g., "terraform/storage.tf"
    line_range: tuple[int, int]  # (start_line, end_line)
    description: str
    remediation: str | None = None
    framework: str | None = None  # e.g., "CIS AWS 1.4"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API submission."""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "severity": self.severity.value,
            "resource": self.resource,
            "file_path": self.file_path,
            "line_range": list(self.line_range),
            "description": self.description,
            "remediation": self.remediation,
            "framework": self.framework,
            "metadata": self.metadata or {},
        }


@dataclass
class ScanSummary:
    """Summary of scan results."""

    total_checks: int
    passed: int
    failed: int
    skipped: int
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0

    @property
    def total_violations(self) -> int:
        """Get total number of violations."""
        return self.critical + self.high + self.medium + self.low + self.info

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_checks": self.total_checks,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "critical": self.critical,
            "high": self.high,
            "medium": self.medium,
            "low": self.low,
            "info": self.info,
        }


@dataclass
class ScanResults:
    """Complete scan results from a single scanner."""

    scanner: str  # "checkov" or "opa"
    version: str  # Scanner version
    scan_type: ScanType
    started_at: datetime
    completed_at: datetime
    summary: ScanSummary
    violations: list[Violation]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def duration_seconds(self) -> float:
        """Calculate scan duration in seconds."""
        return (self.completed_at - self.started_at).total_seconds()

    def get_violations_by_severity(self) -> dict[str, int]:
        """Get violation counts by severity."""
        return {
            "critical": self.summary.critical,
            "high": self.summary.high,
            "medium": self.summary.medium,
            "low": self.summary.low,
            "info": self.summary.info,
        }

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API submission."""
        return {
            "scanner": self.scanner,
            "version": self.version,
            "scan_type": self.scan_type.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat(),
            "duration_seconds": self.duration_seconds,
            "summary": self.summary.to_dict(),
            "violations": [v.to_dict() for v in self.violations],
            "metadata": self.metadata,
        }
