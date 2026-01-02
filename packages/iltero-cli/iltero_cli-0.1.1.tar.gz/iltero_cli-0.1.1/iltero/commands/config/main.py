"""Config commands - show, set, reset."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.commands.config import app
from iltero.core.config import ConfigManager
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

console = Console()

# Valid configuration keys that can be set
VALID_KEYS = [
    "api_url",
    "output_format",
    "debug",
    "no_color",
    "default_org",
    "default_workspace",
    "default_environment",
    "request_timeout",
    "scan_timeout",
]


def show_config(
    key: str | None = typer.Argument(None, help="Specific config key to show"),
) -> None:
    """Show current configuration."""
    try:
        config = ConfigManager()

        if key:
            # Show specific key
            value = config.get(key)
            if value is not None:
                console.print(f"[bold]{key}[/bold]: {value}")
            else:
                print_info(f"Config key '{key}' is not set.")
            return

        # Show all config
        table = create_table("Key", "Value", "Source", title="Configuration")

        for k in VALID_KEYS:
            file_value = config.file_config.get(k)
            env_value = getattr(config.env_config, k, None)

            # Determine source and value
            if file_value is not None:
                source = "file"
                value = file_value
            elif env_value is not None:
                source = "env/default"
                value = env_value
            else:
                source = "-"
                value = "-"

            # Mask sensitive values
            if k == "token" and value and value != "-":
                value = value[:8] + "..." if len(str(value)) > 8 else "***"

            table.add_row(k, str(value), source)

        console.print(table)
        console.print(f"\n[dim]Config file: {config.config_path}[/dim]")
    except Exception as e:
        print_error(f"Failed to show config: {e}")
        raise typer.Exit(1) from e


def set_config(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value."""
    try:
        if key not in VALID_KEYS:
            print_error(f"Invalid key '{key}'. Valid keys: {', '.join(VALID_KEYS)}")
            raise typer.Exit(1)

        config = ConfigManager()

        # Convert value types
        if key in ("debug", "no_color"):
            parsed_value = value.lower() in ("true", "1", "yes")
        elif key in ("request_timeout", "scan_timeout"):
            try:
                parsed_value = int(value)
            except ValueError:
                print_error(f"Invalid integer value for {key}: {value}")
                raise typer.Exit(1)
        else:
            parsed_value = value

        config.set(key, parsed_value)
        print_success(f"Set {key} = {parsed_value}")
    except typer.Exit:
        raise
    except Exception as e:
        print_error(f"Failed to set config: {e}")
        raise typer.Exit(1) from e


def reset_config(
    key: str | None = typer.Argument(None, help="Specific key to reset (or all if not specified)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Reset configuration to defaults."""
    try:
        config = ConfigManager()

        if key:
            # Reset specific key
            if key in config.file_config:
                del config.file_config[key]
                config._save_config(config.file_config)
                print_success(f"Reset {key} to default")
            else:
                print_info(f"Key '{key}' was not set in config file.")
            return

        # Reset all config
        if not force:
            confirm = typer.confirm("Reset all configuration to defaults?")
            if not confirm:
                print_info("Cancelled.")
                return

        config.file_config = {}
        config._save_config(config.file_config)
        print_success("Configuration reset to defaults")
    except Exception as e:
        print_error(f"Failed to reset config: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("show")(show_config)
app.command("set")(set_config)
app.command("reset")(reset_config)
