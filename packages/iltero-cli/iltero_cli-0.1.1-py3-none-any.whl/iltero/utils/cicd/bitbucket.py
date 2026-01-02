"""Bitbucket Pipelines context extractor."""

from __future__ import annotations

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .base import CICDProvider


class BitbucketPipelinesProvider(CICDProvider):
    """Bitbucket Pipelines context extractor."""

    def detect(self) -> bool:
        """Detect if running in Bitbucket Pipelines."""
        return bool(self.get_env("BITBUCKET_BUILD_NUMBER"))

    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from Bitbucket Pipelines environment."""
        # Repository info
        workspace = self.get_env("BITBUCKET_WORKSPACE")
        repo_slug = self.get_env("BITBUCKET_REPO_SLUG")
        repo_full_name = self.get_env("BITBUCKET_REPO_FULL_NAME")

        repo_name = repo_full_name or (
            f"{workspace}/{repo_slug}" if workspace and repo_slug else None
        )

        repo_url = None
        if workspace and repo_slug:
            repo_url = f"https://bitbucket.org/{workspace}/{repo_slug}"

        # PR info
        pr_id = self.get_env("BITBUCKET_PR_ID")
        pr_number = int(pr_id) if pr_id else None

        # Branch info
        branch = self.get_env("BITBUCKET_BRANCH")
        base_branch = self.get_env("BITBUCKET_PR_DESTINATION_BRANCH")

        # Commit info
        commit_sha = self.get_env("BITBUCKET_COMMIT")

        # Build info
        build_number = self.get_env_int("BITBUCKET_BUILD_NUMBER")
        pipeline_uuid = self.get_env("BITBUCKET_PIPELINE_UUID")

        # Step info
        step_uuid = self.get_env("BITBUCKET_STEP_UUID")

        # PR URL
        pr_url = None
        if pr_number and workspace and repo_slug:
            pr_url = f"https://bitbucket.org/{workspace}/{repo_slug}/pull-requests/{pr_number}"

        # Deployment environment
        deployment_env = self.get_env("BITBUCKET_DEPLOYMENT_ENVIRONMENT")

        return CICDContextSchema(
            repository_url=repo_url,
            repository_name=repo_name,
            commit_sha=commit_sha,
            commit_message=None,  # Not available
            branch=branch,
            base_branch=base_branch,
            pull_request_number=pr_number,
            pull_request_url=pr_url,
            pull_request_title=None,  # Not available
            triggered_by=None,  # Not available
            triggered_by_email=None,
            pipeline_name=pipeline_uuid,
            pipeline_run_number=build_number,
            job_name=step_uuid,
            pr_approvers=None,  # Would need API call
            pr_reviewers=None,  # Would need API call
            required_approvals=None,  # Would need API call
            approval_count=None,
            provider="bitbucket",
            provider_event=deployment_env,
            runner_os=None,
            runner_name=None,
        )
