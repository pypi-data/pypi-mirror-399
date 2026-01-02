"""Authentication management for Iltero CLI."""

import keyring

from .config import ConfigManager
from .exceptions import AuthenticationError


class AuthManager:
    """Manages API token authentication."""

    KEYRING_SERVICE = "iltero-cli"
    KEYRING_USERNAME = "api-token"

    def __init__(self, config: ConfigManager):
        self.config = config

    def get_token(self) -> str:
        """Get API token from env var or keyring.

        Priority:
        1. ILTERO_TOKEN environment variable
        2. System keyring

        Raises:
            AuthenticationError: If no token found
        """
        # Check environment variable first (CI/CD mode)
        token = self.config.env_config.token
        if token:
            return token

        # Fall back to keyring (interactive mode)
        token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
        if token:
            return token

        raise AuthenticationError(
            "No API token found. Set ILTERO_TOKEN environment variable "
            "or run 'iltero auth set-token' to store token in keyring."
        )

    def set_token(self, token: str) -> None:
        """Store API token in system keyring.

        Args:
            token: API token to store

        Raises:
            AuthenticationError: If keyring storage fails
        """
        if not token or not token.strip():
            raise AuthenticationError("Token cannot be empty")

        # Validate token format (should start with itk_)
        if not token.startswith("itk_"):
            raise AuthenticationError("Invalid token format. Token should start with 'itk_'")

        try:
            keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME, token)
        except Exception as e:
            raise AuthenticationError(f"Failed to store token in keyring: {e}")

    def clear_token(self) -> None:
        """Remove API token from keyring."""
        try:
            keyring.delete_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
        except keyring.errors.PasswordDeleteError:
            # Token not found, which is fine
            pass
        except Exception as e:
            raise AuthenticationError(f"Failed to clear token from keyring: {e}")

    def has_token(self) -> bool:
        """Check if a token is available."""
        try:
            self.get_token()
            return True
        except AuthenticationError:
            return False
