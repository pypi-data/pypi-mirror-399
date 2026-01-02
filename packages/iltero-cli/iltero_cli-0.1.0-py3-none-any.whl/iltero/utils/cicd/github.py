"""GitHub Actions CI/CD context extractor."""

from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)

from .base import CICDProvider


class GitHubActionsProvider(CICDProvider):
    """GitHub Actions context extractor."""

    def detect(self) -> bool:
        """Detect if running in GitHub Actions."""
        return self.get_env("GITHUB_ACTIONS") == "true"

    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from GitHub Actions environment."""
        # Repository info
        repo = self.get_env("GITHUB_REPOSITORY", "")
        repo_url = f"https://github.com/{repo}" if repo else None

        # Parse PR number from GITHUB_REF or event payload
        pr_number = self._get_pr_number()
        pr_url = f"https://github.com/{repo}/pull/{pr_number}" if (pr_number and repo) else None

        # Branch information
        branch = self._get_branch()
        base_branch = self.get_env("GITHUB_BASE_REF")

        # Workflow information
        workflow = self.get_env("GITHUB_WORKFLOW")
        run_number = self.get_env_int("GITHUB_RUN_NUMBER")
        job = self.get_env("GITHUB_JOB")

        # Actor information
        actor = self.get_env("GITHUB_ACTOR")

        # Commit information
        commit_sha = self.get_env("GITHUB_SHA")
        commit_message = self._get_commit_message()

        # Runner information
        runner_os = self.get_env("RUNNER_OS")
        runner_name = self.get_env("RUNNER_NAME")

        # Event type
        event = self.get_env("GITHUB_EVENT_NAME")

        # PR review information (from event payload if available)
        pr_title = self._get_pr_title()
        pr_approvers, pr_reviewers = self._get_pr_review_info()

        # Fetch additional data from GitHub API if token is available
        api_data = self._fetch_api_data(repo, pr_number, branch)

        # Use API data to enrich context
        triggered_by_email = api_data.get("actor_email")
        required_approvals = api_data.get("required_approvals")

        return CICDContextSchema(
            repository_url=repo_url,
            repository_name=repo or None,
            commit_sha=commit_sha,
            commit_message=commit_message,
            branch=branch,
            base_branch=base_branch,
            pull_request_number=pr_number,
            pull_request_url=pr_url,
            pull_request_title=pr_title,
            triggered_by=actor,
            triggered_by_email=triggered_by_email,
            pipeline_name=workflow,
            pipeline_run_number=run_number,
            job_name=job,
            pr_approvers=pr_approvers,
            pr_reviewers=pr_reviewers,
            required_approvals=required_approvals,
            approval_count=len(pr_approvers) if pr_approvers else None,
            provider="github",
            provider_event=event,
            runner_os=runner_os,
            runner_name=runner_name,
        )

    def _get_pr_number(self) -> int | None:
        """Extract PR number from GITHUB_REF or event payload."""
        # Try GITHUB_REF first (refs/pull/123/merge)
        ref = self.get_env("GITHUB_REF")
        if ref and ref.startswith("refs/pull/"):
            parts = ref.split("/")
            if len(parts) >= 3:
                try:
                    return int(parts[2])
                except ValueError:
                    pass

        # Try event payload
        event_path = self.get_env("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path) as f:
                    event_data = json.load(f)
                    pr = event_data.get("pull_request", {})
                    number = pr.get("number")
                    if number:
                        return int(number)
            except (OSError, json.JSONDecodeError, ValueError):
                pass

        return None

    def _get_branch(self) -> str | None:
        """Get current branch name."""
        # GITHUB_HEAD_REF is set for PRs
        branch = self.get_env("GITHUB_HEAD_REF")
        if branch:
            return branch

        # GITHUB_REF_NAME for direct pushes
        ref_name = self.get_env("GITHUB_REF_NAME")
        if ref_name:
            return ref_name

        # Parse from GITHUB_REF
        ref = self.get_env("GITHUB_REF")
        if ref and ref.startswith("refs/heads/"):
            return ref.replace("refs/heads/", "")

        return None

    def _get_commit_message(self) -> str | None:
        """Get commit message from event payload."""
        event_path = self.get_env("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path) as f:
                    event_data = json.load(f)

                    # For push events
                    head_commit = event_data.get("head_commit", {})
                    message = head_commit.get("message")
                    if message:
                        return message

                    # For PR events
                    pr = event_data.get("pull_request", {})
                    title = pr.get("title")
                    if title:
                        return title

            except (OSError, json.JSONDecodeError):
                pass

        return None

    def _get_pr_title(self) -> str | None:
        """Get PR title from event payload."""
        event_path = self.get_env("GITHUB_EVENT_PATH")
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path) as f:
                    event_data = json.load(f)
                    pr = event_data.get("pull_request", {})
                    return pr.get("title")
            except (OSError, json.JSONDecodeError):
                pass

        return None

    def _get_pr_review_info(
        self,
    ) -> tuple[list[str] | None, list[str] | None]:
        """Get PR approvers and reviewers from event payload.

        Returns:
            Tuple of (approvers, reviewers) lists or (None, None).
        """
        event_path = self.get_env("GITHUB_EVENT_PATH")
        if not event_path or not os.path.exists(event_path):
            return None, None

        try:
            with open(event_path) as f:
                event_data = json.load(f)
                pr = event_data.get("pull_request", {})

                # Get requested reviewers
                reviewers = set()
                requested_reviewers = pr.get("requested_reviewers", [])
                for reviewer in requested_reviewers:
                    if isinstance(reviewer, dict):
                        login = reviewer.get("login")
                        if login:
                            reviewers.add(login)

                # Get reviews (includes approvals)
                approvers = set()
                reviews = event_data.get("reviews", [])
                for review in reviews:
                    if isinstance(review, dict):
                        user = review.get("user", {})
                        login = user.get("login") if isinstance(user, dict) else None
                        state = review.get("state")

                        if login:
                            reviewers.add(login)
                            if state == "APPROVED":
                                approvers.add(login)

                return (
                    list(approvers) if approvers else None,
                    list(reviewers) if reviewers else None,
                )

        except (OSError, json.JSONDecodeError):
            return None, None

    def _fetch_api_data(
        self,
        repo: str | None,
        pr_number: int | None,
        branch: str | None,
    ) -> dict:
        """Fetch additional data from GitHub API.

        Args:
            repo: Repository in owner/name format.
            pr_number: Pull request number if available.
            branch: Branch name if available.

        Returns:
            Dictionary with API data (empty if API calls fail).
        """
        result = {}

        # Check if token is available
        token = self.get_env("GITHUB_TOKEN")
        if not token or not repo:
            return result

        try:
            # Fetch user email for actor
            actor = self.get_env("GITHUB_ACTOR")
            if actor:
                actor_email = self._fetch_user_email(token, actor)
                if actor_email:
                    result["actor_email"] = actor_email

            # Fetch branch protection rules for required approvals
            if branch:
                required_approvals = self._fetch_required_approvals(token, repo, branch)
                if required_approvals is not None:
                    result["required_approvals"] = required_approvals

        except Exception:
            # Silently fail - API data is optional enhancement
            pass

        return result

    def _fetch_user_email(self, token: str, username: str) -> str | None:
        """Fetch user email from GitHub API.

        Args:
            token: GitHub API token.
            username: GitHub username.

        Returns:
            User email or None.
        """
        try:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            req = Request(
                f"https://api.github.com/users/{username}",
                headers=headers,
            )

            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get("email")

        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            return None

    def _fetch_required_approvals(self, token: str, repo: str, branch: str) -> int | None:
        """Fetch required approvals count from branch protection.

        Args:
            token: GitHub API token.
            repo: Repository in owner/name format.
            branch: Branch name.

        Returns:
            Required approvals count or None.
        """
        try:
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            url = f"https://api.github.com/repos/{repo}/branches/{branch}/protection"
            req = Request(url, headers=headers)

            with urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                required_pr_reviews = data.get("required_pull_request_reviews", {})
                return required_pr_reviews.get("required_approving_review_count")

        except (HTTPError, URLError, json.JSONDecodeError, TimeoutError):
            return None
