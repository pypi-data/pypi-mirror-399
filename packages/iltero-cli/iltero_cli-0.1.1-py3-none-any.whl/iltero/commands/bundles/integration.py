"""Stack integration commands for template bundles."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from iltero.api_client.api.stack_template_bundle import (
    bootstrap_stack_with_template_bundle as api_bootstrap,
)
from iltero.api_client.api.stack_template_bundle import (
    get_template_bundle_bootstrap_status as api_bootstrap_status,
)
from iltero.api_client.api.stack_template_bundle import (
    stacktemplatebundle_analyze_template_bundle_pattern_6479600c as api_analyze,
)
from iltero.api_client.api.stack_template_bundle import (
    stacktemplatebundle_resolve_cross_unit_dependencies_0b80a788 as api_dependencies,
)
from iltero.api_client.iltero_api_client.models.aws_cloud_config_schema import (
    AWSCloudConfigSchema,
)
from iltero.api_client.iltero_api_client.models.azure_cloud_config_schema import (
    AzureCloudConfigSchema,
)
from iltero.api_client.iltero_api_client.models.gcp_cloud_config_schema import (
    GCPCloudConfigSchema,
)
from iltero.api_client.iltero_api_client.models.template_bundle_bootstrap_request_schema import (
    TemplateBundleBootstrapRequestSchema,
)
from iltero.api_client.iltero_api_client.models.terraform_backend_config_schema import (
    TerraformBackendConfigSchema,
)
from iltero.api_client.iltero_api_client.models.terraform_backend_schema import (
    TerraformBackendSchema,
)
from iltero.commands.bundles.main import console
from iltero.core.http import get_retry_client
from iltero.utils.output import print_error, print_success


def bootstrap_bundle(
    bundle_id: str = typer.Argument(
        ...,
        help="Template bundle ID to bootstrap",
    ),
    stack_id: str = typer.Option(
        ...,
        "--stack-id",
        "-s",
        help="Stack ID to bootstrap with bundle",
        envvar="ILTERO_STACK_ID",
    ),
    config_file: Path | None = typer.Option(
        None,
        "--config-file",
        "-f",
        help="JSON file with cloud_config and terraform_backend",
        exists=True,
    ),
    cloud_provider: str | None = typer.Option(
        None,
        "--cloud-provider",
        help="Cloud provider: aws, gcp, azure",
    ),
    aws_region: str | None = typer.Option(
        None,
        "--aws-region",
        help="[AWS] AWS region for resources",
        envvar="AWS_REGION",
    ),
    aws_role_arn: str | None = typer.Option(
        None,
        "--aws-role-arn",
        help="[AWS] AWS IAM role ARN to assume for deployment",
        envvar="AWS_ROLE_ARN",
    ),
    aws_plan_bucket: str | None = typer.Option(
        None,
        "--aws-plan-bucket",
        help="[AWS] S3 bucket for storing Terraform plans",
        envvar="ILTERO_PLAN_BUCKET",
    ),
    gcp_project_id: str | None = typer.Option(
        None,
        "--gcp-project-id",
        help="[GCP] GCP project ID",
        envvar="GCP_PROJECT_ID",
    ),
    gcp_region: str | None = typer.Option(
        None,
        "--gcp-region",
        help="[GCP] GCP region for resources",
        envvar="GCP_REGION",
    ),
    gcp_service_account: str | None = typer.Option(
        None,
        "--gcp-service-account",
        help="[GCP] Service account email for deployment",
        envvar="GCP_SERVICE_ACCOUNT",
    ),
    gcp_plan_bucket: str | None = typer.Option(
        None,
        "--gcp-plan-bucket",
        help="[GCP] GCS bucket for storing Terraform plans",
        envvar="GCP_PLAN_BUCKET",
    ),
    azure_subscription_id: str | None = typer.Option(
        None,
        "--azure-subscription-id",
        help="[Azure] Azure subscription ID",
        envvar="AZURE_SUBSCRIPTION_ID",
    ),
    azure_tenant_id: str | None = typer.Option(
        None,
        "--azure-tenant-id",
        help="[Azure] Azure tenant ID",
        envvar="AZURE_TENANT_ID",
    ),
    azure_client_id: str | None = typer.Option(
        None,
        "--azure-client-id",
        help="[Azure] Azure client ID for service principal",
        envvar="AZURE_CLIENT_ID",
    ),
    azure_resource_group: str | None = typer.Option(
        None,
        "--azure-resource-group",
        help="[Azure] Azure resource group",
        envvar="AZURE_RESOURCE_GROUP",
    ),
    azure_location: str | None = typer.Option(
        None,
        "--azure-location",
        help="[Azure] Azure location for resources",
        envvar="AZURE_LOCATION",
    ),
    azure_plan_storage_account: str | None = typer.Option(
        None,
        "--azure-plan-storage-account",
        help="[Azure] Storage account for Terraform plans",
        envvar="AZURE_PLAN_STORAGE_ACCOUNT",
    ),
    azure_plan_container: str | None = typer.Option(
        None,
        "--azure-plan-container",
        help="[Azure] Storage container for Terraform plans",
        envvar="AZURE_PLAN_CONTAINER",
    ),
    backend_type: str | None = typer.Option(
        None,
        "--backend-type",
        help="Terraform backend type: s3, gcs, azurerm",
    ),
    backend_bucket: str | None = typer.Option(
        None,
        "--backend-bucket",
        help="Backend storage bucket/container name",
    ),
    backend_region: str | None = typer.Option(
        None,
        "--backend-region",
        help="Backend region",
    ),
    backend_dynamodb_table: str | None = typer.Option(
        None,
        "--backend-dynamodb-table",
        help="DynamoDB table for state locking (S3 backend)",
    ),
    backend_kms_key_id: str | None = typer.Option(
        None,
        "--backend-kms-key-id",
        help="KMS key ID for state encryption",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Bootstrap a stack with a template bundle.

    Associates a template bundle from the marketplace with an existing
    stack, configuring UIC coordination, compliance intelligence, and
    infrastructure units for deployment.

    Configuration can be provided in two ways:

    1. JSON file (recommended):
       iltero bundles bootstrap <bundle-id> --stack-id <id> \\
         --config-file config.json

       Example config.json:
       {
         "cloud_config": {
           "provider": "aws",
           "aws_region": "us-east-1",
           "aws_role_arn": "arn:aws:iam::123456789012:role/Role",
           "plan_bucket": "my-plans"
         },
         "terraform_backend": {
           "type": "s3",
           "config": {
             "bucket": "my-state",
             "region": "us-east-1",
             "encrypt": true,
             "dynamodb_table": "terraform-locks"
           }
         }
       }

    2. CLI parameters:
       AWS: iltero bundles bootstrap <bundle-id> --stack-id <id> \\
         --cloud-provider aws --aws-region us-east-1 \\
         --aws-role-arn arn:aws:iam::123456789012:role/Role \\
         --aws-plan-bucket my-plans \\
         --backend-type s3 --backend-bucket my-state \\
         --backend-region us-east-1

       GCP: iltero bundles bootstrap <bundle-id> --stack-id <id> \\
         --cloud-provider gcp --gcp-project-id my-project \\
         --gcp-region us-central1 \\
         --gcp-service-account sa@project.iam.gserviceaccount.com \\
         --gcp-plan-bucket my-plans \\
         --backend-type gcs --backend-bucket my-state \\
         --backend-region us-central1

       Azure: iltero bundles bootstrap <bundle-id> --stack-id <id> \\
         --cloud-provider azure \\
         --azure-subscription-id <sub-id> \\
         --azure-tenant-id <tenant-id> \\
         --azure-client-id <client-id> \\
         --azure-resource-group my-rg --azure-location eastus \\
         --azure-plan-storage-account myplans \\
         --azure-plan-container plans \\
         --backend-type azurerm --backend-bucket mystate \\
         --backend-region eastus

    Returns a task ID for tracking the asynchronous bootstrap operation.
    """
    try:
        client = get_retry_client()

        if config_file:
            config_data = json.loads(config_file.read_text())
            cloud_config_data = config_data.get("cloud_config", {})
            backend_data = config_data.get("terraform_backend", {})

            provider = cloud_config_data.get("provider") or cloud_provider
            if not provider:
                raise ValueError(
                    "Cloud provider not specified. "
                    "Add 'provider' to cloud_config in JSON "
                    "or use --cloud-provider"
                )

            provider = provider.lower()
            if provider == "aws":
                required_fields = [
                    "aws_region",
                    "aws_role_arn",
                    "plan_bucket",
                ]
                missing = [f for f in required_fields if not cloud_config_data.get(f)]
                if missing:
                    raise ValueError(f"AWS cloud_config missing: {', '.join(missing)}")
                cloud_config = AWSCloudConfigSchema.from_dict(cloud_config_data)
            elif provider == "gcp":
                required_fields = [
                    "project_id",
                    "region",
                    "service_account_email",
                    "plan_bucket",
                ]
                missing = [f for f in required_fields if not cloud_config_data.get(f)]
                if missing:
                    raise ValueError(f"GCP cloud_config missing: {', '.join(missing)}")
                cloud_config = GCPCloudConfigSchema.from_dict(cloud_config_data)
            elif provider == "azure":
                required_fields = [
                    "subscription_id",
                    "tenant_id",
                    "client_id",
                    "resource_group",
                    "location",
                    "plan_storage_account",
                    "plan_container",
                ]
                missing = [f for f in required_fields if not cloud_config_data.get(f)]
                if missing:
                    raise ValueError(f"Azure cloud_config missing: {', '.join(missing)}")
                cloud_config = AzureCloudConfigSchema.from_dict(cloud_config_data)
            else:
                raise ValueError(
                    f"Unsupported cloud provider: {provider}. Must be: aws, gcp, or azure"
                )

            backend_config_data = backend_data.get("config", {})
            required_backend = ["bucket", "region"]
            missing_backend = [f for f in required_backend if not backend_config_data.get(f)]
            if missing_backend:
                raise ValueError(f"Backend config missing: {', '.join(missing_backend)}")

            backend_config = TerraformBackendConfigSchema.from_dict(backend_config_data)
            backend_type_value = backend_data.get("type")
            if not backend_type_value:
                raise ValueError("terraform_backend.type is required in config file")

            terraform_backend = TerraformBackendSchema(
                type_=backend_type_value,
                config=backend_config,
                workspace=backend_data.get("workspace"),
            )
        else:
            if not cloud_provider:
                raise ValueError(
                    "Cloud provider must be specified via --cloud-provider or --config-file"
                )

            provider = cloud_provider.lower()
            if provider == "aws":
                if not all([aws_region, aws_role_arn, aws_plan_bucket]):
                    raise ValueError(
                        "AWS requires: --aws-region, --aws-role-arn, --aws-plan-bucket"
                    )
                cloud_config = AWSCloudConfigSchema(
                    aws_region=aws_region,
                    aws_role_arn=aws_role_arn,
                    plan_bucket=aws_plan_bucket,
                )
            elif provider == "gcp":
                if not all(
                    [
                        gcp_project_id,
                        gcp_region,
                        gcp_service_account,
                        gcp_plan_bucket,
                    ]
                ):
                    raise ValueError(
                        "GCP requires: --gcp-project-id, --gcp-region, "
                        "--gcp-service-account, --gcp-plan-bucket"
                    )
                cloud_config = GCPCloudConfigSchema(
                    project_id=gcp_project_id,
                    region=gcp_region,
                    service_account_email=gcp_service_account,
                    plan_bucket=gcp_plan_bucket,
                )
            elif provider == "azure":
                if not all(
                    [
                        azure_subscription_id,
                        azure_tenant_id,
                        azure_client_id,
                        azure_resource_group,
                        azure_location,
                        azure_plan_storage_account,
                        azure_plan_container,
                    ]
                ):
                    raise ValueError(
                        "Azure requires: --azure-subscription-id, "
                        "--azure-tenant-id, --azure-client-id, "
                        "--azure-resource-group, --azure-location, "
                        "--azure-plan-storage-account, "
                        "--azure-plan-container"
                    )
                cloud_config = AzureCloudConfigSchema(
                    subscription_id=azure_subscription_id,
                    tenant_id=azure_tenant_id,
                    client_id=azure_client_id,
                    resource_group=azure_resource_group,
                    location=azure_location,
                    plan_storage_account=azure_plan_storage_account,
                    plan_container=azure_plan_container,
                )
            else:
                raise ValueError(
                    f"Unsupported cloud provider: {provider}. Must be: aws, gcp, or azure"
                )

            if not backend_type:
                raise ValueError(
                    "Terraform backend type required: --backend-type (s3, gcs, or azurerm)"
                )

            valid_backends = ["s3", "gcs", "azurerm"]
            if backend_type not in valid_backends:
                raise ValueError(
                    f"Invalid backend type: {backend_type}. "
                    f"Must be one of: {', '.join(valid_backends)}"
                )

            if not all([backend_bucket, backend_region]):
                raise ValueError("Backend requires: --backend-bucket, --backend-region")

            backend_config = TerraformBackendConfigSchema(
                bucket=backend_bucket,
                region=backend_region,
                encrypt=True,
                dynamodb_table=backend_dynamodb_table,
                kms_key_id=backend_kms_key_id,
            )

            terraform_backend = TerraformBackendSchema(
                type_=backend_type,
                config=backend_config,
            )

        bootstrap_request = TemplateBundleBootstrapRequestSchema(
            stack_id=stack_id,
            template_bundle_id=bundle_id,
            cloud_config=cloud_config,
            terraform_backend=terraform_backend,
        )

        auth_client = client.get_authenticated_client()
        response = api_bootstrap.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
            body=bootstrap_request,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        console.print("\n[bold green]Bootstrap Initiated[/bold green]")
        console.print(f"[bold]Stack ID:[/bold] {stack_id}")
        console.print(f"[bold]Bundle ID:[/bold] {bundle_id}")

        if task_id := data.get("task_id"):
            console.print(f"[bold]Task ID:[/bold] {task_id}")
            console.print("\n[dim]Check status with:[/dim]")
            console.print(f"  iltero bundles bootstrap-status {task_id} --stack-id={stack_id}")

        if status := data.get("status"):
            console.print(f"[bold]Status:[/bold] {status}")

        console.print()
        print_success("Bootstrap task created successfully")

    except ValueError as e:
        print_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        print_error(f"Error bootstrapping bundle: {e}")
        raise typer.Exit(1)


