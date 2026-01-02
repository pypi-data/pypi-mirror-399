"""Bundle commands for template bundle marketplace."""

from __future__ import annotations

from iltero.commands.bundles.integration import (
    analyze_bundle,
    bootstrap_bundle,
    bootstrap_status,
    show_dependencies,
)
from iltero.commands.bundles.main import BUNDLE_COLUMNS, app, console
from iltero.commands.bundles.marketplace import (
    list_bundles,
    search_bundles,
    show_bundle,
    validate_bundle,
)

# Register marketplace commands
app.command("list")(list_bundles)
app.command("show")(show_bundle)
app.command("search")(search_bundles)
app.command("validate")(validate_bundle)

# Register integration commands
app.command("bootstrap")(bootstrap_bundle)
app.command("bootstrap-status")(bootstrap_status)
app.command("analyze")(analyze_bundle)
app.command("dependencies")(show_dependencies)

__all__ = [
    "app",
    "console",
    "BUNDLE_COLUMNS",
    # Marketplace
    "list_bundles",
    "show_bundle",
    "search_bundles",
    "validate_bundle",
    # Integration
    "bootstrap_bundle",
    "bootstrap_status",
    "analyze_bundle",
    "show_dependencies",
]
