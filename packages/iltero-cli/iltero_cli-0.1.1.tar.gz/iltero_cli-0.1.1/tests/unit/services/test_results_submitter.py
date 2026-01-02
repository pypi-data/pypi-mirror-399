"""Tests for ScanResultsSubmitter service."""

from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from iltero.scanners.models import ScanResults, ScanSummary, ScanType, Severity, Violation
from iltero.services.models import PolicyResolutionProvenance
from iltero.services.results_submitter import (
    ScanResultsSubmissionError,
    ScanResultsSubmitter,
)


class TestScanResultsSubmissionError:
    """Test ScanResultsSubmissionError exception."""

    def test_error_message(self):
        """Test error message formatting."""
        error = ScanResultsSubmissionError(
            scan_id="scan-123",
            message="Connection failed",
        )

        assert "scan-123" in str(error)
        assert "Connection failed" in str(error)
        assert error.exit_code == 12

    def test_error_with_status_code(self):
        """Test error with status code."""
        error = ScanResultsSubmissionError(
            scan_id="scan-456",
            message="Not found",
            status_code=404,
        )

        assert error.status_code == 404


class TestScanResultsSubmitter:
    """Test ScanResultsSubmitter class."""

    def _create_sample_scan_results(self) -> ScanResults:
        """Create sample scan results for testing."""
        return ScanResults(
            scanner="checkov",
            version="3.0.0",
            scan_type=ScanType.STATIC,
            started_at=datetime(2024, 12, 27, 10, 0, 0, tzinfo=UTC),
            completed_at=datetime(2024, 12, 27, 10, 5, 0, tzinfo=UTC),
            summary=ScanSummary(
                total_checks=100,
                passed=95,
                failed=5,
                skipped=0,
                critical=1,
                high=2,
                medium=2,
                low=0,
                info=0,
            ),
            violations=[
                Violation(
                    check_id="CKV_AWS_1",
                    check_name="S3 encryption",
                    severity=Severity.CRITICAL,
                    resource="aws_s3_bucket.data",
                    file_path="main.tf",
                    line_range=(10, 20),
                    description="S3 bucket not encrypted",
                ),
            ],
        )

    def test_init_without_client(self):
        """Test initialization without client."""
        submitter = ScanResultsSubmitter()
        assert submitter._api_client is None

    def test_init_with_client(self):
        """Test initialization with client."""
        mock_client = Mock()
        submitter = ScanResultsSubmitter(api_client=mock_client)
        assert submitter._api_client == mock_client

    def test_build_scan_results_payload(self):
        """Test building payload from scan results."""
        submitter = ScanResultsSubmitter()
        scan_results = self._create_sample_scan_results()

        payload = submitter._build_scan_results_payload(scan_results)

        assert payload["scanner"] == "checkov"
        assert payload["version"] == "3.0.0"
        assert payload["scan_type"] == "static"
        assert payload["summary"]["total_checks"] == 100
        assert len(payload["violations"]) == 1

    def test_build_scan_results_payload_with_provenance(self):
        """Test building payload with policy resolution provenance."""
        submitter = ScanResultsSubmitter()
        scan_results = self._create_sample_scan_results()

        provenance = PolicyResolutionProvenance(
            manifest_id="m-123",
            manifest_hash="h-456",
            resolved_at="2024-12-27T00:00:00Z",
            bundle_required=["policy1"],
        )

        payload = submitter._build_scan_results_payload(
            scan_results,
            policy_resolution=provenance,
        )

        assert "policy_resolution" in payload
        assert payload["policy_resolution"]["manifest_id"] == "m-123"

    @patch("iltero.services.results_submitter.submit_scan_results")
    @patch("iltero.services.results_submitter.get_retry_client")
    def test_submit_results_success(self, mock_get_client, mock_submit):
        """Test successful results submission."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = Mock()
        mock_response.parsed.to_dict.return_value = {"status": "success"}
        mock_submit.sync_detailed.return_value = mock_response

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        submitter = ScanResultsSubmitter()
        scan_results = self._create_sample_scan_results()

        response = submitter.submit_results(
            scan_id="scan-123",
            scan_results=scan_results,
        )

        assert response == {"status": "success"}
        mock_submit.sync_detailed.assert_called_once()

    @patch("iltero.services.results_submitter.submit_scan_results")
    @patch("iltero.services.results_submitter.get_retry_client")
    def test_submit_results_http_error(self, mock_get_client, mock_submit):
        """Test submission with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_submit.sync_detailed.return_value = mock_response

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        submitter = ScanResultsSubmitter()
        scan_results = self._create_sample_scan_results()

        with pytest.raises(ScanResultsSubmissionError) as exc_info:
            submitter.submit_results(
                scan_id="scan-fail",
                scan_results=scan_results,
            )

        assert exc_info.value.status_code == 500

    @patch("iltero.services.results_submitter.submit_scan_results")
    @patch("iltero.services.results_submitter.get_retry_client")
    def test_submit_results_empty_response(self, mock_get_client, mock_submit):
        """Test submission with empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = None
        mock_submit.sync_detailed.return_value = mock_response

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        submitter = ScanResultsSubmitter()
        scan_results = self._create_sample_scan_results()

        with pytest.raises(ScanResultsSubmissionError) as exc_info:
            submitter.submit_results(
                scan_id="scan-empty",
                scan_results=scan_results,
            )

        assert "Empty response" in str(exc_info.value)

    @patch("iltero.services.results_submitter.submit_scan_results")
    @patch("iltero.services.results_submitter.get_retry_client")
    def test_submit_results_with_metadata(self, mock_get_client, mock_submit):
        """Test submission with all metadata."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = Mock()
        mock_response.parsed.to_dict.return_value = {}
        mock_submit.sync_detailed.return_value = mock_response

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        submitter = ScanResultsSubmitter()
        scan_results = self._create_sample_scan_results()

        submitter.submit_results(
            scan_id="scan-meta",
            scan_results=scan_results,
            scanner_version="3.2.1",
            pipeline_url="https://github.com/org/repo/actions/runs/123",
            commit_sha="abc123def456",
            branch="main",
        )

        # Verify the call was made
        call_args = mock_submit.sync_detailed.call_args
        body = call_args[1]["body"]

        assert body.scanner_version == "3.2.1"
        assert body.pipeline_url == "https://github.com/org/repo/actions/runs/123"
        assert body.commit_sha == "abc123def456"
        assert body.branch == "main"

    @patch("iltero.services.results_submitter.submit_scan_results")
    @patch("iltero.services.results_submitter.get_retry_client")
    def test_submit_and_save(self, mock_get_client, mock_submit):
        """Test submit_and_save updates run state."""
        import tempfile
        from pathlib import Path

        from iltero.services.state_manager import ScanRunState

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = Mock()
        mock_response.parsed.to_dict.return_value = {"status": "ok"}
        mock_submit.sync_detailed.return_value = mock_response

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        with tempfile.TemporaryDirectory() as tmpdir:
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=Path(tmpdir),
            )

            submitter = ScanResultsSubmitter()
            scan_results = self._create_sample_scan_results()

            response = submitter.submit_and_save(
                run_state=run_state,
                scan_id="scan-save",
                scan_results=scan_results,
            )

            assert response == {"status": "ok"}
            assert run_state.phases["submit_results"].status == "completed"

    def test_submit_multiple_results(self):
        """Test submitting multiple scan results."""
        # Create mock for submit_results
        submitter = ScanResultsSubmitter()

        with patch.object(submitter, "submit_results") as mock_submit:
            mock_submit.return_value = {"status": "ok"}

            results = [
                self._create_sample_scan_results(),
                self._create_sample_scan_results(),
            ]

            responses = submitter.submit_multiple_results(
                scan_id="scan-multi",
                results=results,
            )

            assert len(responses) == 2
            assert mock_submit.call_count == 2
