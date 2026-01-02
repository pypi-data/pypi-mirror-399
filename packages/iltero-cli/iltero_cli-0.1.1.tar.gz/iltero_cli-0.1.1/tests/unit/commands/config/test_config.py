"""Tests for config commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


class TestConfigShow:
    """Tests for config show command."""

    @patch("iltero.commands.config.main.ConfigManager")
    def test_show_all_config(self, mock_config_class):
        """Test showing all configuration."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_config.file_config = {"output_format": "json"}
        mock_config.env_config = Mock()
        mock_config.env_config.api_url = "https://api.iltero.io"
        mock_config.env_config.output_format = "table"
        mock_config.env_config.debug = False
        mock_config.env_config.no_color = False
        mock_config.env_config.default_org = None
        mock_config.env_config.default_workspace = None
        mock_config.env_config.default_environment = None
        mock_config.env_config.request_timeout = 30
        mock_config.env_config.scan_timeout = 300
        mock_config.config_path = "/home/user/.iltero/config.yaml"

        result = runner.invoke(app, ["config", "show"])

        assert result.exit_code == 0

    @patch("iltero.commands.config.main.ConfigManager")
    def test_show_specific_key(self, mock_config_class):
        """Test showing specific config key."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_config.get.return_value = "json"

        result = runner.invoke(app, ["config", "show", "output_format"])

        assert result.exit_code == 0
        mock_config.get.assert_called_once_with("output_format")

    @patch("iltero.commands.config.main.ConfigManager")
    def test_show_missing_key(self, mock_config_class):
        """Test showing missing config key."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_config.get.return_value = None

        result = runner.invoke(app, ["config", "show", "unknown_key"])

        assert result.exit_code == 0
        assert "not set" in result.output


class TestConfigSet:
    """Tests for config set command."""

    @patch("iltero.commands.config.main.ConfigManager")
    def test_set_string_config(self, mock_config_class):
        """Test setting string config value."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(app, ["config", "set", "output_format", "json"])

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with("output_format", "json")

    @patch("iltero.commands.config.main.ConfigManager")
    def test_set_bool_config(self, mock_config_class):
        """Test setting boolean config value."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(app, ["config", "set", "debug", "true"])

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with("debug", True)

    @patch("iltero.commands.config.main.ConfigManager")
    def test_set_int_config(self, mock_config_class):
        """Test setting integer config value."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(app, ["config", "set", "request_timeout", "60"])

        assert result.exit_code == 0
        mock_config.set.assert_called_once_with("request_timeout", 60)

    def test_set_invalid_key(self):
        """Test setting invalid config key."""
        result = runner.invoke(app, ["config", "set", "invalid_key", "value"])

        assert result.exit_code == 1
        assert "Invalid key" in result.output

    @patch("iltero.commands.config.main.ConfigManager")
    def test_set_invalid_int_value(self, mock_config_class):
        """Test setting invalid integer value."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(app, ["config", "set", "request_timeout", "not_a_number"])

        assert result.exit_code == 1
        assert "Invalid integer" in result.output


class TestConfigReset:
    """Tests for config reset command."""

    @patch("iltero.commands.config.main.ConfigManager")
    def test_reset_specific_key(self, mock_config_class):
        """Test resetting specific config key."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_config.file_config = {"output_format": "json"}

        result = runner.invoke(app, ["config", "reset", "output_format"])

        assert result.exit_code == 0
        mock_config._save_config.assert_called_once()

    @patch("iltero.commands.config.main.ConfigManager")
    def test_reset_missing_key(self, mock_config_class):
        """Test resetting missing config key."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_config.file_config = {}

        result = runner.invoke(app, ["config", "reset", "unknown_key"])

        assert result.exit_code == 0
        assert "was not set" in result.output

    @patch("iltero.commands.config.main.ConfigManager")
    def test_reset_all_with_force(self, mock_config_class):
        """Test resetting all config with force flag."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config
        mock_config.file_config = {"output_format": "json", "debug": True}

        result = runner.invoke(app, ["config", "reset", "--force"])

        assert result.exit_code == 0
        mock_config._save_config.assert_called_once_with({})

    @patch("iltero.commands.config.main.ConfigManager")
    def test_reset_all_cancelled(self, mock_config_class):
        """Test resetting all config cancelled by user."""
        mock_config = Mock()
        mock_config_class.return_value = mock_config

        result = runner.invoke(app, ["config", "reset"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output
