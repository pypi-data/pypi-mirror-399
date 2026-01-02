"""Tests for CI/CD context detection."""

from __future__ import annotations

import json
from unittest.mock import mock_open, patch

from iltero.utils.cicd import (
    detect_cicd_context,
    get_provider_name,
    is_ci_environment,
)


class MockResponse:
    """Mock response for urlopen in tests."""

    def __init__(self, data: bytes):
        """Initialize mock response with data."""
        self.data = data

    def read(self):
        """Return mock data."""
        return self.data

    def __enter__(self):
        """Support context manager."""
        return self

    def __exit__(self, *args):
        """Support context manager."""
        pass


class TestCICDDetection:
    """Test CI/CD environment detection."""

    def test_no_ci_environment(self):
        """Test that None is returned when not in CI/CD."""
        with patch.dict("os.environ", {}, clear=True):
            assert detect_cicd_context() is None
            assert not is_ci_environment()
            assert get_provider_name() is None

    def test_github_actions_detection(self):
        """Test GitHub Actions environment detection."""
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_SHA": "abc123",
            "GITHUB_ACTOR": "testuser",
            "GITHUB_WORKFLOW": "CI",
            "GITHUB_RUN_NUMBER": "42",
            "GITHUB_REF": "refs/heads/main",
            "RUNNER_OS": "Linux",
        }

        with patch.dict("os.environ", env, clear=True):
            assert is_ci_environment()
            assert get_provider_name() == "github"

            context = detect_cicd_context()
            assert context is not None
            assert context.provider == "github"
            assert context.repository_name == "owner/repo"
            assert context.commit_sha == "abc123"
            assert context.triggered_by == "testuser"
            assert context.branch == "main"
            assert context.pipeline_run_number == 42

    def test_github_actions_pr_detection(self):
        """Test GitHub Actions PR environment."""
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_REF": "refs/pull/123/merge",
            "GITHUB_HEAD_REF": "feature-branch",
            "GITHUB_BASE_REF": "main",
        }

        with patch.dict("os.environ", env, clear=True):
            context = detect_cicd_context()
            assert context is not None
            assert context.pull_request_number == 123
            assert context.branch == "feature-branch"
            assert context.base_branch == "main"

    def test_gitlab_ci_detection(self):
        """Test GitLab CI environment detection."""
        env = {
            "GITLAB_CI": "true",
            "CI_PROJECT_URL": "https://gitlab.com/owner/repo",
            "CI_PROJECT_PATH": "owner/repo",
            "CI_COMMIT_SHA": "def456",
            "CI_COMMIT_REF_NAME": "develop",
            "GITLAB_USER_LOGIN": "gitlab_user",
            "GITLAB_USER_EMAIL": "user@example.com",
            "CI_PIPELINE_IID": "100",
            "CI_JOB_NAME": "test-job",
        }

        with patch.dict("os.environ", env, clear=True):
            assert is_ci_environment()
            assert get_provider_name() == "gitlab"

            context = detect_cicd_context()
            assert context is not None
            assert context.provider == "gitlab"
            assert context.repository_name == "owner/repo"
            assert context.commit_sha == "def456"
            assert context.branch == "develop"
            assert context.triggered_by == "gitlab_user"
            assert context.triggered_by_email == "user@example.com"

    def test_azure_devops_detection(self):
        """Test Azure DevOps environment detection."""
        env = {
            "TF_BUILD": "True",
            "BUILD_REPOSITORY_URI": ("https://dev.azure.com/org/project/_git/repo"),
            "BUILD_REPOSITORY_NAME": "repo",
            "BUILD_SOURCEVERSION": "ghi789",
            "BUILD_SOURCEBRANCHNAME": "master",
            "BUILD_REQUESTEDFOR": "azure_user",
            "BUILD_REQUESTEDFOREMAIL": "azure@example.com",
            "BUILD_BUILDID": "200",
            "AGENT_OS": "Windows_NT",
        }

        with patch.dict("os.environ", env, clear=True):
            assert is_ci_environment()
            assert get_provider_name() == "azure_devops"

            context = detect_cicd_context()
            assert context is not None
            assert context.provider == "azure_devops"
            assert context.repository_name == "repo"
            assert context.commit_sha == "ghi789"

    def test_bitbucket_detection(self):
        """Test Bitbucket Pipelines environment detection."""
        env = {
            "BITBUCKET_BUILD_NUMBER": "50",
            "BITBUCKET_WORKSPACE": "workspace",
            "BITBUCKET_REPO_SLUG": "repo",
            "BITBUCKET_COMMIT": "jkl012",
            "BITBUCKET_BRANCH": "staging",
        }

        with patch.dict("os.environ", env, clear=True):
            assert is_ci_environment()
            assert get_provider_name() == "bitbucket"

            context = detect_cicd_context()
            assert context is not None
            assert context.provider == "bitbucket"
            assert context.repository_name == "workspace/repo"
            assert context.commit_sha == "jkl012"

    def test_jenkins_detection(self):
        """Test Jenkins environment detection."""
        env = {
            "JENKINS_URL": "https://jenkins.example.com",
            "GIT_COMMIT": "mno345",
            "GIT_BRANCH": "origin/production",
            "JOB_NAME": "deploy-job",
            "BUILD_NUMBER": "300",
            "BUILD_USER": "jenkins_user",
        }

        with patch.dict("os.environ", env, clear=True):
            assert is_ci_environment()
            assert get_provider_name() == "jenkins"

            context = detect_cicd_context()
            assert context is not None
            assert context.provider == "jenkins"
            assert context.commit_sha == "mno345"
            assert context.branch == "production"  # origin/ prefix removed
            assert context.triggered_by == "jenkins_user"

    def test_circleci_detection(self):
        """Test CircleCI environment detection."""
        env = {
            "CIRCLECI": "true",
            "CIRCLE_SHA1": "pqr678",
            "CIRCLE_BRANCH": "hotfix",
            "CIRCLE_PROJECT_USERNAME": "circle_owner",
            "CIRCLE_PROJECT_REPONAME": "circle_repo",
            "CIRCLE_BUILD_NUM": "400",
            "CIRCLE_USERNAME": "circle_user",
        }

        with patch.dict("os.environ", env, clear=True):
            assert is_ci_environment()
            assert get_provider_name() == "circleci"

            context = detect_cicd_context()
            assert context is not None
            assert context.provider == "circleci"
            assert context.commit_sha == "pqr678"
            assert context.branch == "hotfix"


