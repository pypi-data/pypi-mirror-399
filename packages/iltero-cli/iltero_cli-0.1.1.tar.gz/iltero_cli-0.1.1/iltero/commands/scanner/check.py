"""Scanner availability check command."""

from __future__ import annotations

import sys
from typing import Annotated

import typer
from rich.console import Console

from iltero.scanners import CheckovScanner, CloudCustodianScanner, OPAScanner
from iltero.utils.tables import create_table

console = Console()

# Exit codes
EXIT_SUCCESS = 0
EXIT_SCANNER_MISSING = 1


def scanner_check(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed installation instructions",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output in JSON format",
        ),
    ] = False,
) -> None:
    """Check if required scanners are installed and available.

    Verifies installation status for:
    - Checkov (static analysis)
    - OPA (policy evaluation)
    - Cloud Custodian (runtime scanning)

    Example:
        $ iltero scanner check
        $ iltero scanner check --verbose
    """
    scanners = [
        {
            "scanner": CheckovScanner(),
            "name": "Checkov",
            "description": "Static IaC security analysis",
            "install_pip": "pip install checkov",
            "install_brew": "brew install checkov",
            "docs": "https://www.checkov.io/1.Welcome/Quick%20Start.html",
            "command": "scan static",
        },
        {
            "scanner": OPAScanner(),
            "name": "OPA",
            "description": "Policy evaluation engine",
            "install_pip": None,
            "install_brew": "brew install opa",
            "install_binary": "https://www.openpolicyagent.org/docs/latest/",
            "docs": "https://www.openpolicyagent.org/",
            "command": "scan evaluation",
        },
        {
            "scanner": CloudCustodianScanner(),
            "name": "Cloud Custodian",
            "description": "Runtime cloud compliance",
            "install_pip": "pip install c7n",
            "install_brew": None,
            "docs": "https://cloudcustodian.io/docs/quickstart/index.html",
            "command": "scan runtime",
        },
    ]

    results = []
    all_available = True

    for info in scanners:
        scanner = info["scanner"]
        available = scanner.is_available()
        version = scanner.get_version() if available else None

        if not available:
            all_available = False

        results.append(
            {
                "name": info["name"],
                "available": available,
                "version": version,
                "description": info["description"],
                "install_pip": info.get("install_pip"),
                "install_brew": info.get("install_brew"),
                "install_binary": info.get("install_binary"),
                "docs": info["docs"],
                "command": info["command"],
            }
        )

    if json_output:
        _output_json(results, all_available)
    else:
        _output_table(results, all_available, verbose)

    sys.exit(EXIT_SUCCESS if all_available else EXIT_SCANNER_MISSING)


def _output_json(results: list[dict], all_available: bool) -> None:
    """Output results in JSON format."""
    import json

    output = {
        "all_available": all_available,
        "scanners": [
            {
                "name": r["name"],
                "available": r["available"],
                "version": r["version"],
                "description": r["description"],
                "command": r["command"],
            }
            for r in results
        ],
    }
    console.print(json.dumps(output, indent=2))


def _output_table(
    results: list[dict],
    all_available: bool,
    verbose: bool,
) -> None:
    """Output results in table format."""
    console.print("\n[bold]Scanner Availability Check[/bold]\n")

    table = create_table("Scanner", "Status", "Version", "Used By")
    table.columns[0].style = "cyan"

    for r in results:
        if r["available"]:
            status = "[green]✓ Installed[/green]"
            version = r["version"] or "unknown"
        else:
            status = "[red]✗ Not Found[/red]"
            version = "-"

        table.add_row(
            r["name"],
            status,
            version,
            f"[dim]iltero {r['command']}[/dim]",
        )

    console.print(table)
    console.print()

    if all_available:
        console.print("[green]✓ All scanners ready![/green]\n")
    else:
        console.print("[yellow]⚠ Some scanners are not installed[/yellow]\n")

        if verbose:
            _print_installation_instructions(results)
        else:
            console.print("[dim]Run with --verbose for installation instructions[/dim]\n")


def _print_installation_instructions(results: list[dict]) -> None:
    """Print detailed installation instructions for missing scanners."""
    missing = [r for r in results if not r["available"]]

    if not missing:
        return

    console.print("[bold]Installation Instructions[/bold]\n")

    for r in missing:
        console.print(f"[cyan]{r['name']}[/cyan] - {r['description']}")

        if r.get("install_pip"):
            console.print(f"  [dim]pip:[/dim]    {r['install_pip']}")

        if r.get("install_brew"):
            console.print(f"  [dim]brew:[/dim]   {r['install_brew']}")

        if r.get("install_binary"):
            console.print(f"  [dim]binary:[/dim] {r['install_binary']}")

        console.print(f"  [dim]docs:[/dim]   {r['docs']}")
        console.print()