def bootstrap_status(
    task_id: str = typer.Argument(
        ...,
        help="Bootstrap task ID",
    ),
    stack_id: str = typer.Option(
        ...,
        "--stack-id",
        "-s",
        help="Stack ID",
        envvar="ILTERO_STACK_ID",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Check template bundle bootstrap status.

    Monitor the progress of an asynchronous bootstrap operation,
    showing current status, completed steps, and any errors.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_bootstrap_status.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
            task_id=task_id,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        # Pretty print status
        console.print("\n[bold]Bootstrap Status[/bold]")
        console.print(f"[bold]Task ID:[/bold] {task_id}")
        console.print(f"[bold]Stack ID:[/bold] {stack_id}")

        if status := data.get("status"):
            status_color = {
                "pending": "yellow",
                "in_progress": "blue",
                "completed": "green",
                "failed": "red",
            }.get(status, "white")
            console.print(f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]")

        if progress := data.get("progress"):
            console.print(f"[bold]Progress:[/bold] {progress}%")

        if steps := data.get("completed_steps"):
            console.print("\n[bold]Completed Steps:[/bold]")
            if isinstance(steps, list):
                for step in steps:
                    console.print(f"  ✓ {step}")
            else:
                console.print(f"  {steps}")

        if current := data.get("current_step"):
            console.print(f"\n[bold]Current Step:[/bold] {current}")

        if error := data.get("error"):
            console.print(f"\n[bold red]Error:[/bold red] {error}")

        console.print()

    except Exception as e:
        print_error(f"Error getting bootstrap status: {e}")
        raise typer.Exit(1)


def analyze_bundle(
    stack_id: str = typer.Option(
        ...,
        "--stack-id",
        "-s",
        help="Stack ID with template bundle integration",
        envvar="ILTERO_STACK_ID",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Analyze template bundle pattern for a stack.

    Returns detailed analysis including pattern type, UIC coordination status,
    infrastructure units, compliance configuration, and deployment metrics.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_analyze.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        # Pretty print analysis
        console.print("\n[bold]Template Bundle Analysis[/bold]")
        console.print(f"[bold]Stack ID:[/bold] {stack_id}")

        if pattern := data.get("pattern_type"):
            console.print(f"[bold]Pattern Type:[/bold] {pattern}")

        if uic_status := data.get("uic_coordination_status"):
            console.print(f"[bold]UIC Coordination:[/bold] {uic_status}")

        if units := data.get("infrastructure_units"):
            console.print("\n[bold]Infrastructure Units:[/bold]")
            if isinstance(units, list):
                for unit in units:
                    console.print(f"  • {unit}")
            else:
                console.print(f"  {units}")

        if compliance := data.get("compliance_config"):
            console.print("\n[bold]Compliance Configuration:[/bold]")
            console.print(f"  {compliance}")

        if metrics := data.get("deployment_metrics"):
            console.print("\n[bold]Deployment Metrics:[/bold]")
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    console.print(f"  {key}: {value}")
            else:
                console.print(f"  {metrics}")

        console.print()

    except Exception as e:
        print_error(f"Error analyzing bundle: {e}")
        raise typer.Exit(1)


def show_dependencies(
    stack_id: str = typer.Option(
        ...,
        "--stack-id",
        "-s",
        help="Stack ID with template bundle integration",
        envvar="ILTERO_STACK_ID",
    ),
    output_format: str = typer.Option(
        "table",
        "--output",
        "-o",
        help="Output format: table, json",
    ),
):
    """Show cross-unit dependencies for template bundle.

    Returns the dependency graph showing how infrastructure units
    are connected through UIC contracts and data flows.
    """
    try:
        client = get_retry_client()
        auth_client = client.get_authenticated_client()

        response = api_dependencies.sync_detailed(
            client=auth_client,
            stack_id=stack_id,
        )

        result = client.handle_response(response)
        data = result.data

        if output_format == "json":
            console.print_json(data=data)
            return

        # Pretty print dependencies
        console.print("\n[bold]Cross-Unit Dependencies[/bold]")
        console.print(f"[bold]Stack ID:[/bold] {stack_id}")

        if graph := data.get("dependency_graph"):
            console.print("\n[bold]Dependency Graph:[/bold]")
            if isinstance(graph, list):
                for dep in graph:
                    if isinstance(dep, dict):
                        from_unit = dep.get("from", "?")
                        to_unit = dep.get("to", "?")
                        via = dep.get("via", "")
                        via_text = f" (via {via})" if via else ""
                        console.print(f"  {from_unit} → {to_unit}{via_text}")
                    else:
                        console.print(f"  {dep}")
            else:
                console.print(f"  {graph}")

        if contracts := data.get("uic_contracts"):
            console.print("\n[bold]UIC Contracts:[/bold]")
            if isinstance(contracts, list):
                for contract in contracts:
                    console.print(f"  • {contract}")
            else:
                console.print(f"  {contracts}")

        if flows := data.get("data_flows"):
            console.print("\n[bold]Data Flows:[/bold]")
            if isinstance(flows, list):
                for flow in flows:
                    console.print(f"  • {flow}")
            else:
                console.print(f"  {flows}")

        console.print()

    except Exception as e:
        print_error(f"Error getting dependencies: {e}")
        raise typer.Exit(1)
