"""Tests for policy resolution data models."""

from datetime import UTC, datetime
from uuid import UUID

from iltero.services.models import (
    ComplianceManifest,
    PolicyArtifact,
    PolicyResolutionProvenance,
    PolicyResolutionResult,
    PolicyResolutionSummary,
    PolicySource,
)


class TestPolicySource:
    """Test PolicySource enum."""

    def test_policy_source_values(self):
        """Test policy source enum values."""
        assert PolicySource.BUNDLE.value == "bundle"
        assert PolicySource.ORG.value == "org"
        assert PolicySource.ENVIRONMENT.value == "environment"


class TestPolicyArtifact:
    """Test PolicyArtifact model."""

    def test_create_artifact(self):
        """Test creating a policy artifact."""
        artifact = PolicyArtifact(
            key="security/encryption",
            source=PolicySource.BUNDLE,
            required=True,
        )

        assert artifact.key == "security/encryption"
        assert artifact.source == PolicySource.BUNDLE
        assert artifact.required is True
        assert artifact.artifact_uri is None
        assert artifact.artifact_sha256 is None
        assert artifact.version is None

    def test_artifact_with_all_fields(self):
        """Test artifact with all optional fields."""
        artifact = PolicyArtifact(
            key="compliance/cis",
            source=PolicySource.ORG,
            required=False,
            artifact_uri="https://s3.example.com/policy.rego",
            artifact_sha256="abc123def456",
            version="1.0.0",
        )

        assert artifact.artifact_uri == "https://s3.example.com/policy.rego"
        assert artifact.artifact_sha256 == "abc123def456"
        assert artifact.version == "1.0.0"

    def test_artifact_to_dict(self):
        """Test artifact serialization."""
        artifact = PolicyArtifact(
            key="test",
            source=PolicySource.ENVIRONMENT,
            required=True,
            version="2.0.0",
        )

        data = artifact.to_dict()

        assert data["key"] == "test"
        assert data["source"] == "environment"
        assert data["required"] is True
        assert data["version"] == "2.0.0"

    def test_artifact_from_dict(self):
        """Test artifact deserialization."""
        data = {
            "key": "test/policy",
            "source": "bundle",
            "required": True,
            "artifact_uri": "https://example.com/policy.rego",
            "artifact_sha256": "sha256hash",
            "version": "1.2.3",
        }

        artifact = PolicyArtifact.from_dict(data)

        assert artifact.key == "test/policy"
        assert artifact.source == PolicySource.BUNDLE
        assert artifact.required is True
        assert artifact.artifact_uri == "https://example.com/policy.rego"

    def test_artifact_from_dict_minimal(self):
        """Test artifact deserialization with minimal data."""
        data = {
            "key": "minimal",
            "source": "org",
            "required": False,
        }

        artifact = PolicyArtifact.from_dict(data)

        assert artifact.key == "minimal"
        assert artifact.source == PolicySource.ORG
        assert artifact.artifact_uri is None


class TestComplianceManifest:
    """Test ComplianceManifest model."""

    def test_create_manifest(self):
        """Test creating a compliance manifest."""
        manifest_id = UUID("12345678-1234-5678-1234-567812345678")
        manifest = ComplianceManifest(
            id=manifest_id,
            hash="sha256:abc123",
            version="1.0.0",
            generated_at=datetime(2024, 12, 27, tzinfo=UTC),
            frameworks=["CIS", "SOC2"],
            policy_bundle_keys=["security", "compliance"],
            policy_bundle_version="2.0.0",
        )

        assert manifest.id == manifest_id
        assert manifest.hash == "sha256:abc123"
        assert manifest.frameworks == ["CIS", "SOC2"]
        assert manifest.signature is None

    def test_manifest_to_dict(self):
        """Test manifest serialization."""
        manifest_id = UUID("12345678-1234-5678-1234-567812345678")
        manifest = ComplianceManifest(
            id=manifest_id,
            hash="test-hash",
            version="1.0.0",
            generated_at=datetime(2024, 12, 27, 10, 30, 0, tzinfo=UTC),
            frameworks=["terraform"],
            policy_bundle_keys=["aws"],
            policy_bundle_version="1.0.0",
            signature="sig123",
        )

        data = manifest.to_dict()

        assert data["id"] == str(manifest_id)
        assert data["hash"] == "test-hash"
        assert data["signature"] == "sig123"
        assert "2024-12-27" in data["generated_at"]

    def test_manifest_from_dict(self):
        """Test manifest deserialization."""
        data = {
            "id": "12345678-1234-5678-1234-567812345678",
            "hash": "h-789",
            "version": "2.0.0",
            "generated_at": "2024-12-27T12:00:00Z",
            "frameworks": ["PCI"],
            "policy_bundle_keys": ["pci/v1"],
            "policy_bundle_version": "3.0.0",
        }

        manifest = ComplianceManifest.from_dict(data)

        assert manifest.id == UUID("12345678-1234-5678-1234-567812345678")
        assert manifest.frameworks == ["PCI"]