class TestGitHubActionsEventPayload:
    """Test GitHub Actions event payload parsing."""

    def test_pr_info_from_event_payload(self):
        """Test extracting PR info from GitHub event payload."""
        event_data = {
            "pull_request": {
                "number": 456,
                "title": "Add new feature",
                "requested_reviewers": [
                    {"login": "reviewer1"},
                    {"login": "reviewer2"},
                ],
            },
            "reviews": [
                {"user": {"login": "reviewer1"}, "state": "APPROVED"},
                {"user": {"login": "reviewer3"}, "state": "COMMENTED"},
            ],
        }

        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_EVENT_PATH": "/tmp/github_event.json",
        }

        with patch.dict("os.environ", env, clear=True):
            mock_data = json.dumps(event_data)
            with patch("builtins.open", mock_open(read_data=mock_data)):
                with patch("os.path.exists", return_value=True):
                    context = detect_cicd_context()
                    assert context is not None
                    assert context.pull_request_number == 456
                    assert context.pull_request_title == "Add new feature"
                    assert "reviewer1" in (context.pr_approvers or [])
                    assert "reviewer1" in (context.pr_reviewers or [])
                    assert "reviewer2" in (context.pr_reviewers or [])

    def test_commit_message_from_push_event(self):
        """Test extracting commit message from push event."""
        event_data = {
            "head_commit": {
                "message": "Fix critical bug",
            }
        }

        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_PATH": "/tmp/github_event.json",
        }

        with patch.dict("os.environ", env, clear=True):
            mock_data = json.dumps(event_data)
            with patch("builtins.open", mock_open(read_data=mock_data)):
                with patch("os.path.exists", return_value=True):
                    context = detect_cicd_context()
                    assert context is not None
                    assert context.commit_message == "Fix critical bug"


