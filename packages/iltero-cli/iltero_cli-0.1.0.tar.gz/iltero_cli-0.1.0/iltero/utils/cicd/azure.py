"""Azure DevOps Pipelines context extractor."""

from __future__ import annotations

import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .base import CICDProvider


class AzureDevOpsProvider(CICDProvider):
    """Azure DevOps Pipelines context extractor."""

    def detect(self) -> bool:
        """Detect if running in Azure DevOps."""
        return bool(self.get_env("AZURE_HTTP_USER_AGENT") or self.get_env("TF_BUILD"))

    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from Azure DevOps environment."""
        # Repository info
        repo_url = self.get_env("BUILD_REPOSITORY_URI")
        repo_name = self.get_env("BUILD_REPOSITORY_NAME")

        # PR info
        pr_number_str = self.get_env("SYSTEM_PULLREQUEST_PULLREQUESTNUMBER")
        pr_number = int(pr_number_str) if pr_number_str else None
        pr_id = self.get_env("SYSTEM_PULLREQUEST_PULLREQUESTID")

        # Branch info
        branch = self.get_env("BUILD_SOURCEBRANCHNAME")
        base_branch = self.get_env("SYSTEM_PULLREQUEST_TARGETBRANCH")

        # Commit info
        commit_sha = self.get_env("BUILD_SOURCEVERSION")
        commit_message = self.get_env("BUILD_SOURCEVERSIONMESSAGE")

        # Build info
        build_name = self.get_env("BUILD_DEFINITIONNAME")
        build_id = self.get_env_int("BUILD_BUILDID")

        # Job info
        job_name = self.get_env("AGENT_JOBNAME")

        # User info
        requested_for = self.get_env("BUILD_REQUESTEDFOR")
        requested_for_email = self.get_env("BUILD_REQUESTEDFOREMAIL")

        # Build reason (trigger type)
        build_reason = self.get_env("BUILD_REASON")

        # Agent info
        agent_os = self.get_env("AGENT_OS")
        agent_name = self.get_env("AGENT_NAME")

        # Get collection and project info
        collection_uri = self.get_env("SYSTEM_COLLECTIONURI")
        team_project = self.get_env("SYSTEM_TEAMPROJECT")

        # PR URL construction
        pr_url = None
        if pr_id and repo_url and collection_uri and team_project:
            # Azure DevOps PR URL pattern
            pr_url = (
                f"{collection_uri.rstrip('/')}/{team_project}/_git/{repo_name}/pullrequest/{pr_id}"
            )

        # Fetch additional data from Azure DevOps API if token available
        api_data = self._fetch_api_data(
            collection_uri, team_project, repo_name, pr_number, requested_for
        )

        # Use API data to enrich context
        if not requested_for_email and api_data.get("user_email"):
            requested_for_email = api_data.get("user_email")
        pr_title = api_data.get("pr_title")
        pr_approvers = api_data.get("pr_approvers")
        required_approvals = api_data.get("required_approvals")

        return CICDContextSchema(
            repository_url=repo_url,
            repository_name=repo_name,
            commit_sha=commit_sha,
            commit_message=commit_message,
            branch=branch,
            base_branch=base_branch,
            pull_request_number=pr_number,
            pull_request_url=pr_url,
            pull_request_title=pr_title,
            triggered_by=requested_for,
            triggered_by_email=requested_for_email,
            pipeline_name=build_name,
            pipeline_run_number=build_id,
            job_name=job_name,
            pr_approvers=pr_approvers,
            pr_reviewers=None,
            required_approvals=required_approvals,
            approval_count=len(pr_approvers) if pr_approvers else None,
            provider="azure_devops",
            provider_event=build_reason,
            runner_os=agent_os,
            runner_name=agent_name,
        )

    def _fetch_api_data(
        self,
        collection_uri: str | None,
        team_project: str | None,
        repo_name: str | None,
        pr_number: int | None,
        user_name: str | None,
    ) -> dict:
        """Fetch additional data from Azure DevOps API.

        Args:
            collection_uri: Azure DevOps collection URI.
            team_project: Team project name.
            repo_name: Repository name.
            pr_number: Pull request number.
            user_name: User display name.

        Returns:
            Dictionary with API data (empty if API calls fail).
        """
        result = {}

        # Check if token is available
        token = self.get_env("SYSTEM_ACCESSTOKEN")
        if not token or not collection_uri or not team_project:
            return result

        try:
            # Fetch PR information if available
            if pr_number and repo_name:
                pr_data = self._fetch_pr_info(
                    token,
                    collection_uri,
                    team_project,
                    repo_name,
                    pr_number,
                )
                if pr_data.get("title"):
                    result["pr_title"] = pr_data["title"]
                if pr_data.get("approvers"):
                    result["pr_approvers"] = pr_data["approvers"]
                if pr_data.get("required_approvals") is not None:
                    result["required_approvals"] = pr_data["required_approvals"]

        except Exception:
            # Silently fail - API data is optional enhancement
            pass

        return result

    def _fetch_pr_info(
        self,
        token: str,
        collection_uri: str,
        team_project: str,
        repo_name: str,
        pr_number: int,
    ) -> dict:
        """Fetch PR information from Azure DevOps API.

        Args:
            token: Azure DevOps access token.
            collection_uri: Collection URI.
            team_project: Team project name.
            repo_name: Repository name.
            pr_number: Pull request number.

        Returns:
            Dict with PR title, approvers, and required approvals.
        """
        result = {}

        try:
            # Encode token for Basic auth
            auth_str = f":{token}"
            b64_auth = base64.b64encode(auth_str.encode()).decode()

            headers = {
                "Authorization": f"Basic {b64_auth}",
                "Accept": "application/json",
            }

            # Fetch PR details
            url = (
                f"{collection_uri.rstrip('/')}/{team_project}/"
                f"_apis/git/repositories/{repo_name}/"
                f"pullrequests/{pr_number}?api-version=7.0"
            )
            req = Request(url, headers=headers)

            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())

                # Extract PR title
                if "title" in data:
                    result["title"] = data["title"]

                # Extract approvers from reviewers
                reviewers = data.get("reviewers", [])
                approvers = [
                    reviewer["displayName"]
                    for reviewer in reviewers
                    if reviewer.get("vote") == 10  # 10 = approved
                ]
                if approvers:
                    result["approvers"] = approvers

            # Fetch branch policy to get required approvals
            policy_data = self._fetch_branch_policy(token, collection_uri, team_project, repo_name)
            if policy_data.get("required_approvals") is not None:
                result["required_approvals"] = policy_data["required_approvals"]

        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            pass

        return result

    def _fetch_branch_policy(
        self,
        token: str,
        collection_uri: str,
        team_project: str,
        repo_name: str,
    ) -> dict:
        """Fetch branch policy for required approvals.

        Args:
            token: Azure DevOps access token.
            collection_uri: Collection URI.
            team_project: Team project name.
            repo_name: Repository name.

        Returns:
            Dict with required_approvals count.
        """
        result = {}

        try:
            # Encode token for Basic auth
            auth_str = f":{token}"
            b64_auth = base64.b64encode(auth_str.encode()).decode()

            headers = {
                "Authorization": f"Basic {b64_auth}",
                "Accept": "application/json",
            }

            # Fetch repository ID first
            repo_url = (
                f"{collection_uri.rstrip('/')}/{team_project}/"
                f"_apis/git/repositories/{repo_name}?api-version=7.0"
            )
            req = Request(repo_url, headers=headers)

            with urlopen(req, timeout=5) as response:
                repo_data = json.loads(response.read().decode())
                repo_id = repo_data.get("id")

            if not repo_id:
                return result

            # Fetch policies for the repository
            policy_url = (
                f"{collection_uri.rstrip('/')}/{team_project}/"
                f"_apis/policy/configurations?api-version=7.0"
            )
            req = Request(policy_url, headers=headers)

            with urlopen(req, timeout=5) as response:
                policies = json.loads(response.read().decode())

                # Find approval policy
                for policy in policies.get("value", []):
                    policy_type = policy.get("type", {})
                    # Approval policy type ID
                    if policy_type.get("id") == ("fa4e907d-c16b-4a4c-9dfa-4906e5d171dd"):
                        settings = policy.get("settings", {})
                        min_approvers = settings.get("minimumApproverCount")
                        if min_approvers is not None:
                            result["required_approvals"] = min_approvers
                            break

        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            pass

        return result
