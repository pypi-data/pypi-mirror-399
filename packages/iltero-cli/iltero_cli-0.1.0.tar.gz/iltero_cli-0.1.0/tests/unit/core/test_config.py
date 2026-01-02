"""Tests for ConfigManager."""

import tempfile
from pathlib import Path

import pytest

from iltero.core.config import ConfigManager


@pytest.fixture
def temp_config_dir():
    """Create temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def test_config_manager_initialization(temp_config_dir, monkeypatch):
    """Test ConfigManager initialization."""
    monkeypatch.setattr("iltero.core.config.ConfigManager.DEFAULT_CONFIG_DIR", temp_config_dir)

    config = ConfigManager()
    assert config.config_dir == temp_config_dir
    assert config.config_dir.exists()


def test_config_get_default(temp_config_dir, monkeypatch):
    """Test getting default config value."""
    monkeypatch.setattr("iltero.core.config.ConfigManager.DEFAULT_CONFIG_DIR", temp_config_dir)

    config = ConfigManager()
    assert config.get("api_url") == "https://api.iltero.io"


def test_config_set_and_get(temp_config_dir, monkeypatch):
    """Test setting and getting config value."""
    monkeypatch.setattr("iltero.core.config.ConfigManager.DEFAULT_CONFIG_DIR", temp_config_dir)

    config = ConfigManager()
    config.set("test_key", "test_value")
    assert config.get("test_key") == "test_value"


def test_env_var_precedence(temp_config_dir, monkeypatch):
    """Test that environment variables take precedence."""
    monkeypatch.setattr("iltero.core.config.ConfigManager.DEFAULT_CONFIG_DIR", temp_config_dir)
    monkeypatch.setenv("ILTERO_API_URL", "https://test.example.com")

    config = ConfigManager()
    config.set("api_url", "https://file.example.com")

    # Environment variable should take precedence
    assert config.get("api_url") == "https://test.example.com"


def test_config_file_persistence(temp_config_dir, monkeypatch):
    """Test that config persists to file."""
    monkeypatch.setattr("iltero.core.config.ConfigManager.DEFAULT_CONFIG_DIR", temp_config_dir)

    config1 = ConfigManager()
    config1.set("test_key", "test_value")

    # Create new instance to verify persistence
    config2 = ConfigManager()
    assert config2.get("test_key") == "test_value"
