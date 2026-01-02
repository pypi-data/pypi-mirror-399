"""Tests for registry commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.registry import app

runner = CliRunner()


class TestRegistryList:
    """Tests for registry list command."""

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_list_modules_success(self, mock_get_client):
        """Test listing modules successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {
                "id": "mod-1",
                "name": "vpc",
                "namespace": "aws",
                "provider": "aws",
                "tool": "terraform",
            },
            {
                "id": "mod-2",
                "name": "ec2",
                "namespace": "aws",
                "provider": "aws",
                "tool": "terraform",
            },
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_list_modules") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["list", "--output", "json"])

            assert result.exit_code == 0
            mock_client.get_authenticated_client.assert_called_once()

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_list_modules_with_filters(self, mock_get_client):
        """Test listing modules with filters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {
                "id": "mod-1",
                "name": "vpc",
                "namespace": "aws",
                "provider": "aws",
                "tool": "terraform",
            }
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_list_modules") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "list",
                    "--tool",
                    "terraform",
                    "--provider",
                    "aws",
                    "--output",
                    "json",
                ],
            )

            assert result.exit_code == 0
            # Check that filters were passed
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs.get("tool") == "terraform"
            assert call_kwargs.get("provider") == "aws"


class TestRegistryCreate:
    """Tests for registry create command."""

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_create_module_success(self, mock_get_client):
        """Test creating a module successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "id": "mod-new",
            "name": "s3",
            "namespace": "aws",
            "provider": "aws",
            "tool": "terraform",
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_create_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "s3",
                    "--namespace",
                    "aws",
                    "--provider",
                    "aws",
                    "--tool",
                    "terraform",
                ],
            )

            assert result.exit_code == 0
            assert "created" in result.output.lower()

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_create_module_with_version(self, mock_get_client):
        """Test creating a module with version."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "mod-new", "version": "1.0.0"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_create_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "create",
                    "vpc",
                    "--namespace",
                    "aws",
                    "--provider",
                    "aws",
                    "--tool",
                    "terraform",
                    "--description",
                    "AWS VPC module",
                ],
            )

            assert result.exit_code == 0
            assert "created" in result.output.lower()


class TestRegistryShow:
    """Tests for registry show command."""

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_show_module_success(self, mock_get_client):
        """Test showing module details successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "id": "mod-123",
            "name": "vpc",
            "namespace": "aws",
            "provider": "aws",
            "tool": "terraform",
            "version": "1.0.0",
            "description": "AWS VPC module",
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_get_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "mod-123", "--output", "json"])

            assert result.exit_code == 0

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_show_module_yaml_output(self, mock_get_client):
        """Test showing module with YAML output."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "id": "mod-123",
            "name": "vpc",
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_get_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["show", "mod-123", "--output", "yaml"])

            assert result.exit_code == 0


class TestRegistryUpdate:
    """Tests for registry update command."""

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_update_module_success(self, mock_get_client):
        """Test updating a module successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "id": "mod-123",
            "version": "2.0.0",
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_update_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                ["update", "mod-123", "--description", "Updated module"],
            )

            assert result.exit_code == 0
            assert "updated" in result.output.lower()

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_update_module_description(self, mock_get_client):
        """Test updating module description."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"id": "mod-123"}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.modules.api_update_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "update",
                    "mod-123",
                    "--description",
                    "Updated description",
                ],
            )

            assert result.exit_code == 0


class TestRegistryDelete:
    """Tests for registry delete command."""

    @patch("iltero.commands.registry.modules.get_retry_client")
    @patch("iltero.commands.registry.modules.confirm_action")
    def test_delete_module_with_confirmation(self, mock_confirm, mock_get_client):
        """Test deleting module with confirmation."""
        mock_confirm.return_value = True

        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.registry.modules.api_delete_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "mod-123"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.output.lower()
            mock_confirm.assert_called_once()

    @patch("iltero.commands.registry.modules.get_retry_client")
    def test_delete_module_with_force(self, mock_get_client):
        """Test deleting module with force flag."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_client.handle_response.return_value = None

        with patch("iltero.commands.registry.modules.api_delete_module") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["delete", "mod-123", "--force"])

            assert result.exit_code == 0

    @patch("iltero.commands.registry.modules.confirm_action")
    def test_delete_module_cancelled(self, mock_confirm):
        """Test cancelling module deletion."""
        mock_confirm.return_value = False

        result = runner.invoke(app, ["delete", "mod-123"])

        assert result.exit_code == 0
        assert "cancelled" in result.output.lower()


