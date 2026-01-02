from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
    from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
    from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
    from ..models.terraform_backend_schema import TerraformBackendSchema


T = TypeVar("T", bound="TemplateBundleBootstrapRequestSchema")


@_attrs_define
class TemplateBundleBootstrapRequestSchema:
    """Template Bundle bootstrap request schema.

    Attributes:
        stack_id (str): Unique identifier for the stack to bootstrap
        cloud_config (AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema): Cloud provider
            configuration required for bootstrap
        terraform_backend (TerraformBackendSchema): Schema for Terraform backend configuration.
        template_bundle_id (str): Template Bundle to bootstrap
        template_version (None | str | Unset): Specific version
        project_name (None | str | Unset): Project name
        workspace_environment_ids (list[str] | None | Unset): Target environments
        validate_before_deployment (bool | None | Unset): Validate before deployment Default: True.
        collect_compliance_evidence (bool | None | Unset): Enable evidence collection Default: True.
    """

    stack_id: str
    cloud_config: AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema
    terraform_backend: TerraformBackendSchema
    template_bundle_id: str
    template_version: None | str | Unset = UNSET
    project_name: None | str | Unset = UNSET
    workspace_environment_ids: list[str] | None | Unset = UNSET
    validate_before_deployment: bool | None | Unset = True
    collect_compliance_evidence: bool | None | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
        from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema

        stack_id = self.stack_id

        cloud_config: dict[str, Any]
        if isinstance(self.cloud_config, AWSCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, GCPCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        else:
            cloud_config = self.cloud_config.to_dict()

        terraform_backend = self.terraform_backend.to_dict()

        template_bundle_id = self.template_bundle_id

        template_version: None | str | Unset
        if isinstance(self.template_version, Unset):
            template_version = UNSET
        else:
            template_version = self.template_version

        project_name: None | str | Unset
        if isinstance(self.project_name, Unset):
            project_name = UNSET
        else:
            project_name = self.project_name

        workspace_environment_ids: list[str] | None | Unset
        if isinstance(self.workspace_environment_ids, Unset):
            workspace_environment_ids = UNSET
        elif isinstance(self.workspace_environment_ids, list):
            workspace_environment_ids = self.workspace_environment_ids

        else:
            workspace_environment_ids = self.workspace_environment_ids

        validate_before_deployment: bool | None | Unset
        if isinstance(self.validate_before_deployment, Unset):
            validate_before_deployment = UNSET
        else:
            validate_before_deployment = self.validate_before_deployment

        collect_compliance_evidence: bool | None | Unset
        if isinstance(self.collect_compliance_evidence, Unset):
            collect_compliance_evidence = UNSET
        else:
            collect_compliance_evidence = self.collect_compliance_evidence

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "cloud_config": cloud_config,
                "terraform_backend": terraform_backend,
                "template_bundle_id": template_bundle_id,
            }
        )
        if template_version is not UNSET:
            field_dict["template_version"] = template_version
        if project_name is not UNSET:
            field_dict["project_name"] = project_name
        if workspace_environment_ids is not UNSET:
            field_dict["workspace_environment_ids"] = workspace_environment_ids
        if validate_before_deployment is not UNSET:
            field_dict["validate_before_deployment"] = validate_before_deployment
        if collect_compliance_evidence is not UNSET:
            field_dict["collect_compliance_evidence"] = collect_compliance_evidence

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
        from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
        from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
        from ..models.terraform_backend_schema import TerraformBackendSchema

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        def _parse_cloud_config(data: object) -> AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cloud_config_type_0 = AWSCloudConfigSchema.from_dict(data)

                return cloud_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cloud_config_type_1 = GCPCloudConfigSchema.from_dict(data)

                return cloud_config_type_1
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, dict):
                raise TypeError()
            cloud_config_type_2 = AzureCloudConfigSchema.from_dict(data)

            return cloud_config_type_2

        cloud_config = _parse_cloud_config(d.pop("cloud_config"))

        terraform_backend = TerraformBackendSchema.from_dict(d.pop("terraform_backend"))

        template_bundle_id = d.pop("template_bundle_id")

        def _parse_template_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        template_version = _parse_template_version(d.pop("template_version", UNSET))

        def _parse_project_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_name = _parse_project_name(d.pop("project_name", UNSET))

        def _parse_workspace_environment_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                workspace_environment_ids_type_0 = cast(list[str], data)

                return workspace_environment_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        workspace_environment_ids = _parse_workspace_environment_ids(d.pop("workspace_environment_ids", UNSET))

        def _parse_validate_before_deployment(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        validate_before_deployment = _parse_validate_before_deployment(d.pop("validate_before_deployment", UNSET))

        def _parse_collect_compliance_evidence(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        collect_compliance_evidence = _parse_collect_compliance_evidence(d.pop("collect_compliance_evidence", UNSET))

        template_bundle_bootstrap_request_schema = cls(
            stack_id=stack_id,
            cloud_config=cloud_config,
            terraform_backend=terraform_backend,
            template_bundle_id=template_bundle_id,
            template_version=template_version,
            project_name=project_name,
            workspace_environment_ids=workspace_environment_ids,
            validate_before_deployment=validate_before_deployment,
            collect_compliance_evidence=collect_compliance_evidence,
        )

        template_bundle_bootstrap_request_schema.additional_properties = d
        return template_bundle_bootstrap_request_schema

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
