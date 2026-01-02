"""Policy resolution service for compliance scanning."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from iltero.core.exceptions import APIError
from iltero.core.http import get_retry_client
from iltero.services.models import (
    PolicyResolutionProvenance,
    PolicyResolutionResult,
)

if TYPE_CHECKING:
    from iltero.services.state_manager import ScanRunState


class PolicyResolutionService:
    """Service for resolving effective policies for a stack.

    This service:
    1. Calls /v1/compliance/resolve-policies to get effective policies
    2. Parses and validates the response
    3. Builds provenance for audit trail
    """

    def __init__(self) -> None:
        """Initialize the policy resolution service."""
        self._client = get_retry_client()

    def resolve_policies(
        self,
        template_bundle_id: str,
        workspace_id: str,
        environment: str,
        env_policy_sets: list[str] | None = None,
        stack_id: str | None = None,
    ) -> PolicyResolutionResult:
        """Resolve effective policies for a stack.

        Args:
            template_bundle_id: str of the template bundle.
            workspace_id: str of the workspace.
            environment: Environment key (e.g., 'production').
            env_policy_sets: Optional environment-level policy additions.
            stack_id: Optional stack UUID for linking scan to stack.

        Returns:
            PolicyResolutionResult with manifest and policy artifacts.

        Raises:
            APIError: If the API call fails.
        """
        auth_client = self._client.get_authenticated_client()

        # Build request payload
        payload: dict[str, Any] = {
            "template_bundle_id": str(template_bundle_id),
            "workspace_id": str(workspace_id),
            "environment": environment,
        }

        if env_policy_sets:
            payload["env_policy_sets"] = env_policy_sets

        if stack_id:
            payload["stack_id"] = str(stack_id)

        # Make the API call
        response = auth_client.get_httpx_client().post(
            "/v1/compliance/resolve-policies",
            json=payload,
        )

        if response.status_code != 200:
            raise APIError(
                f"Policy resolution failed: {response.text}",
                status_code=response.status_code,
            )

        response_data = response.json()

        # Handle standard API response wrapper
        if "data" in response_data:
            resolution_data = response_data["data"]
        else:
            resolution_data = response_data

        return PolicyResolutionResult.from_dict(resolution_data)

    def resolve_and_save(
        self,
        run_state: ScanRunState,
        template_bundle_id: str,
        workspace_id: str,
        env_policy_sets: list[str] | None = None,
    ) -> PolicyResolutionResult:
        """Resolve policies and save to run state.

        Args:
            run_state: The current scan run state.
            template_bundle_id: str of the template bundle.
            workspace_id: str of the workspace.
            env_policy_sets: Optional environment-level policy additions.

        Returns:
            PolicyResolutionResult with manifest and policy artifacts.
        """
        run_state.start_phase("resolve_policies")

        try:
            # Resolve policies, passing stack_id if available
            stack_id = run_state.stack_id if hasattr(run_state, "stack_id") else None
            result = self.resolve_policies(
                template_bundle_id=template_bundle_id,
                workspace_id=workspace_id,
                environment=run_state.environment,
                env_policy_sets=env_policy_sets,
                stack_id=stack_id,
            )

            # Save resolution to state
            run_state.save_resolution(result)

            # Update scan_id if returned
            if result.scan_id:
                run_state.scan_id = str(result.scan_id)
                run_state.save()

            run_state.complete_phase(
                "resolve_policies",
                artifact_count=len(result.effective_policy_sets),
                manifest_id=str(result.manifest.id),
            )

            return result

        except Exception as e:
            run_state.fail_phase("resolve_policies", str(e))
            raise

    def build_provenance(
        self,
        resolution: PolicyResolutionResult,
        downloaded_artifacts: dict[str, str] | None = None,
    ) -> PolicyResolutionProvenance:
        """Build provenance from resolution result.

        Args:
            resolution: The policy resolution result.
            downloaded_artifacts: Mapping of artifact key to verified SHA256.

        Returns:
            PolicyResolutionProvenance for audit trail.
        """
        return PolicyResolutionProvenance.from_resolution(
            resolution=resolution,
            downloaded_artifacts=downloaded_artifacts,
        )
