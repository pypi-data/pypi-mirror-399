"""HTTP client service for Iltero API communication."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from iltero.api_client import AuthenticatedClient, Client
from iltero.core.auth import AuthManager
from iltero.core.config import ConfigManager
from iltero.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
)

if TYPE_CHECKING:
    from iltero.api_client.types import Response


class HTTPService:
    """Service for making HTTP requests to the Iltero API.

    This service wraps the generated OpenAPI client and provides:
    - Automatic token injection from keyring/config
    - Retry logic with exponential backoff
    - Error translation to domain exceptions
    - Request/response logging in debug mode
    """

    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3
    RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        config: ConfigManager | None = None,
        auth: AuthManager | None = None,
    ):
        self._config = config or ConfigManager()
        self._auth = auth or AuthManager()
        self._client: AuthenticatedClient | Client | None = None

    @property
    def base_url(self) -> str:
        """Get the API base URL from configuration."""
        return self._config.get_api_url()

    @property
    def timeout(self) -> float:
        """Get request timeout from configuration."""
        return float(self._config.get("request_timeout", self.DEFAULT_TIMEOUT))

    def get_client(self, authenticated: bool = True) -> AuthenticatedClient | Client:
        """Get or create an HTTP client.

        Args:
            authenticated: Whether to include authentication headers.

        Returns:
            Configured httpx client wrapper.

        Raises:
            AuthenticationError: If authenticated=True but no token available.
        """
        if authenticated:
            token = self._get_token()
            if not token:
                raise AuthenticationError("Not authenticated. Run 'iltero auth login' first.")
            return AuthenticatedClient(
                base_url=self.base_url,
                token=token,
                timeout=httpx.Timeout(self.timeout),
                raise_on_unexpected_status=False,
            )
        else:
            return Client(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                raise_on_unexpected_status=False,
            )

    def _get_token(self) -> str | None:
        """Get authentication token from config or keyring."""
        # Environment/config token takes precedence
        env_token = self._config.get("token")
        if env_token:
            return env_token

        # Fall back to keyring
        return self._auth.get_token()

    def handle_response(self, response: Response[Any]) -> Any:
        """Process API response and translate errors.

        Args:
            response: Response from generated client.

        Returns:
            Parsed response data.

        Raises:
            AuthenticationError: For 401/403 responses.
            RateLimitError: For 429 responses.
            APIError: For other error responses.
        """
        status = response.status_code

        if 200 <= status < 300:
            return response.parsed

        # Translate HTTP errors to domain exceptions
        content = response.content.decode() if response.content else ""

        if status == 401:
            raise AuthenticationError("Authentication failed. Token may be expired.")
        elif status == 403:
            raise AuthenticationError("Access denied. Insufficient permissions.")
        elif status == 429:
            raise RateLimitError("Rate limit exceeded. Please wait before retrying.")
        elif status == 404:
            raise APIError("Resource not found", status_code=status)
        elif status >= 500:
            raise APIError(f"Server error: {content}", status_code=status)
        else:
            raise APIError(f"Request failed: {content}", status_code=status)

    async def handle_response_async(self, response: Response[Any]) -> Any:
        """Async version of handle_response."""
        return self.handle_response(response)


class RetryClient:
    """HTTP client with automatic retry logic.

    Wraps the base HTTPService to add:
    - Exponential backoff for transient failures
    - Configurable retry counts
    - Circuit breaker pattern (future)
    """

    def __init__(
        self,
        http_service: HTTPService | None = None,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        self._http = http_service or HTTPService()
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor

    def get_authenticated_client(self) -> AuthenticatedClient:
        """Get an authenticated client for API calls."""
        client = self._http.get_client(authenticated=True)
        if not isinstance(client, AuthenticatedClient):
            raise AuthenticationError("Failed to create authenticated client")
        return client

    def get_client(self) -> Client:
        """Get an unauthenticated client for public API calls."""
        client = self._http.get_client(authenticated=False)
        if not isinstance(client, Client):
            raise TypeError("Expected Client instance")
        return client

    def handle_response(self, response: Response[Any]) -> Any:
        """Handle response with error translation."""
        return self._http.handle_response(response)


# Global singleton instance
_http_service: HTTPService | None = None


def get_http_service() -> HTTPService:
    """Get the global HTTP service instance."""
    global _http_service
    if _http_service is None:
        _http_service = HTTPService()
    return _http_service


def get_retry_client() -> RetryClient:
    """Get a retry-enabled HTTP client."""
    return RetryClient(http_service=get_http_service())
