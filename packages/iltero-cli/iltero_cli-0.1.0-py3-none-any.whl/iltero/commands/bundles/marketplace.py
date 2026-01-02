"""Marketplace commands for discovering and viewing template bundles."""

from __future__ import annotations

import typer

from iltero.api_client.api.terraform_management import (
    terraform_discover_template_bundles_marketplace_e05d1b72 as api_discover_bundles,
)
from iltero.api_client.api.terraform_management import (
    terraform_get_template_bundle_details_marketplace_f00bad9b as api_get_bundle,
)
from iltero.api_client.api.terraform_management import (
    terraform_validate_template_bundle_compliance_marketplace_e5f3a942 as api_validate_compliance,
)
from iltero.api_client.models.compliance_validation_request_schema import (
    ComplianceValidationRequestSchema,
)
from iltero.commands.bundles.main import BUNDLE_COLUMNS, console
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table


def list_bundles(
    industry: str | None = typer.Option(
        None,
        "--industry",
        "-i",
        help="Filter by industry (e.g., healthcare, finance)",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Filter by cloud provider (aws, azure, gcp)",
    ),
    compliance: str | None = typer.Option(
        None,
        "--compliance",
        "-c",
        help="Filter by compliance framework (hipaa, soc2, pci-dss)",
    ),
    tier: str | None = typer.Option(
        None,
        "--tier",
        "-t",
        help="Filter by tier (free, standard, enterprise)",
    ),
    use_case: str | None = typer.Option(
        None,
        "--use-case",
        "-u",
        help="Filter by business use case",
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Filter by marketplace category",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """List available template bundles from marketplace.

    Discover pre-built infrastructure templates filtered by industry,
    provider, compliance requirements, and other criteria.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_discover_bundles.sync_detailed(
            client=auth_client,
            industry=industry,
            compliance_frameworks=compliance,
            provider=provider,
            tier=tier,
            business_use_case=use_case,
            marketplace_category=category,
        )

        result = client.handle_response(response)
        data = result.data
        if not data:
            print_info("No bundles found matching criteria")
            return

        if output_format == "json":
            console.print_json(data=data)
            return

        # Table output
        table = create_table(
            *[col_name for _, col_name in BUNDLE_COLUMNS],
            title="Template Bundles",
        )

        bundles = data if isinstance(data, list) else [data]
        for bundle in bundles:
            row = []
            for col_key, _ in BUNDLE_COLUMNS:
                value = bundle.get(col_key, "")
                # Handle list values (like compliance frameworks)
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(bundles)} bundle(s)")

    except Exception as e:
        print_error(f"Error listing bundles: {e}")
        raise typer.Exit(1)


def show_bundle(
    bundle_id: str = typer.Argument(
        ...,
        help="Template bundle ID",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Show detailed information about a template bundle.

    Display complete details including infrastructure units, UIC contracts,
    compliance configuration, and deployment requirements.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get_bundle.sync_detailed(
            client=auth_client,
            template_bundle_id=bundle_id,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        # Pretty print bundle details
        console.print(f"\n[bold]Template Bundle:[/bold] {data.get('name', bundle_id)}")
        console.print(f"[bold]ID:[/bold] {data.get('id', bundle_id)}")

        if desc := data.get("description"):
            console.print(f"[bold]Description:[/bold] {desc}")

        if provider := data.get("provider"):
            console.print(f"[bold]Provider:[/bold] {provider}")

        if industry := data.get("industry"):
            console.print(f"[bold]Industry:[/bold] {industry}")

        if tier := data.get("tier"):
            console.print(f"[bold]Tier:[/bold] {tier}")

        if frameworks := data.get("compliance_frameworks"):
            if isinstance(frameworks, list):
                frameworks = ", ".join(frameworks)
            console.print(f"[bold]Compliance:[/bold] {frameworks}")

        if category := data.get("marketplace_category"):
            console.print(f"[bold]Category:[/bold] {category}")

        if units := data.get("infrastructure_units"):
            console.print("\n[bold]Infrastructure Units:[/bold]")
            if isinstance(units, list):
                for unit in units:
                    console.print(f"  • {unit}")
            else:
                console.print(f"  {units}")

        if uic := data.get("uic_contracts"):
            console.print("\n[bold]UIC Contracts:[/bold]")
            console.print(f"  {uic}")

        console.print()

    except Exception as e:
        print_error(f"Error showing bundle: {e}")
        raise typer.Exit(1)


def search_bundles(
    query: str = typer.Argument(
        ...,
        help="Search query",
    ),
    industry: str | None = typer.Option(
        None,
        "--industry",
        "-i",
        help="Filter by industry",
    ),
    provider: str | None = typer.Option(
        None,
        "--provider",
        "-p",
        help="Filter by cloud provider",
    ),
    compliance: str | None = typer.Option(
        None,
        "--compliance",
        "-c",
        help="Filter by compliance framework",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Search template bundles by keyword.

    Search across bundle names, descriptions, and metadata using
    the provided query string.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        # Use discover endpoint with filters
        response = api_discover_bundles.sync_detailed(
            client=auth_client,
            industry=industry,
            compliance_frameworks=compliance,
            provider=provider,
        )

        result = client.handle_response(response)
        data = result.data
        if not data:
            print_info(f"No bundles found matching '{query}'")
            return

        # Client-side filtering by query
        bundles = data if isinstance(data, list) else [data]
        query_lower = query.lower()
        filtered = [
            b
            for b in bundles
            if query_lower in str(b.get("name", "")).lower()
            or query_lower in str(b.get("description", "")).lower()
            or query_lower in str(b.get("marketplace_category", "")).lower()
        ]

        if not filtered:
            print_info(f"No bundles found matching '{query}'")
            return

        if output_format == "json":
            console.print_json(data=filtered)
            return

        # Table output
        table = create_table(
            *[col_name for _, col_name in BUNDLE_COLUMNS],
            title=f"Search Results: '{query}'",
        )

        for bundle in filtered:
            row = []
            for col_key, _ in BUNDLE_COLUMNS:
                value = bundle.get(col_key, "")
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                row.append(str(value) if value else "-")
            table.add_row(*row)

        console.print(table)
        print_success(f"Found {len(filtered)} bundle(s)")

    except Exception as e:
        print_error(f"Error searching bundles: {e}")
        raise typer.Exit(1)


def validate_bundle(
    bundle_id: str = typer.Argument(
        ...,
        help="Template bundle ID",
    ),
    frameworks: str | None = typer.Option(
        None,
        "--frameworks",
        "-f",
        help="Comma-separated compliance frameworks to validate",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Validate template bundle compliance.

    Check bundle against compliance frameworks and security requirements
    before bootstrapping a stack.
    """
    try:
        client = get_retry_client()

        # Parse frameworks
        frameworks_list = frameworks.split(",") if frameworks else []

        validation_request = ComplianceValidationRequestSchema(
            frameworks=frameworks_list,
        )

        auth_client = client.get_authenticated_client()
        response = api_validate_compliance.sync_detailed(
            client=auth_client,
            template_bundle_id=bundle_id,
            body=validation_request,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        # Pretty print validation results
        console.print("\n[bold]Compliance Validation Results[/bold]")
        console.print(f"[bold]Bundle ID:[/bold] {bundle_id}")

        if frameworks:
            console.print(f"[bold]Frameworks:[/bold] {frameworks}")

        if status := data.get("status"):
            status_color = "green" if status == "passed" else "red"
            console.print(f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]")

        if violations := data.get("violations"):
            console.print("\n[bold red]Violations:[/bold red]")
            if isinstance(violations, list):
                for v in violations:
                    console.print(f"  • {v}")
            else:
                console.print(f"  {violations}")

        if warnings := data.get("warnings"):
            console.print("\n[bold yellow]Warnings:[/bold yellow]")
            if isinstance(warnings, list):
                for w in warnings:
                    console.print(f"  • {w}")
            else:
                console.print(f"  {warnings}")

        if passed := data.get("controls_passed"):
            console.print(f"\n[bold green]Controls Passed:[/bold green] {passed}")

        if failed := data.get("controls_failed"):
            console.print(f"[bold red]Controls Failed:[/bold red] {failed}")

        console.print()

    except Exception as e:
        print_error(f"Error validating bundle: {e}")
        raise typer.Exit(1)
