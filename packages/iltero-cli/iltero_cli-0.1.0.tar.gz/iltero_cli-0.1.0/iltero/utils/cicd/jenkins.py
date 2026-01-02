"""Jenkins CI/CD context extractor."""

from __future__ import annotations

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .base import CICDProvider


class JenkinsProvider(CICDProvider):
    """Jenkins context extractor."""

    def detect(self) -> bool:
        """Detect if running in Jenkins."""
        return bool(self.get_env("JENKINS_URL") or self.get_env("JENKINS_HOME"))

    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from Jenkins environment."""
        # Repository info
        git_url = self.get_env("GIT_URL")

        # Branch information
        git_branch = self.get_env("GIT_BRANCH")
        branch = None
        if git_branch:
            branch = git_branch[7:] if git_branch.startswith("origin/") else git_branch

        # PR/Change info (from common Jenkins PR plugins)
        change_id = self.get_env("CHANGE_ID")
        pr_number = None
        if change_id:
            try:
                pr_number = int(change_id)
            except ValueError:
                pass

        change_target = self.get_env("CHANGE_TARGET")
        change_url = self.get_env("CHANGE_URL")
        change_title = self.get_env("CHANGE_TITLE")
        change_author = self.get_env("CHANGE_AUTHOR")
        change_author_email = self.get_env("CHANGE_AUTHOR_EMAIL")

        # Commit info
        commit_sha = self.get_env("GIT_COMMIT")
        git_committer_name = self.get_env("GIT_COMMITTER_NAME")
        git_committer_email = self.get_env("GIT_COMMITTER_EMAIL")

        # Build info
        job_name = self.get_env("JOB_NAME")
        build_number = self.get_env_int("BUILD_NUMBER")

        # User info (who triggered the build)
        build_user = self.get_env("BUILD_USER")
        build_user_email = self.get_env("BUILD_USER_EMAIL")

        # Triggered by (prefer BUILD_USER, fallback to git committer)
        triggered_by = build_user or change_author or git_committer_name
        triggered_email = build_user_email or change_author_email or git_committer_email

        # Node info
        node_name = self.get_env("NODE_NAME")

        # Build cause/reason
        build_cause = self._get_build_cause()

        return CICDContextSchema(
            repository_url=git_url,
            repository_name=None,  # Not available
            commit_sha=commit_sha,
            commit_message=None,  # Not available in env vars
            branch=branch,
            base_branch=change_target,
            pull_request_number=pr_number,
            pull_request_url=change_url,
            pull_request_title=change_title,
            triggered_by=triggered_by,
            triggered_by_email=triggered_email,
            pipeline_name=job_name,
            pipeline_run_number=build_number,
            job_name=job_name,
            pr_approvers=None,  # Would need API call
            pr_reviewers=None,  # Would need API call
            required_approvals=None,  # Would need API call
            approval_count=None,
            provider="jenkins",
            provider_event=build_cause,
            runner_os=None,
            runner_name=node_name,
        )

    def _get_build_cause(self) -> str | None:
        """Determine what triggered the build.

        Returns:
            Build trigger cause or None.
        """
        # Common Jenkins env vars for build causes
        if self.get_env("ghprbPullId"):
            return "pull_request"
        elif self.get_env("BRANCH_NAME"):
            return "branch"
        elif self.get_env("TAG_NAME"):
            return "tag"

        # Check for manual trigger
        build_user = self.get_env("BUILD_USER")
        if build_user:
            return "manual"

        # SCM polling
        if self.get_env("BUILD_CAUSE") == "SCMTRIGGER":
            return "scm"

        return None
