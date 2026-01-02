"""Tests for ContextManager."""

import pytest
import yaml

from iltero.core.context import ContextManager
from iltero.core.exceptions import ConfigurationError


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory."""
    return tmp_path / ".iltero"


@pytest.fixture
def context_manager(temp_config_dir):
    """Create a ContextManager with temp directory."""
    return ContextManager(temp_config_dir)


class TestContextManager:
    """Tests for ContextManager class."""

    def test_init_creates_empty_context(self, context_manager):
        """Test initialization with no existing context file."""
        assert context_manager.get_all() == {}

    def test_init_loads_existing_context(self, temp_config_dir):
        """Test loading existing context from file."""
        temp_config_dir.mkdir(parents=True, exist_ok=True)
        context_file = temp_config_dir / "context.yaml"
        context_file.write_text(
            yaml.dump(
                {
                    "organization": "test-org",
                    "workspace": "test-workspace",
                }
            )
        )

        manager = ContextManager(temp_config_dir)
        assert manager.get_org() == "test-org"
        assert manager.get_workspace() == "test-workspace"

    def test_init_handles_malformed_yaml(self, temp_config_dir):
        """Test handling of malformed YAML file."""
        temp_config_dir.mkdir(parents=True, exist_ok=True)
        context_file = temp_config_dir / "context.yaml"
        context_file.write_text("invalid: yaml: content: [")

        with pytest.raises(ConfigurationError, match="Failed to load context"):
            ContextManager(temp_config_dir)

    def test_set_org(self, context_manager, temp_config_dir):
        """Test setting organization."""
        context_manager.set_org("my-org")
        assert context_manager.get_org() == "my-org"

        # Verify persisted to file
        context_file = temp_config_dir / "context.yaml"
        assert context_file.exists()
        saved = yaml.safe_load(context_file.read_text())
        assert saved["organization"] == "my-org"

    def test_set_workspace(self, context_manager, temp_config_dir):
        """Test setting workspace."""
        context_manager.set_workspace("my-workspace")
        assert context_manager.get_workspace() == "my-workspace"

        # Verify persisted
        context_file = temp_config_dir / "context.yaml"
        saved = yaml.safe_load(context_file.read_text())
        assert saved["workspace"] == "my-workspace"

    def test_set_environment(self, context_manager, temp_config_dir):
        """Test setting environment."""
        context_manager.set_environment("production")
        assert context_manager.get_environment() == "production"

        # Verify persisted
        context_file = temp_config_dir / "context.yaml"
        saved = yaml.safe_load(context_file.read_text())
        assert saved["environment"] == "production"

    def test_get_org_returns_none_when_not_set(self, context_manager):
        """Test getting org when not set returns None."""
        assert context_manager.get_org() is None

    def test_get_workspace_returns_none_when_not_set(self, context_manager):
        """Test getting workspace when not set returns None."""
        assert context_manager.get_workspace() is None

    def test_get_environment_returns_none_when_not_set(self, context_manager):
        """Test getting environment when not set returns None."""
        assert context_manager.get_environment() is None

    def test_clear(self, context_manager, temp_config_dir):
        """Test clearing all context."""
        # Set some values
        context_manager.set_org("my-org")
        context_manager.set_workspace("my-workspace")
        context_manager.set_environment("production")

        # Clear
        context_manager.clear()

        assert context_manager.get_org() is None
        assert context_manager.get_workspace() is None
        assert context_manager.get_environment() is None
        assert context_manager.get_all() == {}

        # Verify file is updated
        context_file = temp_config_dir / "context.yaml"
        saved = yaml.safe_load(context_file.read_text())
        assert saved == {}

    def test_get_all(self, context_manager):
        """Test getting all context values."""
        context_manager.set_org("org1")
        context_manager.set_workspace("ws1")
        context_manager.set_environment("env1")

        all_context = context_manager.get_all()
        assert all_context == {
            "organization": "org1",
            "workspace": "ws1",
            "environment": "env1",
        }

    def test_get_all_returns_copy(self, context_manager):
        """Test that get_all returns a copy, not the original dict."""
        context_manager.set_org("my-org")
        all_context = context_manager.get_all()

        # Modifying the returned dict should not affect internal state
        all_context["organization"] = "modified"
        assert context_manager.get_org() == "my-org"

    def test_creates_config_dir_if_not_exists(self, temp_config_dir):
        """Test that config directory is created when saving."""
        manager = ContextManager(temp_config_dir)
        manager.set_org("test-org")

        assert temp_config_dir.exists()
        assert (temp_config_dir / "context.yaml").exists()

    def test_multiple_operations_persist_correctly(self, context_manager, temp_config_dir):
        """Test that multiple operations persist correctly."""
        context_manager.set_org("org1")
        context_manager.set_workspace("ws1")
        context_manager.set_environment("env1")

        # Load a fresh manager and verify
        fresh_manager = ContextManager(temp_config_dir)
        assert fresh_manager.get_org() == "org1"
        assert fresh_manager.get_workspace() == "ws1"
        assert fresh_manager.get_environment() == "env1"

    def test_overwrite_existing_value(self, context_manager):
        """Test overwriting existing context values."""
        context_manager.set_org("org1")
        assert context_manager.get_org() == "org1"

        context_manager.set_org("org2")
        assert context_manager.get_org() == "org2"
