"""Workspace management commands."""

from __future__ import annotations

from iltero.api_client.api.workspaces import (
    create_workspace as api_create_workspace,
)
from iltero.api_client.api.workspaces import (
    delete_workspace as api_delete_workspace,
)
from iltero.api_client.api.workspaces import get_workspace as api_get_workspace
from iltero.api_client.api.workspaces import (
    list_workspaces as api_list_workspaces,
)
from iltero.api_client.api.workspaces import (
    update_workspace as api_update_workspace,
)
from iltero.commands.workspace.main import (
    WORKSPACE_COLUMNS,
    app,
    console,
)
from iltero.commands.workspace.operations import (
    create_workspace,
    delete_workspace,
    list_workspaces,
    show_workspace,
    update_workspace,
)
from iltero.core.http import get_retry_client

# Register commands
app.command("list")(list_workspaces)
app.command("create")(create_workspace)
app.command("show")(show_workspace)
app.command("update")(update_workspace)
app.command("delete")(delete_workspace)

__all__ = [
    "app",
    "console",
    "WORKSPACE_COLUMNS",
    "list_workspaces",
    "create_workspace",
    "show_workspace",
    "update_workspace",
    "delete_workspace",
    "get_retry_client",
    "api_list_workspaces",
    "api_create_workspace",
    "api_get_workspace",
    "api_update_workspace",
    "api_delete_workspace",
]
