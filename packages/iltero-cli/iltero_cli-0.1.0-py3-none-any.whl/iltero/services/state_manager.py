"""Local state management for compliance scans."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from iltero.services.models import (
    PolicyResolutionProvenance,
    PolicyResolutionResult,
)


@dataclass
class PhaseStatus:
    """Status of a scan phase."""

    status: str  # "pending", "in_progress", "completed", "failed"
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhaseStatus:
        """Create from dictionary."""
        return cls(
            status=data.get("status", "pending"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class ScanRunState:
    """State for a single scan run."""

    stack_id: str
    local_run_id: str  # Local ID for state tracking
    environment: str
    base_path: Path
    run_id: str | None = None  # From webhook validate response
    scan_id: str | None = None  # From resolve-policies response
    compliance_scan_id: str | None = None  # From webhook response
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    phases: dict[str, PhaseStatus] = field(default_factory=dict)
    cicd_context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize default phases if not set."""
        default_phases = [
            "resolve_policies",
            "download_artifacts",
            "static_scan",
            "webhook_validate",
            "plan_evaluation",
            "webhook_plan",
            "webhook_apply",
            "submit_results",
        ]
        for phase in default_phases:
            if phase not in self.phases:
                self.phases[phase] = PhaseStatus(status="pending")

    @property
    def state_file(self) -> Path:
        """Path to state.json file."""
        return self.base_path / "state.json"

    @property
    def resolution_file(self) -> Path:
        """Path to resolution.json file."""
        return self.base_path / "resolution.json"

    @property
    def provenance_file(self) -> Path:
        """Path to provenance.json file."""
        return self.base_path / "provenance.json"

    @property
    def static_scan_file(self) -> Path:
        """Path to static_scan.json file."""
        return self.base_path / "static_scan.json"

    @property
    def plan_eval_file(self) -> Path:
        """Path to plan_eval.json file."""
        return self.base_path / "plan_eval.json"

    def get_scan_id_for_submission(self) -> str | None:
        """Get the scan_id to use for final results submission.

        Prefers scan_id from resolve-policies, falls back to compliance_scan_id.
        """
        return self.scan_id or self.compliance_scan_id

    def save(self) -> None:
        """Save state to disk."""
        self.updated_at = datetime.utcnow().isoformat() + "Z"
        self.base_path.mkdir(parents=True, exist_ok=True)

        state_data = {
            "version": "1.0",
            "stack_id": self.stack_id,
            "local_run_id": self.local_run_id,
            "environment": self.environment,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "ids": {
                "run_id": self.run_id,
                "scan_id": self.scan_id,
                "compliance_scan_id": self.compliance_scan_id,
            },
            "phases": {name: phase.to_dict() for name, phase in self.phases.items()},
            "cicd_context": self.cicd_context,
        }

        self.state_file.write_text(json.dumps(state_data, indent=2))

    @classmethod
    def load(cls, base_path: Path) -> ScanRunState:
        """Load state from disk."""
        state_file = base_path / "state.json"
        if not state_file.exists():
            raise FileNotFoundError(f"State file not found: {state_file}")

        data = json.loads(state_file.read_text())
        ids = data.get("ids", {})

        phases = {}
        for name, phase_data in data.get("phases", {}).items():
            phases[name] = PhaseStatus.from_dict(phase_data)

        return cls(
            stack_id=data["stack_id"],
            local_run_id=data["local_run_id"],
            environment=data["environment"],
            base_path=base_path,
            run_id=ids.get("run_id"),
            scan_id=ids.get("scan_id"),
            compliance_scan_id=ids.get("compliance_scan_id"),
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat() + "Z"),
            phases=phases,
            cicd_context=data.get("cicd_context", {}),
        )

    def start_phase(self, phase: str) -> None:
        """Mark a phase as started."""
        if phase not in self.phases:
            self.phases[phase] = PhaseStatus(status="pending")

        self.phases[phase].status = "in_progress"
        self.phases[phase].started_at = datetime.utcnow().isoformat() + "Z"
        self.save()

    def complete_phase(self, phase: str, **metadata: Any) -> None:
        """Mark a phase as completed."""
        if phase not in self.phases:
            self.phases[phase] = PhaseStatus(status="pending")

        self.phases[phase].status = "completed"
        self.phases[phase].completed_at = datetime.utcnow().isoformat() + "Z"
        self.phases[phase].metadata.update(metadata)
        self.save()

    def fail_phase(self, phase: str, error: str) -> None:
        """Mark a phase as failed."""
        if phase not in self.phases:
            self.phases[phase] = PhaseStatus(status="pending")

        self.phases[phase].status = "failed"
        self.phases[phase].completed_at = datetime.utcnow().isoformat() + "Z"
        self.phases[phase].error = error
        self.save()

    def save_resolution(self, resolution: PolicyResolutionResult) -> None:
        """Save policy resolution response."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.resolution_file.write_text(json.dumps(resolution.to_dict(), indent=2))

        # Update scan_id if returned
        if resolution.scan_id:
            self.scan_id = str(resolution.scan_id)
            self.save()

    def load_resolution(self) -> PolicyResolutionResult | None:
        """Load saved policy resolution."""
        if not self.resolution_file.exists():
            return None
        data = json.loads(self.resolution_file.read_text())
        return PolicyResolutionResult.from_dict(data)

    def save_provenance(self, provenance: PolicyResolutionProvenance) -> None:
        """Save computed provenance."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.provenance_file.write_text(json.dumps(provenance.to_dict(), indent=2))

    def load_provenance(self) -> PolicyResolutionProvenance | None:
        """Load saved provenance."""
        if not self.provenance_file.exists():
            return None
        data = json.loads(self.provenance_file.read_text())
        return PolicyResolutionProvenance.from_dict(data)

    def save_static_results(self, results: dict[str, Any]) -> None:
        """Save static scan results."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.static_scan_file.write_text(json.dumps(results, indent=2))

    def load_static_results(self) -> dict[str, Any] | None:
        """Load static scan results."""
        if not self.static_scan_file.exists():
            return None
        return json.loads(self.static_scan_file.read_text())

    def save_plan_results(self, results: dict[str, Any]) -> None:
        """Save plan evaluation results."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.plan_eval_file.write_text(json.dumps(results, indent=2))

    def load_plan_results(self) -> dict[str, Any] | None:
        """Load plan evaluation results."""
        if not self.plan_eval_file.exists():
            return None
        return json.loads(self.plan_eval_file.read_text())


