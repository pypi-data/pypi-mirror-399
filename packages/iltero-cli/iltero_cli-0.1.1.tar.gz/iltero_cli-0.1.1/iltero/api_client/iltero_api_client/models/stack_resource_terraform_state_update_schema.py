from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stack_resource_terraform_state_update_schema_terraform_state import (
        StackResourceTerraformStateUpdateSchemaTerraformState,
    )


T = TypeVar("T", bound="StackResourceTerraformStateUpdateSchema")


@_attrs_define
class StackResourceTerraformStateUpdateSchema:
    """Schema for updating Terraform state of a resource.

    Attributes:
        resource_type (str): Resource type
        resource_id (str): Resource identifier
        terraform_state (StackResourceTerraformStateUpdateSchemaTerraformState): New Terraform state
        terraform_address (None | str | Unset): Optional Terraform address update
    """

    resource_type: str
    resource_id: str
    terraform_state: StackResourceTerraformStateUpdateSchemaTerraformState
    terraform_address: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_type = self.resource_type

        resource_id = self.resource_id

        terraform_state = self.terraform_state.to_dict()

        terraform_address: None | str | Unset
        if isinstance(self.terraform_address, Unset):
            terraform_address = UNSET
        else:
            terraform_address = self.terraform_address

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "terraform_state": terraform_state,
            }
        )
        if terraform_address is not UNSET:
            field_dict["terraform_address"] = terraform_address

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_resource_terraform_state_update_schema_terraform_state import (
            StackResourceTerraformStateUpdateSchemaTerraformState,
        )

        d = dict(src_dict)
        resource_type = d.pop("resource_type")

        resource_id = d.pop("resource_id")

        terraform_state = StackResourceTerraformStateUpdateSchemaTerraformState.from_dict(d.pop("terraform_state"))

        def _parse_terraform_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        terraform_address = _parse_terraform_address(d.pop("terraform_address", UNSET))

        stack_resource_terraform_state_update_schema = cls(
            resource_type=resource_type,
            resource_id=resource_id,
            terraform_state=terraform_state,
            terraform_address=terraform_address,
        )

        stack_resource_terraform_state_update_schema.additional_properties = d
        return stack_resource_terraform_state_update_schema

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
