"""SARIF formatter for scan results.

SARIF (Static Analysis Results Interchange Format) is a standard format
for the output of static analysis tools. This formatter produces SARIF 2.1.0
compatible output suitable for GitHub Code Scanning and other SARIF consumers.

Reference: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from iltero.scanners.formatters.base import BaseFormatter
from iltero.scanners.models import Severity

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


class SARIFFormatter(BaseFormatter):
    """Format scan results as SARIF 2.1.0 for GitHub Code Scanning."""

    SARIF_SCHEMA = (
        "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/"
        "master/Schemata/sarif-schema-2.1.0.json"
    )

    def format(self, results: ScanResults) -> str:
        """Convert ScanResults to SARIF JSON string.

        Args:
            results: The scan results to format.

        Returns:
            SARIF JSON string.
        """
        sarif_dict = self.to_dict(results)
        return json.dumps(sarif_dict, indent=2)

    def to_dict(self, results: ScanResults) -> dict:
        """Convert ScanResults to SARIF dictionary.

        Args:
            results: The scan results to format.

        Returns:
            SARIF dictionary structure.
        """
        return {
            "version": "2.1.0",
            "$schema": self.SARIF_SCHEMA,
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": results.scanner,
                            "version": results.version,
                            "informationUri": "https://iltero.io",
                            "rules": self._build_rules(results),
                        }
                    },
                    "results": self._build_results(results),
                }
            ],
        }

    def _build_rules(self, results: ScanResults) -> list[dict]:
        """Build SARIF rules from unique check IDs.

        Args:
            results: The scan results.

        Returns:
            List of SARIF rule definitions.
        """
        seen_rules: dict[str, dict] = {}

        for violation in results.violations:
            if violation.check_id not in seen_rules:
                rule: dict = {
                    "id": violation.check_id,
                    "shortDescription": {"text": violation.check_id},
                    "fullDescription": {"text": violation.description},
                    "defaultConfiguration": {"level": self._severity_to_level(violation.severity)},
                }
                # Add help URI from metadata if available
                if violation.metadata.get("guideline_url"):
                    rule["helpUri"] = violation.metadata["guideline_url"]
                seen_rules[violation.check_id] = rule

        return list(seen_rules.values())

    def _build_results(self, results: ScanResults) -> list[dict]:
        """Build SARIF results from violations.

        Args:
            results: The scan results.

        Returns:
            List of SARIF result objects.
        """
        sarif_results = []

        for violation in results.violations:
            result = {
                "ruleId": violation.check_id,
                "level": self._severity_to_level(violation.severity),
                "message": {"text": violation.description},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": violation.file_path},
                            "region": {
                                "startLine": violation.line_range[0],
                                "endLine": violation.line_range[1],
                            },
                        }
                    }
                ],
            }

            # Add fix information if remediation is available
            if violation.remediation:
                result["fixes"] = [
                    {
                        "description": {"text": violation.remediation},
                    }
                ]

            sarif_results.append(result)

        return sarif_results

    def _severity_to_level(self, severity: Severity) -> str:
        """Map severity to SARIF level.

        Args:
            severity: The violation severity.

        Returns:
            SARIF level string.
        """
        mapping = {
            Severity.CRITICAL: "error",
            Severity.HIGH: "error",
            Severity.MEDIUM: "warning",
            Severity.LOW: "note",
            Severity.INFO: "note",
        }
        return mapping.get(severity, "warning")

    def get_extension(self) -> str:
        """Return file extension for SARIF format."""
        return ".sarif"

    @property
    def name(self) -> str:
        """Return the formatter name."""
        return "SARIF"
