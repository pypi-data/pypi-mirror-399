from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegistryModuleCreateSchema")


@_attrs_define
class RegistryModuleCreateSchema:
    """Schema for Registry module creation.

    Attributes:
        tool (str): IaC tool type (terraform, opentofu, pulumi)
        namespace (str): Module namespace (e.g., iltero, org name)
        name (str): Module name (e.g., network-baseline, storage-baseline, compute-baseline)
        provider (str): Cloud provider (e.g., aws, azure, gcp)
        description (None | str | Unset): Module description (infrastructure units require comprehensive descriptions)
        is_public (bool | Unset): Whether the module is public or private Default: False.
        is_infrastructure_unit (bool | Unset): Whether this module is an infrastructure unit (complete capability vs
            single resource) Default: False.
        capabilities (list[str] | Unset): Infrastructure capabilities provided (only for infrastructure units)
        compliance_frameworks (list[str] | Unset): Supported compliance frameworks (only for infrastructure units)
    """

    tool: str
    namespace: str
    name: str
    provider: str
    description: None | str | Unset = UNSET
    is_public: bool | Unset = False
    is_infrastructure_unit: bool | Unset = False
    capabilities: list[str] | Unset = UNSET
    compliance_frameworks: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool = self.tool

        namespace = self.namespace

        name = self.name

        provider = self.provider

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_public = self.is_public

        is_infrastructure_unit = self.is_infrastructure_unit

        capabilities: list[str] | Unset = UNSET
        if not isinstance(self.capabilities, Unset):
            capabilities = self.capabilities

        compliance_frameworks: list[str] | Unset = UNSET
        if not isinstance(self.compliance_frameworks, Unset):
            compliance_frameworks = self.compliance_frameworks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tool": tool,
                "namespace": namespace,
                "name": name,
                "provider": provider,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if is_public is not UNSET:
            field_dict["is_public"] = is_public
        if is_infrastructure_unit is not UNSET:
            field_dict["is_infrastructure_unit"] = is_infrastructure_unit
        if capabilities is not UNSET:
            field_dict["capabilities"] = capabilities
        if compliance_frameworks is not UNSET:
            field_dict["compliance_frameworks"] = compliance_frameworks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tool = d.pop("tool")

        namespace = d.pop("namespace")

        name = d.pop("name")

        provider = d.pop("provider")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        is_public = d.pop("is_public", UNSET)

        is_infrastructure_unit = d.pop("is_infrastructure_unit", UNSET)

        capabilities = cast(list[str], d.pop("capabilities", UNSET))

        compliance_frameworks = cast(list[str], d.pop("compliance_frameworks", UNSET))

        registry_module_create_schema = cls(
            tool=tool,
            namespace=namespace,
            name=name,
            provider=provider,
            description=description,
            is_public=is_public,
            is_infrastructure_unit=is_infrastructure_unit,
            capabilities=capabilities,
            compliance_frameworks=compliance_frameworks,
        )

        registry_module_create_schema.additional_properties = d
        return registry_module_create_schema

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
