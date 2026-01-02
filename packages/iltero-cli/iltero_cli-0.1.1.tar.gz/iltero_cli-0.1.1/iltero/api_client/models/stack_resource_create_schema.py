from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stack_resource_create_schema_metadata import StackResourceCreateSchemaMetadata
    from ..models.stack_resource_create_schema_terraform_state_type_0 import (
        StackResourceCreateSchemaTerraformStateType0,
    )


T = TypeVar("T", bound="StackResourceCreateSchema")


@_attrs_define
class StackResourceCreateSchema:
    """Schema for stack resource creation.

    Attributes:
        resource_type (str): Terraform resource type (e.g., 'aws_s3_bucket', 'aws_instance')
        resource_id (str): Provider-specific resource identifier
        cloud_provider (str): Cloud provider ('aws', 'azure', 'gcp')
        resource_name (None | str | Unset): Human-readable resource name
        terraform_address (None | str | Unset): Terraform resource address (e.g., 'module.web.aws_instance.app[0]')
        terraform_state (None | StackResourceCreateSchemaTerraformStateType0 | Unset): Initial Terraform state
        metadata (StackResourceCreateSchemaMetadata | Unset): Resource metadata and tags
        lifecycle_status (str | Unset): Initial lifecycle status Default: 'pending'.
    """

    resource_type: str
    resource_id: str
    cloud_provider: str
    resource_name: None | str | Unset = UNSET
    terraform_address: None | str | Unset = UNSET
    terraform_state: None | StackResourceCreateSchemaTerraformStateType0 | Unset = UNSET
    metadata: StackResourceCreateSchemaMetadata | Unset = UNSET
    lifecycle_status: str | Unset = "pending"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.stack_resource_create_schema_terraform_state_type_0 import (
            StackResourceCreateSchemaTerraformStateType0,
        )

        resource_type = self.resource_type

        resource_id = self.resource_id

        cloud_provider = self.cloud_provider

        resource_name: None | str | Unset
        if isinstance(self.resource_name, Unset):
            resource_name = UNSET
        else:
            resource_name = self.resource_name

        terraform_address: None | str | Unset
        if isinstance(self.terraform_address, Unset):
            terraform_address = UNSET
        else:
            terraform_address = self.terraform_address

        terraform_state: dict[str, Any] | None | Unset
        if isinstance(self.terraform_state, Unset):
            terraform_state = UNSET
        elif isinstance(self.terraform_state, StackResourceCreateSchemaTerraformStateType0):
            terraform_state = self.terraform_state.to_dict()
        else:
            terraform_state = self.terraform_state

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        lifecycle_status = self.lifecycle_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "cloud_provider": cloud_provider,
            }
        )
        if resource_name is not UNSET:
            field_dict["resource_name"] = resource_name
        if terraform_address is not UNSET:
            field_dict["terraform_address"] = terraform_address
        if terraform_state is not UNSET:
            field_dict["terraform_state"] = terraform_state
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if lifecycle_status is not UNSET:
            field_dict["lifecycle_status"] = lifecycle_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_resource_create_schema_metadata import StackResourceCreateSchemaMetadata
        from ..models.stack_resource_create_schema_terraform_state_type_0 import (
            StackResourceCreateSchemaTerraformStateType0,
        )

        d = dict(src_dict)
        resource_type = d.pop("resource_type")

        resource_id = d.pop("resource_id")

        cloud_provider = d.pop("cloud_provider")

        def _parse_resource_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resource_name = _parse_resource_name(d.pop("resource_name", UNSET))

        def _parse_terraform_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        terraform_address = _parse_terraform_address(d.pop("terraform_address", UNSET))

        def _parse_terraform_state(data: object) -> None | StackResourceCreateSchemaTerraformStateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                terraform_state_type_0 = StackResourceCreateSchemaTerraformStateType0.from_dict(data)

                return terraform_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackResourceCreateSchemaTerraformStateType0 | Unset, data)

        terraform_state = _parse_terraform_state(d.pop("terraform_state", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: StackResourceCreateSchemaMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = StackResourceCreateSchemaMetadata.from_dict(_metadata)

        lifecycle_status = d.pop("lifecycle_status", UNSET)

        stack_resource_create_schema = cls(
            resource_type=resource_type,
            resource_id=resource_id,
            cloud_provider=cloud_provider,
            resource_name=resource_name,
            terraform_address=terraform_address,
            terraform_state=terraform_state,
            metadata=metadata,
            lifecycle_status=lifecycle_status,
        )

        stack_resource_create_schema.additional_properties = d
        return stack_resource_create_schema

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
