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
    from ..models.stack_update_schema_cloud_config_type_3 import StackUpdateSchemaCloudConfigType3
    from ..models.terraform_backend_schema import TerraformBackendSchema


T = TypeVar("T", bound="StackUpdateSchema")


@_attrs_define
class StackUpdateSchema:
    """Schema for updating stack operations.

    Attributes:
        name (None | str | Unset): Name of the stack
        description (None | str | Unset): Description of the stack
        terraform_backend (None | TerraformBackendSchema | Unset): Configuration for Terraform backend
        terraform_working_directory (None | str | Unset): Working directory for Terraform operations
        is_active (bool | None | Unset): Whether the stack is active
        cloud_config (AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema | None |
            StackUpdateSchemaCloudConfigType3 | Unset): Cloud provider specific configuration
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    terraform_backend: None | TerraformBackendSchema | Unset = UNSET
    terraform_working_directory: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    cloud_config: (
        AWSCloudConfigSchema
        | AzureCloudConfigSchema
        | GCPCloudConfigSchema
        | None
        | StackUpdateSchemaCloudConfigType3
        | Unset
    ) = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
        from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
        from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
        from ..models.stack_update_schema_cloud_config_type_3 import StackUpdateSchemaCloudConfigType3
        from ..models.terraform_backend_schema import TerraformBackendSchema

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        terraform_backend: dict[str, Any] | None | Unset
        if isinstance(self.terraform_backend, Unset):
            terraform_backend = UNSET
        elif isinstance(self.terraform_backend, TerraformBackendSchema):
            terraform_backend = self.terraform_backend.to_dict()
        else:
            terraform_backend = self.terraform_backend

        terraform_working_directory: None | str | Unset
        if isinstance(self.terraform_working_directory, Unset):
            terraform_working_directory = UNSET
        else:
            terraform_working_directory = self.terraform_working_directory

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        cloud_config: dict[str, Any] | None | Unset
        if isinstance(self.cloud_config, Unset):
            cloud_config = UNSET
        elif isinstance(self.cloud_config, AWSCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, GCPCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, AzureCloudConfigSchema):
            cloud_config = self.cloud_config.to_dict()
        elif isinstance(self.cloud_config, StackUpdateSchemaCloudConfigType3):
            cloud_config = self.cloud_config.to_dict()
        else:
            cloud_config = self.cloud_config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if terraform_backend is not UNSET:
            field_dict["terraform_backend"] = terraform_backend
        if terraform_working_directory is not UNSET:
            field_dict["terraform_working_directory"] = terraform_working_directory
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if cloud_config is not UNSET:
            field_dict["cloud_config"] = cloud_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
        from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
        from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
        from ..models.stack_update_schema_cloud_config_type_3 import StackUpdateSchemaCloudConfigType3
        from ..models.terraform_backend_schema import TerraformBackendSchema

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_terraform_backend(data: object) -> None | TerraformBackendSchema | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                terraform_backend_type_0 = TerraformBackendSchema.from_dict(data)

                return terraform_backend_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TerraformBackendSchema | Unset, data)

        terraform_backend = _parse_terraform_backend(d.pop("terraform_backend", UNSET))

        def _parse_terraform_working_directory(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        terraform_working_directory = _parse_terraform_working_directory(d.pop("terraform_working_directory", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_cloud_config(
            data: object,
        ) -> (
            AWSCloudConfigSchema
            | AzureCloudConfigSchema
            | GCPCloudConfigSchema
            | None
            | StackUpdateSchemaCloudConfigType3
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
                cloud_config_type_3 = StackUpdateSchemaCloudConfigType3.from_dict(data)

                return cloud_config_type_3
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                AWSCloudConfigSchema
                | AzureCloudConfigSchema
                | GCPCloudConfigSchema
                | None
                | StackUpdateSchemaCloudConfigType3
                | Unset,
                data,
            )

        cloud_config = _parse_cloud_config(d.pop("cloud_config", UNSET))

        stack_update_schema = cls(
            name=name,
            description=description,
            terraform_backend=terraform_backend,
            terraform_working_directory=terraform_working_directory,
            is_active=is_active,
            cloud_config=cloud_config,
        )

        stack_update_schema.additional_properties = d
        return stack_update_schema

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
