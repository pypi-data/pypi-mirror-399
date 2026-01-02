"""Tests for workspace commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.workspace import app

runner = CliRunner()


class TestWorkspaceList:
    """Tests for workspace list command."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_list_workspaces_success(self, mock_get_client):
        """Test listing workspaces successfully."""
        # Setup mock
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "ws-1", "name": "workspace-1", "description": "Test 1"},
            {"id": "ws-2", "name": "workspace-2", "description": "Test 2"},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_list_workspaces") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["list", "--output", "json"])

            assert result.exit_code == 0
            mock_client.get_authenticated_client.assert_called_once()

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_list_workspaces_with_filters(self, mock_get_client):
        """Test listing workspaces with filters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = []
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_list_workspaces") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            runner.invoke(
                app,
                [
                    "list",
                    "--environment",
                    "env-123",
                    "--name",
                    "test",
                    "--active",
                ],
            )

            mock_api.sync_detailed.assert_called_once()
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs["environment_id"] == "env-123"
            assert call_kwargs["name"] == "test"
            assert call_kwargs["active"] is True

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_list_workspaces_error(self, mock_get_client):
        """Test list workspaces handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Connection failed")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestWorkspaceCreate:
    """Tests for workspace create command."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_create_workspace_success(self, mock_get_client):
        """Test creating workspace successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "ws-new", "name": "new-workspace"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_create_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "new-workspace",
                    "--description",
                    "A new workspace",
                ],
            )

            assert result.exit_code == 0
            assert "created successfully" in result.output

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_create_workspace_with_all_options(self, mock_get_client):
        """Test creating workspace with all options."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "ws-1"})

        with patch("iltero.commands.workspace.operations.api_create_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            runner.invoke(
                app,
                [
                    "create",
                    "my-workspace",
                    "--description",
                    "Test desc",
                    "--slug",
                    "my-ws",
                    "--environment",
                    "env-1",
                    "--environment",
                    "env-2",
                    "--default-environment",
                    "env-1",
                ],
            )

            mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_create_workspace_missing_name(self, mock_get_client):
        """Test create workspace requires name argument."""
        result = runner.invoke(app, ["create"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output


class TestWorkspaceShow:
    """Tests for workspace show command."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_show_workspace_success(self, mock_get_client):
        """Test showing workspace details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_data = Mock()
        mock_data.to_dict.return_value = {
            "id": "ws-123",
            "name": "test-workspace",
            "description": "Test description",
        }
        mock_response.parsed = Mock()
        mock_response.parsed.data = mock_data
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_get_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "ws-123"])

            assert result.exit_code == 0
            mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_show_workspace_json_output(self, mock_get_client):
        """Test showing workspace with JSON output."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "ws-123", "name": "test"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.workspace.operations.api_get_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "ws-123", "--output", "json"])

            assert result.exit_code == 0


class TestWorkspaceUpdate:
    """Tests for workspace update command."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_update_workspace_success(self, mock_get_client):
        """Test updating workspace successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "ws-123"})

        with patch("iltero.commands.workspace.operations.api_update_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "update",
                    "ws-123",
                    "--name",
                    "updated-name",
                    "--description",
                    "Updated description",
                ],
            )

            assert result.exit_code == 0
            assert "updated successfully" in result.output

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_update_workspace_active_flag(self, mock_get_client):
        """Test updating workspace active status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "ws-123"})

        with patch("iltero.commands.workspace.operations.api_update_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["update", "ws-123", "--inactive"])

            assert result.exit_code == 0


class TestWorkspaceDelete:
    """Tests for workspace delete command."""

    @patch("iltero.commands.workspace.operations.get_retry_client")
    @patch("iltero.commands.workspace.operations.confirm_action")
    def test_delete_workspace_with_confirmation(self, mock_confirm, mock_get_client):
        """Test deleting workspace with confirmation."""
        mock_confirm.return_value = True

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.workspace.operations.api_delete_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "ws-123"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output
            mock_confirm.assert_called_once()

    @patch("iltero.commands.workspace.operations.get_retry_client")
    def test_delete_workspace_with_force(self, mock_get_client):
        """Test deleting workspace with force flag."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.workspace.operations.api_delete_workspace") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "ws-123", "--force"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output

    @patch("iltero.commands.workspace.operations.confirm_action")
    def test_delete_workspace_cancelled(self, mock_confirm):
        """Test deleting workspace cancelled by user."""
        mock_confirm.return_value = False

        result = runner.invoke(app, ["delete", "ws-123"])

        assert result.exit_code == 0
        assert "cancelled" in result.output
