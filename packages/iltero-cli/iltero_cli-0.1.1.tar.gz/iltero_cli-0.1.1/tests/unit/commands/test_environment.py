"""Tests for environment commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.environment import app

runner = CliRunner()


class TestEnvironmentList:
    """Tests for environment list command."""

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_list_environments_success(self, mock_get_client):
        """Test listing environments successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "env-1", "name": "production", "is_production": True},
            {"id": "env-2", "name": "staging", "is_production": False},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_list_environments") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["list", "--output", "json"])

            assert result.exit_code == 0
            mock_client.get_authenticated_client.assert_called_once()

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_list_environments_with_pagination(self, mock_get_client):
        """Test listing environments with pagination."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = []
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_list_environments") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            runner.invoke(
                app,
                [
                    "list",
                    "--page",
                    "2",
                    "--limit",
                    "25",
                ],
            )

            mock_api.sync_detailed.assert_called_once()
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs["page"] == 2
            assert call_kwargs["limit"] == 25

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_list_environments_with_filters(self, mock_get_client):
        """Test listing environments with filters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = []
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_list_environments") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            runner.invoke(
                app,
                [
                    "list",
                    "--search",
                    "prod",
                    "--production",
                    "--default",
                ],
            )

            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs["search"] == "prod"
            assert call_kwargs["is_production"] is True
            assert call_kwargs["is_default"] is True


class TestEnvironmentCreate:
    """Tests for environment create command."""

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_create_environment_success(self, mock_get_client):
        """Test creating environment successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "env-new", "name": "new-environment"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_create_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "new-environment",
                    "--description",
                    "A new environment",
                ],
            )

            assert result.exit_code == 0
            assert "created successfully" in result.output

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_create_production_environment(self, mock_get_client):
        """Test creating production environment."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "env-1"})

        with patch("iltero.commands.environment.operations.api_create_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "production",
                    "--production",
                    "--color",
                    "#ff0000",
                    "--branch",
                    "main",
                ],
            )

            assert result.exit_code == 0
            mock_api.sync_detailed.assert_called_once()

    def test_create_environment_missing_name(self):
        """Test create environment requires name argument."""
        result = runner.invoke(app, ["create"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output


class TestEnvironmentShow:
    """Tests for environment show command."""

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_show_environment_success(self, mock_get_client):
        """Test showing environment details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_data = Mock()
        mock_data.to_dict.return_value = {
            "id": "env-123",
            "name": "production",
            "is_production": True,
        }
        mock_response.parsed = Mock()
        mock_response.parsed.data = mock_data
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_get_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "env-123"])

            assert result.exit_code == 0
            mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_show_environment_yaml_output(self, mock_get_client):
        """Test showing environment with YAML output."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "env-123", "name": "test"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.environment.operations.api_get_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "env-123", "--output", "yaml"])

            assert result.exit_code == 0


class TestEnvironmentUpdate:
    """Tests for environment update command."""

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_update_environment_success(self, mock_get_client):
        """Test updating environment successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "env-123"})

        with patch("iltero.commands.environment.operations.api_update_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "update",
                    "env-123",
                    "--name",
                    "updated-name",
                    "--description",
                    "Updated description",
                ],
            )

            assert result.exit_code == 0
            assert "updated successfully" in result.output

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_update_environment_production_flag(self, mock_get_client):
        """Test updating environment production status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "env-123"})

        with patch("iltero.commands.environment.operations.api_update_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "update",
                    "env-123",
                    "--production",
                ],
            )

            assert result.exit_code == 0


class TestEnvironmentDelete:
    """Tests for environment delete command."""

    @patch("iltero.commands.environment.operations.get_retry_client")
    @patch("iltero.commands.environment.operations.confirm_action")
    def test_delete_environment_with_confirmation(self, mock_confirm, mock_get_client):
        """Test deleting environment with confirmation."""
        mock_confirm.return_value = True

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.environment.operations.api_delete_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "env-123"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output
            mock_confirm.assert_called_once()

    @patch("iltero.commands.environment.operations.get_retry_client")
    def test_delete_environment_with_force(self, mock_get_client):
        """Test deleting environment with force flag."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.environment.operations.api_delete_environment") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "env-123", "--force"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output

    @patch("iltero.commands.environment.operations.confirm_action")
    def test_delete_environment_cancelled(self, mock_confirm):
        """Test deleting environment cancelled by user."""
        mock_confirm.return_value = False

        result = runner.invoke(app, ["delete", "env-123"])

        assert result.exit_code == 0
        assert "cancelled" in result.output
