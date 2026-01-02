"""Tests for HTTP service module."""

from unittest.mock import Mock, patch

import pytest

from iltero.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
)
from iltero.core.http import HTTPService, RetryClient, get_http_service


class TestHTTPService:
    """Tests for HTTPService class."""

    def test_init_creates_dependencies(self):
        """Test HTTPService initializes with dependencies."""
        with (
            patch("iltero.core.http.ConfigManager") as mock_config_class,
            patch("iltero.core.http.AuthManager") as mock_auth_class,
        ):
            mock_config = Mock()
            mock_auth = Mock()
            mock_config_class.return_value = mock_config
            mock_auth_class.return_value = mock_auth

            service = HTTPService()

            assert service._config == mock_config
            assert service._auth == mock_auth

    def test_init_with_custom_config(self):
        """Test HTTPService accepts custom config and auth."""
        mock_config = Mock()
        mock_auth = Mock()

        service = HTTPService(config=mock_config, auth=mock_auth)

        assert service._config == mock_config
        assert service._auth == mock_auth

    def test_base_url_from_config(self):
        """Test base_url property uses config."""
        mock_config = Mock()
        mock_config.get_api_url.return_value = "https://custom.api.io"

        service = HTTPService(config=mock_config, auth=Mock())

        assert service.base_url == "https://custom.api.io"

    def test_timeout_from_config(self):
        """Test timeout property uses config."""
        mock_config = Mock()
        mock_config.get.return_value = 60

        service = HTTPService(config=mock_config, auth=Mock())

        assert service.timeout == 60.0

    def test_timeout_default_value(self):
        """Test timeout uses default when not in config."""
        mock_config = Mock()
        # Simulate get() returning the default when key is not set
        mock_config.get.side_effect = lambda key, default=None: default

        service = HTTPService(config=mock_config, auth=Mock())

        assert service.timeout == HTTPService.DEFAULT_TIMEOUT

    def test_get_client_unauthenticated(self):
        """Test getting unauthenticated client."""
        mock_config = Mock()
        mock_config.get_api_url.return_value = "https://test.api.io"
        mock_config.get.return_value = 30

        service = HTTPService(config=mock_config, auth=Mock())
        client = service.get_client(authenticated=False)

        from iltero.api_client import Client

        assert isinstance(client, Client)

    def test_get_client_authenticated_with_env_token(self):
        """Test getting authenticated client with env token."""
        mock_config = Mock()
        mock_config.get_api_url.return_value = "https://test.api.io"
        mock_config.get.side_effect = lambda key, default=None: {
            "token": "env-token-123",
            "request_timeout": 30,
        }.get(key, default)

        service = HTTPService(config=mock_config, auth=Mock())
        client = service.get_client(authenticated=True)

        from iltero.api_client import AuthenticatedClient

        assert isinstance(client, AuthenticatedClient)

    def test_get_client_authenticated_with_keyring_token(self):
        """Test getting authenticated client with keyring token."""
        mock_config = Mock()
        mock_config.get_api_url.return_value = "https://test.api.io"
        # get() should return None for token but default for timeout
        mock_config.get.side_effect = lambda key, default=None: {
            "request_timeout": 30,
        }.get(key, default)

        mock_auth = Mock()
        mock_auth.get_token.return_value = "keyring-token-456"

        service = HTTPService(config=mock_config, auth=mock_auth)
        client = service.get_client(authenticated=True)

        from iltero.api_client import AuthenticatedClient

        assert isinstance(client, AuthenticatedClient)

    def test_get_client_authenticated_no_token_raises(self):
        """Test getting authenticated client without token raises error."""
        mock_config = Mock()
        mock_config.get_api_url.return_value = "https://test.api.io"
        mock_config.get.return_value = None

        mock_auth = Mock()
        mock_auth.get_token.return_value = None

        service = HTTPService(config=mock_config, auth=mock_auth)

        with pytest.raises(AuthenticationError) as exc_info:
            service.get_client(authenticated=True)

        assert "Not authenticated" in str(exc_info.value)

    def test_handle_response_success(self):
        """Test handle_response returns parsed data on success."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.parsed = {"data": "test"}

        result = service.handle_response(mock_response)
        assert result == {"data": "test"}

    def test_handle_response_201_success(self):
        """Test handle_response returns parsed data on 201."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.parsed = {"id": "new-resource"}

        result = service.handle_response(mock_response)
        assert result == {"id": "new-resource"}

    def test_handle_response_401_raises_auth_error(self):
        """Test handle_response raises AuthenticationError on 401."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.content = b"Unauthorized"

        with pytest.raises(AuthenticationError) as exc_info:
            service.handle_response(mock_response)

        assert "expired" in str(exc_info.value).lower()

    def test_handle_response_403_raises_auth_error(self):
        """Test handle_response raises AuthenticationError on 403."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.content = b"Forbidden"

        with pytest.raises(AuthenticationError) as exc_info:
            service.handle_response(mock_response)

        assert "denied" in str(exc_info.value).lower()

    def test_handle_response_429_raises_rate_limit_error(self):
        """Test handle_response raises RateLimitError on 429."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.content = b"Too Many Requests"

        with pytest.raises(RateLimitError):
            service.handle_response(mock_response)

    def test_handle_response_404_raises_api_error(self):
        """Test handle_response raises APIError on 404."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.content = b"Not Found"

        with pytest.raises(APIError) as exc_info:
            service.handle_response(mock_response)

        assert exc_info.value.status_code == 404

    def test_handle_response_500_raises_api_error(self):
        """Test handle_response raises APIError on 500."""
        service = HTTPService(config=Mock(), auth=Mock())

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.content = b"Internal Server Error"

        with pytest.raises(APIError) as exc_info:
            service.handle_response(mock_response)

        assert exc_info.value.status_code == 500


