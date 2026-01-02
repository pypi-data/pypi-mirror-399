"""Stack management commands."""

from __future__ import annotations

from iltero.api_client.api.stacks import create_stack as api_create_stack
from iltero.api_client.api.stacks import delete_stack as api_delete_stack
from iltero.api_client.api.stacks import get_stack as api_get_stack
from iltero.api_client.api.stacks import list_stacks as api_list_stacks
from iltero.api_client.api.stacks import update_stack as api_update_stack
from iltero.commands.stack import approvals, drift, exceptions, runs, validation, variables
from iltero.commands.stack import remediation as stack_remediation
from iltero.commands.stack.main import STACK_COLUMNS, app, console
from iltero.commands.stack.operations import (
    create_stack,
    delete_stack,
    list_stacks,
    show_stack,
    update_stack,
)
from iltero.core.http import get_retry_client

# Register commands
app.command("list")(list_stacks)
app.command("create")(create_stack)
app.command("show")(show_stack)
app.command("update")(update_stack)
app.command("delete")(delete_stack)

# Register sub-apps
app.add_typer(approvals.app, name="approvals")
app.add_typer(drift.app, name="drift")
app.add_typer(exceptions.app, name="exceptions")
app.add_typer(stack_remediation.app, name="remediation")
app.add_typer(validation.app, name="validation")
app.add_typer(runs.app, name="runs")
app.add_typer(variables.app, name="variables")

__all__ = [
    "app",
    "console",
    "STACK_COLUMNS",
    "list_stacks",
    "create_stack",
    "show_stack",
    "update_stack",
    "delete_stack",
    "get_retry_client",
    "api_list_stacks",
    "api_create_stack",
    "api_get_stack",
    "api_update_stack",
    "api_delete_stack",
    "approvals",
    "drift",
    "exceptions",
    "stack_remediation",
    "validation",
    "runs",
    "variables",
]
