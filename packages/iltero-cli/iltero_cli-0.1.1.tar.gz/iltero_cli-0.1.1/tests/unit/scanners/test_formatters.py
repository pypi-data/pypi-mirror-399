"""Tests for output formatters."""

import json
import xml.etree.ElementTree as ET
from datetime import datetime

import pytest

from iltero.scanners.formatters import (
    BaseFormatter,
    JSONFormatter,
    JUnitFormatter,
    SARIFFormatter,
    TableFormatter,
)
from iltero.scanners.models import (
    ScanResults,
    ScanSummary,
    ScanType,
    Severity,
    Violation,
)


@pytest.fixture
def sample_violation():
    """Create a sample violation for testing."""
    return Violation(
        check_id="CKV_AWS_1",
        check_name="Ensure S3 bucket encryption",
        severity=Severity.HIGH,
        resource="aws_s3_bucket.data",
        file_path="terraform/storage.tf",
        line_range=(10, 15),
        description="S3 bucket does not have encryption enabled",
        remediation="Add server_side_encryption_configuration block",
        framework="CIS AWS 1.4",
    )


@pytest.fixture
def sample_results(sample_violation):
    """Create sample scan results for testing."""
    return ScanResults(
        scanner="checkov",
        version="2.5.0",
        scan_type=ScanType.STATIC,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        violations=[sample_violation],
        summary=ScanSummary(
            total_checks=10,
            passed=9,
            failed=1,
            skipped=0,
            high=1,
        ),
    )


@pytest.fixture
def empty_results():
    """Create empty scan results for testing."""
    return ScanResults(
        scanner="checkov",
        version="2.5.0",
        scan_type=ScanType.STATIC,
        started_at=datetime.now(),
        completed_at=datetime.now(),
        violations=[],
        summary=ScanSummary(
            total_checks=10,
            passed=10,
            failed=0,
            skipped=0,
        ),
    )


class TestJSONFormatter:
    """Tests for JSON formatter."""

    def test_format_returns_valid_json(self, sample_results):
        """Test that format returns valid JSON."""
        formatter = JSONFormatter()
        output = formatter.format(sample_results)

        # Should be valid JSON
        data = json.loads(output)
        assert data is not None

    def test_format_includes_scanner_info(self, sample_results):
        """Test that JSON includes scanner info."""
        formatter = JSONFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        assert data["scanner"] == "checkov"
        assert data["version"] == "2.5.0"

    def test_format_includes_violations(self, sample_results):
        """Test that JSON includes violations."""
        formatter = JSONFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        assert len(data["violations"]) == 1
        assert data["violations"][0]["check_id"] == "CKV_AWS_1"

    def test_format_includes_summary(self, sample_results):
        """Test that JSON includes summary."""
        formatter = JSONFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        assert data["summary"]["total_checks"] == 10
        assert data["summary"]["passed"] == 9
        assert data["summary"]["failed"] == 1

    def test_compact_mode(self, sample_results):
        """Test compact JSON mode without indentation."""
        formatter = JSONFormatter(compact=True)
        output = formatter.format(sample_results)

        # Compact JSON should not have newlines (except in values)
        assert "\n" not in output.split('"')[0]

    def test_get_extension(self):
        """Test file extension."""
        formatter = JSONFormatter()
        assert formatter.get_extension() == ".json"

    def test_name(self):
        """Test formatter name."""
        formatter = JSONFormatter()
        assert formatter.name == "JSON"


class TestSARIFFormatter:
    """Tests for SARIF formatter."""

    def test_format_returns_valid_json(self, sample_results):
        """Test that format returns valid JSON."""
        formatter = SARIFFormatter()
        output = formatter.format(sample_results)

        data = json.loads(output)
        assert data is not None

    def test_sarif_version(self, sample_results):
        """Test SARIF version is correct."""
        formatter = SARIFFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        assert data["version"] == "2.1.0"
        assert "$schema" in data

    def test_sarif_has_runs(self, sample_results):
        """Test SARIF has runs array."""
        formatter = SARIFFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        assert "runs" in data
        assert len(data["runs"]) == 1

    def test_sarif_tool_info(self, sample_results):
        """Test SARIF includes tool information."""
        formatter = SARIFFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        tool = data["runs"][0]["tool"]["driver"]
        assert tool["name"] == "checkov"
        assert tool["version"] == "2.5.0"

    def test_sarif_results(self, sample_results):
        """Test SARIF results mapping."""
        formatter = SARIFFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        results = data["runs"][0]["results"]
        assert len(results) == 1
        assert results[0]["ruleId"] == "CKV_AWS_1"
        assert results[0]["level"] == "error"  # HIGH maps to error

    def test_sarif_location(self, sample_results):
        """Test SARIF location information."""
        formatter = SARIFFormatter()
        output = formatter.format(sample_results)
        data = json.loads(output)

        result = data["runs"][0]["results"][0]
        location = result["locations"][0]["physicalLocation"]

        assert location["artifactLocation"]["uri"] == "terraform/storage.tf"
        assert location["region"]["startLine"] == 10
        assert location["region"]["endLine"] == 15

    def test_sarif_severity_mapping(self, sample_results):
        """Test severity to SARIF level mapping."""
        formatter = SARIFFormatter()

        # Test different severities
        assert formatter._severity_to_level(Severity.CRITICAL) == "error"
        assert formatter._severity_to_level(Severity.HIGH) == "error"
        assert formatter._severity_to_level(Severity.MEDIUM) == "warning"
        assert formatter._severity_to_level(Severity.LOW) == "note"
        assert formatter._severity_to_level(Severity.INFO) == "note"

    def test_sarif_empty_results(self, empty_results):
        """Test SARIF with no violations."""
        formatter = SARIFFormatter()
        output = formatter.format(empty_results)
        data = json.loads(output)

        results = data["runs"][0]["results"]
        assert len(results) == 0

    def test_to_dict_returns_dict(self, sample_results):
        """Test to_dict returns dictionary."""
        formatter = SARIFFormatter()
        data = formatter.to_dict(sample_results)

        assert isinstance(data, dict)
        assert data["version"] == "2.1.0"

    def test_get_extension(self):
        """Test file extension."""
        formatter = SARIFFormatter()
        assert formatter.get_extension() == ".sarif"

    def test_name(self):
        """Test formatter name."""
        formatter = SARIFFormatter()
        assert formatter.name == "SARIF"


