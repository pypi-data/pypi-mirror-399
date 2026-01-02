"""Compliance scan orchestrator with policy resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from iltero.services.models import PolicyResolutionProvenance
from iltero.services.policy_downloader import PolicyArtifactDownloader
from iltero.services.policy_resolution import PolicyResolutionService
from iltero.services.results_submitter import ScanResultsSubmitter
from iltero.services.stack_info import StackInfo, get_stack_info
from iltero.services.state_manager import ScanRunState, ScanStateManager
from iltero.utils.cicd import detect_cicd_context

if TYPE_CHECKING:
    from iltero.scanners.models import ScanResults


@dataclass
class ComplianceScanContext:
    """Context for a compliance scan run."""

    stack_info: StackInfo
    run_state: ScanRunState
    provenance: PolicyResolutionProvenance | None
    policy_paths: list[Path]
    scan_id: str | None


class ComplianceScanOrchestrator:
    """Orchestrates compliance scanning with policy resolution.

    This orchestrator:
    1. Retrieves stack information
    2. Resolves effective policies
    3. Downloads policy artifacts
    4. Prepares scan context for scanners
    5. Submits results with provenance
    """

    def __init__(
        self,
        state_manager: ScanStateManager | None = None,
        policy_resolution: PolicyResolutionService | None = None,
        artifact_downloader: PolicyArtifactDownloader | None = None,
        results_submitter: ScanResultsSubmitter | None = None,
    ):
        """Initialize the orchestrator.

        Args:
            state_manager: Optional state manager instance.
            policy_resolution: Optional policy resolution service.
            artifact_downloader: Optional artifact downloader.
            results_submitter: Optional results submitter.
        """
        self.state_manager = state_manager or ScanStateManager()
        self.policy_resolution = policy_resolution or PolicyResolutionService()
        self.artifact_downloader = artifact_downloader or PolicyArtifactDownloader()
        self.results_submitter = results_submitter or ScanResultsSubmitter()

    def prepare_scan(
        self,
        stack_id: str,
        environment: str | None = None,
        resolve_policies: bool = True,
        force_download: bool = False,
    ) -> ComplianceScanContext:
        """Prepare a compliance scan with policy resolution.

        Args:
            stack_id: The stack ID to scan.
            environment: Optional environment override.
            resolve_policies: Whether to resolve policies (default True).
            force_download: Force re-download of policy artifacts.

        Returns:
            ComplianceScanContext with scan preparation results.
        """
        # Get stack information
        stack_info = get_stack_info(stack_id)

        # Use provided environment or stack default
        env = environment or stack_info.environment or "development"

        # Detect CI/CD context
        cicd_context = detect_cicd_context()

        # Create run state
        run_state = self.state_manager.create_run(
            stack_id=stack_id,
            environment=env,
            cicd_context=cicd_context,
        )

        provenance: PolicyResolutionProvenance | None = None
        policy_paths: list[Path] = []
        scan_id: str | None = None

        if resolve_policies and stack_info.template_bundle_id:
            # Resolve policies
            resolution = self.policy_resolution.resolve_and_save(
                run_state=run_state,
                template_bundle_id=stack_info.template_bundle_id,
                workspace_id=stack_info.workspace_id,
                environment=env,
                env_policy_sets=stack_info.policy_sets or None,
                stack_id=stack_id,
            )

            # Build provenance
            provenance = self.policy_resolution.build_provenance(resolution)
            run_state.save_provenance(provenance.to_dict())

            # Get scan_id from resolution
            scan_id = resolution.scan_id

            # Download policy artifacts
            artifacts = resolution.effective_policy_sets
            if artifacts:
                downloaded = self.artifact_downloader.download_and_save(
                    run_state=run_state,
                    artifacts=artifacts,
                    force=force_download,
                )
                policy_paths = self.artifact_downloader.get_artifact_paths(downloaded)

        return ComplianceScanContext(
            stack_info=stack_info,
            run_state=run_state,
            provenance=provenance,
            policy_paths=policy_paths,
            scan_id=scan_id,
        )

    def submit_scan_results(
        self,
        context: ComplianceScanContext,
        scan_results: ScanResults,
        scanner_version: str | None = None,
        pipeline_url: str | None = None,
        commit_sha: str | None = None,
        branch: str | None = None,
    ) -> dict | None:
        """Submit scan results with provenance.

        Args:
            context: The compliance scan context.
            scan_results: Results from the scanner.
            scanner_version: Version of the scanner used.
            pipeline_url: URL to CI/CD pipeline run.
            commit_sha: Git commit SHA.
            branch: Git branch name.

        Returns:
            API response dict if scan_id is available, None otherwise.
        """
        if not context.scan_id:
            return None

        return self.results_submitter.submit_and_save(
            run_state=context.run_state,
            scan_id=context.scan_id,
            scan_results=scan_results,
            policy_resolution=context.provenance,
            scanner_version=scanner_version,
            pipeline_url=pipeline_url,
            commit_sha=commit_sha,
            branch=branch,
        )

    def get_external_checks_dirs(
        self,
        context: ComplianceScanContext,
        additional_dirs: list[Path] | None = None,
    ) -> list[str]:
        """Get list of external check directories for Checkov.

        Combines resolved policy paths with any additional directories.

        Args:
            context: The compliance scan context.
            additional_dirs: Additional external check directories.

        Returns:
            List of directory paths as strings.
        """
        dirs: list[str] = []

        # Add resolved policy paths
        for path in context.policy_paths:
            if path.is_file():
                # Checkov wants directory, not file
                dirs.append(str(path.parent))
            else:
                dirs.append(str(path))

        # Add additional directories
        if additional_dirs:
            for path in additional_dirs:
                dirs.append(str(path))

        # Deduplicate while preserving order
        seen = set()
        unique_dirs = []
        for d in dirs:
            if d not in seen:
                seen.add(d)
                unique_dirs.append(d)

        return unique_dirs

    def load_existing_run(
        self,
        stack_id: str,
        run_id: str | None = None,
    ) -> ComplianceScanContext | None:
        """Load an existing run's context.

        Args:
            stack_id: The stack ID.
            run_id: Optional specific run ID. If not provided, loads latest.

        Returns:
            ComplianceScanContext if found, None otherwise.
        """
        run_state: ScanRunState | None = None

        if run_id:
            run_state = self.state_manager.load_run(stack_id, run_id)
        else:
            run_state = self.state_manager.get_latest_run(stack_id)

        if not run_state:
            return None

        # Get stack info
        stack_info = get_stack_info(stack_id)

        # Load provenance if available
        provenance: PolicyResolutionProvenance | None = None
        resolution = run_state.load_resolution()
        if resolution:
            provenance = self.policy_resolution.build_provenance(resolution)

        return ComplianceScanContext(
            stack_info=stack_info,
            run_state=run_state,
            provenance=provenance,
            policy_paths=[],  # Would need to re-download
            scan_id=str(resolution.scan_id) if resolution and resolution.scan_id else None,
        )
