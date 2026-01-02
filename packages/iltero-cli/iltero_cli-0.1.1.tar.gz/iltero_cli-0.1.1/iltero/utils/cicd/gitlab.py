"""GitLab CI context extractor."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .base import CICDProvider


class GitLabCIProvider(CICDProvider):
    """GitLab CI context extractor."""

    def detect(self) -> bool:
        """Detect if running in GitLab CI."""
        return self.get_env("GITLAB_CI") == "true"

    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from GitLab CI environment."""
        # Repository info
        repo_url = self.get_env("CI_PROJECT_URL")
        repo_name = self.get_env("CI_PROJECT_PATH")

        # Merge request info
        mr_iid = self.get_env("CI_MERGE_REQUEST_IID")
        mr_number = int(mr_iid) if mr_iid else None

        # Branch info
        branch = self.get_env("CI_COMMIT_REF_NAME")
        base_branch = self.get_env("CI_MERGE_REQUEST_TARGET_BRANCH_NAME")

        # Commit info
        commit_sha = self.get_env("CI_COMMIT_SHA")
        commit_message = self.get_env("CI_COMMIT_MESSAGE")
        commit_title = self.get_env("CI_COMMIT_TITLE")

        # Pipeline info
        pipeline_name = self.get_env("CI_PIPELINE_NAME")
        pipeline_iid = self.get_env("CI_PIPELINE_IID")
        pipeline_number = int(pipeline_iid) if pipeline_iid else None

        # Job info
        job_name = self.get_env("CI_JOB_NAME")

        # User info
        user_login = self.get_env("GITLAB_USER_LOGIN")
        user_email = self.get_env("GITLAB_USER_EMAIL")

        # MR details
        mr_url = self.get_env("CI_MERGE_REQUEST_PROJECT_URL")
        mr_title = self.get_env("CI_MERGE_REQUEST_TITLE")

        # Pipeline source
        pipeline_source = self.get_env("CI_PIPELINE_SOURCE")

        # Runner info
        runner_description = self.get_env("CI_RUNNER_DESCRIPTION")

        # Approval info (may be in env if configured)
        # GitLab can expose MR approval data via custom env vars
        approvers = self._get_approvers()

        # Fetch additional data from GitLab API if token is available
        api_data = self._fetch_api_data(repo_name, mr_number, user_login, user_email)

        # Use API data to enrich context
        if not user_email and api_data.get("user_email"):
            user_email = api_data.get("user_email")
        if not approvers and api_data.get("approvers"):
            approvers = api_data.get("approvers")
        required_approvals = api_data.get("required_approvals")

        return CICDContextSchema(
            repository_url=repo_url,
            repository_name=repo_name,
            commit_sha=commit_sha,
            commit_message=commit_message or commit_title,
            branch=branch,
            base_branch=base_branch,
            pull_request_number=mr_number,
            pull_request_url=mr_url,
            pull_request_title=mr_title,
            triggered_by=user_login,
            triggered_by_email=user_email,
            pipeline_name=pipeline_name,
            pipeline_run_number=pipeline_number,
            job_name=job_name,
            pr_approvers=approvers,
            pr_reviewers=None,
            required_approvals=required_approvals,
            approval_count=len(approvers) if approvers else None,
            provider="gitlab",
            provider_event=pipeline_source,
            runner_os=None,
            runner_name=runner_description,
        )

    def _get_approvers(self) -> list[str] | None:
        """Get MR approvers if available in environment.

        GitLab can expose this via CI_MERGE_REQUEST_APPROVED_BY or
        custom variables.
        """
        # Try common custom variable patterns
        approvers_str = self.get_env("CI_MERGE_REQUEST_APPROVED_BY")
        if approvers_str:
            return self.get_env_list("CI_MERGE_REQUEST_APPROVED_BY")

        return None

    def _fetch_api_data(
        self,
        project_path: str | None,
        mr_iid: int | None,
        username: str | None,
        user_email: str | None,
    ) -> dict:
        """Fetch additional data from GitLab API.

        Args:
            project_path: Project path (e.g., 'group/project').
            mr_iid: Merge request IID.
            username: GitLab username.
            user_email: User email from env (may be None).

        Returns:
            Dictionary with API data (empty if API calls fail).
        """
        result = {}

        # Check if token is available
        token = self.get_env("CI_JOB_TOKEN") or self.get_env("GITLAB_TOKEN")
        gitlab_url = self.get_env("CI_SERVER_URL") or "https://gitlab.com"

        if not token or not project_path:
            return result

        try:
            # Fetch user email if not in environment
            if not user_email and username:
                email = self._fetch_user_email(token, gitlab_url, username)
                if email:
                    result["user_email"] = email

            # Fetch MR approval information
            if mr_iid:
                approval_data = self._fetch_mr_approvals(token, gitlab_url, project_path, mr_iid)
                if approval_data.get("approvers"):
                    result["approvers"] = approval_data["approvers"]
                if approval_data.get("required_approvals") is not None:
                    result["required_approvals"] = approval_data["required_approvals"]

        except Exception:
            # Silently fail - API data is optional enhancement
            pass

        return result

    def _fetch_user_email(self, token: str, gitlab_url: str, username: str) -> str | None:
        """Fetch user email from GitLab API.

        Args:
            token: GitLab API token.
            gitlab_url: GitLab instance URL.
            username: GitLab username.

        Returns:
            User email or None.
        """
        try:
            headers = {
                "PRIVATE-TOKEN": token,
                "Accept": "application/json",
            }

            # Search for user by username
            url = f"{gitlab_url}/api/v4/users?username={username}"
            req = Request(url, headers=headers)

            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                if data and len(data) > 0:
                    return data[0].get("email")

        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            return None

        return None

    def _fetch_mr_approvals(
        self,
        token: str,
        gitlab_url: str,
        project_path: str,
        mr_iid: int,
    ) -> dict:
        """Fetch MR approval information from GitLab API.

        Args:
            token: GitLab API token.
            gitlab_url: GitLab instance URL.
            project_path: Project path (URL-encoded).
            mr_iid: Merge request IID.

        Returns:
            Dict with approvers and required_approvals.
        """
        result = {}

        try:
            headers = {
                "PRIVATE-TOKEN": token,
                "Accept": "application/json",
            }

            # URL-encode project path
            from urllib.parse import quote

            encoded_project = quote(project_path, safe="")

            # Fetch MR approvals
            url = (
                f"{gitlab_url}/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}/approvals"
            )
            req = Request(url, headers=headers)

            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

                # Extract approvers
                approved_by = data.get("approved_by", [])
                if approved_by:
                    approvers = [
                        user["user"]["username"]
                        for user in approved_by
                        if "user" in user and "username" in user["user"]
                    ]
                    if approvers:
                        result["approvers"] = approvers

                # Extract required approvals
                approvals_required = data.get("approvals_required")
                if approvals_required is not None:
                    result["required_approvals"] = approvals_required

        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            pass

        return result
