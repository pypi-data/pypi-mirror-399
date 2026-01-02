from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.severity_thresholds_schema import SeverityThresholdsSchema


T = TypeVar("T", bound="RemediationPolicySchema")


@_attrs_define
class RemediationPolicySchema:
    """Schema for remediation policies.

    Attributes:
        auto_remediation_enabled (bool | Unset): Enable automatic remediation Default: False.
        approval_required (bool | Unset): Require approval for remediations Default: True.
        severity_thresholds (SeverityThresholdsSchema | Unset): Schema for remediation severity thresholds.
        remediation_timeout_hours (int | Unset): Timeout for remediation actions in hours Default: 48.
    """

    auto_remediation_enabled: bool | Unset = False
    approval_required: bool | Unset = True
    severity_thresholds: SeverityThresholdsSchema | Unset = UNSET
    remediation_timeout_hours: int | Unset = 48
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        auto_remediation_enabled = self.auto_remediation_enabled

        approval_required = self.approval_required

        severity_thresholds: dict[str, Any] | Unset = UNSET
        if not isinstance(self.severity_thresholds, Unset):
            severity_thresholds = self.severity_thresholds.to_dict()

        remediation_timeout_hours = self.remediation_timeout_hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if auto_remediation_enabled is not UNSET:
            field_dict["auto_remediation_enabled"] = auto_remediation_enabled
        if approval_required is not UNSET:
            field_dict["approval_required"] = approval_required
        if severity_thresholds is not UNSET:
            field_dict["severity_thresholds"] = severity_thresholds
        if remediation_timeout_hours is not UNSET:
            field_dict["remediation_timeout_hours"] = remediation_timeout_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.severity_thresholds_schema import SeverityThresholdsSchema

        d = dict(src_dict)
        auto_remediation_enabled = d.pop("auto_remediation_enabled", UNSET)

        approval_required = d.pop("approval_required", UNSET)

        _severity_thresholds = d.pop("severity_thresholds", UNSET)
        severity_thresholds: SeverityThresholdsSchema | Unset
        if isinstance(_severity_thresholds, Unset):
            severity_thresholds = UNSET
        else:
            severity_thresholds = SeverityThresholdsSchema.from_dict(_severity_thresholds)

        remediation_timeout_hours = d.pop("remediation_timeout_hours", UNSET)

        remediation_policy_schema = cls(
            auto_remediation_enabled=auto_remediation_enabled,
            approval_required=approval_required,
            severity_thresholds=severity_thresholds,
            remediation_timeout_hours=remediation_timeout_hours,
        )

        remediation_policy_schema.additional_properties = d
        return remediation_policy_schema

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
