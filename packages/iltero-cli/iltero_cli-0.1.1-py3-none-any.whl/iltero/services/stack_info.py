"""Stack information retrieval service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iltero.api_client.iltero_api_client.api.stacks import get_stack
from iltero.core.exceptions import IlteroError
from iltero.core.http import get_retry_client


class StackNotFoundError(IlteroError):
    """Stack not found."""

    def __init__(self, stack_id: str):
        super().__init__(f"Stack '{stack_id}' not found", exit_code=13)
        self.stack_id = stack_id


class StackInfoError(IlteroError):
    """Error retrieving stack information."""

    def __init__(self, stack_id: str, message: str):
        super().__init__(f"Error retrieving stack '{stack_id}': {message}", exit_code=14)
        self.stack_id = stack_id


@dataclass
class StackInfo:
    """Stack information for compliance scanning."""

    stack_id: str
    name: str
    workspace_id: str
    template_bundle_id: str | None
    environment: str | None
    policy_sets: list[str]
    repository_id: str | None
    default_branch: str | None

    @classmethod
    def from_api_response(cls, stack_id: str, data: dict[str, Any]) -> StackInfo:
        """Create StackInfo from API response data.

        Args:
            stack_id: The stack ID used in the request.
            data: The 'data' field from API response.

        Returns:
            StackInfo instance.
        """
        return cls(
            stack_id=stack_id,
            name=data.get("name", ""),
            workspace_id=data.get("workspace_id", ""),
            template_bundle_id=data.get("template_bundle_id"),
            environment=data.get("environment"),
            policy_sets=data.get("policy_sets", []),
            repository_id=data.get("repository_id"),
            default_branch=data.get("default_branch"),
        )


def get_stack_info(stack_id: str) -> StackInfo:
    """Retrieve stack information from the API.

    Args:
        stack_id: The stack ID to retrieve.

    Returns:
        StackInfo with stack details.

    Raises:
        StackNotFoundError: If stack doesn't exist.
        StackInfoError: If there's an error retrieving stack info.
    """
    client = get_retry_client().get_authenticated_client()

    try:
        response = get_stack.sync_detailed(
            stack_id=stack_id,
            client=client,
        )

        if response.status_code == 404:
            raise StackNotFoundError(stack_id)

        if response.status_code != 200:
            raise StackInfoError(
                stack_id,
                f"HTTP {response.status_code}",
            )

        if response.parsed is None:
            raise StackInfoError(stack_id, "Empty response from API")

        # Parse the response
        response_dict = response.parsed.to_dict()

        # Handle standard API response wrapper
        data = response_dict.get("data", response_dict)

        return StackInfo.from_api_response(stack_id, data)

    except (StackNotFoundError, StackInfoError):
        raise

    except Exception as e:
        raise StackInfoError(stack_id, str(e))
