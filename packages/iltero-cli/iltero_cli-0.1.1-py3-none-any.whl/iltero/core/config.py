"""Configuration management for Iltero CLI."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import ConfigurationError


class IlteroConfig(BaseSettings):
    """Global configuration from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="ILTERO_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Backend settings
    api_url: str = Field(default="https://api.iltero.io", description="Backend API base URL")
    token: str | None = Field(default=None, description="API token (overrides keyring)")

    # CLI behavior
    output_format: str = Field(default="table", description="Default output format")
    debug: bool = Field(default=False, description="Enable debug logging")
    no_color: bool = Field(default=False, description="Disable colored output")

    # Context settings
    default_org: str | None = Field(default=None, description="Default organization")
    default_workspace: str | None = Field(default=None, description="Default workspace")
    default_environment: str | None = Field(default=None, description="Default environment")

    # Timeouts (seconds)
    request_timeout: int = Field(default=30, description="HTTP request timeout")
    scan_timeout: int = Field(default=300, description="Scanner execution timeout")


class ConfigManager:
    """Manages CLI configuration and context."""

    DEFAULT_CONFIG_DIR = Path.home() / ".iltero"
    CONFIG_FILE = "config.yaml"
    CONTEXT_FILE = "context.yaml"

    def __init__(self):
        self.config_dir = self.DEFAULT_CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_path = self.config_dir / self.CONFIG_FILE
        self.context_path = self.config_dir / self.CONTEXT_FILE

        # Load environment-based config
        self.env_config = IlteroConfig()

        # Load file-based config
        self.file_config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigurationError(f"Failed to load config: {e}")

    def _save_config(self, config: dict[str, Any]) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_path, "w") as f:
                yaml.safe_dump(config, f, default_flow_style=False)
        except Exception as e:
            raise ConfigurationError(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value (env vars take precedence)."""
        # Check environment config first
        env_value = getattr(self.env_config, key, None)
        if env_value is not None:
            return env_value

        # Fall back to file config
        return self.file_config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set config value in file."""
        self.file_config[key] = value
        self._save_config(self.file_config)

    def get_api_url(self) -> str:
        """Get backend API base URL."""
        return self.get("api_url", self.env_config.api_url)
