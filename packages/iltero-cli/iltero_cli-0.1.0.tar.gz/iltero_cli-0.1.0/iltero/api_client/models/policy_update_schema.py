from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyUpdateSchema")


@_attrs_define
class PolicyUpdateSchema:
    """Schema for policy updates.

    Attributes:
        name (None | str | Unset): Human-readable name of the policy
        description (None | str | Unset): Detailed description of the policy
        severity (None | str | Unset): Impact level of violations (LOW, MEDIUM, HIGH, CRITICAL)
        remediation_guidance (None | str | Unset): Instructions for fixing violations
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    severity: None | str | Unset = UNSET
    remediation_guidance: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
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

        severity: None | str | Unset
        if isinstance(self.severity, Unset):
            severity = UNSET
        else:
            severity = self.severity

        remediation_guidance: None | str | Unset
        if isinstance(self.remediation_guidance, Unset):
            remediation_guidance = UNSET
        else:
            remediation_guidance = self.remediation_guidance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if severity is not UNSET:
            field_dict["severity"] = severity
        if remediation_guidance is not UNSET:
            field_dict["remediation_guidance"] = remediation_guidance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        def _parse_severity(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        severity = _parse_severity(d.pop("severity", UNSET))

        def _parse_remediation_guidance(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        remediation_guidance = _parse_remediation_guidance(d.pop("remediation_guidance", UNSET))

        policy_update_schema = cls(
            name=name,
            description=description,
            severity=severity,
            remediation_guidance=remediation_guidance,
        )

        policy_update_schema.additional_properties = d
        return policy_update_schema

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
