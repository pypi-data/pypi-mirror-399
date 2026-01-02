"""Context management for Iltero CLI."""

from pathlib import Path
from typing import Any

import yaml

from .exceptions import ConfigurationError


class ContextManager:
    """Manages current organization/workspace/environment context."""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.context_file = config_dir / "context.yaml"
        self._context = self._load_context()

    def _load_context(self) -> dict[str, Any]:
        """Load context from file."""
        if not self.context_file.exists():
            return {}

        try:
            with open(self.context_file) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigurationError(f"Failed to load context: {e}")

    def _save_context(self) -> None:
        """Save context to file."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.context_file, "w") as f:
                yaml.safe_dump(self._context, f, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Failed to save context: {e}")

    def get_org(self) -> str | None:
        """Get current organization."""
        return self._context.get("organization")

    def set_org(self, org: str) -> None:
        """Set current organization."""
        self._context["organization"] = org
        self._save_context()

    def get_workspace(self) -> str | None:
        """Get current workspace."""
        return self._context.get("workspace")

    def set_workspace(self, workspace: str) -> None:
        """Set current workspace."""
        self._context["workspace"] = workspace
        self._save_context()

    def get_environment(self) -> str | None:
        """Get current environment."""
        return self._context.get("environment")

    def set_environment(self, environment: str) -> None:
        """Set current environment."""
        self._context["environment"] = environment
        self._save_context()

    def clear(self) -> None:
        """Clear all context."""
        self._context = {}
        self._save_context()

    def get_all(self) -> dict[str, str]:
        """Get all context values."""
        return self._context.copy()
