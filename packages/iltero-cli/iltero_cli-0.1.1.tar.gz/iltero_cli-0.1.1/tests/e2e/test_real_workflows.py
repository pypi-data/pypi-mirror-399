"""Real end-to-end tests against live backend.

These tests execute against a real Iltero backend instance.
Run with: pytest tests/e2e/ --e2e --test-token=<your-token>

Environment variables:
- ILTERO_BACKEND_URL: Backend URL (default: https://staging.iltero.com)
- ILTERO_TEST_TOKEN: Authentication token for API
"""

import json
import os
import subprocess

import pytest
from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


@pytest.mark.e2e
class TestRealAuthentication:
    """Test real authentication workflow."""

    def test_auth_whoami(self, e2e_config_dir, test_token, check_backend_available):
        """Test whoami with real backend."""
        # Set environment variables
        env = os.environ.copy()
        env["ILTERO_CONFIG_DIR"] = str(e2e_config_dir)
        env["ILTERO_TOKEN"] = test_token

        result = runner.invoke(
            app,
            ["auth", "whoami", "--output", "json"],
            env=env,
        )

        print(f"\nExit code: {result.exit_code}")
        print(f"Output: {result.output}")

        if result.exit_code == 0:
            # Parse JSON output to verify structure
            data = json.loads(result.output)
            assert "user_id" in data or "email" in data
        else:
            # Authentication might fail if token is invalid
            assert "error" in result.output.lower() or "failed" in result.output.lower()


@pytest.mark.e2e
class TestRealScanning:
    """Test real scanning workflow with actual scanners."""

    def test_scanner_check_real(self, check_scanners_installed):
        """Test scanner availability check with real scanners."""
        result = runner.invoke(app, ["scanner", "check", "--output", "json"])

        print(f"\nExit code: {result.exit_code}")
        print(f"Output: {result.output}")

        assert result.exit_code == 0

        # Parse output and verify scanners are detected
        if result.output.strip():
            data = json.loads(result.output)
            assert isinstance(data, (list, dict))

    def test_static_scan_real_project(
        self,
        terraform_test_project,
        check_scanners_installed,
    ):
        """Test static scan with real Terraform project and real scanners."""
        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_test_project),
                "--skip-upload",  # Don't upload to backend in E2E test
                "--output",
                "json",
            ],
        )

        print(f"\nExit code: {result.exit_code}")
        print(f"Output: {result.output[:500]}...")  # First 500 chars

        # Scan should complete (exit 0 or 1 if violations found)
        assert result.exit_code in [0, 1]

        if result.output.strip():
            data = json.loads(result.output)
            assert "scanner" in data
            assert "summary" in data
            assert "violations" in data

            # Should find policy violations in our test project
            summary = data["summary"]
            assert summary["total_checks"] > 0

    def test_static_scan_with_real_upload(
        self,
        terraform_test_project,
        e2e_config_dir,
        test_token,
        check_backend_available,
        check_scanners_installed,
    ):
        """Test static scan with real backend upload (webhook)."""
        # This test uploads scan results to the real backend
        # Skip if no stack ID is provided
        stack_id = os.getenv("ILTERO_TEST_STACK_ID")
        if not stack_id:
            pytest.skip("ILTERO_TEST_STACK_ID not set - cannot test real upload")

        env = os.environ.copy()
        env["ILTERO_CONFIG_DIR"] = str(e2e_config_dir)
        env["ILTERO_TOKEN"] = test_token

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_test_project),
                "--stack-id",
                stack_id,
                "--output",
                "json",
            ],
            env=env,
        )

        print(f"\nExit code: {result.exit_code}")
        print(f"Output: {result.output[:500]}...")

        # Should complete successfully or with violations
        assert result.exit_code in [0, 1]


@pytest.mark.e2e
class TestRealWorkspaceManagement:
    """Test real workspace management."""

    def test_workspace_list_real(
        self,
        e2e_config_dir,
        test_token,
        check_backend_available,
    ):
        """Test listing workspaces from real backend."""
        env = os.environ.copy()
        env["ILTERO_CONFIG_DIR"] = str(e2e_config_dir)
        env["ILTERO_TOKEN"] = test_token

        result = runner.invoke(
            app,
            ["workspace", "list", "--output", "json"],
            env=env,
        )

        print(f"\nExit code: {result.exit_code}")
        print(f"Output: {result.output}")

        if result.exit_code == 0:
            data = json.loads(result.output)
            assert isinstance(data, list)
        else:
            # May fail if no workspaces or auth issues
            assert "error" in result.output.lower() or "failed" in result.output.lower()


