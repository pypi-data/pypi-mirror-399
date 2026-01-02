from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.aws_cloud_config_schema import AWSCloudConfigSchema
    from ..models.azure_cloud_config_schema import AzureCloudConfigSchema
    from ..models.gcp_cloud_config_schema import GCPCloudConfigSchema
    from ..models.terraform_backend_schema import TerraformBackendSchema


T = TypeVar("T", bound="StackBootstrapRequestSchema")


@_attrs_define
class StackBootstrapRequestSchema:
    """Schema for requesting a stack bootstrap operation.

    Attributes:
        stack_id (str): Unique identifier for the stack to bootstrap
        cloud_config (AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema): Cloud provider
            configuration required for bootstrap
        terraform_backend (TerraformBackendSchema): Schema for Terraform backend configuration.
    """

    stack_id: str
    cloud_config: AWSCloudConfigSchema | AzureCloudConfigSchema | GCPCloudConfigSchema
    terraform_backend: TerraformBackendSchema
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

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "cloud_config": cloud_config,
                "terraform_backend": terraform_backend,
            }
        )

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

        stack_bootstrap_request_schema = cls(
            stack_id=stack_id,
            cloud_config=cloud_config,
            terraform_backend=terraform_backend,
        )

        stack_bootstrap_request_schema.additional_properties = d
        return stack_bootstrap_request_schema

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