class TestJUnitFormatter:
    """Tests for JUnit formatter."""

    def test_format_returns_valid_xml(self, sample_results):
        """Test that format returns valid XML."""
        formatter = JUnitFormatter()
        output = formatter.format(sample_results)

        # Should be valid XML
        root = ET.fromstring(output)
        assert root is not None

    def test_junit_has_testsuites(self, sample_results):
        """Test JUnit has testsuites element."""
        formatter = JUnitFormatter()
        output = formatter.format(sample_results)
        root = ET.fromstring(output)

        assert root.tag == "testsuites"

    def test_junit_testsuite_attributes(self, sample_results):
        """Test JUnit testsuite attributes."""
        formatter = JUnitFormatter()
        output = formatter.format(sample_results)
        root = ET.fromstring(output)

        testsuite = root.find("testsuite")
        assert testsuite is not None
        assert testsuite.get("name") == "checkov"
        assert testsuite.get("tests") == "10"
        assert testsuite.get("failures") == "1"

    def test_junit_failure_testcase(self, sample_results):
        """Test JUnit failure test case."""
        formatter = JUnitFormatter()
        output = formatter.format(sample_results)
        root = ET.fromstring(output)

        # Find testcase with failure
        testsuite = root.find("testsuite")
        testcases = testsuite.findall("testcase")

        # Find the failure testcase
        failure_testcase = None
        for tc in testcases:
            if tc.find("failure") is not None:
                failure_testcase = tc
                break

        assert failure_testcase is not None
        assert failure_testcase.get("name") == "CKV_AWS_1"

        failure = failure_testcase.find("failure")
        assert failure is not None
        assert failure.get("type") == "high"

    def test_junit_xml_declaration(self, sample_results):
        """Test JUnit output has XML declaration."""
        formatter = JUnitFormatter()
        output = formatter.format(sample_results)

        assert output.startswith('<?xml version="1.0"')

    def test_junit_empty_results(self, empty_results):
        """Test JUnit with no violations."""
        formatter = JUnitFormatter()
        output = formatter.format(empty_results)
        root = ET.fromstring(output)

        testsuite = root.find("testsuite")
        assert testsuite.get("failures") == "0"

    def test_get_extension(self):
        """Test file extension."""
        formatter = JUnitFormatter()
        assert formatter.get_extension() == ".xml"

    def test_name(self):
        """Test formatter name."""
        formatter = JUnitFormatter()
        assert formatter.name == "JUnit"


class TestTableFormatter:
    """Tests for Table formatter."""

    def test_format_returns_string(self, sample_results):
        """Test that format returns a string."""
        formatter = TableFormatter()
        output = formatter.format(sample_results)

        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_includes_scanner_info(self, sample_results):
        """Test that output includes scanner info."""
        formatter = TableFormatter()
        output = formatter.format(sample_results)

        assert "checkov" in output
        assert "2.5.0" in output

    def test_format_includes_violation(self, sample_results):
        """Test that output includes violation info."""
        formatter = TableFormatter()
        output = formatter.format(sample_results)

        # Table may truncate long values, check for partial match
        assert "CKV" in output
        assert "aws_s3_bucket" in output

    def test_format_includes_summary(self, sample_results):
        """Test that output includes summary."""
        formatter = TableFormatter()
        output = formatter.format(sample_results)

        assert "Scan Summary" in output

    def test_max_violations_limit(self, sample_results):
        """Test max violations limit."""
        formatter = TableFormatter(max_violations=0)
        output = formatter.format(sample_results)

        # Should still have summary but limited violations
        assert "Scan Summary" in output

    def test_show_summary_false(self, sample_results):
        """Test hiding summary."""
        formatter = TableFormatter(show_summary=False)
        output = formatter.format(sample_results)

        assert "Scan Summary" not in output

    def test_show_violations_false(self, sample_results):
        """Test hiding violations."""
        formatter = TableFormatter(show_violations=False)
        output = formatter.format(sample_results)

        # Should have summary but no violations table
        assert "Scan Summary" in output

    def test_empty_results(self, empty_results):
        """Test with no violations."""
        formatter = TableFormatter()
        output = formatter.format(empty_results)

        assert "Scan Summary" in output

    def test_get_extension(self):
        """Test file extension."""
        formatter = TableFormatter()
        assert formatter.get_extension() == ".txt"

    def test_name(self):
        """Test formatter name."""
        formatter = TableFormatter()
        assert formatter.name == "Table"


class TestBaseFormatter:
    """Tests for BaseFormatter interface."""

    def test_cannot_instantiate_base_formatter(self):
        """Test that BaseFormatter cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseFormatter()