class TestRetryClient:
    """Tests for RetryClient class."""

    def test_init_creates_http_service(self):
        """Test RetryClient creates HTTPService if not provided."""
        with patch("iltero.core.http.HTTPService") as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            client = RetryClient()

            assert client._http == mock_service

    def test_init_uses_provided_service(self):
        """Test RetryClient uses provided HTTPService."""
        mock_service = Mock(spec=HTTPService)

        client = RetryClient(http_service=mock_service)

        assert client._http == mock_service

    def test_init_custom_retry_settings(self):
        """Test RetryClient accepts custom retry settings."""
        mock_service = Mock(spec=HTTPService)

        client = RetryClient(
            http_service=mock_service,
            max_retries=5,
            backoff_factor=1.0,
        )

        assert client._max_retries == 5
        assert client._backoff_factor == 1.0

    def test_get_authenticated_client(self):
        """Test get_authenticated_client returns AuthenticatedClient."""
        mock_service = Mock(spec=HTTPService)
        mock_auth_client = Mock()
        mock_auth_client.__class__ = type("AuthenticatedClient", (), {})
        mock_service.get_client.return_value = mock_auth_client

        # Patch isinstance check
        with patch("iltero.core.http.AuthenticatedClient", mock_auth_client.__class__):
            client = RetryClient(http_service=mock_service)
            client.get_authenticated_client()

        mock_service.get_client.assert_called_once_with(authenticated=True)

    def test_handle_response_delegates_to_service(self):
        """Test handle_response delegates to HTTPService."""
        mock_service = Mock(spec=HTTPService)
        mock_service.handle_response.return_value = {"data": "test"}

        client = RetryClient(http_service=mock_service)
        mock_response = Mock()

        result = client.handle_response(mock_response)

        mock_service.handle_response.assert_called_once_with(mock_response)
        assert result == {"data": "test"}


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_http_service_creates_instance(self):
        """Test get_http_service creates HTTPService."""
        import iltero.core.http as http_module

        http_module._http_service = None

        with patch.object(http_module, "HTTPService") as mock_class:
            mock_instance = Mock()
            mock_class.return_value = mock_instance

            result = get_http_service()

            mock_class.assert_called_once()
            assert result == mock_instance

    def test_get_http_service_returns_singleton(self):
        """Test get_http_service returns same instance."""
        import iltero.core.http as http_module

        # Set a known instance
        mock_service = Mock()
        http_module._http_service = mock_service

        result = get_http_service()

        assert result is mock_service

        # Clean up
        http_module._http_service = None
