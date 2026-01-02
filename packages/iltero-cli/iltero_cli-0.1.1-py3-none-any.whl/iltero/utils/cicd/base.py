"""Base provider interface and utilities."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

from iltero.api_client.iltero_api_client.models.cicd_context_schema import (
    CICDContextSchema,
)


class CICDProvider(ABC):
    """Base class for CI/CD provider context extractors."""

    @abstractmethod
    def detect(self) -> bool:
        """Detect if running in this CI/CD environment.

        Returns:
            True if this provider is detected, False otherwise.
        """
        pass

    @abstractmethod
    def get_context(self) -> CICDContextSchema:
        """Extract CI/CD context from environment.

        Returns:
            CICDContextSchema with collected context.
        """
        pass

    def get_env(self, key: str, default: str | None = None) -> str | None:
        """Get environment variable with optional default.

        Args:
            key: Environment variable name.
            default: Default value if not found.

        Returns:
            Environment variable value or default.
        """
        value = os.getenv(key, default)
        return value if value else None

    def get_env_int(self, key: str, default: int | None = None) -> int | None:
        """Get environment variable as integer.

        Args:
            key: Environment variable name.
            default: Default value if not found or invalid.

        Returns:
            Environment variable value as int or default.
        """
        value = self.get_env(key)
        if value:
            try:
                return int(value)
            except ValueError:
                return default
        return default

    def get_env_list(self, key: str, separator: str = ",") -> list[str] | None:
        """Get environment variable as list.

        Args:
            key: Environment variable name.
            separator: String separator for splitting.

        Returns:
            List of values or None.
        """
        value = self.get_env(key)
        if value:
            return [item.strip() for item in value.split(separator) if item.strip()]
        return None

    def get_env_bool(self, key: str) -> bool:
        """Get environment variable as boolean.

        Args:
            key: Environment variable name.

        Returns:
            True if value is 'true', '1', 'yes', etc., False otherwise.
        """
        value = self.get_env(key)
        if not value:
            return False
        return value.lower() in ("true", "1", "yes", "on")
