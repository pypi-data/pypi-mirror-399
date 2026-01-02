from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BranchProtectionPolicySchema")


@_attrs_define
class BranchProtectionPolicySchema:
    """Schema for branch protection configuration.

    Attributes:
        enabled (bool | Unset): Enable branch protection Default: True.
        target_branch (str | Unset): Branch these protection rules apply to Default: 'main'.
        required_approvals (int | Unset): Number of required approvals Default: 0.
        dismiss_stale_reviews (bool | Unset): Dismiss stale pull request reviews Default: False.
        require_code_owner_reviews (bool | Unset): Require code owner reviews Default: False.
        enforce_admins (bool | Unset): Enforce rules for administrators Default: False.
        require_linear_history (bool | Unset): Require linear history Default: False.
        allow_force_pushes (bool | Unset): Allow force pushes Default: False.
        allow_deletions (bool | Unset): Allow branch deletions Default: False.
        required_status_checks (list[str] | Unset): Required status checks
    """

    enabled: bool | Unset = True
    target_branch: str | Unset = "main"
    required_approvals: int | Unset = 0
    dismiss_stale_reviews: bool | Unset = False
    require_code_owner_reviews: bool | Unset = False
    enforce_admins: bool | Unset = False
    require_linear_history: bool | Unset = False
    allow_force_pushes: bool | Unset = False
    allow_deletions: bool | Unset = False
    required_status_checks: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        target_branch = self.target_branch

        required_approvals = self.required_approvals

        dismiss_stale_reviews = self.dismiss_stale_reviews

        require_code_owner_reviews = self.require_code_owner_reviews

        enforce_admins = self.enforce_admins

        require_linear_history = self.require_linear_history

        allow_force_pushes = self.allow_force_pushes

        allow_deletions = self.allow_deletions

        required_status_checks: list[str] | Unset = UNSET
        if not isinstance(self.required_status_checks, Unset):
            required_status_checks = self.required_status_checks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if target_branch is not UNSET:
            field_dict["target_branch"] = target_branch
        if required_approvals is not UNSET:
            field_dict["required_approvals"] = required_approvals
        if dismiss_stale_reviews is not UNSET:
            field_dict["dismiss_stale_reviews"] = dismiss_stale_reviews
        if require_code_owner_reviews is not UNSET:
            field_dict["require_code_owner_reviews"] = require_code_owner_reviews
        if enforce_admins is not UNSET:
            field_dict["enforce_admins"] = enforce_admins
        if require_linear_history is not UNSET:
            field_dict["require_linear_history"] = require_linear_history
        if allow_force_pushes is not UNSET:
            field_dict["allow_force_pushes"] = allow_force_pushes
        if allow_deletions is not UNSET:
            field_dict["allow_deletions"] = allow_deletions
        if required_status_checks is not UNSET:
            field_dict["required_status_checks"] = required_status_checks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        target_branch = d.pop("target_branch", UNSET)

        required_approvals = d.pop("required_approvals", UNSET)

        dismiss_stale_reviews = d.pop("dismiss_stale_reviews", UNSET)

        require_code_owner_reviews = d.pop("require_code_owner_reviews", UNSET)

        enforce_admins = d.pop("enforce_admins", UNSET)

        require_linear_history = d.pop("require_linear_history", UNSET)

        allow_force_pushes = d.pop("allow_force_pushes", UNSET)

        allow_deletions = d.pop("allow_deletions", UNSET)

        required_status_checks = cast(list[str], d.pop("required_status_checks", UNSET))

        branch_protection_policy_schema = cls(
            enabled=enabled,
            target_branch=target_branch,
            required_approvals=required_approvals,
            dismiss_stale_reviews=dismiss_stale_reviews,
            require_code_owner_reviews=require_code_owner_reviews,
            enforce_admins=enforce_admins,
            require_linear_history=require_linear_history,
            allow_force_pushes=allow_force_pushes,
            allow_deletions=allow_deletions,
            required_status_checks=required_status_checks,
        )

        branch_protection_policy_schema.additional_properties = d
        return branch_protection_policy_schema

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