class TestGitHubAPIIntegration:
    """Test GitHub API integration."""

    def test_api_fetch_with_token(self):
        """Test fetching data from GitHub API when token is available."""
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_ACTOR": "testuser",
            "GITHUB_SHA": "abc123",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_TOKEN": "test-token",
        }

        # Mock API responses
        user_data = {"email": "test@example.com"}
        protection_data = {"required_pull_request_reviews": {"required_approving_review_count": 2}}

        with patch.dict("os.environ", env, clear=True):
            # Mock the Request class
            with patch("iltero.utils.cicd.github.Request"):
                # Mock urlopen with multiple return values
                with patch("iltero.utils.cicd.github.urlopen") as mock_url:
                    # Create mock response objects
                    class MockResponse:
                        def __init__(self, data):
                            self.data = json.dumps(data).encode()

                        def read(self):
                            return self.data

                        def __enter__(self):
                            return self

                        def __exit__(self, *args):
                            pass

                    # Side effect for two API calls
                    mock_url.side_effect = [
                        MockResponse(user_data),
                        MockResponse(protection_data),
                    ]

                    context = detect_cicd_context()
                    assert context is not None
                    assert context.triggered_by_email == "test@example.com"
                    assert context.required_approvals == 2

    def test_api_fetch_without_token(self):
        """Test graceful fallback when no token is available."""
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_ACTOR": "testuser",
            "GITHUB_SHA": "abc123",
        }

        with patch.dict("os.environ", env, clear=True):
            context = detect_cicd_context()
            assert context is not None
            # Should not have email without API access
            assert context.triggered_by_email is None
            assert context.required_approvals is None

    def test_api_fetch_with_api_errors(self):
        """Test handling of API errors."""
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_REPOSITORY": "owner/repo",
            "GITHUB_ACTOR": "testuser",
            "GITHUB_SHA": "abc123",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_TOKEN": "test-token",
        }

        with patch.dict("os.environ", env, clear=True):
            with patch("iltero.utils.cicd.github.urlopen") as mock_urlopen:
                # Simulate API error
                from io import BytesIO
                from urllib.error import HTTPError

                mock_urlopen.side_effect = HTTPError(
                    "http://api.github.com/users/testuser",
                    404,
                    "Not Found",
                    {},  # type: ignore
                    BytesIO(b""),
                )


class TestGitLabAPIIntegration:
    """Test GitLab API integration."""

    def test_gitlab_api_fetch_with_token(self) -> None:
        """Test GitLab API calls when CI_JOB_TOKEN is available."""
        env = {
            "GITLAB_CI": "true",
            "CI_PROJECT_PATH": "user/repo",
            "CI_COMMIT_SHA": "abc123",
            "CI_COMMIT_REF_NAME": "main",
            "CI_JOB_TOKEN": "test-token",
            "CI_SERVER_URL": "https://gitlab.example.com",
            "GITLAB_USER_LOGIN": "testuser",
            "CI_MERGE_REQUEST_IID": "42",
        }

        # Mock user API response
        user_response = json.dumps([{"email": "test@example.com"}]).encode()

        # Mock MR approvals API response
        approvals_response = json.dumps(
            {
                "approved_by": [
                    {"user": {"username": "approver1"}},
                    {"user": {"username": "approver2"}},
                ],
                "approvals_required": 2,
            }
        ).encode()

        with patch.dict("os.environ", env, clear=True):
            with patch("iltero.utils.cicd.gitlab.urlopen") as mock_urlopen:
                # Setup mock responses
                mock_urlopen.side_effect = [
                    MockResponse(user_response),
                    MockResponse(approvals_response),
                ]

                context = detect_cicd_context()
                assert context is not None
                assert context.triggered_by_email == "test@example.com"
                assert context.pr_approvers == ["approver1", "approver2"]
                assert context.required_approvals == 2

    def test_gitlab_api_fetch_without_token(self) -> None:
        """Test GitLab detection without token falls back gracefully."""
        env = {
            "GITLAB_CI": "true",
            "CI_PROJECT_PATH": "user/repo",
            "CI_COMMIT_SHA": "abc123",
            "CI_COMMIT_REF_NAME": "main",
            "GITLAB_USER_LOGIN": "testuser",
            "GITLAB_USER_EMAIL": "fallback@example.com",
        }

        with patch.dict("os.environ", env, clear=True):
            context = detect_cicd_context()
            assert context is not None
            assert context.triggered_by_email == "fallback@example.com"
            assert context.pr_approvers is None
            assert context.required_approvals is None

    def test_gitlab_api_fetch_with_api_errors(self) -> None:
        """Test GitLab API calls handle errors gracefully."""
        env = {
            "GITLAB_CI": "true",
            "CI_PROJECT_PATH": "user/repo",
            "CI_COMMIT_SHA": "abc123",
            "CI_COMMIT_REF_NAME": "main",
            "CI_JOB_TOKEN": "test-token",
            "CI_SERVER_URL": "https://gitlab.example.com",
            "GITLAB_USER_LOGIN": "testuser",
        }

        with patch.dict("os.environ", env, clear=True):
            with patch("iltero.utils.cicd.gitlab.urlopen") as mock_urlopen:
                # Simulate API error
                from io import BytesIO
                from urllib.error import HTTPError

                mock_urlopen.side_effect = HTTPError(
                    "http://gitlab.example.com/api/v4/users",
                    404,
                    "Not Found",
                    {},  # type: ignore
                    BytesIO(b""),
                )

                context = detect_cicd_context()
                assert context is not None
                # Should work without API data
                assert context.triggered_by == "testuser"


