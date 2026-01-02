"""Tests for stack runs commands."""

from unittest.mock import Mock, patch

from typer.testing import CliRunner

from iltero.commands.stack import app

runner = CliRunner()


class TestStackRunsList:
    """Tests for stack runs list command."""

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_list")
    def test_list_runs_success(self, mock_api, mock_get_client) -> None:
        """Test listing stack runs."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "runs": [
                {
                    "id": "run-abc123",
                    "status": "success",
                    "type": "apply",
                    "trigger": "manual",
                    "duration_seconds": 125,
                    "created_at": "2025-12-04T10:00:00Z",
                },
                {
                    "id": "run-def456",
                    "status": "failed",
                    "type": "plan",
                    "trigger": "webhook",
                    "duration_seconds": 45,
                    "created_at": "2025-12-04T09:30:00Z",
                },
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["runs", "list", "stack-123"])

        assert result.exit_code == 0
        assert "run-abc123" in result.output
        assert "success" in result.output
        assert "run-def456" in result.output
        assert "failed" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_list")
    def test_list_runs_empty(self, mock_api, mock_get_client) -> None:
        """Test listing when no runs exist."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"runs": []}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(app, ["runs", "list", "stack-123"])

        assert result.exit_code == 0
        assert "No runs found" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_list")
    def test_list_runs_with_limit(self, mock_api, mock_get_client) -> None:
        """Test limiting results."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        runs = [{"id": f"run-{i}", "status": "success"} for i in range(10)]
        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {"runs": runs}
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["runs", "list", "stack-123", "--limit", "5"],
        )

        assert result.exit_code == 0
        assert "5" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_list")
    def test_list_runs_filter_status(self, mock_api, mock_get_client) -> None:
        """Test filtering by status."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "runs": [
                {"id": "run-1", "status": "success"},
                {"id": "run-2", "status": "failed"},
                {"id": "run-3", "status": "success"},
            ]
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["runs", "list", "stack-123", "--status", "failed"],
        )

        assert result.exit_code == 0
        assert "run-2" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    def test_list_runs_error(self, mock_get_client) -> None:
        """Test error handling."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("API error")

        result = runner.invoke(app, ["runs", "list", "stack-123"])

        assert result.exit_code == 1
        assert "Failed to list runs" in result.output


class TestStackRunsShow:
    """Tests for stack runs show command."""

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_get")
    def test_show_run_success(self, mock_api, mock_get_client) -> None:
        """Test showing run details."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "run": {
                "id": "run-abc123",
                "stack_id": "stack-123",
                "status": "success",
                "type": "apply",
                "trigger": "manual",
                "created_at": "2025-12-04T10:00:00Z",
                "started_at": "2025-12-04T10:00:05Z",
                "finished_at": "2025-12-04T10:02:10Z",
                "duration_seconds": 125,
                "resource_changes": {
                    "add": 5,
                    "change": 2,
                    "destroy": 1,
                },
                "outputs": {
                    "vpc_id": "vpc-12345",
                    "subnet_ids": ["subnet-a", "subnet-b"],
                },
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["runs", "show", "stack-123", "run-abc123"],
        )

        assert result.exit_code == 0
        assert "run-abc123" in result.output
        assert "success" in result.output
        assert "vpc_id" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_get")
    def test_show_run_failed_with_error(self, mock_api, mock_get_client) -> None:
        """Test showing failed run with error message."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = {
            "run": {
                "id": "run-failed",
                "status": "failed",
                "error": "Resource limit exceeded",
            }
        }
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["runs", "show", "stack-123", "run-failed"],
        )

        assert result.exit_code == 0
        assert "failed" in result.output
        assert "Resource limit exceeded" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    @patch("iltero.commands.stack.runs.api_get")
    def test_show_run_not_found(self, mock_api, mock_get_client) -> None:
        """Test showing non-existent run."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_auth_client = Mock()
        mock_client.get_authenticated_client.return_value = mock_auth_client

        mock_response = Mock()
        mock_response.parsed = Mock()
        mock_response.parsed.data = None
        mock_api.sync_detailed.return_value = mock_response
        mock_client.handle_response.return_value = mock_response.parsed

        result = runner.invoke(
            app,
            ["runs", "show", "stack-123", "run-notfound"],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    @patch("iltero.commands.stack.runs.get_retry_client")
    def test_show_run_error(self, mock_get_client) -> None:
        """Test error handling."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        mock_client.get_authenticated_client.side_effect = Exception("API error")

        result = runner.invoke(
            app,
            ["runs", "show", "stack-123", "run-abc"],
        )

        assert result.exit_code == 1
        assert "Failed to get run" in result.output
