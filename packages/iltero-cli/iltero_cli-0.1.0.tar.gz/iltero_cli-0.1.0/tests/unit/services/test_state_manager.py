"""Tests for ScanStateManager service."""

import tempfile
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

from iltero.services.models import (
    ComplianceManifest,
    PolicyResolutionProvenance,
    PolicyResolutionResult,
    PolicyResolutionSummary,
)
from iltero.services.state_manager import PhaseStatus, ScanRunState, ScanStateManager


class TestPhaseStatus:
    """Test PhaseStatus dataclass."""

    def test_create_phase_status(self):
        """Test creating a phase status."""
        status = PhaseStatus(status="pending")
        assert status.status == "pending"
        assert status.started_at is None
        assert status.completed_at is None
        assert status.error is None
        assert status.metadata == {}

    def test_phase_status_with_all_fields(self):
        """Test phase status with all fields."""
        status = PhaseStatus(
            status="completed",
            started_at="2024-12-27T10:00:00Z",
            completed_at="2024-12-27T10:05:00Z",
            error=None,
            metadata={"artifacts_count": 5},
        )
        assert status.status == "completed"
        assert status.started_at == "2024-12-27T10:00:00Z"
        assert status.metadata["artifacts_count"] == 5

    def test_phase_status_to_dict(self):
        """Test converting phase status to dict."""
        status = PhaseStatus(
            status="failed",
            started_at="2024-12-27T10:00:00Z",
            error="Connection timeout",
        )
        data = status.to_dict()
        assert data["status"] == "failed"
        assert data["error"] == "Connection timeout"

    def test_phase_status_from_dict(self):
        """Test creating phase status from dict."""
        data = {
            "status": "in_progress",
            "started_at": "2024-12-27T10:00:00Z",
            "completed_at": None,
            "error": None,
            "metadata": {"step": 1},
        }
        status = PhaseStatus.from_dict(data)
        assert status.status == "in_progress"
        assert status.metadata["step"] == 1


