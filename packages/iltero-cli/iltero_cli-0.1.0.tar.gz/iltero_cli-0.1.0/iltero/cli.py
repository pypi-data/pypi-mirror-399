"""Main CLI application entry point."""

import sys

import typer
from rich.console import Console
from rich.traceback import install as install_rich_traceback

from .core.auth import AuthManager
from .core.config import ConfigManager
from .core.context import ContextManager
from .core.exceptions import IlteroError
from .version import __version__

# Install rich traceback handler for better error display
install_rich_traceback(show_locals=True)

# Create main Typer app
app = typer.Typer(
    name="iltero",
    help="Unified CLI for Iltero platform",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=True,
)

# Create console for rich output
console = Console()

# Global state (initialized on first command)
config: ConfigManager | None = None
auth: AuthManager | None = None
context: ContextManager | None = None


def get_config() -> ConfigManager:
    """Get or create config manager."""
    global config
    if config is None:
        config = ConfigManager()
    return config


def get_auth() -> AuthManager:
    """Get or create auth manager."""
    global auth
    if auth is None:
        auth = AuthManager(get_config())
    return auth


def get_context() -> ContextManager:
    """Get or create context manager."""
    global context
    if context is None:
        cfg = get_config()
        context = ContextManager(cfg.config_dir)
    return context


# Version callback
def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"iltero version {__version__}")
        raise typer.Exit()


# Global options
@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
        envvar="ILTERO_DEBUG",
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, json, yaml",
        envvar="ILTERO_OUTPUT_FORMAT",
    ),
):
    """
    Iltero CLI - Unified command-line interface for the Iltero platform.

    Use 'iltero COMMAND --help' for more information about a specific command.
    """
    # Store global options in config
    cfg = get_config()
    if debug:
        cfg.set("debug", True)
    if output_format:
        cfg.set("output_format", output_format)


# Import and register command groups
from .commands import auth as auth_commands  # noqa: E402
from .commands import bundles as bundles_commands  # noqa: E402
from .commands import compliance as compliance_commands  # noqa: E402
from .commands import config as config_commands  # noqa: E402
from .commands import environment as environment_commands  # noqa: E402
from .commands import registry as registry_commands  # noqa: E402
from .commands import repository as repository_commands  # noqa: E402
from .commands import scan as scan_commands  # noqa: E402
from .commands import scanner as scanner_commands  # noqa: E402
from .commands import stack as stack_commands  # noqa: E402
from .commands import token as token_commands  # noqa: E402
from .commands import workspace as workspace_commands  # noqa: E402

app.add_typer(auth_commands.app, name="auth", help="Authentication management")
app.add_typer(token_commands.app, name="token", help="Token operations")
app.add_typer(workspace_commands.app, name="workspace", help="Workspace management")
app.add_typer(environment_commands.app, name="environment", help="Environment management")
app.add_typer(stack_commands.app, name="stack", help="Stack management")
app.add_typer(scan_commands.app, name="scan", help="Compliance scanning")
app.add_typer(scanner_commands.app, name="scanner", help="Scanner installation")
app.add_typer(registry_commands.app, name="registry", help="Module registry")
app.add_typer(repository_commands.app, name="repository", help="Repository management")
app.add_typer(bundles_commands.app, name="bundles", help="Template bundles")
app.add_typer(compliance_commands.app, name="compliance", help="Compliance management")
app.add_typer(config_commands.app, name="config", help="CLI configuration")


def cli_main():
    """Main entry point with error handling."""
    try:
        app()
    except IlteroError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        if get_config().get("debug", False):
            # In debug mode, show full traceback
            raise
        console.print(f"[red]Unexpected error:[/red] {e}")
        console.print("[dim]Run with --debug for more details[/dim]")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
