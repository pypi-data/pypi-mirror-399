"""Compliance assessment commands - summary, full."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_stack_assessment import (
    get_compliance_summary as api_summary,
)
from iltero.api_client.api.compliance_stack_assessment import (
    perform_full_assessment as api_full,
)
from iltero.api_client.models.assessment_config_schema import (
    AssessmentConfigSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance assessment management")
console = Console()


def _get_score_display(score: int | float | str | None) -> str:
    """Get colored score display string."""
    if score is None:
        return "-"
    if isinstance(score, int | float):
        if score >= 80:
            return f"[green]{score}%[/green]"
        if score >= 60:
            return f"[yellow]{score}%[/yellow]"
        return f"[red]{score}%[/red]"
    return str(score)


def summary(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
) -> None:
    """Get compliance summary for a stack."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_summary.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("No summary data found.")
            return

        summary_data = data.get("summary", data)

        table = create_table("Metric", "Value", title="Compliance Summary")

        # Overall score with color coding
        score = summary_data.get("overall_score", summary_data.get("score"))
        table.add_row("Overall Score", _get_score_display(score))
        table.add_row("Status", summary_data.get("status", "-"))
        policies = summary_data.get("total_policies", "-")
        table.add_row("Total Policies", str(policies))
        compliant = summary_data.get("compliant_count", "-")
        table.add_row("Compliant", str(compliant))
        violations = summary_data.get("violation_count", "-")
        table.add_row("Violations", str(violations))
        last = summary_data.get("last_assessment", "-")
        table.add_row("Last Assessed", last)

        console.print(table)

        # Show framework breakdown if available
        frameworks = summary_data.get("frameworks", [])
        if frameworks:
            fw_table = create_table("Framework", "Score", "Status")
            for fw in frameworks:
                fw_score = fw.get("score", "-")
                fw_table.add_row(
                    fw.get("name", "-"),
                    _get_score_display(fw_score),
                    fw.get("status", "-"),
                )
            console.print(fw_table)
    except Exception as e:
        print_error(f"Failed to get summary: {e}")
        raise typer.Exit(1) from e


def full_assessment(
    stack_id: str = typer.Argument(..., help="Stack identifier"),
    include_validation: bool = typer.Option(True, "--validation/--no-validation"),
    include_evidence: bool = typer.Option(True, "--evidence/--no-evidence"),
    include_monitoring: bool = typer.Option(True, "--monitoring/--no-monitoring"),
    validation_mode: str = typer.Option("FULL", "--mode", "-m", help="Mode: FULL, QUICK, CUSTOM"),
    auto_remediate: bool = typer.Option(False, "--auto-remediate"),
    frameworks: str | None = typer.Option(None, "--frameworks", help="CSV"),
) -> None:
    """Perform full compliance assessment for a stack."""
    try:
        framework_list = None
        if frameworks:
            framework_list = [f.strip() for f in frameworks.split(",")]

        body = AssessmentConfigSchema(
            include_validation=include_validation,
            include_evidence=include_evidence,
            include_monitoring=include_monitoring,
            validation_mode=validation_mode,
            auto_remediate=auto_remediate,
            frameworks=framework_list,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_full.sync_detailed(
            stack_id=stack_id,
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Assessment failed.")
            return

        assessment = data.get("assessment", data)
        print_success(f"Assessment completed for stack: {stack_id}")

        table = create_table("Metric", "Value", title="Assessment Results")

        # Score with color coding
        score = assessment.get("overall_score", assessment.get("score"))
        table.add_row("Overall Score", _get_score_display(score))
        table.add_row("Status", assessment.get("status", "-"))
        table.add_row("Validation Mode", validation_mode)

        policies = assessment.get("policies_evaluated", "-")
        table.add_row("Policies Evaluated", str(policies))
        violations = assessment.get("violations_found", "-")
        table.add_row("Violations Found", str(violations))
        evidence = assessment.get("evidence_collected", "-")
        table.add_row("Evidence Collected", str(evidence))
        table.add_row("Duration", assessment.get("duration", "-"))

        console.print(table)

        # Show violations summary if any
        violations_list = assessment.get("violations", [])
        if violations_list:
            count = len(violations_list)
            console.print(f"\n[yellow]Found {count} violation(s)[/yellow]")
    except Exception as e:
        print_error(f"Failed to perform assessment: {e}")
        raise typer.Exit(1) from e


app.command("summary")(summary)
app.command("full")(full_assessment)
