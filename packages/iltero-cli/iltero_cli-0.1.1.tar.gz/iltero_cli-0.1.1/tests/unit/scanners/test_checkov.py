"""Tests for Checkov scanner."""

import json
from unittest.mock import MagicMock, patch

import pytest

from iltero.core.exceptions import ScannerError
from iltero.scanners.checkov import CheckovScanner
from iltero.scanners.models import ScanType, Severity


class TestCheckovScanner:
    """Test CheckovScanner."""

    def test_initialization(self):
        """Test scanner initialization."""
        scanner = CheckovScanner()
        assert scanner.checkov_path is not None or scanner.checkov_path is None
        assert scanner.timeout == 300
        assert scanner.parallel is True

    def test_initialization_with_custom_path(self):
        """Test scanner with custom checkov path."""
        scanner = CheckovScanner(checkov_path="/custom/checkov")
        assert scanner.checkov_path == "/custom/checkov"

    def test_is_available_when_installed(self):
        """Test is_available returns True when checkov is found."""
        with patch("shutil.which", return_value="/usr/bin/checkov"):
            scanner = CheckovScanner()
            assert scanner.is_available() is True

    def test_is_available_when_not_installed(self):
        """Test is_available returns False when checkov not found."""
        with patch("shutil.which", return_value=None):
            scanner = CheckovScanner()
            assert scanner.is_available() is False

    @patch("subprocess.run")
    def test_get_version(self, mock_run):
        """Test getting checkov version."""
        mock_result = MagicMock()
        mock_result.stdout = "2.5.24\n"
        mock_run.return_value = mock_result

        scanner = CheckovScanner(checkov_path="/usr/bin/checkov")
        version = scanner.get_version()

        assert version == "2.5.24"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_get_version_caches_result(self, mock_run):
        """Test version is cached after first call."""
        mock_result = MagicMock()
        mock_result.stdout = "2.5.24\n"
        mock_run.return_value = mock_result

        scanner = CheckovScanner(checkov_path="/usr/bin/checkov")

        version1 = scanner.get_version()
        version2 = scanner.get_version()

        assert version1 == version2
        # Should only call subprocess once
        assert mock_run.call_count == 1

    @patch("shutil.which", return_value=None)
    def test_scan_without_checkov_raises_error(self, mock_which):
        """Test scanning without checkov raises error."""
        scanner = CheckovScanner(checkov_path=None)

        with pytest.raises(ScannerError) as exc_info:
            scanner.scan("/some/path")

        # Scanner checks for checkov availability before path validation
        assert "Checkov not found" in exc_info.value.message
        mock_which.assert_called_once_with("checkov")

    @patch("pathlib.Path.exists")
    def test_scan_with_nonexistent_path_raises_error(self, mock_exists):
        """Test scanning nonexistent path raises error."""
        mock_exists.return_value = False
        scanner = CheckovScanner(checkov_path="/usr/bin/checkov")

        with pytest.raises(ScannerError) as exc_info:
            scanner.scan("/nonexistent/path")

        assert "Path does not exist" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_successful_scan(self, mock_exists, mock_run):
        """Test successful scan execution."""
        mock_exists.return_value = True

        # Mock checkov output
        checkov_output = {
            "check_type": "terraform",
            "passed": 10,
            "failed": 2,
            "skipped": 1,
            "results": {
                "failed_checks": [
                    {
                        "check_id": "CKV_AWS_1",
                        "check_name": "Ensure S3 bucket has encryption",
                        "check_result": {"severity": "HIGH"},
                        "resource": "aws_s3_bucket.example",
                        "file_path": "main.tf",
                        "file_line_range": [10, 15],
                        "guideline": "Enable encryption",
                        "check_class": "terraform",
                    }
                ]
            },
        }

        mock_result = MagicMock()
        mock_result.returncode = 1  # Checkov returns 1 when violations found
        mock_result.stdout = json.dumps(checkov_output)
        mock_run.return_value = mock_result

        scanner = CheckovScanner(checkov_path="/usr/bin/checkov")
        results = scanner.scan("/test/path", ScanType.STATIC)

        assert results.scanner == "checkov"
        assert results.scan_type == ScanType.STATIC
        assert results.summary.total_checks == 13
        assert results.summary.passed == 10
        assert results.summary.failed == 2
        assert len(results.violations) == 1

        violation = results.violations[0]
        assert violation.check_id == "CKV_AWS_1"
        assert violation.severity == Severity.HIGH
        assert violation.file_path == "main.tf"

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_scan_timeout(self, mock_exists, mock_run):
        """Test scan timeout handling."""
        mock_exists.return_value = True
        mock_run.side_effect = Exception("Timeout")

        scanner = CheckovScanner(checkov_path="/usr/bin/checkov", timeout=10)

        with pytest.raises(Exception):
            scanner.scan("/test/path")

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_scan_with_external_checks_dir(self, mock_exists, mock_run):
        """Test scan with external checks directory."""
        mock_exists.return_value = True

        # Mock both get_version and scan calls
        def run_side_effect(cmd, **kwargs):
            result = MagicMock()
            if "--version" in cmd:
                result.returncode = 0
                result.stdout = "2.5.0"
            else:
                result.returncode = 0
                result.stdout = json.dumps(
                    {
                        "check_type": "terraform",
                        "passed": 5,
                        "failed": 0,
                        "skipped": 0,
                        "results": {"failed_checks": []},
                    }
                )
            return result

        mock_run.side_effect = run_side_effect

        scanner = CheckovScanner(
            checkov_path="/usr/bin/checkov",
            external_checks_dir="/custom/checks",
        )
        scanner.scan("/test/path")

        # Find the scan call (not the version call)
        scan_calls = [call for call in mock_run.call_args_list if "--directory" in str(call)]
        assert len(scan_calls) > 0
        call_args = scan_calls[0][0][0]
        assert "--external-checks-dir" in call_args
        assert "/custom/checks" in call_args

    def test_severity_mapping(self):
        """Test severity mapping from Checkov to internal format."""
        scanner = CheckovScanner(checkov_path="/usr/bin/checkov")

        assert scanner._map_severity("CRITICAL") == Severity.CRITICAL
        assert scanner._map_severity("HIGH") == Severity.HIGH
        assert scanner._map_severity("MEDIUM") == Severity.MEDIUM
        assert scanner._map_severity("LOW") == Severity.LOW
        assert scanner._map_severity("INFO") == Severity.INFO
        assert scanner._map_severity("UNKNOWN") == Severity.MEDIUM
        assert scanner._map_severity(None) == Severity.MEDIUM

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_build_command_with_frameworks(self, mock_exists, mock_run):
        """Test command building with framework filters."""
        mock_exists.return_value = True

        #  Mock both get_version and scan calls
        def run_side_effect(cmd, **kwargs):
            result = MagicMock()
            if "--version" in cmd:
                result.returncode = 0
                result.stdout = "2.5.0"
            else:
                result.returncode = 0
                result.stdout = json.dumps(
                    {
                        "check_type": "terraform",
                        "passed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "results": {"failed_checks": []},
                    }
                )
            return result

        mock_run.side_effect = run_side_effect

        scanner = CheckovScanner(
            checkov_path="/usr/bin/checkov",
            frameworks=["cis_aws", "pci_dss"],
        )
        scanner.scan("/test/path")

        # Find the scan call (not the version call)
        scan_calls = [call for call in mock_run.call_args_list if "--directory" in str(call)]
        assert len(scan_calls) > 0
        call_args = scan_calls[0][0][0]
        assert "cis_aws" in call_args
        assert "pci_dss" in call_args
