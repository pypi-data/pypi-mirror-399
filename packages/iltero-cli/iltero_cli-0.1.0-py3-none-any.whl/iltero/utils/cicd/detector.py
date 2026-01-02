"""Main CI/CD context detector."""

from __future__ import annotations

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .azure import AzureDevOpsProvider
from .bitbucket import BitbucketPipelinesProvider
from .circleci import CircleCIProvider
from .github import GitHubActionsProvider
from .gitlab import GitLabCIProvider
from .jenkins import JenkinsProvider

# Provider instances in priority order
PROVIDERS = [
    GitHubActionsProvider(),
    GitLabCIProvider(),
    AzureDevOpsProvider(),
    BitbucketPipelinesProvider(),
    JenkinsProvider(),
    CircleCIProvider(),
]


def detect_cicd_context() -> CICDContextSchema | None:
    """Detect CI/CD context from environment variables.

    Automatically detects the CI/CD provider and extracts comprehensive
    context information for audit trails and compliance evidence.

    Supported providers:
    - GitHub Actions
    - GitLab CI
    - Azure DevOps Pipelines
    - Bitbucket Pipelines
    - Jenkins
    - CircleCI

    Returns:
        CICDContextSchema if running in a CI/CD environment, None otherwise.

    Example:
        >>> context = detect_cicd_context()
        >>> if context:
        ...     print(f"Running in {context.provider}")
        ...     print(f"Commit: {context.commit_sha}")
        ...     print(f"Branch: {context.branch}")
    """
    for provider in PROVIDERS:
        if provider.detect():
            return provider.get_context()

    return None


def get_provider_name() -> str | None:
    """Get the name of the detected CI/CD provider.

    Returns:
        Provider name (e.g., 'github', 'gitlab') or None.

    Example:
        >>> provider = get_provider_name()
        >>> if provider:
        ...     print(f"Running in {provider}")
    """
    for provider in PROVIDERS:
        if provider.detect():
            context = provider.get_context()
            return context.provider if context else None

    return None


def is_ci_environment() -> bool:
    """Check if running in any CI/CD environment.

    Returns:
        True if in CI/CD, False otherwise.

    Example:
        >>> if is_ci_environment():
        ...     print("Running in CI/CD")
    """
    return any(provider.detect() for provider in PROVIDERS)
