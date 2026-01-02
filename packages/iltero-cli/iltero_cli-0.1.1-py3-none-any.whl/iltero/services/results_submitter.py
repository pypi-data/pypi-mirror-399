"""Scan results submitter service."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from iltero.api_client.iltero_api_client.api.compliance_scans import submit_scan_results
from iltero.api_client.iltero_api_client.models.scan_results_submission_schema import (
    ScanResultsSubmissionSchema,
)
from iltero.api_client.iltero_api_client.models.scan_results_submission_schema_scan_results import (
    ScanResultsSubmissionSchemaScanResults,
)
from iltero.core.exceptions import IlteroError
from iltero.core.http import get_retry_client

if TYPE_CHECKING:
    from iltero.api_client.iltero_api_client.client import AuthenticatedClient
    from iltero.scanners.models import ScanResults
    from iltero.services.models import PolicyResolutionProvenance
    from iltero.services.state_manager import ScanRunState


class ScanResultsSubmissionError(IlteroError):
    """Failed to submit scan results."""

    def __init__(self, scan_id: str, message: str, status_code: int | None = None):
        full_message = f"Failed to submit results for scan '{scan_id}': {message}"
        super().__init__(full_message, exit_code=12)
        self.scan_id = scan_id
        self.status_code = status_code


class ScanResultsSubmitter:
    """Submits scan results to the compliance API.

    This service:
    1. Formats scan results for API submission
    2. Includes policy resolution provenance for audit trail
    3. Handles submission via generated API client
    4. Updates run state with submission status
    """

    def __init__(self, api_client: AuthenticatedClient | None = None):
        """Initialize the results submitter.

        Args:
            api_client: Optional pre-configured API client. If not provided,
                a new client will be created from settings.
        """
        self._api_client = api_client

    def _get_api_client(self) -> AuthenticatedClient:
        """Get or create the API client."""
        if self._api_client is not None:
            return self._api_client

        return get_retry_client().get_authenticated_client()

    def _build_scan_results_payload(
        self,
        scan_results: ScanResults,
        policy_resolution: PolicyResolutionProvenance | None = None,
    ) -> dict[str, Any]:
        """Build the scan results payload for submission.

        Args:
            scan_results: The scan results from the scanner.
            policy_resolution: Optional policy resolution provenance.

        Returns:
            Dict payload for the scan_results field.
        """
        payload = scan_results.to_dict()

        # Include policy resolution provenance if available
        if policy_resolution:
            payload["policy_resolution"] = policy_resolution.to_dict()

        return payload

    def submit_results(
        self,
        scan_id: str,
        scan_results: ScanResults,
        policy_resolution: PolicyResolutionProvenance | None = None,
        scanner_version: str | None = None,
        pipeline_url: str | None = None,
        commit_sha: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Submit scan results to the compliance API.

        Args:
            scan_id: The scan ID to submit results for.
            scan_results: The scan results from the scanner.
            policy_resolution: Optional policy resolution provenance for audit.
            scanner_version: Version of the scanner used.
            pipeline_url: URL to the CI/CD pipeline run.
            commit_sha: Git commit SHA that was scanned.
            branch: Git branch that was scanned.

        Returns:
            API response data.

        Raises:
            ScanResultsSubmissionError: If submission fails.
        """
        client = self._get_api_client()

        # Build scan results payload
        results_payload = self._build_scan_results_payload(
            scan_results=scan_results,
            policy_resolution=policy_resolution,
        )

        # Create the schema with additional properties for scan results
        scan_results_schema = ScanResultsSubmissionSchemaScanResults()
        for key, value in results_payload.items():
            scan_results_schema[key] = value

        # Build submission schema
        submission = ScanResultsSubmissionSchema(
            scan_results=scan_results_schema,
            scanner_version=scanner_version,
            pipeline_url=pipeline_url,
            commit_sha=commit_sha,
            branch=branch,
        )

        try:
            response = submit_scan_results.sync_detailed(
                scan_id=scan_id,
                client=client,
                body=submission,
            )

            if response.status_code != 200:
                raise ScanResultsSubmissionError(
                    scan_id=scan_id,
                    message=f"HTTP {response.status_code}",
                    status_code=response.status_code,
                )

            if response.parsed is None:
                raise ScanResultsSubmissionError(
                    scan_id=scan_id,
                    message="Empty response from API",
                )

            return response.parsed.to_dict()

        except ScanResultsSubmissionError:
            raise

        except Exception as e:
            raise ScanResultsSubmissionError(
                scan_id=scan_id,
                message=str(e),
            )

    def submit_and_save(
        self,
        run_state: ScanRunState,
        scan_id: str,
        scan_results: ScanResults,
        policy_resolution: PolicyResolutionProvenance | None = None,
        scanner_version: str | None = None,
        pipeline_url: str | None = None,
        commit_sha: str | None = None,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Submit results and update run state.

        Args:
            run_state: The current scan run state.
            scan_id: The scan ID to submit results for.
            scan_results: The scan results from the scanner.
            policy_resolution: Optional policy resolution provenance.
            scanner_version: Version of the scanner used.
            pipeline_url: URL to the CI/CD pipeline run.
            commit_sha: Git commit SHA that was scanned.
            branch: Git branch that was scanned.

        Returns:
            API response data.
        """
        run_state.start_phase("submit_results")

        try:
            response = self.submit_results(
                scan_id=scan_id,
                scan_results=scan_results,
                policy_resolution=policy_resolution,
                scanner_version=scanner_version,
                pipeline_url=pipeline_url,
                commit_sha=commit_sha,
                branch=branch,
            )

            run_state.complete_phase(
                "submit_results",
                scan_id=scan_id,
                response_status="success",
            )

            return response

        except Exception as e:
            run_state.fail_phase("submit_results", str(e))
            raise

    def submit_multiple_results(
        self,
        scan_id: str,
        results: list[ScanResults],
        policy_resolution: PolicyResolutionProvenance | None = None,
        scanner_version: str | None = None,
        pipeline_url: str | None = None,
        commit_sha: str | None = None,
        branch: str | None = None,
    ) -> list[dict[str, Any]]:
        """Submit multiple scan results (e.g., static + evaluation).

        Args:
            scan_id: The scan ID to submit results for.
            results: List of scan results from different scanners.
            policy_resolution: Optional policy resolution provenance.
            scanner_version: Version of the scanner used.
            pipeline_url: URL to the CI/CD pipeline run.
            commit_sha: Git commit SHA that was scanned.
            branch: Git branch that was scanned.

        Returns:
            List of API response data.
        """
        responses = []

        for scan_results in results:
            response = self.submit_results(
                scan_id=scan_id,
                scan_results=scan_results,
                policy_resolution=policy_resolution,
                scanner_version=scanner_version,
                pipeline_url=pipeline_url,
                commit_sha=commit_sha,
                branch=branch,
            )
            responses.append(response)

        return responses
