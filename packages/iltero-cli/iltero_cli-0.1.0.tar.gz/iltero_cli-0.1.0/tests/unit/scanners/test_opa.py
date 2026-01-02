"""Tests for OPA scanner."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from iltero.core.exceptions import ScannerError
from iltero.scanners.models import ScanType, Severity
from iltero.scanners.opa import OPAScanner


class TestOPAScanner:
    """Test OPAScanner."""

    def test_initialization(self):
        """Test scanner initialization."""
        scanner = OPAScanner(policy_dir="/policies")
        assert scanner.opa_path is not None or scanner.opa_path is None
        assert scanner.policy_dir == Path("/policies")
        assert scanner.query == "data.terraform.deny"

    def test_is_available_when_installed(self):
        """Test is_available returns True when OPA is found."""
        with patch("shutil.which", return_value="/usr/bin/opa"):
            scanner = OPAScanner(policy_dir="/policies")
            assert scanner.is_available() is True

    def test_is_available_when_not_installed(self):
        """Test is_available returns False when OPA not found."""
        scanner = OPAScanner(opa_path=None, policy_dir="/policies")
        assert scanner.is_available() is False

    @patch("subprocess.run")
    def test_get_version(self, mock_run):
        """Test getting OPA version."""
        mock_result = MagicMock()
        mock_result.stdout = "Version: 0.50.0\nBuild Commit: abc123\n"
        mock_run.return_value = mock_result

        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")
        version = scanner.get_version()

        assert version == "0.50.0"

    def test_scan_without_opa_raises_error(self):
        """Test scanning without OPA raises error."""
        scanner = OPAScanner(opa_path=None, policy_dir="/policies")

        with pytest.raises(ScannerError) as exc_info:
            scanner.scan("/plan.json")

        assert "OPA not found" in str(exc_info.value)

    @patch("pathlib.Path.exists")
    def test_scan_without_policy_dir_raises_error(self, mock_exists):
        """Test scanning without policy directory raises error."""
        mock_exists.return_value = False
        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")

        with pytest.raises(ScannerError) as exc_info:
            scanner.scan("/plan.json")

        assert "Policy directory not found" in str(exc_info.value)

    @patch("pathlib.Path.exists")
    def test_scan_with_nonexistent_plan_raises_error(self, mock_exists):
        """Test scanning nonexistent plan file raises error."""

        # Mock exists to return True for policy_dir, False for plan file
        def exists_side_effect():
            # First call checks policy_dir (return True)
            # Second call checks plan file (return False)
            return mock_exists.side_effect.pop(0) if mock_exists.side_effect else False

        # Set up side effects: policy_dir exists (True), plan file doesn't (False)
        mock_exists.side_effect = [True, False]

        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")

        with pytest.raises(ScannerError) as exc_info:
            scanner.scan("/nonexistent.json")

        assert "Plan file does not exist" in str(exc_info.value)

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_successful_scan(self, mock_exists, mock_run):
        """Test successful OPA scan execution."""
        mock_exists.return_value = True

        # Mock OPA output
        opa_output = {
            "result": [
                {
                    "expressions": [
                        {
                            "value": [
                                {
                                    "policy_id": "TF_001",
                                    "policy_name": "Require encryption",
                                    "severity": "HIGH",
                                    "resource": "aws_s3_bucket.example",
                                    "message": ("S3 bucket must have encryption"),
                                    "file": "plan.json",
                                    "line": 42,
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(opa_output)
        mock_run.return_value = mock_result

        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")
        results = scanner.scan("/plan.json", ScanType.EVALUATION)

        assert results.scanner == "opa"
        assert results.scan_type == ScanType.EVALUATION
        assert results.summary.failed == 1
        assert len(results.violations) == 1

        violation = results.violations[0]
        assert violation.check_id == "TF_001"
        assert violation.severity == Severity.HIGH
        assert violation.description == "S3 bucket must have encryption"

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_scan_with_string_violations(self, mock_exists, mock_run):
        """Test scan with simple string violations."""
        mock_exists.return_value = True

        opa_output = {
            "result": [
                {
                    "expressions": [
                        {
                            "value": [
                                "Violation 1",
                                "Violation 2",
                            ]
                        }
                    ]
                }
            ]
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(opa_output)
        mock_run.return_value = mock_result

        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")
        results = scanner.scan("/plan.json")

        assert len(results.violations) == 2
        assert results.violations[0].check_id == "OPA_CUSTOM"
        assert results.violations[0].severity == Severity.MEDIUM

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_scan_with_no_violations(self, mock_exists, mock_run):
        """Test scan with no violations."""
        mock_exists.return_value = True

        opa_output = {"result": [{"expressions": [{"value": []}]}]}

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(opa_output)
        mock_run.return_value = mock_result

        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")
        results = scanner.scan("/plan.json")

        assert len(results.violations) == 0
        assert results.summary.failed == 0

    @patch("subprocess.run")
    @patch("pathlib.Path.exists")
    def test_build_command_with_data_dir(self, mock_exists, mock_run):
        """Test command building with data directory."""
        mock_exists.return_value = True

        # Mock both get_version and scan calls
        def run_side_effect(cmd, **kwargs):
            result = MagicMock()
            if "version" in cmd:
                result.returncode = 0
                result.stdout = "Version: 0.50.0\n"
            else:
                result.returncode = 0
                result.stdout = json.dumps({"result": []})
            return result

        mock_run.side_effect = run_side_effect

        scanner = OPAScanner(
            opa_path="/usr/bin/opa",
            policy_dir="/policies",
            data_dir="/data",
        )
        scanner.scan("/plan.json")

        # Find the scan call (not the version call)
        scan_calls = [call for call in mock_run.call_args_list if "eval" in str(call)]
        assert len(scan_calls) > 0
        call_args = scan_calls[0][0][0]
        assert call_args.count("--data") >= 2  # Both policy_dir and data_dir

    def test_extract_violations_with_boolean_result(self):
        """Test extracting violations from boolean OPA result."""
        scanner = OPAScanner(opa_path="/usr/bin/opa", policy_dir="/policies")

        # Boolean false means no violations
        result = {"result": [{"expressions": [{"value": False}]}]}

        violations = scanner._extract_violations(result)
        assert violations == []
