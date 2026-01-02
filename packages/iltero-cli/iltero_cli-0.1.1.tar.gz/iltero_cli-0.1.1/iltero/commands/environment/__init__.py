"""Environment management commands."""

from __future__ import annotations

from iltero.api_client.api.environment_management import (
    create_environment as api_create_environment,
)
from iltero.api_client.api.environment_management import (
    delete_environment as api_delete_environment,
)
from iltero.api_client.api.environment_management import (
    get_environment as api_get_environment,
)
from iltero.api_client.api.environment_management import (
    list_environments as api_list_environments,
)
from iltero.api_client.api.environment_management import (
    update_environment as api_update_environment,
)
from iltero.commands.environment.main import (
    ENVIRONMENT_COLUMNS,
    app,
    console,
)
from iltero.commands.environment.operations import (
    create_environment,
    delete_environment,
    list_environments,
    show_environment,
    update_environment,
)
from iltero.core.http import get_retry_client

# Register commands
app.command("list")(list_environments)
app.command("create")(create_environment)
app.command("show")(show_environment)
app.command("update")(update_environment)
app.command("delete")(delete_environment)

__all__ = [
    "app",
    "console",
    "ENVIRONMENT_COLUMNS",
    "list_environments",
    "create_environment",
    "show_environment",
    "update_environment",
    "delete_environment",
    "get_retry_client",
    "api_list_environments",
    "api_create_environment",
    "api_get_environment",
    "api_update_environment",
    "api_delete_environment",
]
