"""Tests for scan commands."""

from datetime import datetime
from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.scan import app
from iltero.scanners.models import ScanResults, ScanSummary, ScanType

runner = CliRunner()


class TestScanStatic:
    """Tests for static scan command."""

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_basic(self, mock_orchestrator, tmp_path):
        """Test basic static scan execution."""
        # Create a temporary directory to scan
        test_dir = tmp_path / "terraform"
        test_dir.mkdir()

        # Setup mock
        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        # Create proper ScanResults object
        summary = ScanSummary(
            total_checks=10,
            passed=8,
            failed=2,
            skipped=0,
            critical=0,
            high=2,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="2.3.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            ["static", str(test_dir), "--skip-upload"],
        )

        if result.exit_code != 0:
            print(f"\\nExit code: {result.exit_code}")
            print(f"Output:\\n{result.output}")
            if result.exception:
                import traceback

                traceback.print_exception(
                    type(result.exception),
                    result.exception,
                    result.exception.__traceback__,
                )

        assert result.exit_code == 0
        mock_instance.scan_static.assert_called_once()

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_with_failures(self, mock_orchestrator, tmp_path):
        """Test static scan with policy failures."""
        test_dir = tmp_path / "terraform"
        test_dir.mkdir()

        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        # Create proper ScanResults with failures
        summary = ScanSummary(
            total_checks=10,
            passed=7,
            failed=3,
            skipped=0,
            critical=0,
            high=3,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="2.3.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "3 high violations found",
        )

        result = runner.invoke(
            app,
            [
                "static",
                str(test_dir),
                "--fail-on",
                "high",
                "--skip-upload",
            ],
        )

        # Should exit with failure code
        assert result.exit_code == 1

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_with_stack_id(self, mock_orchestrator, tmp_path):
        """Test static scan with stack ID for backend upload."""
        test_dir = tmp_path / "terraform"
        test_dir.mkdir()

        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        # Create proper ScanResults
        summary = ScanSummary(
            total_checks=5,
            passed=5,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="2.3.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        with patch("iltero.commands.scan.static.upload_results") as mock_upload:
            mock_upload.return_value = True

            result = runner.invoke(
                app,
                [
                    "static",
                    str(test_dir),
                    "--stack-id",
                    "stack-123",
                ],
            )

            assert result.exit_code == 0
            mock_upload.assert_called_once()

    @patch("iltero.commands.scan.static.ScanOrchestrator")
    def test_static_scan_with_output_file(self, mock_orchestrator, tmp_path):
        """Test static scan with output file."""
        test_dir = tmp_path / "terraform"
        test_dir.mkdir()

        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["checkov"]

        # Create proper ScanResults
        summary = ScanSummary(
            total_checks=5,
            passed=5,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="2.3.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_instance.scan_static.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        with patch("iltero.commands.scan.static.save_results") as mock_save:
            result = runner.invoke(
                app,
                [
                    "static",
                    str(test_dir),
                    "--output-file",
                    "results.json",
                    "--skip-upload",
                ],
            )

            assert result.exit_code == 0
            mock_save.assert_called_once()


class TestScanEvaluation:
    """Tests for evaluation scan command."""

    @patch("iltero.commands.scan.evaluation.ScanOrchestrator")
    def test_evaluation_scan_basic(self, mock_orchestrator, tmp_path):
        """Test basic evaluation scan execution."""
        # Create temporary files
        plan_file = tmp_path / "plan.json"
        plan_file.write_text('{"test": "data"}')
        policy_dir = tmp_path / "policies"
        policy_dir.mkdir()

        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["opa"]

        # Create proper ScanResults
        summary = ScanSummary(
            total_checks=10,
            passed=10,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="opa",
            version="0.60.0",
            scan_type=ScanType.EVALUATION,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_instance.scan_plan.return_value = results
        mock_instance.check_thresholds.return_value = (True, "")

        result = runner.invoke(
            app,
            [
                "evaluation",
                str(plan_file),
                "--opa-policy-dir",
                str(policy_dir),
                "--skip-upload",
            ],
        )

        assert result.exit_code == 0
        mock_instance.scan_plan.assert_called_once()

    @patch("iltero.commands.scan.evaluation.ScanOrchestrator")
    def test_evaluation_scan_with_failures(self, mock_orchestrator, tmp_path):
        """Test evaluation scan with policy failures."""
        # Create temporary files
        plan_file = tmp_path / "plan.json"
        plan_file.write_text('{"test": "data"}')
        policy_dir = tmp_path / "policies"
        policy_dir.mkdir()

        mock_instance = Mock()
        mock_orchestrator.return_value = mock_instance
        mock_instance.available_scanners = ["opa"]

        # Create proper ScanResults with failures
        summary = ScanSummary(
            total_checks=10,
            passed=8,
            failed=2,
            skipped=0,
            critical=2,
            high=0,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="opa",
            version="0.60.0",
            scan_type=ScanType.EVALUATION,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_instance.scan_plan.return_value = results
        mock_instance.check_thresholds.return_value = (
            False,
            "2 critical violations found",
        )

        result = runner.invoke(
            app,
            [
                "evaluation",
                str(plan_file),
                "--opa-policy-dir",
                str(policy_dir),
                "--fail-on",
                "critical",
                "--skip-upload",
            ],
        )

        # Should exit with failure code
        assert result.exit_code == 1


class TestScanStatus:
    """Tests for scan status commands."""

    @patch("iltero.commands.scan.status.get_retry_client")
    def test_scan_status(self, mock_get_client):
        """Test getting scan status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "id": "scan-123",
            "status": "completed",
            "summary": {"total": 10, "passed": 8, "failed": 2},
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.scan.status.api_get_scan") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["status", "scan-123"])

            assert result.exit_code == 0
            assert "scan-123" in result.output or "completed" in result.output

    @patch("iltero.commands.scan.status.get_retry_client")
    def test_list_scans(self, mock_get_client):
        """Test listing scans."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "scan-1", "status": "completed"},
            {"id": "scan-2", "status": "running"},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.scan.status.api_list_scans") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["list"])

            assert result.exit_code == 0


class TestUploadResults:
    """Tests for upload_results function."""

    def test_upload_results_success(self):
        """Test successful upload of scan results."""
        from iltero.commands.scan.main import upload_results

        # Create test results
        summary = ScanSummary(
            total_checks=10,
            passed=10,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )
        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="3.0.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        # Patch the imports inside the function
        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_validation_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                # Setup mocks
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                # Call upload_results
                success = upload_results(
                    results=results,
                    stack_id="stack-123",
                    unit="web",
                    environment="development",
                    run_id="run-456",
                    external_run_id="gh-run-789",
                    external_run_url="https://github.com/org/repo/runs/789",
                )

                assert success is True
                mock_sync.assert_called_once()

                # Verify the payload
                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.stack_id == "stack-123"
                assert payload.success is True  # No violations
                assert payload.run_id == "run-456"
                assert payload.external_run_id == "gh-run-789"

    def test_upload_results_with_violations(self):
        """Test upload with critical violations marks success=False."""
        from iltero.commands.scan.main import upload_results

        # Create test results with critical violations
        summary = ScanSummary(
            total_checks=10,
            passed=8,
            failed=2,
            skipped=0,
            critical=2,
            high=0,
            medium=0,
            low=0,
            info=0,
        )
        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="3.0.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_validation_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                # Call upload_results
                success = upload_results(
                    results=results,
                    stack_id="stack-123",
                    unit=None,
                    environment="production",
                )

                assert success is True  # Upload succeeded
                # But payload.success should be False due to violations
                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.success is False  # Critical violations

    def test_upload_results_api_error(self):
        """Test upload handles API errors gracefully."""
        from iltero.commands.scan.main import upload_results

        # Create test results
        summary = ScanSummary(
            total_checks=1,
            passed=1,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )
        now = datetime.now()
        results = ScanResults(
            scanner="checkov",
            version="3.0.0",
            scan_type=ScanType.STATIC,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
            # Setup mocks to raise an exception
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            mock_client.get_authenticated_client.side_effect = Exception("Connection failed")

            # Call upload_results - should return False, not raise
            success = upload_results(
                results=results,
                stack_id="stack-123",
                unit=None,
                environment="development",
            )

            assert success is False


class TestUploadPlanResults:
    """Tests for upload_plan_results function."""

    def test_upload_plan_results_success(self):
        """Test successful upload of plan results."""
        from iltero.commands.scan.main import upload_plan_results

        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_plan_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                # Setup mocks
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                # Call upload_plan_results
                success = upload_plan_results(
                    run_id="run-123",
                    success=True,
                    plan_results={"format_version": "1.1"},
                    plan_summary={"create": 5, "update": 2, "delete": 0},
                    plan_url="https://storage.example.com/plan.json",
                )

                assert success is True
                mock_sync.assert_called_once()

                # Verify the payload
                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.run_id == "run-123"
                assert payload.success is True

    def test_upload_plan_results_with_compliance(self):
        """Test upload plan results with OPA compliance results."""
        from iltero.commands.scan.main import upload_plan_results

        # Create compliance results
        summary = ScanSummary(
            total_checks=5,
            passed=4,
            failed=1,
            skipped=0,
            critical=0,
            high=1,
            medium=0,
            low=0,
            info=0,
        )
        now = datetime.now()
        compliance_results = ScanResults(
            scanner="opa",
            version="0.50.0",
            scan_type=ScanType.EVALUATION,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_plan_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                success = upload_plan_results(
                    run_id="run-456",
                    success=False,  # Plan has violations
                    compliance_results=compliance_results,
                )

                assert success is True
                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.run_id == "run-456"
                assert payload.success is False
                # compliance_results should be set
                assert payload.compliance_results is not None

    def test_upload_plan_results_api_error(self):
        """Test upload handles API errors gracefully."""
        from iltero.commands.scan.main import upload_plan_results

        with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            mock_client.get_authenticated_client.side_effect = Exception("Connection failed")

            success = upload_plan_results(
                run_id="run-789",
                success=True,
            )

            assert success is False


class TestUploadApplyResults:
    """Tests for upload_apply_results function."""

    def test_upload_apply_results_success(self):
        """Test successful upload of apply results."""
        from iltero.commands.scan.main import upload_apply_results

        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_apply_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                success = upload_apply_results(
                    run_id="run-123",
                    success=True,
                    apply_results={
                        "resources_created": 5,
                        "resources_updated": 2,
                        "resources_deleted": 0,
                    },
                )

                assert success is True
                mock_sync.assert_called_once()

                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.run_id == "run-123"
                assert payload.success is True
                assert payload.schedule_drift_detection is False

    def test_upload_apply_results_with_drift_detection(self):
        """Test upload apply results with drift detection scheduling."""
        from iltero.commands.scan.main import upload_apply_results

        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_apply_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                success = upload_apply_results(
                    run_id="run-456",
                    success=True,
                    schedule_drift_detection=True,
                )

                assert success is True
                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.schedule_drift_detection is True

    def test_upload_apply_results_failure(self):
        """Test upload of failed apply results."""
        from iltero.commands.scan.main import upload_apply_results

        with patch(
            "iltero.api_client.iltero_api_client.api.stacks_deployment_webhooks"
            ".webhook_apply_phase.sync_detailed"
        ) as mock_sync:
            with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
                mock_client = Mock()
                mock_get_client.return_value = mock_client
                mock_auth_client = Mock()
                mock_client.get_authenticated_client.return_value = mock_auth_client

                mock_response = Mock()
                mock_response.parsed = Mock()
                mock_client.handle_response.return_value = mock_response.parsed

                mock_sync.return_value = mock_response

                success = upload_apply_results(
                    run_id="run-789",
                    success=False,  # Apply failed
                    apply_results={"error": "Resource quota exceeded"},
                )

                assert success is True  # Upload succeeded
                call_args = mock_sync.call_args
                payload = call_args.kwargs["body"]
                assert payload.success is False  # But apply failed

    def test_upload_apply_results_api_error(self):
        """Test upload handles API errors gracefully."""
        from iltero.commands.scan.main import upload_apply_results

        with patch("iltero.commands.scan.main.get_retry_client") as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            mock_client.get_authenticated_client.side_effect = Exception("Network error")

            success = upload_apply_results(
                run_id="run-000",
                success=True,
            )

            assert success is False


class TestScanRuntime:
    """Tests for runtime scan command."""

    @patch("iltero.commands.scan.runtime.CloudCustodianScanner")
    def test_runtime_scan_basic(self, mock_scanner_class, tmp_path):
        """Test basic runtime scan execution."""
        # Create a policy file
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.is_available.return_value = True

        # Create proper ScanResults
        summary = ScanSummary(
            total_checks=5,
            passed=5,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="cloud-custodian",
            version="0.9.23",
            scan_type=ScanType.RUNTIME,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_scanner.scan.return_value = results

        with patch("iltero.commands.scan.runtime.upload_apply_results") as mock_upload:
            mock_upload.return_value = True

            result = runner.invoke(
                app,
                [
                    "runtime",
                    str(policy_file),
                    "--run-id",
                    "run-123",
                    "--region",
                    "us-east-1",
                ],
            )

            if result.exit_code != 0:
                print(f"Output: {result.output}")
                if result.exception:
                    import traceback

                    traceback.print_exception(
                        type(result.exception),
                        result.exception,
                        result.exception.__traceback__,
                    )

            assert result.exit_code == 0
            mock_scanner.scan.assert_called_once()
            mock_upload.assert_called_once()

    @patch("iltero.commands.scan.runtime.CloudCustodianScanner")
    def test_runtime_scan_not_available(self, mock_scanner_class, tmp_path):
        """Test runtime scan when Custodian not available."""
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.is_available.return_value = False

        result = runner.invoke(
            app,
            [
                "runtime",
                str(policy_file),
                "--run-id",
                "run-123",
            ],
        )

        # Should exit with scanner error
        assert result.exit_code == 4  # EXIT_SCANNER_ERROR

    @patch("iltero.commands.scan.runtime.CloudCustodianScanner")
    def test_runtime_scan_with_violations(self, mock_scanner_class, tmp_path):
        """Test runtime scan with violations."""
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.is_available.return_value = True

        # Create results with violations
        summary = ScanSummary(
            total_checks=5,
            passed=3,
            failed=2,
            skipped=0,
            critical=1,
            high=1,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="cloud-custodian",
            version="0.9.23",
            scan_type=ScanType.RUNTIME,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_scanner.scan.return_value = results

        with patch("iltero.commands.scan.runtime.upload_apply_results") as mock_upload:
            mock_upload.return_value = True

            result = runner.invoke(
                app,
                [
                    "runtime",
                    str(policy_file),
                    "--run-id",
                    "run-123",
                    "--fail-on",
                    "critical",
                ],
            )

            # Should fail due to critical violations
            assert result.exit_code == 1  # EXIT_SCAN_FAILED

    @patch("iltero.commands.scan.runtime.CloudCustodianScanner")
    def test_runtime_scan_with_drift_schedule(self, mock_scanner_class, tmp_path):
        """Test runtime scan with drift detection scheduling."""
        policy_file = tmp_path / "policy.yml"
        policy_file.write_text("policies: []")

        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        mock_scanner.is_available.return_value = True

        summary = ScanSummary(
            total_checks=5,
            passed=5,
            failed=0,
            skipped=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            info=0,
        )

        now = datetime.now()
        results = ScanResults(
            scanner="cloud-custodian",
            version="0.9.23",
            scan_type=ScanType.RUNTIME,
            started_at=now,
            completed_at=now,
            summary=summary,
            violations=[],
            metadata={},
        )

        mock_scanner.scan.return_value = results

        with patch("iltero.commands.scan.runtime.upload_apply_results") as mock_upload:
            mock_upload.return_value = True

            result = runner.invoke(
                app,
                [
                    "runtime",
                    str(policy_file),
                    "--run-id",
                    "run-123",
                    "--schedule-drift",
                ],
            )

            assert result.exit_code == 0
            # Verify schedule_drift_detection was passed
            call_kwargs = mock_upload.call_args.kwargs
            assert call_kwargs["schedule_drift_detection"] is True
