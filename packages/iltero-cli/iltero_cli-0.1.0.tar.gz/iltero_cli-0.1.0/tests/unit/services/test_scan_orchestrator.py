"""Tests for ComplianceScanOrchestrator service."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import UUID

from iltero.services.models import (
    ComplianceManifest,
    PolicyArtifact,
    PolicyResolutionProvenance,
    PolicyResolutionResult,
    PolicyResolutionSummary,
    PolicySource,
)
from iltero.services.scan_orchestrator import (
    ComplianceScanContext,
    ComplianceScanOrchestrator,
)


class TestComplianceScanContext:
    """Test ComplianceScanContext dataclass."""

    def test_create_context(self):
        """Test creating a scan context."""
        mock_stack_info = Mock()
        mock_run_state = Mock()

        context = ComplianceScanContext(
            stack_info=mock_stack_info,
            run_state=mock_run_state,
            provenance=None,
            policy_paths=[Path("/tmp/policy1.rego")],
            scan_id="scan-123",
        )

        assert context.stack_info == mock_stack_info
        assert context.run_state == mock_run_state
        assert context.provenance is None
        assert len(context.policy_paths) == 1
        assert context.scan_id == "scan-123"


class TestComplianceScanOrchestrator:
    """Test ComplianceScanOrchestrator class."""

    def test_init_custom_services(self):
        """Test initialization with custom services."""
        mock_state_manager = Mock()
        mock_policy_resolution = Mock()
        mock_artifact_downloader = Mock()
        mock_results_submitter = Mock()

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=mock_policy_resolution,
            artifact_downloader=mock_artifact_downloader,
            results_submitter=mock_results_submitter,
        )

        assert orchestrator.state_manager == mock_state_manager
        assert orchestrator.policy_resolution == mock_policy_resolution
        assert orchestrator.artifact_downloader == mock_artifact_downloader
        assert orchestrator.results_submitter == mock_results_submitter

    @patch("iltero.services.scan_orchestrator.get_stack_info")
    @patch("iltero.services.scan_orchestrator.detect_cicd_context")
    def test_prepare_scan_without_policies(self, mock_detect_cicd, mock_get_stack_info):
        """Test prepare_scan without policy resolution."""
        # Mock stack info without template bundle
        mock_stack = Mock()
        mock_stack.template_bundle_id = None
        mock_stack.environment = "development"
        mock_stack.policy_sets = []
        mock_get_stack_info.return_value = mock_stack

        mock_detect_cicd.return_value = {}

        mock_state_manager = Mock()
        mock_run_state = Mock()
        mock_state_manager.create_run.return_value = mock_run_state

        # Provide all mocks to avoid auth initialization
        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=Mock(),
        )

        context = orchestrator.prepare_scan(
            stack_id="stack-no-bundle",
            resolve_policies=True,
        )

        assert context.stack_info == mock_stack
        assert context.provenance is None
        assert context.policy_paths == []

    @patch("iltero.services.scan_orchestrator.get_stack_info")
    @patch("iltero.services.scan_orchestrator.detect_cicd_context")
    def test_prepare_scan_with_policies(self, mock_detect_cicd, mock_get_stack_info):
        """Test prepare_scan with policy resolution."""
        manifest_id = UUID("12345678-1234-5678-1234-567812345678")

        # Mock stack info with template bundle
        mock_stack = Mock()
        mock_stack.template_bundle_id = "bundle-123"
        mock_stack.workspace_id = "ws-456"
        mock_stack.environment = "production"
        mock_stack.policy_sets = ["security"]
        mock_get_stack_info.return_value = mock_stack

        mock_detect_cicd.return_value = {"provider": "github"}

        # Mock state manager
        mock_state_manager = Mock()
        mock_run_state = Mock()
        mock_state_manager.create_run.return_value = mock_run_state

        # Mock policy resolution
        mock_policy_resolution = Mock()
        mock_resolution = PolicyResolutionResult(
            manifest=ComplianceManifest(
                id=manifest_id,
                hash="h-1",
                version="1.0.0",
                generated_at=datetime.now(UTC),
                frameworks=[],
                policy_bundle_keys=[],
                policy_bundle_version="1.0.0",
            ),
            effective_policy_sets=[
                PolicyArtifact(
                    key="policy1",
                    source=PolicySource.BUNDLE,
                    required=True,
                    artifact_uri="https://example.com/policy.rego",
                )
            ],
            resolution_summary=PolicyResolutionSummary(
                bundle_required=["policy1"],
                org_required=[],
                env_additions=[],
                total_unique=1,
                dedupe_applied=False,
            ),
            scan_id=UUID("12345678-1234-5678-1234-567812345679"),
        )
        mock_policy_resolution.resolve_and_save.return_value = mock_resolution
        mock_policy_resolution.build_provenance.return_value = PolicyResolutionProvenance(
            manifest_id=str(manifest_id),
            manifest_hash="h-1",
        )

        # Mock artifact downloader
        mock_artifact_downloader = Mock()
        mock_artifact_downloader.download_and_save.return_value = {
            "policy1": (Path("/cache/policy1.rego"), "hash1"),
        }
        mock_artifact_downloader.get_artifact_paths.return_value = [
            Path("/cache/policy1.rego"),
        ]

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=mock_policy_resolution,
            artifact_downloader=mock_artifact_downloader,
        )

        context = orchestrator.prepare_scan(
            stack_id="stack-with-bundle",
            resolve_policies=True,
        )

        assert context.provenance is not None
        assert context.scan_id == UUID("12345678-1234-5678-1234-567812345679")
        assert len(context.policy_paths) == 1

    @patch("iltero.services.scan_orchestrator.get_stack_info")
    @patch("iltero.services.scan_orchestrator.detect_cicd_context")
    def test_prepare_scan_skip_resolution(self, mock_detect_cicd, mock_get_stack_info):
        """Test prepare_scan with resolution disabled."""
        mock_stack = Mock()
        mock_stack.template_bundle_id = "bundle-123"
        mock_stack.environment = "dev"
        mock_stack.policy_sets = []
        mock_get_stack_info.return_value = mock_stack

        mock_detect_cicd.return_value = {}

        mock_state_manager = Mock()
        mock_run_state = Mock()
        mock_state_manager.create_run.return_value = mock_run_state

        mock_policy_resolution = Mock()

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=mock_policy_resolution,
        )

        context = orchestrator.prepare_scan(
            stack_id="stack-skip",
            resolve_policies=False,  # Skip resolution
        )

        # Policy resolution should not be called
        mock_policy_resolution.resolve_and_save.assert_not_called()
        assert context.provenance is None

    def test_submit_scan_results_no_scan_id(self):
        """Test submit_scan_results without scan_id."""
        mock_state_manager = Mock()
        mock_results_submitter = Mock()

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=mock_results_submitter,
        )

        context = ComplianceScanContext(
            stack_info=Mock(),
            run_state=Mock(),
            provenance=None,
            policy_paths=[],
            scan_id=None,  # No scan ID
        )

        mock_scan_results = Mock()

        result = orchestrator.submit_scan_results(
            context=context,
            scan_results=mock_scan_results,
        )

        assert result is None

    def test_submit_scan_results_with_scan_id(self):
        """Test submit_scan_results with scan_id."""
        mock_state_manager = Mock()
        mock_results_submitter = Mock()
        mock_results_submitter.submit_and_save.return_value = {"status": "ok"}

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=mock_results_submitter,
        )

        context = ComplianceScanContext(
            stack_info=Mock(),
            run_state=Mock(),
            provenance=Mock(),
            policy_paths=[],
            scan_id="scan-submit",
        )

        mock_scan_results = Mock()

        result = orchestrator.submit_scan_results(
            context=context,
            scan_results=mock_scan_results,
            scanner_version="3.0.0",
        )

        assert result == {"status": "ok"}
        mock_results_submitter.submit_and_save.assert_called_once()

    def test_get_external_checks_dirs(self):
        """Test get_external_checks_dirs."""
        mock_state_manager = Mock()

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=Mock(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create actual files to test is_file() behavior
            cache_dir = Path(tmpdir) / "cache"
            cache_dir.mkdir()
            subdir = cache_dir / "subdir"
            subdir.mkdir()
            extra_dir = Path(tmpdir) / "extra" / "checks"
            extra_dir.mkdir(parents=True)

            policy1 = cache_dir / "policy1.rego"
            policy1.touch()
            policy2 = subdir / "policy2.rego"
            policy2.touch()

            context = ComplianceScanContext(
                stack_info=Mock(),
                run_state=Mock(),
                provenance=None,
                policy_paths=[policy1, policy2],
                scan_id=None,
            )

            dirs = orchestrator.get_external_checks_dirs(
                context,
                additional_dirs=[extra_dir],
            )

            # Should include parent dirs of policy files + additional
            assert str(cache_dir) in dirs
            assert str(subdir) in dirs
            assert str(extra_dir) in dirs

    def test_get_external_checks_dirs_deduplicates(self):
        """Test get_external_checks_dirs removes duplicates."""
        mock_state_manager = Mock()

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=Mock(),
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create actual files in same directory
            cache_dir = Path(tmpdir) / "cache"
            cache_dir.mkdir()

            policy1 = cache_dir / "policy1.rego"
            policy1.touch()
            policy2 = cache_dir / "policy2.rego"
            policy2.touch()

            context = ComplianceScanContext(
                stack_info=Mock(),
                run_state=Mock(),
                provenance=None,
                policy_paths=[policy1, policy2],
                scan_id=None,
            )

            dirs = orchestrator.get_external_checks_dirs(context)

            # Should have only one cache entry
            assert dirs.count(str(cache_dir)) == 1

    @patch("iltero.services.scan_orchestrator.get_stack_info")
    def test_load_existing_run(self, mock_get_stack_info):
        """Test load_existing_run."""
        mock_stack = Mock()
        mock_get_stack_info.return_value = mock_stack

        mock_run_state = Mock()
        mock_run_state.load_resolution.return_value = None

        mock_state_manager = Mock()
        mock_state_manager.load_run.return_value = mock_run_state

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=Mock(),
        )

        context = orchestrator.load_existing_run(
            stack_id="stack-load",
            run_id="run-123",
        )

        assert context is not None
        assert context.stack_info == mock_stack
        assert context.run_state == mock_run_state

    def test_load_existing_run_not_found(self):
        """Test load_existing_run when run doesn't exist."""
        mock_state_manager = Mock()
        mock_state_manager.load_run.return_value = None

        orchestrator = ComplianceScanOrchestrator(
            state_manager=mock_state_manager,
            policy_resolution=Mock(),
            artifact_downloader=Mock(),
            results_submitter=Mock(),
        )

        context = orchestrator.load_existing_run(
            stack_id="stack-missing",
            run_id="run-missing",
        )

        assert context is None