class TestScanRunState:
    """Test ScanRunState class."""

    def test_create_run_state(self):
        """Test creating a run state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-123",
                stack_id="stack-456",
                environment="production",
                base_path=base_path,
            )

            assert run_state.local_run_id == "run-123"
            assert run_state.stack_id == "stack-456"
            assert run_state.environment == "production"
            assert run_state.run_id is None
            assert run_state.scan_id is None

    def test_default_phases_initialized(self):
        """Test that default phases are initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            assert "resolve_policies" in run_state.phases
            assert "download_artifacts" in run_state.phases
            assert "static_scan" in run_state.phases
            assert run_state.phases["resolve_policies"].status == "pending"

    def test_start_phase(self):
        """Test starting a phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            run_state.start_phase("resolve_policies")

            assert run_state.phases["resolve_policies"].status == "in_progress"
            assert run_state.phases["resolve_policies"].started_at is not None

    def test_complete_phase(self):
        """Test completing a phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            run_state.start_phase("download_artifacts")
            run_state.complete_phase("download_artifacts", artifacts_count=5)

            phase = run_state.phases["download_artifacts"]
            assert phase.status == "completed"
            assert phase.completed_at is not None
            assert phase.metadata["artifacts_count"] == 5

    def test_fail_phase(self):
        """Test failing a phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            run_state.start_phase("static_scan")
            run_state.fail_phase("static_scan", "Connection timeout")

            phase = run_state.phases["static_scan"]
            assert phase.status == "failed"
            assert phase.error == "Connection timeout"

    def test_save_and_load(self):
        """Test saving and loading state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create and save state
            run_state = ScanRunState(
                local_run_id="run-persist",
                stack_id="stack-persist",
                environment="staging",
                base_path=base_path,
            )
            run_state.run_id = "external-id"
            run_state.start_phase("resolve_policies")
            run_state.complete_phase("resolve_policies")
            run_state.save()

            # Load state
            loaded_state = ScanRunState.load(base_path)

            assert loaded_state.local_run_id == "run-persist"
            assert loaded_state.stack_id == "stack-persist"
            assert loaded_state.run_id == "external-id"
            assert loaded_state.phases["resolve_policies"].status == "completed"

    def test_state_file_path(self):
        """Test state file path property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            assert run_state.state_file == base_path / "state.json"
            assert run_state.resolution_file == base_path / "resolution.json"
            assert run_state.provenance_file == base_path / "provenance.json"

    def test_save_resolution(self):
        """Test saving resolution data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            manifest_id = UUID("12345678-1234-5678-1234-567812345678")
            manifest = ComplianceManifest(
                id=manifest_id,
                hash="h-1",
                version="1.0.0",
                generated_at=datetime.now(),
                frameworks=["terraform"],
                policy_bundle_keys=["aws"],
                policy_bundle_version="1.0.0",
            )
            summary = PolicyResolutionSummary(
                bundle_required=["policy1"],
                org_required=[],
                env_additions=[],
                total_unique=1,
                dedupe_applied=False,
            )
            resolution = PolicyResolutionResult(
                manifest=manifest,
                effective_policy_sets=[],
                resolution_summary=summary,
            )
            run_state.save_resolution(resolution)

            # Verify file was created
            assert run_state.resolution_file.exists()

            # Load and verify
            loaded = run_state.load_resolution()
            assert loaded is not None
            assert loaded.manifest.id == manifest_id

    def test_load_resolution_not_found(self):
        """Test loading resolution when not saved."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            result = run_state.load_resolution()
            assert result is None

    def test_save_and_load_provenance(self):
        """Test saving and loading provenance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            provenance = PolicyResolutionProvenance(
                manifest_id="m-123",
                manifest_hash="h-456",
                resolved_at="2024-12-27T12:00:00Z",
                bundle_required=["policy1"],
            )
            run_state.save_provenance(provenance)

            # Load and verify
            loaded = run_state.load_provenance()
            assert loaded is not None
            assert loaded.manifest_id == "m-123"
            assert loaded.bundle_required == ["policy1"]

    def test_get_scan_id_for_submission(self):
        """Test getting scan ID for submission."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=base_path,
            )

            # Initially none
            assert run_state.get_scan_id_for_submission() is None

            # Prefers scan_id
            run_state.scan_id = "scan-123"
            assert run_state.get_scan_id_for_submission() == "scan-123"

            # Falls back to compliance_scan_id
            run_state.scan_id = None
            run_state.compliance_scan_id = "comp-456"
            assert run_state.get_scan_id_for_submission() == "comp-456"


class TestScanStateManager:
    """Test ScanStateManager class."""

    def test_init_default_base_dir(self):
        """Test default base directory."""
        manager = ScanStateManager()
        assert manager.base_dir == Path(".iltero")

    def test_init_custom_base_dir(self):
        """Test custom base directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)
            assert manager.base_dir == base_dir

    def test_create_run(self):
        """Test creating a new run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            run = manager.create_run(
                stack_id="test-stack",
                environment="production",
            )

            assert run.stack_id == "test-stack"
            assert run.environment == "production"
            assert run.local_run_id is not None
            # State file should exist
            assert run.state_file.exists()

    def test_create_run_with_cicd_context(self):
        """Test creating a run with CI/CD context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            cicd_context = {
                "provider": "github",
                "run_id": "12345",
                "commit_sha": "abc123",
            }
            run = manager.create_run(
                stack_id="test-stack",
                environment="staging",
                cicd_context=cicd_context,
            )

            assert run.cicd_context["provider"] == "github"
            assert run.cicd_context["run_id"] == "12345"

    def test_load_run(self):
        """Test loading an existing run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            # Create run
            run = manager.create_run(
                stack_id="load-test-stack",
                environment="dev",
            )
            local_run_id = run.local_run_id

            # Load run
            loaded_run = manager.load_run("load-test-stack", local_run_id)
            assert loaded_run.stack_id == "load-test-stack"
            assert loaded_run.local_run_id == local_run_id

    def test_load_run_not_found(self):
        """Test loading a non-existent run."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            with pytest.raises(FileNotFoundError):
                manager.load_run("nonexistent-stack", "nonexistent-run")

    def test_get_latest_run(self):
        """Test getting the latest run."""
        import time

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            # Create multiple runs with small delay to ensure different mtimes
            manager.create_run("test-stack", "dev")
            time.sleep(0.01)  # Ensure different modification times
            run2 = manager.create_run("test-stack", "dev")

            # Latest should be run2
            latest = manager.get_latest_run("test-stack")
            assert latest is not None
            assert latest.local_run_id == run2.local_run_id

    def test_get_latest_run_no_runs(self):
        """Test getting latest run when no runs exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            result = manager.get_latest_run("nonexistent-stack")
            assert result is None

    def test_list_runs(self):
        """Test listing runs for a stack."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            # Create multiple runs
            for _ in range(3):
                manager.create_run("list-test-stack", "dev")

            runs = manager.list_runs("list-test-stack")
            assert len(runs) == 3

    def test_list_runs_with_limit(self):
        """Test listing runs with limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            # Create multiple runs
            for _ in range(5):
                manager.create_run("limit-test-stack", "dev")

            runs = manager.list_runs("limit-test-stack", limit=2)
            assert len(runs) == 2

    def test_cleanup_old_runs(self):
        """Test cleaning up old runs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            # Create multiple runs
            for _ in range(5):
                manager.create_run("cleanup-test-stack", "dev")

            # Cleanup keeping only 2
            removed = manager.cleanup_old_runs("cleanup-test-stack", keep=2)
            assert removed == 3

            # Verify only 2 remain
            runs = manager.list_runs("cleanup-test-stack")
            assert len(runs) == 2

    def test_policy_cache_dir(self):
        """Test policy cache directory property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            assert manager.policy_cache_dir == base_dir / "policy_cache"

    def test_scans_dir(self):
        """Test scans directory property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir)
            manager = ScanStateManager(base_dir=base_dir)

            assert manager.scans_dir == base_dir / "scans"
