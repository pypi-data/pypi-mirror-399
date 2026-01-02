"""Data models for policy resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class PolicySource(str, Enum):
    """Source of a policy artifact."""

    BUNDLE = "bundle"
    ORG = "org"
    ENVIRONMENT = "environment"


@dataclass
class PolicyArtifact:
    """Represents a single policy artifact to download."""

    key: str
    source: PolicySource
    required: bool
    artifact_uri: str | None = None
    artifact_sha256: str | None = None
    version: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyArtifact:
        """Create from API response dictionary."""
        return cls(
            key=data["key"],
            source=PolicySource(data["source"]),
            required=data.get("required", True),
            artifact_uri=data.get("artifact_uri"),
            artifact_sha256=data.get("artifact_sha256"),
            version=data.get("version"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "source": self.source.value,
            "required": self.required,
            "artifact_uri": self.artifact_uri,
            "artifact_sha256": self.artifact_sha256,
            "version": self.version,
        }


@dataclass
class ComplianceManifest:
    """Compliance manifest from the registry."""

    id: str
    hash: str
    version: str
    generated_at: datetime
    frameworks: list[str]
    policy_bundle_keys: list[str]
    policy_bundle_version: str
    signature: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ComplianceManifest:
        """Create from API response dictionary."""
        generated_at = data["generated_at"]
        if isinstance(generated_at, str):
            generated_at = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))

        return cls(
            id=UUID(data["id"]) if isinstance(data["id"], str) else data["id"],
            hash=data["hash"],
            version=data["version"],
            signature=data.get("signature"),
            generated_at=generated_at,
            frameworks=data.get("frameworks", []),
            policy_bundle_keys=data.get("policy_bundle_keys", []),
            policy_bundle_version=data.get("policy_bundle_version", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "hash": self.hash,
            "version": self.version,
            "signature": self.signature,
            "generated_at": self.generated_at.isoformat(),
            "frameworks": self.frameworks,
            "policy_bundle_keys": self.policy_bundle_keys,
            "policy_bundle_version": self.policy_bundle_version,
        }


@dataclass
class PolicyResolutionSummary:
    """Summary of policy resolution for audit trail."""

    bundle_required: list[str]
    org_required: list[str]
    env_additions: list[str]
    total_unique: int
    dedupe_applied: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyResolutionSummary:
        """Create from API response dictionary."""
        return cls(
            bundle_required=data.get("bundle_required", []),
            org_required=data.get("org_required", []),
            env_additions=data.get("env_additions", []),
            total_unique=data.get("total_unique", 0),
            dedupe_applied=data.get("dedupe_applied", False),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "bundle_required": self.bundle_required,
            "org_required": self.org_required,
            "env_additions": self.env_additions,
            "total_unique": self.total_unique,
            "dedupe_applied": self.dedupe_applied,
        }


@dataclass
class PolicyResolutionResult:
    """Result of policy resolution from the API."""

    manifest: ComplianceManifest
    effective_policy_sets: list[PolicyArtifact]
    resolution_summary: PolicyResolutionSummary
    scan_id: str | None = None
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyResolutionResult:
        """Create from API response dictionary."""
        scan_id = data.get("scan_id")
        if scan_id and isinstance(scan_id, str):
            scan_id = UUID(scan_id)

        return cls(
            manifest=ComplianceManifest.from_dict(data["manifest"]),
            effective_policy_sets=[
                PolicyArtifact.from_dict(p) for p in data.get("effective_policy_sets", [])
            ],
            resolution_summary=PolicyResolutionSummary.from_dict(
                data.get("resolution_summary", {})
            ),
            scan_id=scan_id,
            warnings=data.get("warnings", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "manifest": self.manifest.to_dict(),
            "effective_policy_sets": [p.to_dict() for p in self.effective_policy_sets],
            "resolution_summary": self.resolution_summary.to_dict(),
            "scan_id": str(self.scan_id) if self.scan_id else None,
            "warnings": self.warnings,
        }


@dataclass
class PolicyResolutionProvenance:
    """Policy resolution provenance for audit trail."""

    manifest_id: str | None = None
    manifest_hash: str | None = None
    resolved_at: str | None = None
    bundle_required: list[str] = field(default_factory=list)
    org_required: list[str] = field(default_factory=list)
    env_additions: list[str] = field(default_factory=list)
    effective_artifacts: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_resolution(
        cls,
        resolution: PolicyResolutionResult,
        downloaded_artifacts: dict[str, str] | None = None,
    ) -> PolicyResolutionProvenance:
        """Build provenance from resolution result.

        Args:
            resolution: The policy resolution result from API.
            downloaded_artifacts: Mapping of artifact key to verified SHA256.
        """
        downloaded_artifacts = downloaded_artifacts or {}

        # Build effective artifacts with verified SHA256
        effective_artifacts = []
        for artifact in resolution.effective_policy_sets:
            sha256 = downloaded_artifacts.get(artifact.key, artifact.artifact_sha256)
            effective_artifacts.append(
                {
                    "key": artifact.key,
                    "sha256": sha256,
                    "version": artifact.version,
                    "source": artifact.source.value,
                }
            )

        return cls(
            manifest_id=str(resolution.manifest.id),
            manifest_hash=resolution.manifest.hash,
            resolved_at=datetime.utcnow().isoformat() + "Z",
            bundle_required=resolution.resolution_summary.bundle_required,
            org_required=resolution.resolution_summary.org_required,
            env_additions=resolution.resolution_summary.env_additions,
            effective_artifacts=effective_artifacts,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyResolutionProvenance:
        """Create from dictionary."""
        return cls(
            manifest_id=data.get("manifest_id"),
            manifest_hash=data.get("manifest_hash"),
            resolved_at=data.get("resolved_at"),
            bundle_required=data.get("bundle_required", []),
            org_required=data.get("org_required", []),
            env_additions=data.get("env_additions", []),
            effective_artifacts=data.get("effective_artifacts", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API submission."""
        return {
            "manifest_id": self.manifest_id,
            "manifest_hash": self.manifest_hash,
            "resolved_at": self.resolved_at,
            "bundle_required": self.bundle_required,
            "org_required": self.org_required,
            "env_additions": self.env_additions,
            "effective_artifacts": self.effective_artifacts,
        }
