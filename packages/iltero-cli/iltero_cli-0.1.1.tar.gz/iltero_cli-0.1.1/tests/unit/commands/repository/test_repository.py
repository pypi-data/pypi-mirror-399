"""Tests for repository commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.cli import app

runner = CliRunner()


class TestRepositoryList:
    """Tests for repository list command."""

    @patch("iltero.commands.repository.main.get_retry_client")
    @patch("iltero.commands.repository.main.api_list")
    def test_list_repositories_success(self, mock_api, mock_get_client):
        """Test listing repositories."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "repositories": [
                {
                    "id": "repo-1",
                    "name": "my-repo",
                    "provider": "github",
                    "status": "active",
                    "url": "https://github.com/org/my-repo",
                },
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["repository", "list"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.repository.main.get_retry_client")
    @patch("iltero.commands.repository.main.api_list")
    def test_list_repositories_empty(self, mock_api, mock_get_client):
        """Test listing when no repositories exist."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"repositories": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["repository", "list"])

        assert result.exit_code == 0
        assert "No repositories found" in result.output

    @patch("iltero.commands.repository.main.get_retry_client")
    def test_list_repositories_error(self, mock_get_client):
        """Test list handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["repository", "list"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRepositoryShow:
    """Tests for repository show command."""

    @patch("iltero.commands.repository.main.get_retry_client")
    @patch("iltero.commands.repository.main.api_get")
    def test_show_repository_success(self, mock_api, mock_get_client):
        """Test showing repository details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "repository": {
                "id": "repo-1",
                "name": "my-repo",
                "provider": "github",
                "url": "https://github.com/org/my-repo",
                "status": "active",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["repository", "show", "repo-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.repository.main.get_retry_client")
    def test_show_repository_error(self, mock_get_client):
        """Test show handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["repository", "show", "repo-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRepositoryCreate:
    """Tests for repository create command."""

    @patch("iltero.commands.repository.main.get_retry_client")
    @patch("iltero.commands.repository.main.api_create")
    def test_create_repository_success(self, mock_api, mock_get_client):
        """Test creating repository."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "repository": {
                "id": "repo-new",
                "name": "new-repo",
                "provider": "github",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            [
                "repository",
                "create",
                "new-repo",
                "--url",
                "https://github.com/org/new-repo",
            ],
        )

        assert result.exit_code == 0
        assert "Repository created" in result.output

    @patch("iltero.commands.repository.main.get_retry_client")
    def test_create_repository_error(self, mock_get_client):
        """Test create handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(
            app,
            [
                "repository",
                "create",
                "new-repo",
                "--url",
                "https://github.com/org/new-repo",
            ],
        )

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRepositorySync:
    """Tests for repository sync command."""

    @patch("iltero.commands.repository.main.get_retry_client")
    @patch("iltero.commands.repository.main.api_sync")
    def test_sync_repository_success(self, mock_api, mock_get_client):
        """Test syncing repository."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"status": "syncing"}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["repository", "sync", "repo-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.repository.main.get_retry_client")
    def test_sync_repository_error(self, mock_get_client):
        """Test sync handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["repository", "sync", "repo-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output


class TestRepositoryInit:
    """Tests for repository init command."""

    @patch("iltero.commands.repository.main.get_retry_client")
    @patch("iltero.commands.repository.main.api_initialize")
    def test_init_repository_success(self, mock_api, mock_get_client):
        """Test initializing repository."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"pr_url": "https://github.com/org/repo/pull/1"}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["repository", "init", "repo-1"])

        assert result.exit_code == 0
        mock_api.sync_detailed.assert_called_once()

    @patch("iltero.commands.repository.main.get_retry_client")
    def test_init_repository_error(self, mock_get_client):
        """Test init handles errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("Error")

        result = runner.invoke(app, ["repository", "init", "repo-1"])

        assert result.exit_code == 1
        assert "Failed" in result.output