class TestAzureAPIIntegration:
    """Test Azure DevOps API integration."""

    def test_azure_api_fetch_with_token(self) -> None:
        """Test Azure API calls when SYSTEM_ACCESSTOKEN is available."""
        env = {
            "TF_BUILD": "true",
            "BUILD_REPOSITORY_URI": "https://dev.azure.com/org/project/_git/repo",
            "BUILD_SOURCEVERSION": "abc123",
            "BUILD_SOURCEBRANCH": "refs/heads/main",
            "SYSTEM_ACCESSTOKEN": "test-token",
            "SYSTEM_COLLECTIONURI": "https://dev.azure.com/org/",
            "SYSTEM_TEAMPROJECT": "project",
            "BUILD_REPOSITORY_NAME": "repo",
            "SYSTEM_PULLREQUEST_PULLREQUESTNUMBER": "42",
        }

        # Mock PR API response
        pr_response = json.dumps(
            {
                "title": "Test PR",
                "reviewers": [
                    {"displayName": "Approver 1", "vote": 10},
                    {"displayName": "Approver 2", "vote": 10},
                    {"displayName": "Reviewer 3", "vote": 0},
                ],
            }
        ).encode()

        # Mock repository API response
        repo_response = json.dumps({"id": "repo-id-123"}).encode()

        # Mock policy API response
        policy_response = json.dumps(
            {
                "value": [
                    {
                        "type": {"id": "fa4e907d-c16b-4a4c-9dfa-4906e5d171dd"},
                        "settings": {"minimumApproverCount": 2},
                    },
                ],
            }
        ).encode()

        with patch.dict("os.environ", env, clear=True):
            with patch("iltero.utils.cicd.azure.urlopen") as mock_urlopen:
                # Setup mock responses
                mock_urlopen.side_effect = [
                    MockResponse(pr_response),
                    MockResponse(repo_response),
                    MockResponse(policy_response),
                ]

                context = detect_cicd_context()
                assert context is not None
                assert context.pull_request_title == "Test PR"
                assert context.pr_approvers == ["Approver 1", "Approver 2"]
                assert context.required_approvals == 2

    def test_azure_api_fetch_without_token(self) -> None:
        """Test Azure detection without token falls back gracefully."""
        env = {
            "TF_BUILD": "true",
            "BUILD_REPOSITORY_URI": ("https://dev.azure.com/org/project/_git/repo"),
            "BUILD_SOURCEVERSION": "abc123",
            "BUILD_SOURCEBRANCH": "refs/heads/main",
        }

        with patch.dict("os.environ", env, clear=True):
            context = detect_cicd_context()
            assert context is not None
            assert context.pull_request_title is None
            assert context.pr_approvers is None
            assert context.required_approvals is None

    def test_azure_api_fetch_with_api_errors(self) -> None:
        """Test Azure API calls handle errors gracefully."""
        env = {
            "TF_BUILD": "true",
            "BUILD_REPOSITORY_URI": ("https://dev.azure.com/org/project/_git/repo"),
            "BUILD_SOURCEVERSION": "abc123",
            "BUILD_SOURCEBRANCH": "refs/heads/main",
            "SYSTEM_ACCESSTOKEN": "test-token",
            "SYSTEM_COLLECTIONURI": "https://dev.azure.com/org/",
            "SYSTEM_TEAMPROJECT": "project",
            "BUILD_REPOSITORY_NAME": "repo",
            "BUILD_REQUESTEDFOR": "testuser",
            "SYSTEM_PULLREQUEST_PULLREQUESTNUMBER": "42",
        }

        with patch.dict("os.environ", env, clear=True):
            with patch("iltero.utils.cicd.azure.urlopen") as mock_urlopen:
                # Simulate API error
                from io import BytesIO
                from urllib.error import HTTPError

                url = "http://dev.azure.com/org/project/_apis/git/repositories/repo/pullrequests/42"
                mock_urlopen.side_effect = HTTPError(
                    url,
                    404,
                    "Not Found",
                    {},  # type: ignore
                    BytesIO(b""),
                )

                context = detect_cicd_context()
                assert context is not None
                # Should work without API data
                assert context.triggered_by == "testuser"
                assert context.commit_sha == "abc123"
                assert context is not None
                # Should gracefully handle API errors
                assert context.triggered_by == "testuser"