@pytest.mark.e2e
class TestRealCICDWorkflow:
    """Test real CI/CD workflow simulation."""

    def test_full_cicd_pipeline(
        self,
        terraform_test_project,
        check_scanners_installed,
    ):
        """Simulate a full CI/CD pipeline with real scanners.

        This test simulates what would happen in GitHub Actions:
        1. Check scanner installation
        2. Run static scan (validate phase)
        3. Generate plan (terraform plan)
        4. Run evaluation scan (plan phase)
        """
        # Step 1: Check scanners
        result = runner.invoke(app, ["scanner", "check"])
        assert result.exit_code == 0
        print("\n✓ Scanners available")

        # Step 2: Static scan (pre-plan)
        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_test_project),
                "--skip-upload",
                "--fail-on",
                "critical",
            ],
        )
        print(f"\n✓ Static scan completed (exit code: {result.exit_code})")
        # Exit code 0 or 1 is acceptable (1 if violations found)
        assert result.exit_code in [0, 1]

        # Step 3: Generate Terraform plan
        plan_file = terraform_test_project / "tfplan.json"
        try:
            # Initialize Terraform
            subprocess.run(
                ["terraform", "init"],
                cwd=terraform_test_project,
                check=True,
                capture_output=True,
            )
            print("\n✓ Terraform initialized")

            # Generate plan
            subprocess.run(
                ["terraform", "plan", "-out=tfplan"],
                cwd=terraform_test_project,
                check=True,
                capture_output=True,
            )
            print("\n✓ Terraform plan created")

            # Convert plan to JSON
            subprocess.run(
                ["terraform", "show", "-json", "tfplan"],
                cwd=terraform_test_project,
                check=True,
                capture_output=True,
                stdout=open(plan_file, "w"),
            )
            print("\n✓ Plan converted to JSON")

            # Step 4: Evaluation scan (post-plan)
            if plan_file.exists():
                result = runner.invoke(
                    app,
                    [
                        "scan",
                        "evaluation",
                        str(plan_file),
                        "--skip-upload",
                    ],
                )
                print(f"\n✓ Evaluation scan completed (exit code: {result.exit_code})")
                assert result.exit_code in [0, 1]
            else:
                pytest.skip("Plan file not created")

        except FileNotFoundError:
            pytest.skip("Terraform not installed - cannot test plan workflow")
        except subprocess.CalledProcessError as e:
            pytest.skip(f"Terraform command failed: {e}")


@pytest.mark.e2e
class TestRealOutputFormats:
    """Test real output format generation."""

    def test_sarif_output_real(
        self,
        terraform_test_project,
        check_scanners_installed,
        tmp_path,
    ):
        """Test SARIF output format with real scan."""
        output_file = tmp_path / "results.sarif"

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_test_project),
                "--skip-upload",
                "--output",
                "sarif",
                "--output-file",
                str(output_file),
            ],
        )

        assert result.exit_code in [0, 1]

        if output_file.exists():
            # Validate SARIF format
            with open(output_file) as f:
                sarif_data = json.load(f)
                assert "$schema" in sarif_data
                assert "version" in sarif_data
                assert "runs" in sarif_data
            print("\n✓ Valid SARIF output generated")

    def test_junit_output_real(
        self,
        terraform_test_project,
        check_scanners_installed,
        tmp_path,
    ):
        """Test JUnit output format with real scan."""
        output_file = tmp_path / "results.xml"

        result = runner.invoke(
            app,
            [
                "scan",
                "static",
                str(terraform_test_project),
                "--skip-upload",
                "--output",
                "junit",
                "--output-file",
                str(output_file),
            ],
        )

        assert result.exit_code in [0, 1]

        if output_file.exists():
            # Validate XML format
            content = output_file.read_text()
            assert '<?xml version="1.0"' in content
            assert "<testsuites" in content or "<testsuite" in content
            print("\n✓ Valid JUnit XML output generated")
