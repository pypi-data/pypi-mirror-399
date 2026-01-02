"""Compliance manifests commands - generate, show, verify."""

from __future__ import annotations

import typer
from rich.console import Console

from iltero.api_client.api.compliance_manifests import (
    generate_manifest as api_generate,
)
from iltero.api_client.api.compliance_manifests import (
    get_manifest_by_bundle as api_get,
)
from iltero.api_client.api.compliance_manifests import (
    verify_manifest as api_verify,
)
from iltero.api_client.models.manifest_generate_request_schema import (
    ManifestGenerateRequestSchema,
)
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_info, print_success
from iltero.utils.tables import create_table

app = typer.Typer(help="Compliance manifests management")
console = Console()


def generate(
    bundle_id: str = typer.Argument(..., help="Template bundle identifier"),
    frameworks: str | None = typer.Option(
        None, "--frameworks", "-f", help="Frameworks (CSV, e.g., CIS_AWS,SOC2)"
    ),
) -> None:
    """Generate a compliance manifest for a bundle."""
    try:
        framework_list = None
        if frameworks:
            framework_list = [f.strip() for f in frameworks.split(",")]

        body = ManifestGenerateRequestSchema(
            bundle_id=bundle_id,
            frameworks=framework_list,
        )

        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_generate.sync_detailed(
            client=auth_client,
            body=body,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Failed to generate manifest.")
            return

        manifest = data.get("manifest", data)
        manifest_id = manifest.get("id", "N/A")
        print_success(f"Manifest generated: {manifest_id}")

        table = create_table("Field", "Value", title="Manifest Details")
        table.add_row("ID", manifest.get("id", "-"))
        table.add_row("Bundle ID", bundle_id)
        table.add_row("Version", manifest.get("version", "-"))
        table.add_row("Status", manifest.get("status", "-"))
        table.add_row("Created At", manifest.get("created_at", "-"))

        console.print(table)

        # Show included frameworks
        fw_list = manifest.get("frameworks", [])
        if fw_list:
            console.print(f"\nFrameworks: [cyan]{', '.join(fw_list)}[/cyan]")
    except Exception as e:
        print_error(f"Failed to generate manifest: {e}")
        raise typer.Exit(1) from e


def show(
    bundle_id: str = typer.Argument(..., help="Bundle identifier"),
) -> None:
    """Show compliance manifest for a bundle."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_get.sync_detailed(
            bundle_id=bundle_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Manifest not found.")
            return

        manifest = data.get("manifest", data)

        table = create_table("Field", "Value", title="Manifest Details")
        table.add_row("ID", manifest.get("id", "-"))
        table.add_row("Bundle ID", manifest.get("bundle_id", bundle_id))
        table.add_row("Version", manifest.get("version", "-"))
        table.add_row("Status", manifest.get("status", "-"))
        hash_val = manifest.get("hash")
        table.add_row("Hash", hash_val[:16] + "..." if hash_val else "-")
        table.add_row("Created At", manifest.get("created_at", "-"))

        console.print(table)

        # Show frameworks
        frameworks = manifest.get("frameworks", [])
        if frameworks:
            fw_table = create_table("Framework", "Controls", "Policies")
            for fw in frameworks:
                if isinstance(fw, dict):
                    fw_table.add_row(
                        fw.get("name", "-"),
                        str(fw.get("control_count", "-")),
                        str(fw.get("policy_count", "-")),
                    )
                else:
                    fw_table.add_row(str(fw), "-", "-")
            console.print(fw_table)

        # Show controls summary
        controls = manifest.get("controls", [])
        if controls:
            count = len(controls)
            console.print(f"\nTotal controls: [cyan]{count}[/cyan]")
    except Exception as e:
        print_error(f"Failed to get manifest: {e}")
        raise typer.Exit(1) from e


def verify(
    manifest_id: str = typer.Argument(..., help="Manifest identifier"),
) -> None:
    """Verify integrity of a compliance manifest."""
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_verify.sync_detailed(
            manifest_id=manifest_id,
            client=auth_client,
        )

        result = client.handle_response(response)
        data = result.data

        if not data:
            print_info("Verification failed.")
            return

        verification = data.get("verification", data)
        is_valid = verification.get("valid", verification.get("is_valid"))

        if is_valid:
            print_success("Manifest verification passed")
        else:
            console.print("[red]✗[/red] Manifest verification failed")

        table = create_table("Check", "Status", title="Verification Results")

        hash_valid = verification.get("hash_valid", "-")
        if hash_valid is True:
            table.add_row("Hash Integrity", "[green]✓ Valid[/green]")
        elif hash_valid is False:
            table.add_row("Hash Integrity", "[red]✗ Invalid[/red]")
        else:
            table.add_row("Hash Integrity", str(hash_valid))

        sig_valid = verification.get("signature_valid", "-")
        if sig_valid is True:
            table.add_row("Signature", "[green]✓ Valid[/green]")
        elif sig_valid is False:
            table.add_row("Signature", "[red]✗ Invalid[/red]")
        else:
            table.add_row("Signature", str(sig_valid))

        expired = verification.get("expired", None)
        if expired is False:
            table.add_row("Expiration", "[green]✓ Not Expired[/green]")
        elif expired is True:
            table.add_row("Expiration", "[red]✗ Expired[/red]")

        console.print(table)

        # Show any errors
        errors = verification.get("errors", [])
        if errors:
            console.print("\n[red]Errors:[/red]")
            for err in errors:
                console.print(f"  • {err}")
    except Exception as e:
        print_error(f"Failed to verify manifest: {e}")
        raise typer.Exit(1) from e


app.command("generate")(generate)
app.command("show")(show)
app.command("verify")(verify)
