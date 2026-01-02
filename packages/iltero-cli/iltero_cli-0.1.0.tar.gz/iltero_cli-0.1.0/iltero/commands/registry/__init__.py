"""Registry commands for module management."""

from __future__ import annotations

from iltero.commands.registry.main import MODULE_COLUMNS, app, console
from iltero.commands.registry.modules import (
    create_module,
    delete_module,
    list_modules,
    show_module,
    update_module,
)
from iltero.commands.registry.search import search_modules
from iltero.commands.registry.templates import templates_app

# Register commands
app.command("list")(list_modules)
app.command("create")(create_module)
app.command("show")(show_module)
app.command("update")(update_module)
app.command("delete")(delete_module)
app.command("search")(search_modules)

# Register template sub-app
app.add_typer(templates_app, name="templates", help="Template bundles")

__all__ = [
    "app",
    "console",
    "MODULE_COLUMNS",
    "list_modules",
    "create_module",
    "show_module",
    "update_module",
    "delete_module",
    "search_modules",
    "templates_app",
]
