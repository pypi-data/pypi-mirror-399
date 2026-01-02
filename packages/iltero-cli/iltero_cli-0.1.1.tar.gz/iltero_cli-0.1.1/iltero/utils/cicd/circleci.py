"""CircleCI context extractor."""

from __future__ import annotations

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .base import CICDProvider


class CircleCIProvider(CICDProvider):
    """CircleCI context extractor."""

    def detect(self) -> bool:
        """Detect if running in CircleCI."""
        return self.get_env("CIRCLECI") == "true"

    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from CircleCI environment."""
        # Repository info
        repo_url = self.get_env("CIRCLE_REPOSITORY_URL")
        username = self.get_env("CIRCLE_PROJECT_USERNAME")
        reponame = self.get_env("CIRCLE_PROJECT_REPONAME")
        repo_name = f"{username}/{reponame}" if username and reponame else None

        # PR info
        pr_number_str = self.get_env("CIRCLE_PR_NUMBER")
        pr_number = int(pr_number_str) if pr_number_str else None
        pr_url = self.get_env("CIRCLE_PULL_REQUEST")

        # Branch info
        branch = self.get_env("CIRCLE_BRANCH")

        # Commit info
        commit_sha = self.get_env("CIRCLE_SHA1")

        # Build/Pipeline info
        workflow_id = self.get_env("CIRCLE_WORKFLOW_ID")
        build_num = self.get_env_int("CIRCLE_BUILD_NUM")

        # Job info
        job_name = self.get_env("CIRCLE_JOB")

        # User info
        username = self.get_env("CIRCLE_USERNAME")
        pr_username = self.get_env("CIRCLE_PR_USERNAME")
        triggered_by = pr_username or username

        # Tag if available
        tag = self.get_env("CIRCLE_TAG")

        return CICDContextSchema(
            repository_url=repo_url,
            repository_name=repo_name,
            commit_sha=commit_sha,
            commit_message=None,  # Not available
            branch=branch,
            base_branch=None,  # Not directly available
            pull_request_number=pr_number,
            pull_request_url=pr_url,
            pull_request_title=None,  # Not available
            triggered_by=triggered_by,
            triggered_by_email=None,  # Not available
            pipeline_name=workflow_id,
            pipeline_run_number=build_num,
            job_name=job_name,
            pr_approvers=None,  # Would need API call
            pr_reviewers=None,  # Would need API call
            required_approvals=None,  # Would need API call
            approval_count=None,
            provider="circleci",
            provider_event="tag" if tag else "branch",
            runner_os=None,
            runner_name=None,
        )
