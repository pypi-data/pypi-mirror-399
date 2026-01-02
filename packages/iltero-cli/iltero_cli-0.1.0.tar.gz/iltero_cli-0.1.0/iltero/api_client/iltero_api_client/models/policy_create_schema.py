from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyCreateSchema")


@_attrs_define
class PolicyCreateSchema:
    """Schema for policy creation.

    Attributes:
        policy_set_id (str): ID of the policy set this policy belongs to
        rule_id (str): Unique identifier for the rule (e.g., CKV_AWS_123)
        name (str): Human-readable name of the policy
        severity (str): Impact level of violations (LOW, MEDIUM, HIGH, CRITICAL)
        description (None | str | Unset): Detailed description of the policy
        remediation_guidance (None | str | Unset): Instructions for fixing violations
    """

    policy_set_id: str
    rule_id: str
    name: str
    severity: str
    description: None | str | Unset = UNSET
    remediation_guidance: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        policy_set_id = self.policy_set_id

        rule_id = self.rule_id

        name = self.name

        severity = self.severity

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        remediation_guidance: None | str | Unset
        if isinstance(self.remediation_guidance, Unset):
            remediation_guidance = UNSET
        else:
            remediation_guidance = self.remediation_guidance

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "policy_set_id": policy_set_id,
                "rule_id": rule_id,
                "name": name,
                "severity": severity,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if remediation_guidance is not UNSET:
            field_dict["remediation_guidance"] = remediation_guidance

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        policy_set_id = d.pop("policy_set_id")

        rule_id = d.pop("rule_id")

        name = d.pop("name")

        severity = d.pop("severity")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_remediation_guidance(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        remediation_guidance = _parse_remediation_guidance(d.pop("remediation_guidance", UNSET))

        policy_create_schema = cls(
            policy_set_id=policy_set_id,
            rule_id=rule_id,
            name=name,
            severity=severity,
            description=description,
            remediation_guidance=remediation_guidance,
        )

        policy_create_schema.additional_properties = d
        return policy_create_schema

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
