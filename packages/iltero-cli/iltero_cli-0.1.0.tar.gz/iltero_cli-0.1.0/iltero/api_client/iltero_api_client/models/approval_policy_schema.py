from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApprovalPolicySchema")


@_attrs_define
class ApprovalPolicySchema:
    """Schema for approval policies.

    Attributes:
        enabled (bool | Unset): Enable approval requirement Default: True.
        required_approvers (int | Unset): Number of required approvers Default: 1.
        approval_groups (list[str] | Unset): Groups that can approve (e.g., security, platform)
        auto_approve_on_success (bool | Unset): Auto-approve if all checks pass Default: False.
        timeout_hours (int | Unset): Approval timeout in hours Default: 72.
        priority_based_approval (bool | Unset): Use priority-based approval flow Default: False.
        require_justification (bool | Unset): Require justification for approval Default: True.
    """

    enabled: bool | Unset = True
    required_approvers: int | Unset = 1
    approval_groups: list[str] | Unset = UNSET
    auto_approve_on_success: bool | Unset = False
    timeout_hours: int | Unset = 72
    priority_based_approval: bool | Unset = False
    require_justification: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        required_approvers = self.required_approvers

        approval_groups: list[str] | Unset = UNSET
        if not isinstance(self.approval_groups, Unset):
            approval_groups = self.approval_groups

        auto_approve_on_success = self.auto_approve_on_success

        timeout_hours = self.timeout_hours

        priority_based_approval = self.priority_based_approval

        require_justification = self.require_justification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if required_approvers is not UNSET:
            field_dict["required_approvers"] = required_approvers
        if approval_groups is not UNSET:
            field_dict["approval_groups"] = approval_groups
        if auto_approve_on_success is not UNSET:
            field_dict["auto_approve_on_success"] = auto_approve_on_success
        if timeout_hours is not UNSET:
            field_dict["timeout_hours"] = timeout_hours
        if priority_based_approval is not UNSET:
            field_dict["priority_based_approval"] = priority_based_approval
        if require_justification is not UNSET:
            field_dict["require_justification"] = require_justification

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        required_approvers = d.pop("required_approvers", UNSET)

        approval_groups = cast(list[str], d.pop("approval_groups", UNSET))

        auto_approve_on_success = d.pop("auto_approve_on_success", UNSET)

        timeout_hours = d.pop("timeout_hours", UNSET)

        priority_based_approval = d.pop("priority_based_approval", UNSET)

        require_justification = d.pop("require_justification", UNSET)

        approval_policy_schema = cls(
            enabled=enabled,
            required_approvers=required_approvers,
            approval_groups=approval_groups,
            auto_approve_on_success=auto_approve_on_success,
            timeout_hours=timeout_hours,
            priority_based_approval=priority_based_approval,
            require_justification=require_justification,
        )

        approval_policy_schema.additional_properties = d
        return approval_policy_schema

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
