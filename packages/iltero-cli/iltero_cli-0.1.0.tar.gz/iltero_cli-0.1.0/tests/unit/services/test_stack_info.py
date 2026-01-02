"""Tests for stack_info service."""

from unittest.mock import Mock, patch

import pytest

from iltero.services.stack_info import (
    StackInfo,
    StackInfoError,
    StackNotFoundError,
    get_stack_info,
)


class TestStackNotFoundError:
    """Test StackNotFoundError exception."""

    def test_error_message(self):
        """Test error message formatting."""
        error = StackNotFoundError("missing-stack")

        assert "missing-stack" in str(error)
        assert error.exit_code == 13
        assert error.stack_id == "missing-stack"


class TestStackInfoError:
    """Test StackInfoError exception."""

    def test_error_message(self):
        """Test error message formatting."""
        error = StackInfoError("stack-123", "Connection timeout")

        assert "stack-123" in str(error)
        assert "Connection timeout" in str(error)
        assert error.exit_code == 14


class TestStackInfo:
    """Test StackInfo dataclass."""

    def test_create_stack_info(self):
        """Test creating StackInfo."""
        info = StackInfo(
            stack_id="stack-1",
            name="Test Stack",
            workspace_id="ws-123",
            template_bundle_id="bundle-456",
            environment="production",
            policy_sets=["security", "compliance"],
            repository_id="repo-789",
            default_branch="main",
        )

        assert info.stack_id == "stack-1"
        assert info.name == "Test Stack"
        assert info.workspace_id == "ws-123"
        assert info.template_bundle_id == "bundle-456"
        assert info.policy_sets == ["security", "compliance"]

    def test_create_stack_info_minimal(self):
        """Test creating StackInfo with minimal fields."""
        info = StackInfo(
            stack_id="stack-min",
            name="Minimal",
            workspace_id="ws-1",
            template_bundle_id=None,
            environment=None,
            policy_sets=[],
            repository_id=None,
            default_branch=None,
        )

        assert info.stack_id == "stack-min"
        assert info.template_bundle_id is None
        assert info.policy_sets == []

    def test_from_api_response(self):
        """Test creating StackInfo from API response."""
        data = {
            "name": "API Stack",
            "workspace_id": "ws-api",
            "template_bundle_id": "bundle-api",
            "environment": "staging",
            "policy_sets": ["cis", "soc2"],
            "repository_id": "repo-api",
            "default_branch": "develop",
        }

        info = StackInfo.from_api_response("stack-api", data)

        assert info.stack_id == "stack-api"
        assert info.name == "API Stack"
        assert info.workspace_id == "ws-api"
        assert info.template_bundle_id == "bundle-api"
        assert info.environment == "staging"
        assert info.policy_sets == ["cis", "soc2"]

    def test_from_api_response_missing_fields(self):
        """Test creating StackInfo with missing optional fields."""
        data = {
            "name": "Minimal Stack",
            "workspace_id": "ws-min",
        }

        info = StackInfo.from_api_response("stack-minimal", data)

        assert info.stack_id == "stack-minimal"
        assert info.name == "Minimal Stack"
        assert info.template_bundle_id is None
        assert info.environment is None
        assert info.policy_sets == []


class TestGetStackInfo:
    """Test get_stack_info function."""

    @patch("iltero.services.stack_info.get_retry_client")
    def test_get_stack_info_success(self, mock_get_client):
        """Test successful stack info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = Mock()
        mock_response.parsed.to_dict.return_value = {
            "data": {
                "name": "Test Stack",
                "workspace_id": "ws-123",
                "template_bundle_id": "bundle-456",
                "environment": "production",
                "policy_sets": ["security"],
                "repository_id": "repo-789",
                "default_branch": "main",
            }
        }

        mock_client = Mock()
        mock_client.sync_detailed = Mock(return_value=mock_response)

        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client

        mock_get_client.return_value = mock_retry_client

        with patch("iltero.services.stack_info.get_stack") as mock_get_stack:
            mock_get_stack.sync_detailed.return_value = mock_response

            info = get_stack_info("stack-test")

            assert info.stack_id == "stack-test"
            assert info.name == "Test Stack"
            assert info.workspace_id == "ws-123"

    @patch("iltero.services.stack_info.get_retry_client")
    def test_get_stack_info_not_found(self, mock_get_client):
        """Test stack not found."""
        mock_response = Mock()
        mock_response.status_code = 404

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        with patch("iltero.services.stack_info.get_stack") as mock_get_stack:
            mock_get_stack.sync_detailed.return_value = mock_response

            with pytest.raises(StackNotFoundError) as exc_info:
                get_stack_info("nonexistent")

            assert exc_info.value.stack_id == "nonexistent"

    @patch("iltero.services.stack_info.get_retry_client")
    def test_get_stack_info_server_error(self, mock_get_client):
        """Test server error."""
        mock_response = Mock()
        mock_response.status_code = 500

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        with patch("iltero.services.stack_info.get_stack") as mock_get_stack:
            mock_get_stack.sync_detailed.return_value = mock_response

            with pytest.raises(StackInfoError):
                get_stack_info("error-stack")

    @patch("iltero.services.stack_info.get_retry_client")
    def test_get_stack_info_empty_response(self, mock_get_client):
        """Test empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = None

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        with patch("iltero.services.stack_info.get_stack") as mock_get_stack:
            mock_get_stack.sync_detailed.return_value = mock_response

            with pytest.raises(StackInfoError) as exc_info:
                get_stack_info("empty-stack")

            assert "Empty response" in str(exc_info.value)

    @patch("iltero.services.stack_info.get_retry_client")
    def test_get_stack_info_unwrapped_response(self, mock_get_client):
        """Test response without data wrapper."""
        # Response without 'data' wrapper
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = Mock()
        mock_response.parsed.to_dict.return_value = {
            "name": "Direct Stack",
            "workspace_id": "ws-direct",
        }

        mock_client = Mock()
        mock_retry_client = Mock()
        mock_retry_client.get_authenticated_client.return_value = mock_client
        mock_get_client.return_value = mock_retry_client

        with patch("iltero.services.stack_info.get_stack") as mock_get_stack:
            mock_get_stack.sync_detailed.return_value = mock_response

            info = get_stack_info("direct-stack")

            assert info.name == "Direct Stack"
            assert info.workspace_id == "ws-direct"
