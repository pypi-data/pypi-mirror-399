"""JUnit XML formatter for scan results.

JUnit XML is a standard format for test results, widely supported by
CI/CD systems like Jenkins, GitHub Actions, GitLab CI, and Azure DevOps.
This formatter converts scan violations into JUnit test failure format.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from iltero.scanners.formatters.base import BaseFormatter

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


class JUnitFormatter(BaseFormatter):
    """Format scan results as JUnit XML for CI/CD integration."""

    def format(self, results: ScanResults) -> str:
        """Convert ScanResults to JUnit XML string.

        Args:
            results: The scan results to format.

        Returns:
            JUnit XML string.
        """
        testsuites = ET.Element("testsuites")
        testsuites.set("name", "Iltero Compliance Scan")
        testsuites.set("tests", str(results.summary.total_checks))
        testsuites.set("failures", str(results.summary.failed))
        testsuites.set("time", str(results.duration_seconds))

        testsuite = ET.SubElement(
            testsuites,
            "testsuite",
            name=results.scanner,
            tests=str(results.summary.total_checks),
            failures=str(results.summary.failed),
            skipped=str(results.summary.skipped),
            time=str(results.duration_seconds),
        )

        # Add passed checks as successful test cases
        passed_count = results.summary.passed
        for i in range(min(passed_count, 100)):  # Limit to avoid huge files
            ET.SubElement(
                testsuite,
                "testcase",
                name=f"passed_check_{i + 1}",
                classname=results.scanner,
                time="0",
            )

        # Add violations as failed test cases
        for violation in results.violations:
            testcase = ET.SubElement(
                testsuite,
                "testcase",
                name=violation.check_id,
                classname=violation.resource or "unknown",
                time="0",
            )

            failure = ET.SubElement(
                testcase,
                "failure",
                message=self._truncate(violation.description, 200),
                type=violation.severity.value,
            )

            # Build detailed failure text
            failure_text_parts = [
                f"File: {violation.file_path}",
                f"Line: {violation.line_range[0]}-{violation.line_range[1]}",
                f"Severity: {violation.severity.value}",
                "",
                violation.description,
            ]

            if violation.remediation:
                failure_text_parts.extend(
                    [
                        "",
                        "Remediation:",
                        violation.remediation,
                    ]
                )

            failure.text = "\n".join(failure_text_parts)

        return self._prettify(testsuites)

    def _prettify(self, element: ET.Element) -> str:
        """Convert ElementTree to formatted XML string.

        Args:
            element: The root XML element.

        Returns:
            Formatted XML string with declaration.
        """
        xml_str = ET.tostring(element, encoding="unicode")
        # Add XML declaration
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length.

        Args:
            text: The text to truncate.
            max_length: Maximum allowed length.

        Returns:
            Truncated text with ellipsis if needed.
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def get_extension(self) -> str:
        """Return file extension for JUnit format."""
        return ".xml"

    @property
    def name(self) -> str:
        """Return the formatter name."""
        return "JUnit"
