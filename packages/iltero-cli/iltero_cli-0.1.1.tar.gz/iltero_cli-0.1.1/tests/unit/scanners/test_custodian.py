"""Tests for Cloud Custodian scanner."""

from unittest.mock import Mock, patch

import pytest

from iltero.scanners.custodian import CloudCustodianScanner
from iltero.scanners.models import Severity


class TestCloudCustodianScanner:
    """Tests for CloudCustodianScanner."""

    def test_scanner_initialization(self):
        """Test scanner initializes with defaults."""
        scanner = CloudCustodianScanner()
        assert scanner.cloud_provider == "aws"
        assert scanner.timeout == 300
        assert scanner.region is None

    def test_scanner_initialization_with_options(self):
        """Test scanner initializes with custom options."""
        scanner = CloudCustodianScanner(
            cloud_provider="azure",
            region="eastus",
            timeout=600,
        )
        assert scanner.cloud_provider == "azure"
        assert scanner.region == "eastus"
        assert scanner.timeout == 600

    @patch("shutil.which")
    def test_is_available_when_installed(self, mock_which):
        """Test is_available returns True when custodian is installed."""
        mock_which.return_value = "/usr/local/bin/custodian"
        scanner = CloudCustodianScanner()
        assert scanner.is_available() is True

    @patch("shutil.which")
    def test_is_available_when_not_installed(self, mock_which):
        """Test is_available returns False when custodian not installed."""
        mock_which.return_value = None
        scanner = CloudCustodianScanner()
        assert scanner.is_available() is False

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_get_version(self, mock_which, mock_run):
        """Test get_version returns correct version."""
        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.return_value = Mock(
            stdout="custodian 0.9.23",
            returncode=0,
        )

        scanner = CloudCustodianScanner()
        version = scanner.get_version()

        assert version == "0.9.23"

    @patch("shutil.which")
    def test_get_version_when_not_installed(self, mock_which):
        """Test get_version returns unknown when not installed."""
        mock_which.return_value = None
        scanner = CloudCustodianScanner()
        assert scanner.get_version() == "unknown"

    def test_collect_policy_files_single_file(self, tmp_path):
        """Test collecting policies from a single file."""
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        scanner = CloudCustodianScanner()
        files = scanner._collect_policy_files(policy_file)

        assert len(files) == 1
        assert files[0] == policy_file

    def test_collect_policy_files_directory(self, tmp_path):
        """Test collecting policies from a directory."""
        (tmp_path / "policy1.yml").write_text("policies: []")
        (tmp_path / "policy2.yaml").write_text("policies: []")
        (tmp_path / "not_a_policy.txt").write_text("test")

        scanner = CloudCustodianScanner()
        files = scanner._collect_policy_files(tmp_path)

        assert len(files) == 2
        assert all(f.suffix in (".yml", ".yaml") for f in files)

    def test_severity_mapping(self):
        """Test severity mapping from Custodian to internal."""
        scanner = CloudCustodianScanner()

        assert scanner.SEVERITY_MAP["critical"] == Severity.CRITICAL
        assert scanner.SEVERITY_MAP["high"] == Severity.HIGH
        assert scanner.SEVERITY_MAP["medium"] == Severity.MEDIUM
        assert scanner.SEVERITY_MAP["low"] == Severity.LOW
        assert scanner.SEVERITY_MAP["info"] == Severity.INFO

    def test_resource_to_violation(self, tmp_path):
        """Test converting a resource to violation."""
        scanner = CloudCustodianScanner()

        resource = {
            "ResourceId": "sg-12345678",
            "GroupName": "my-security-group",
        }

        policy = {
            "name": "sg-open-to-world",
            "resource": "security-group",
            "description": "Security group open to 0.0.0.0/0",
            "metadata": {
                "severity": "high",
                "remediation": "Restrict ingress rules",
            },
        }

        policy_file = tmp_path / "policy.yml"

        violation = scanner._resource_to_violation(resource, policy, policy_file)

        assert violation.check_id == "sg-open-to-world"
        assert violation.severity == Severity.HIGH
        assert "sg-12345678" in violation.resource
        assert violation.remediation == "Restrict ingress rules"

    def test_build_summary(self):
        """Test building summary from violations."""
        from iltero.scanners.models import Violation

        scanner = CloudCustodianScanner()

        violations = [
            Violation(
                check_id="test1",
                check_name="Test 1",
                severity=Severity.CRITICAL,
                resource="r1",
                file_path="p1.yml",
                line_range=(0, 0),
                description="desc",
            ),
            Violation(
                check_id="test2",
                check_name="Test 2",
                severity=Severity.HIGH,
                resource="r2",
                file_path="p2.yml",
                line_range=(0, 0),
                description="desc",
            ),
            Violation(
                check_id="test3",
                check_name="Test 3",
                severity=Severity.HIGH,
                resource="r3",
                file_path="p3.yml",
                line_range=(0, 0),
                description="desc",
            ),
        ]

        summary = scanner._build_summary(violations, 10, 7)

        assert summary.total_checks == 10
        assert summary.passed == 7
        assert summary.failed == 3
        assert summary.critical == 1
        assert summary.high == 2
        assert summary.medium == 0

    @patch("shutil.which")
    def test_scan_raises_when_not_available(self, mock_which, tmp_path):
        """Test scan raises error when Custodian not installed."""
        mock_which.return_value = None

        scanner = CloudCustodianScanner()
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        with pytest.raises(Exception) as exc_info:
            scanner.scan(str(policy_file))

        assert "not found" in str(exc_info.value).lower()

    @patch("shutil.which")
    def test_scan_raises_when_path_not_exists(self, mock_which):
        """Test scan raises error when policy path doesn't exist."""
        mock_which.return_value = "/usr/local/bin/custodian"

        scanner = CloudCustodianScanner()

        with pytest.raises(Exception) as exc_info:
            scanner.scan("/nonexistent/path/policy.yml")

        assert "does not exist" in str(exc_info.value).lower()

    @patch("shutil.which")
    def test_scan_raises_when_no_policy_files(self, mock_which, tmp_path):
        """Test scan raises error when no policy files found."""
        mock_which.return_value = "/usr/local/bin/custodian"

        scanner = CloudCustodianScanner()
        # Create directory with no YAML files
        (tmp_path / "not_a_policy.txt").write_text("test")

        with pytest.raises(Exception) as exc_info:
            scanner.scan(str(tmp_path))

        assert "no policy files" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_custodian_with_region(self, mock_which, mock_run, tmp_path):
        """Test _run_custodian includes region flag."""
        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        scanner = CloudCustodianScanner(region="us-west-2")
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        scanner._run_custodian(policy_file, tmp_path)

        # Check that region was passed
        call_args = mock_run.call_args[0][0]
        assert "--region" in call_args
        assert "us-west-2" in call_args

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_custodian_timeout(self, mock_which, mock_run, tmp_path):
        """Test _run_custodian handles timeout."""
        import subprocess

        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="custodian", timeout=300)

        scanner = CloudCustodianScanner()
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        with pytest.raises(Exception) as exc_info:
            scanner._run_custodian(policy_file, tmp_path)

        assert "timed out" in str(exc_info.value).lower()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_parse_results_with_violations(self, mock_which, mock_run, tmp_path):
        """Test _parse_results correctly parses violations."""
        import json

        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        scanner = CloudCustodianScanner()

        # Create policy file
        policy_file = tmp_path / "policy.yml"
        policy_content = """
policies:
  - name: test-policy
    resource: ec2
    description: Test policy
    metadata:
      severity: high
"""
        policy_file.write_text(policy_content)

        # Create output directory with resources.json
        policy_output_dir = tmp_path / "test-policy"
        policy_output_dir.mkdir()
        resources_file = policy_output_dir / "resources.json"
        resources_file.write_text(
            json.dumps([{"InstanceId": "i-12345", "InstanceType": "t2.micro"}])
        )

        violations, total, passed = scanner._parse_results(
            mock_run.return_value, policy_file, tmp_path
        )

        assert len(violations) == 1
        assert total == 1
        assert passed == 0

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_parse_results_no_violations(self, mock_which, mock_run, tmp_path):
        """Test _parse_results with no violations (empty resources)."""
        import json

        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        scanner = CloudCustodianScanner()

        # Create policy file
        policy_file = tmp_path / "policy.yml"
        policy_content = """
policies:
  - name: compliant-policy
    resource: ec2
    description: Compliant policy
"""
        policy_file.write_text(policy_content)

        # Create output directory with empty resources.json
        policy_output_dir = tmp_path / "compliant-policy"
        policy_output_dir.mkdir()
        resources_file = policy_output_dir / "resources.json"
        resources_file.write_text(json.dumps([]))

        violations, total, passed = scanner._parse_results(
            mock_run.return_value, policy_file, tmp_path
        )

        assert len(violations) == 0
        assert total == 1
        assert passed == 1

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_full_scan_success(self, mock_which, mock_run, tmp_path):
        """Test full scan workflow with successful execution."""
        import json

        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.return_value = Mock(
            returncode=0,
            stdout="custodian 0.9.23",
            stderr="",
        )

        scanner = CloudCustodianScanner(cloud_provider="aws", region="us-east-1")

        # Create policy file
        policy_file = tmp_path / "policy.yml"
        policy_content = """
policies:
  - name: s3-encryption
    resource: s3
    description: Ensure S3 buckets are encrypted
    metadata:
      severity: high
      remediation: Enable default encryption
"""
        policy_file.write_text(policy_content)

        # Create output with violation
        policy_output_dir = tmp_path / "s3-encryption"
        policy_output_dir.mkdir()
        resources_file = policy_output_dir / "resources.json"
        resources_file.write_text(
            json.dumps(
                [{"Name": "unencrypted-bucket", "BucketArn": "arn:aws:s3:::unencrypted-bucket"}]
            )
        )

        # Mock the scan to use our tmp_path as output
        scanner.output_dir = tmp_path

        results = scanner.scan(str(policy_file))

        assert results.scanner == "cloud-custodian"
        assert len(results.violations) == 1
        assert results.violations[0].severity == Severity.HIGH
        assert results.metadata["cloud_provider"] == "aws"
        assert results.metadata["region"] == "us-east-1"

    def test_collect_policy_files_nested_directory(self, tmp_path):
        """Test collecting policies from nested directories."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root_policy.yml").write_text("policies: []")
        (subdir / "nested_policy.yaml").write_text("policies: []")

        scanner = CloudCustodianScanner()
        files = scanner._collect_policy_files(tmp_path)

        assert len(files) == 2

    def test_collect_policy_files_non_yaml(self, tmp_path):
        """Test that non-YAML files are ignored."""
        (tmp_path / "policy.json").write_text("{}")
        (tmp_path / "policy.txt").write_text("test")

        scanner = CloudCustodianScanner()
        files = scanner._collect_policy_files(tmp_path)

        assert len(files) == 0

    def test_resource_to_violation_with_arn(self, tmp_path):
        """Test resource to violation with ARN identifier."""
        scanner = CloudCustodianScanner()

        resource = {
            "Arn": "arn:aws:s3:::my-bucket",
            "Name": "my-bucket",
        }

        policy = {
            "name": "s3-public-access",
            "resource": "s3",
            "description": "S3 bucket has public access",
        }

        policy_file = tmp_path / "policy.yml"

        violation = scanner._resource_to_violation(resource, policy, policy_file)

        # Resource is formatted as {resource_type}/{name}
        assert "s3/my-bucket" in violation.resource
        # ARN is stored in metadata
        assert violation.metadata["resource_data"]["Arn"] == ("arn:aws:s3:::my-bucket")

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_get_version_timeout(self, mock_which, mock_run):
        """Test get_version handles timeout gracefully."""
        import subprocess

        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="custodian", timeout=10)

        scanner = CloudCustodianScanner()
        version = scanner.get_version()

        assert version == "unknown"

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_get_version_empty_output(self, mock_which, mock_run):
        """Test get_version with empty output."""
        mock_which.return_value = "/usr/local/bin/custodian"
        mock_run.return_value = Mock(stdout="", returncode=0)

        scanner = CloudCustodianScanner()
        version = scanner.get_version()

        assert version == "unknown"