class ScanStateManager:
    """Manages local state for compliance scans."""

    def __init__(self, base_dir: Path | None = None):
        """Initialize state manager.

        Args:
            base_dir: Base directory for state files. Defaults to .iltero/
        """
        self.base_dir = base_dir or Path(".iltero")

    @property
    def scans_dir(self) -> Path:
        """Directory for scan state files."""
        return self.base_dir / "scans"

    @property
    def policy_cache_dir(self) -> Path:
        """Directory for cached policy artifacts."""
        return self.base_dir / "policy_cache"

    def create_run(
        self,
        stack_id: str,
        environment: str,
        cicd_context: dict[str, Any] | None = None,
    ) -> ScanRunState:
        """Create a new scan run state.

        Args:
            stack_id: Stack identifier.
            environment: Environment name.
            cicd_context: Optional CI/CD context for audit.

        Returns:
            New ScanRunState instance.
        """
        local_run_id = str(uuid.uuid4())
        base_path = self.scans_dir / stack_id / local_run_id

        run_state = ScanRunState(
            stack_id=stack_id,
            local_run_id=local_run_id,
            environment=environment,
            base_path=base_path,
            cicd_context=cicd_context or {},
        )
        run_state.save()
        return run_state

    def load_run(self, stack_id: str, local_run_id: str) -> ScanRunState:
        """Load an existing run state.

        Args:
            stack_id: Stack identifier.
            local_run_id: Local run identifier.

        Returns:
            Loaded ScanRunState.

        Raises:
            FileNotFoundError: If state file doesn't exist.
        """
        base_path = self.scans_dir / stack_id / local_run_id
        return ScanRunState.load(base_path)

    def get_latest_run(self, stack_id: str) -> ScanRunState | None:
        """Get the most recent run for a stack.

        Args:
            stack_id: Stack identifier.

        Returns:
            Most recent ScanRunState or None if no runs exist.
        """
        stack_dir = self.scans_dir / stack_id
        if not stack_dir.exists():
            return None

        # Find all run directories and sort by modification time
        run_dirs = [d for d in stack_dir.iterdir() if d.is_dir()]
        if not run_dirs:
            return None

        # Sort by state file modification time (most recent first)
        run_dirs.sort(
            key=lambda d: (d / "state.json").stat().st_mtime if (d / "state.json").exists() else 0,
            reverse=True,
        )

        try:
            return ScanRunState.load(run_dirs[0])
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def list_runs(self, stack_id: str, limit: int = 10) -> list[ScanRunState]:
        """List recent runs for a stack.

        Args:
            stack_id: Stack identifier.
            limit: Maximum number of runs to return.

        Returns:
            List of ScanRunState, most recent first.
        """
        stack_dir = self.scans_dir / stack_id
        if not stack_dir.exists():
            return []

        run_dirs = [d for d in stack_dir.iterdir() if d.is_dir()]
        run_dirs.sort(
            key=lambda d: (d / "state.json").stat().st_mtime if (d / "state.json").exists() else 0,
            reverse=True,
        )

        runs = []
        for run_dir in run_dirs[:limit]:
            try:
                runs.append(ScanRunState.load(run_dir))
            except (FileNotFoundError, json.JSONDecodeError):
                continue

        return runs

    def cleanup_old_runs(self, stack_id: str, keep: int = 5) -> int:
        """Remove old run states, keeping the most recent.

        Args:
            stack_id: Stack identifier.
            keep: Number of recent runs to keep.

        Returns:
            Number of runs removed.
        """
        import shutil

        stack_dir = self.scans_dir / stack_id
        if not stack_dir.exists():
            return 0

        run_dirs = [d for d in stack_dir.iterdir() if d.is_dir()]
        run_dirs.sort(
            key=lambda d: (d / "state.json").stat().st_mtime if (d / "state.json").exists() else 0,
            reverse=True,
        )

        removed = 0
        for run_dir in run_dirs[keep:]:
            shutil.rmtree(run_dir)
            removed += 1

        return removed
