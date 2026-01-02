from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.terraform_backend_config_schema import TerraformBackendConfigSchema


T = TypeVar("T", bound="TerraformBackendSchema")


@_attrs_define
class TerraformBackendSchema:
    """Schema for Terraform backend configuration.

    Attributes:
        type_ (str): Type of the Terraform backend (e.g., 's3', 'gcs')
        config (TerraformBackendConfigSchema): Schema for Terraform backend configuration.
        workspace (None | str | Unset): Optional workspace name for the backend
    """

    type_: str
    config: TerraformBackendConfigSchema
    workspace: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        config = self.config.to_dict()

        workspace: None | str | Unset
        if isinstance(self.workspace, Unset):
            workspace = UNSET
        else:
            workspace = self.workspace

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "config": config,
            }
        )
        if workspace is not UNSET:
            field_dict["workspace"] = workspace

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.terraform_backend_config_schema import TerraformBackendConfigSchema

        d = dict(src_dict)
        type_ = d.pop("type")

        config = TerraformBackendConfigSchema.from_dict(d.pop("config"))

        def _parse_workspace(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace = _parse_workspace(d.pop("workspace", UNSET))

        terraform_backend_schema = cls(
            type_=type_,
            config=config,
            workspace=workspace,
        )

        terraform_backend_schema.additional_properties = d
        return terraform_backend_schema

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