class TestPolicyResolutionSummary:
    """Test PolicyResolutionSummary model."""

    def test_create_summary(self):
        """Test creating a resolution summary."""
        summary = PolicyResolutionSummary(
            bundle_required=["policy1", "policy2"],
            org_required=["org-policy"],
            env_additions=["env-policy"],
            total_unique=4,
            dedupe_applied=True,
        )

        assert summary.total_unique == 4
        assert summary.bundle_required == ["policy1", "policy2"]
        assert summary.dedupe_applied is True

    def test_summary_to_dict(self):
        """Test summary serialization."""
        summary = PolicyResolutionSummary(
            bundle_required=["b1", "b2"],
            org_required=["o1"],
            env_additions=["e1"],
            total_unique=4,
            dedupe_applied=False,
        )

        data = summary.to_dict()

        assert data["total_unique"] == 4
        assert data["bundle_required"] == ["b1", "b2"]
        assert data["dedupe_applied"] is False


class TestPolicyResolutionResult:
    """Test PolicyResolutionResult model."""

    def test_create_result(self):
        """Test creating a resolution result."""
        manifest_id = UUID("12345678-1234-5678-1234-567812345678")
        manifest = ComplianceManifest(
            id=manifest_id,
            hash="h-1",
            version="1.0.0",
            generated_at=datetime.now(UTC),
            frameworks=[],
            policy_bundle_keys=[],
            policy_bundle_version="1.0.0",
        )

        summary = PolicyResolutionSummary(
            bundle_required=[],
            org_required=[],
            env_additions=[],
            total_unique=0,
            dedupe_applied=False,
        )

        result = PolicyResolutionResult(
            manifest=manifest,
            effective_policy_sets=[],
            resolution_summary=summary,
        )

        assert result.manifest.id == manifest_id
        assert result.scan_id is None
        assert result.warnings == []

    def test_result_from_dict(self):
        """Test result deserialization."""
        data = {
            "manifest": {
                "id": "12345678-1234-5678-1234-567812345678",
                "hash": "h-test",
                "version": "1.0.0",
                "generated_at": "2024-12-27T00:00:00Z",
                "frameworks": ["aws"],
                "policy_bundle_keys": ["key1"],
                "policy_bundle_version": "1.0.0",
            },
            "effective_policy_sets": [
                {
                    "key": "policy1",
                    "source": "bundle",
                    "required": True,
                }
            ],
            "resolution_summary": {
                "bundle_required": ["policy1"],
                "org_required": [],
                "env_additions": [],
                "total_unique": 1,
                "dedupe_applied": False,
            },
            "scan_id": "12345678-1234-5678-1234-567812345679",
            "warnings": ["Warning 1"],
        }

        result = PolicyResolutionResult.from_dict(data)

        assert result.manifest.id == UUID("12345678-1234-5678-1234-567812345678")
        assert len(result.effective_policy_sets) == 1
        assert result.effective_policy_sets[0].key == "policy1"
        assert result.scan_id == UUID("12345678-1234-5678-1234-567812345679")
        assert result.warnings == ["Warning 1"]


class TestPolicyResolutionProvenance:
    """Test PolicyResolutionProvenance model."""

    def test_create_provenance(self):
        """Test creating provenance."""
        provenance = PolicyResolutionProvenance(
            manifest_id="m-123",
            manifest_hash="h-456",
            resolved_at="2024-12-27T12:00:00Z",
        )

        assert provenance.manifest_id == "m-123"
        assert provenance.bundle_required == []
        assert provenance.effective_artifacts == []

    def test_provenance_to_dict(self):
        """Test provenance serialization."""
        provenance = PolicyResolutionProvenance(
            manifest_id="m-test",
            manifest_hash="h-test",
            resolved_at="2024-12-27T00:00:00Z",
            bundle_required=["policy1", "policy2"],
            org_required=["org-policy"],
            env_additions=["env-policy"],
            effective_artifacts=[
                {"key": "policy1", "sha256": "abc123"},
            ],
        )

        data = provenance.to_dict()

        assert data["manifest_id"] == "m-test"
        assert data["bundle_required"] == ["policy1", "policy2"]
        assert len(data["effective_artifacts"]) == 1

    def test_provenance_from_dict(self):
        """Test provenance deserialization."""
        data = {
            "manifest_id": "m-prov",
            "manifest_hash": "h-prov",
            "resolved_at": "2024-12-27T10:00:00Z",
            "bundle_required": ["b1"],
            "org_required": ["o1"],
            "env_additions": ["e1"],
            "effective_artifacts": [],
        }

        provenance = PolicyResolutionProvenance.from_dict(data)

        assert provenance.manifest_id == "m-prov"
        assert provenance.bundle_required == ["b1"]
        assert provenance.org_required == ["o1"]
