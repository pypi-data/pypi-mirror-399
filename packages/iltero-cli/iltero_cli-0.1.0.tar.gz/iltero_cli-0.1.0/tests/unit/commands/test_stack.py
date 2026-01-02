"""Tests for stack commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestStackList:
    """Tests for stack list command."""

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_list_stacks_success(self, mock_get_client):
        """Test listing stacks successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {"id": "stack-1", "name": "web-app", "active": True},
            {"id": "stack-2", "name": "api-server", "active": True},
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.stack.operations.api_list_stacks") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["list", "--output", "json"])
            if result.exit_code != 0:
                print(f"stdout: {result.stdout}")

            assert result.exit_code == 0
            mock_client.get_authenticated_client.assert_called_once()

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_list_stacks_with_filters(self, mock_get_client):
        """Test listing stacks with filters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = []
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.stack.operations.api_list_stacks") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            runner.invoke(
                app,
                [
                    "list",
                    "--search",
                    "web",
                    "--active",
                ],
            )

            mock_api.sync_detailed.assert_called_once()
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs["search"] == "web"
            assert call_kwargs["active"] is True

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_list_stacks_error(self, mock_get_client):
        """Test list stacks handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Auth failed")

        result = runner.invoke(app, ["list"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestStackCreate:
    """Tests for stack create command."""

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_create_stack_success(self, mock_get_client):
        """Test creating stack successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "stack-new", "name": "new-stack"}
        mock_client.handle_response.return_value = mock_response.parsed

        with (
            patch("iltero.commands.stack.operations.api_create_stack") as mock_api,
            patch("iltero.commands.stack.operations.TerraformBackendSchema") as mock_backend,
        ):
            mock_backend.from_dict.return_value = Mock()
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "new-stack",
                    "--backend-type",
                    "s3",
                    "--backend-bucket",
                    "my-bucket",
                    "--backend-key",
                    "state/terraform.tfstate",
                ],
            )

            assert result.exit_code == 0
            assert "created successfully" in result.output

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_create_stack_with_all_options(self, mock_get_client):
        """Test creating stack with all options."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "stack-1"})

        with (
            patch("iltero.commands.stack.operations.api_create_stack") as mock_api,
            patch("iltero.commands.stack.operations.TerraformBackendSchema") as mock_backend,
        ):
            mock_backend.from_dict.return_value = Mock()
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "my-stack",
                    "--backend-type",
                    "s3",
                    "--backend-bucket",
                    "my-bucket",
                    "--backend-key",
                    "state.tfstate",
                    "--backend-region",
                    "us-east-1",
                    "--description",
                    "Test stack",
                    "--template",
                    "hipaa-core-aws",
                    "--terraform-dir",
                    "./terraform",
                    "--env",
                    "env-1",
                    "--env",
                    "env-2",
                ],
            )

            assert result.exit_code == 0
            mock_api.sync_detailed.assert_called_once()

    def test_create_stack_missing_name(self):
        """Test create stack requires name argument."""
        result = runner.invoke(app, ["create"])

        assert result.exit_code != 0
        assert "Missing argument" in result.output


class TestStackShow:
    """Tests for stack show command."""

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_show_stack_success(self, mock_get_client):
        """Test showing stack details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_data = Mock()
        mock_data.to_dict.return_value = {
            "id": "stack-123",
            "name": "web-app",
            "active": True,
        }
        mock_response.parsed = Mock()
        mock_response.parsed.data = mock_data
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.stack.operations.api_get_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "stack-123"])

            assert result.exit_code == 0
            mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_show_stack_json_output(self, mock_get_client):
        """Test showing stack with JSON output."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "stack-123", "name": "test"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.stack.operations.api_get_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "stack-123", "--output", "json"])

            assert result.exit_code == 0


class TestStackUpdate:
    """Tests for stack update command."""

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_update_stack_success(self, mock_get_client):
        """Test updating stack successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "stack-123"})

        with patch("iltero.commands.stack.operations.api_update_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "update",
                    "stack-123",
                    "--name",
                    "updated-stack",
                    "--description",
                    "Updated description",
                ],
            )

            assert result.exit_code == 0
            assert "updated successfully" in result.output

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_update_stack_active_flag(self, mock_get_client):
        """Test updating stack active status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = Mock(data={"id": "stack-123"})

        with patch("iltero.commands.stack.operations.api_update_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["update", "stack-123", "--inactive"])

            assert result.exit_code == 0


class TestStackDelete:
    """Tests for stack delete command."""

    @patch("iltero.commands.stack.operations.get_retry_client")
    @patch("iltero.commands.stack.operations.confirm_action")
    def test_delete_stack_with_confirmation(self, mock_confirm, mock_get_client):
        """Test deleting stack with confirmation."""
        mock_confirm.return_value = True

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.stack.operations.api_delete_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "stack-123"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output
            mock_confirm.assert_called_once()

    @patch("iltero.commands.stack.operations.get_retry_client")
    def test_delete_stack_with_force(self, mock_get_client):
        """Test deleting stack with force flag."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.stack.operations.api_delete_stack") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "stack-123", "--force"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output

    @patch("iltero.commands.stack.operations.confirm_action")
    def test_delete_stack_cancelled(self, mock_confirm):
        """Test deleting stack cancelled by user."""
        mock_confirm.return_value = False

        result = runner.invoke(app, ["delete", "stack-123"])

        assert result.exit_code == 0
        assert "cancelled" in result.output
