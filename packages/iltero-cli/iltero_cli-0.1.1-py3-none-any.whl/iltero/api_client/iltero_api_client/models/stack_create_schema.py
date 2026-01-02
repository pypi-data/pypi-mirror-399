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
    from ..models.stack_create_schema_cloud_config_type_3 import StackCreateSchemaCloudConfigType3
    from ..models.terraform_backend_schema import TerraformBackendSchema


T = TypeVar("T", bound="StackCreateSchema")


@_attrs_define
class StackCreateSchema:
    """Schema for stack creation with multi-environment support.

    Attributes:
        name (str): Name of the stack
        terraform_backend (TerraformBackendSchema): Schema for Terraform backend configuration.
        description (None | str | Unset): Description of the stack
        repo_path (None | str | Unset): Auto-generated directory path for stack
        template_id (None | str | Unset): Template bundle ID (e.g., 'hipaa-core-aws')
        template_version (None | str | Unset): Template version for upgrade tracking
        terraform_working_directory (None | str | Unset): Working directory for Terraform operations
        workspace_environment_ids (list[str] | None | Unset): List of WorkspaceEnvironment IDs this stack deploys to. If
            not provided, uses workspace's default environment.
        primary_workspace_environment_id (None | str | Unset): Primary WorkspaceEnvironment ID for default operations.
            If not provided, uses first or default environment.
        cloud_config (AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema | None |
            StackCreateSchemaCloudConfigType3 | Unset): Cloud provider specific configuration
    """

    name: str
    terraform_backend: TerraformBackendSchema
    description: None | str | Unset = UNSET
    repo_path: None | str | Unset = UNSET
    template_id: None | str | Unset = UNSET
    template_version: None | str | Unset = UNSET
    terraform_working_directory: None | str | Unset = UNSET
    workspace_environment_ids: list[str] | None | Unset = UNSET
    primary_workspace_environment_id: None | str | Unset = UNSET
    cloud_config: (
        AWSCloudConfigSchema
        | AzureCloudConfigSchema
        | GCPCloudConfigSchema
        | None
        | StackCreateSchemaCloudConfigType3
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
        from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
        from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
        from ..models.stack_create_schema_cloud_config_type_3 import StackCreateSchemaCloudConfigType3

        name = self.name

        terraform_backend = self.terraform_backend.to_dict()

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        repo_path: None | str | Unset
        if isinstance(self.repo_path, Unset):
            repo_path = UNSET
        else:
            repo_path = self.repo_path

        template_id: None | str | Unset
        if isinstance(self.template_id, Unset):
            template_id = UNSET
        else:
            template_id = self.template_id

        template_version: None | str | Unset
        if isinstance(self.template_version, Unset):
            template_version = UNSET
        else:
            template_version = self.template_version

        terraform_working_directory: None | str | Unset
        if isinstance(self.terraform_working_directory, Unset):
            terraform_working_directory = UNSET
        else:
            terraform_working_directory = self.terraform_working_directory

        workspace_environment_ids: list[str] | None | Unset
        if isinstance(self.workspace_environment_ids, Unset):
            workspace_environment_ids = UNSET
        elif isinstance(self.workspace_environment_ids, list):
            workspace_environment_ids = self.workspace_environment_ids

        else:
            workspace_environment_ids = self.workspace_environment_ids

        primary_workspace_environment_id: None | str | Unset
        if isinstance(self.primary_workspace_environment_id, Unset):
            primary_workspace_environment_id = UNSET
        else:
            primary_workspace_environment_id = self.primary_workspace_environment_id

        cloud_config: dict[str, Any] | None | Unset
        if isinstance(self.cloud_config, Unset):
            cloud_config = UNSET
        elif isinstance(self.cloud_config, AWSCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, GCPCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, AzureCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, StackCreateSchemaCloudConfigType3):
            cloud_config = self.cloud_config.to_dict()
        else:
            cloud_config = self.cloud_config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "terraform_backend": terraform_backend,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if repo_path is not UNSET:
            field_dict["repo_path"] = repo_path
        if template_id is not UNSET:
            field_dict["template_id"] = template_id
        if template_version is not UNSET:
            field_dict["template_version"] = template_version
        if terraform_working_directory is not UNSET:
            field_dict["terraform_working_directory"] = terraform_working_directory
        if workspace_environment_ids is not UNSET:
            field_dict["workspace_environment_ids"] = workspace_environment_ids
        if primary_workspace_environment_id is not UNSET:
            field_dict["primary_workspace_environment_id"] = primary_workspace_environment_id
        if cloud_config is not UNSET:
            field_dict["cloud_config"] = cloud_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
        from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
        from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
        from ..models.stack_create_schema_cloud_config_type_3 import StackCreateSchemaCloudConfigType3
        from ..models.terraform_backend_schema import TerraformBackendSchema

        d = dict(src_dict)
        name = d.pop("name")

        terraform_backend = TerraformBackendSchema.from_dict(d.pop("terraform_backend"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_repo_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repo_path = _parse_repo_path(d.pop("repo_path", UNSET))

        def _parse_template_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        template_id = _parse_template_id(d.pop("template_id", UNSET))

        def _parse_template_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        template_version = _parse_template_version(d.pop("template_version", UNSET))

        def _parse_terraform_working_directory(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        terraform_working_directory = _parse_terraform_working_directory(d.pop("terraform_working_directory", UNSET))

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

        def _parse_primary_workspace_environment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_workspace_environment_id = _parse_primary_workspace_environment_id(
            d.pop("primary_workspace_environment_id", UNSET)
        )

        def _parse_cloud_config(
            data: object,
        ) -> (
            AWSCloudConfigSchema
            | AzureCloudConfigSchema
            | GCPCloudConfigSchema
            | None
            | StackCreateSchemaCloudConfigType3
            | Unset
        ):
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
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
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cloud_config_type_2 = AzureCloudConfigSchema.from_dict(data)

                return cloud_config_type_2
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cloud_config_type_3 = StackCreateSchemaCloudConfigType3.from_dict(data)

                return cloud_config_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                AWSCloudConfigSchema
                | AzureCloudConfigSchema
                | GCPCloudConfigSchema
                | None
                | StackCreateSchemaCloudConfigType3
                | Unset,
                data,
            )

        cloud_config = _parse_cloud_config(d.pop("cloud_config", UNSET))

        stack_create_schema = cls(
            name=name,
            terraform_backend=terraform_backend,
            description=description,
            repo_path=repo_path,
            template_id=template_id,
            template_version=template_version,
            terraform_working_directory=terraform_working_directory,
            workspace_environment_ids=workspace_environment_ids,
            primary_workspace_environment_id=primary_workspace_environment_id,
            cloud_config=cloud_config,
        )

        stack_create_schema.additional_properties = d
        return stack_create_schema

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
