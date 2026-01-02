from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SeverityThresholdsSchema")


@_attrs_define
class SeverityThresholdsSchema:
    """Schema for remediation severity thresholds.

    Attributes:
        auto_remediate (list[str] | Unset): Severities that can be auto-remediated
        require_approval (list[str] | Unset): Severities requiring approval
        block_remediation (list[str] | Unset): Severities that block remediation
    """

    auto_remediate: list[str] | Unset = UNSET
    require_approval: list[str] | Unset = UNSET
    block_remediation: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        auto_remediate: list[str] | Unset = UNSET
        if not isinstance(self.auto_remediate, Unset):
            auto_remediate = self.auto_remediate

        require_approval: list[str] | Unset = UNSET
        if not isinstance(self.require_approval, Unset):
            require_approval = self.require_approval

        block_remediation: list[str] | Unset = UNSET
        if not isinstance(self.block_remediation, Unset):
            block_remediation = self.block_remediation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if auto_remediate is not UNSET:
            field_dict["auto_remediate"] = auto_remediate
        if require_approval is not UNSET:
            field_dict["require_approval"] = require_approval
        if block_remediation is not UNSET:
            field_dict["block_remediation"] = block_remediation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        auto_remediate = cast(list[str], d.pop("auto_remediate", UNSET))

        require_approval = cast(list[str], d.pop("require_approval", UNSET))

        block_remediation = cast(list[str], d.pop("block_remediation", UNSET))

        severity_thresholds_schema = cls(
            auto_remediate=auto_remediate,
            require_approval=require_approval,
            block_remediation=block_remediation,
        )

        severity_thresholds_schema.additional_properties = d
        return severity_thresholds_schema

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
