"""Stack validation commands - status, post-deployment."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_stack_validation import (
    get_compliance_status as api_status,
)
from iltero.api_client.api.compliance_stack_validation import (
    validate_post_deployment as api_post,
)
from iltero.api_client.models.post_deployment_validation_request_schema import (  # noqa: E501
    PostDeploymentValidationRequestSchema,
)
from iltero.api_client.models.post_deployment_validation_request_schema_deployment_results import (  # noqa: E501
    PostDeploymentValidationRequestSchemaDeploymentResults,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Stack compliance validation")
console = Console()


def status(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
) -> None:
    """Get compliance validation status for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_status.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No compliance status available.")
            return

        status_data = data.get("status", data)

        # Show overall status
        overall = status_data.get("overall_status", "unknown")
        if overall == "compliant":
            console.print("[green]✓ Stack is compliant[/green]")
        elif overall == "non_compliant":
            console.print("[red]✗ Stack is non-compliant[/red]")
        else:
            console.print(f"[yellow]⚠ Status: {overall}[/yellow]")

        table = create_table("Field", "Value", title="Compliance Status")
        table.add_row("Stack ID", stack_id)
        table.add_row("Overall Status", status_data.get("overall_status", "-"))
        table.add_row("Score", str(status_data.get("score", "-")))
        table.add_row("Violations", str(status_data.get("violation_count", "-")))
        table.add_row("Last Validated", status_data.get("last_validated", "-"))

        console.print(table)

        # Show framework status if available
        frameworks = status_data.get("frameworks", [])
        if frameworks:
            f_table = create_table("Framework", "Status", "Score")
            for fw in frameworks:
                f_table.add_row(
                    fw.get("name", "-"),
                    fw.get("status", "-"),
                    str(fw.get("score", "-")),
                )
            console.print("\n[bold]Framework Status[/bold]")
            console.print(f_table)
    except Exception as e:
        print_error(f"Failed to get compliance status: {e}")
        raise typer.Exit(1) from e


def post_deployment(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    deployment_id: str = typer.Option(None, "--deployment", "-d", help="Deployment ID"),
) -> None:
    """Run post-deployment validation for a stack."""
    try:
        deployment_results = PostDeploymentValidationRequestSchemaDeploymentResults()
        body = PostDeploymentValidationRequestSchema(
            stack_id=stack_id,
            deployment_results=deployment_results,
            deployment_id=deployment_id,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_post.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Validation failed to complete.")
            return

        validation = data.get("validation", data)

        # Show result
        passed = validation.get("passed", False)
        if passed:
            print_success("Post-deployment validation passed")
        else:
            console.print("[red]✗ Post-deployment validation failed[/red]")

        table = create_table("Field", "Value", title="Validation Results")
        table.add_row("Stack ID", stack_id)
        table.add_row("Status", "Passed" if passed else "Failed")
        table.add_row("Checks Run", str(validation.get("checks_run", "-")))
        table.add_row("Checks Passed", str(validation.get("checks_passed", "-")))
        table.add_row("Checks Failed", str(validation.get("checks_failed", "-")))
        table.add_row("Duration", validation.get("duration", "-"))

        console.print(table)

        # Show failures if any
        failures = validation.get("failures", [])
        if failures:
            fail_table = create_table("Check", "Severity", "Message")
            for f in failures[:10]:
                fail_table.add_row(
                    f.get("check", "-"),
                    f.get("severity", "-"),
                    f.get("message", "-")[:50],
                )
            console.print("\n[bold red]Failures[/bold red]")
            console.print(fail_table)
    except Exception as e:
        print_error(f"Failed to run post-deployment validation: {e}")
        raise typer.Exit(1) from e


# Register commands
app.command("status")(status)
app.command("post-deployment")(post_deployment)