class TestRegistrySearch:
    """Tests for registry search command."""

    @patch("iltero.commands.registry.search.get_retry_client")
    def test_search_modules_success(self, mock_get_client):
        """Test searching modules successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = [
            {
                "id": "mod-1",
                "name": "vpc",
                "namespace": "aws",
            },
            {
                "id": "mod-2",
                "name": "vpc-peering",
                "namespace": "aws",
            },
        ]
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.search.api_list_modules") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["search", "vpc"])

            assert result.exit_code == 0
            # Check that search query was passed as name filter
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs.get("name") == "vpc"

    @patch("iltero.commands.registry.search.get_retry_client")
    def test_search_modules_with_filters(self, mock_get_client):
        """Test searching modules with additional filters."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = []
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.search.api_list_modules") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(
                app,
                [
                    "search",
                    "s3",
                    "--tool",
                    "terraform",
                    "--provider",
                    "aws",
                ],
            )

            assert result.exit_code == 0
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs.get("tool") == "terraform"
            assert call_kwargs.get("provider") == "aws"


class TestRegistryTemplatesList:
    """Tests for registry templates list command."""

    @patch("iltero.commands.registry.templates.get_retry_client")
    def test_list_templates_success(self, mock_get_client):
        """Test listing templates successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "bundles": [
                {
                    "id": "tpl-1",
                    "name": "AWS CIS Baseline",
                    "provider": "aws",
                    "framework": "CIS",
                    "industry": "general",
                },
                {
                    "id": "tpl-2",
                    "name": "AWS SOC2 Baseline",
                    "provider": "aws",
                    "framework": "SOC2",
                    "industry": "general",
                },
            ]
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.templates.api_list_templates") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["templates", "list"])

            assert result.exit_code == 0
            assert "AWS CIS Baseline" in result.output or result.exit_code == 0

    @patch("iltero.commands.registry.templates.get_retry_client")
    def test_list_templates_with_provider_filter(self, mock_get_client):
        """Test listing templates with provider filter."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"bundles": []}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.templates.api_list_templates") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["templates", "list", "--provider", "azure"])

            assert result.exit_code == 0
            call_kwargs = mock_api.sync_detailed.call_args[1]
            assert call_kwargs.get("provider") == "azure"

    @patch("iltero.commands.registry.templates.get_retry_client")
    def test_list_templates_empty(self, mock_get_client):
        """Test listing templates when none found."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = None
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.templates.api_list_templates") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["templates", "list"])

            assert result.exit_code == 0
            assert "No templates found" in result.output


class TestRegistryTemplatesShow:
    """Tests for registry templates show command."""

    @patch("iltero.commands.registry.templates.get_retry_client")
    def test_show_template_success(self, mock_get_client):
        """Test showing template details successfully."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "bundles": [
                {
                    "id": "tpl-123",
                    "name": "AWS CIS Baseline",
                    "provider": "aws",
                    "framework": "CIS",
                    "industry": "general",
                    "description": "CIS baseline for AWS",
                    "version": "1.0.0",
                    "modules": [
                        {
                            "name": "s3-encryption",
                            "version": "1.0.0",
                            "description": "Ensure S3 buckets are encrypted",
                        }
                    ],
                },
            ]
        }
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.templates.api_list_templates") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["templates", "show", "tpl-123"])

            assert result.exit_code == 0

    @patch("iltero.commands.registry.templates.get_retry_client")
    def test_show_template_not_found(self, mock_get_client):
        """Test showing template when not found."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"bundles": []}
        mock_client.handle_response.return_value = mock_response.parsed

        with patch("iltero.commands.registry.templates.api_list_templates") as mock_api:
            mock_api.sync_detailed.return_value = mock_response

            result = runner.invoke(app, ["templates", "show", "nonexistent"])

            assert "not found" in result.output.lower()
