"""Tests for PolicyResolutionService."""

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock, patch
from uuid import UUID

import pytest

from iltero.core.exceptions import APIError
from iltero.services.models import (
    ComplianceManifest,
    PolicyArtifact,
    PolicyResolutionResult,
    PolicyResolutionSummary,
    PolicySource,
)
from iltero.services.policy_resolution import PolicyResolutionService


class TestPolicyResolutionService:
    """Test PolicyResolutionService class."""

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_init(self, mock_get_client):
        """Test service initialization."""
        mock_get_client.return_value = Mock()
        service = PolicyResolutionService()
        assert service is not None

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_resolve_policies_success(self, mock_get_client):
        """Test successful policy resolution."""
        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "manifest": {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "hash": "hash-456",
                    "version": "1.0.0",
                    "generated_at": "2024-12-27T00:00:00Z",
                    "frameworks": ["CIS"],
                    "policy_bundle_keys": ["aws/security"],
                    "policy_bundle_version": "2.0.0",
                },
                "effective_policy_sets": [
                    {
                        "key": "aws/security/encryption",
                        "source": "bundle",
                        "required": True,
                        "artifact_uri": "https://s3.example.com/policy.rego",
                        "artifact_sha256": "sha256hash",
                    }
                ],
                "resolution_summary": {
                    "bundle_required": ["aws/security/encryption"],
                    "org_required": [],
                    "env_additions": [],
                    "total_unique": 1,
                    "dedupe_applied": False,
                },
                "scan_id": "12345678-1234-5678-1234-567812345679",
                "warnings": [],
            }
        }

        # Setup the mock chain: client.get_authenticated_client().get_httpx_client().post()
        mock_httpx_client = Mock()
        mock_httpx_client.post.return_value = mock_response

        mock_auth_client = Mock()
        mock_auth_client.get_httpx_client.return_value = mock_httpx_client

        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_auth_client
        mock_get_client.return_value = mock_retry_client

        service = PolicyResolutionService()
        result = service.resolve_policies(
            template_bundle_id="bundle-id",
            workspace_id="workspace-id",
            environment="production",
        )

        assert result.manifest.id == UUID("12345678-1234-5678-1234-567812345678")
        assert len(result.effective_policy_sets) == 1
        assert result.scan_id == UUID("12345678-1234-5678-1234-567812345679")

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_resolve_policies_http_error(self, mock_get_client):
        """Test policy resolution with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_httpx_client = Mock()
        mock_httpx_client.post.return_value = mock_response

        mock_auth_client = Mock()
        mock_auth_client.get_httpx_client.return_value = mock_httpx_client

        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_auth_client
        mock_get_client.return_value = mock_retry_client

        service = PolicyResolutionService()

        with pytest.raises(APIError):
            service.resolve_policies(
                template_bundle_id="bundle-id",
                workspace_id="workspace-id",
                environment="production",
            )

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_resolve_policies_with_optional_params(self, mock_get_client):
        """Test policy resolution with all optional parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "manifest": {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "hash": "h",
                    "version": "1",
                    "generated_at": "2024-12-27T00:00:00Z",
                    "frameworks": [],
                    "policy_bundle_keys": [],
                    "policy_bundle_version": "1",
                },
                "effective_policy_sets": [],
                "resolution_summary": {
                    "bundle_required": [],
                    "org_required": [],
                    "env_additions": [],
                    "total_unique": 0,
                    "dedupe_applied": False,
                },
            }
        }

        mock_httpx_client = Mock()
        mock_httpx_client.post.return_value = mock_response

        mock_auth_client = Mock()
        mock_auth_client.get_httpx_client.return_value = mock_httpx_client

        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_auth_client
        mock_get_client.return_value = mock_retry_client

        service = PolicyResolutionService()
        service.resolve_policies(
            template_bundle_id="bundle-id",
            workspace_id="workspace-id",
            environment="production",
            env_policy_sets=["extra-policy-set"],
            stack_id="stack-123",
        )

        # Verify the request included optional params
        call_args = mock_httpx_client.post.call_args
        request_body = call_args[1]["json"]
        assert request_body["env_policy_sets"] == ["extra-policy-set"]
        assert request_body["stack_id"] == "stack-123"

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_build_provenance(self, mock_get_client):
        """Test building provenance from resolution result."""
        mock_get_client.return_value = Mock()

        manifest_id = UUID("12345678-1234-5678-1234-567812345678")
        manifest = ComplianceManifest(
            id=manifest_id,
            hash="hash-prov",
            version="1.0.0",
            generated_at=datetime(2024, 12, 27, tzinfo=UTC),
            frameworks=["CIS"],
            policy_bundle_keys=["aws"],
            policy_bundle_version="1.0.0",
        )

        artifacts = [
            PolicyArtifact(
                key="bundle/policy1",
                source=PolicySource.BUNDLE,
                required=True,
                artifact_sha256="hash1",
            ),
            PolicyArtifact(
                key="org/policy2",
                source=PolicySource.ORG,
                required=True,
                artifact_sha256="hash2",
            ),
            PolicyArtifact(
                key="env/policy3",
                source=PolicySource.ENVIRONMENT,
                required=False,
                artifact_sha256="hash3",
            ),
        ]

        summary = PolicyResolutionSummary(
            bundle_required=["bundle/policy1"],
            org_required=["org/policy2"],
            env_additions=["env/policy3"],
            total_unique=3,
            dedupe_applied=False,
        )

        result = PolicyResolutionResult(
            manifest=manifest,
            effective_policy_sets=artifacts,
            resolution_summary=summary,
        )

        service = PolicyResolutionService()
        provenance = service.build_provenance(result)

        assert provenance.manifest_id == str(manifest_id)
        assert provenance.manifest_hash == "hash-prov"
        assert len(provenance.effective_artifacts) == 3

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_build_provenance_empty_policies(self, mock_get_client):
        """Test building provenance with no policies."""
        mock_get_client.return_value = Mock()

        manifest_id = UUID("12345678-1234-5678-1234-567812345678")
        manifest = ComplianceManifest(
            id=manifest_id,
            hash="empty-hash",
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

        service = PolicyResolutionService()
        provenance = service.build_provenance(result)

        assert provenance.bundle_required == []
        assert provenance.org_required == []
        assert provenance.env_additions == []
        assert provenance.effective_artifacts == []

    @patch("iltero.services.policy_resolution.get_retry_client")
    def test_resolve_and_save(self, mock_get_client):
        """Test resolve_and_save updates run state."""
        from iltero.services.state_manager import ScanRunState

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "manifest": {
                    "id": "12345678-1234-5678-1234-567812345678",
                    "hash": "h",
                    "version": "1",
                    "generated_at": "2024-12-27T00:00:00Z",
                    "frameworks": [],
                    "policy_bundle_keys": [],
                    "policy_bundle_version": "1",
                },
                "effective_policy_sets": [],
                "resolution_summary": {
                    "bundle_required": [],
                    "org_required": [],
                    "env_additions": [],
                    "total_unique": 0,
                    "dedupe_applied": False,
                },
            }
        }

        mock_httpx_client = Mock()
        mock_httpx_client.post.return_value = mock_response

        mock_auth_client = Mock()
        mock_auth_client.get_httpx_client.return_value = mock_httpx_client

        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_auth_client
        mock_get_client.return_value = mock_retry_client

        with tempfile.TemporaryDirectory() as tmpdir:
            run_state = ScanRunState(
                local_run_id="run-1",
                stack_id="stack-1",
                environment="dev",
                base_path=Path(tmpdir),
            )

            service = PolicyResolutionService()
            service.resolve_and_save(
                run_state=run_state,
                template_bundle_id="bundle-id",
                workspace_id="workspace-id",
            )

            # Verify phase was updated
            assert run_state.phases["resolve_policies"].status == "completed"
