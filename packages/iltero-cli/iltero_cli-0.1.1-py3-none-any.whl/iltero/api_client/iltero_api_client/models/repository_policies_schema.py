from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.branch_protection_policy_schema import BranchProtectionPolicySchema


T = TypeVar("T", bound="RepositoryPoliciesSchema")


@_attrs_define
class RepositoryPoliciesSchema:
    """Schema for repository policies API endpoints.

    Attributes:
        branch_protection (BranchProtectionPolicySchema | None | Unset): Branch protection rules
        auto_merge_enabled (bool | Unset): Enable auto-merge for PRs Default: False.
        delete_branch_on_merge (bool | Unset): Delete branches after merge Default: True.
        allow_squash_merge (bool | Unset): Allow squash merging Default: True.
        allow_merge_commit (bool | Unset): Allow merge commits Default: True.
        allow_rebase_merge (bool | Unset): Allow rebase merging Default: True.
    """

    branch_protection: BranchProtectionPolicySchema | None | Unset = UNSET
    auto_merge_enabled: bool | Unset = False
    delete_branch_on_merge: bool | Unset = True
    allow_squash_merge: bool | Unset = True
    allow_merge_commit: bool | Unset = True
    allow_rebase_merge: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.branch_protection_policy_schema import BranchProtectionPolicySchema

        branch_protection: dict[str, Any] | None | Unset
        if isinstance(self.branch_protection, Unset):
            branch_protection = UNSET
        elif isinstance(self.branch_protection, BranchProtectionPolicySchema):
            branch_protection = self.branch_protection.to_dict()
        else:
            branch_protection = self.branch_protection

        auto_merge_enabled = self.auto_merge_enabled

        delete_branch_on_merge = self.delete_branch_on_merge

        allow_squash_merge = self.allow_squash_merge

        allow_merge_commit = self.allow_merge_commit

        allow_rebase_merge = self.allow_rebase_merge

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if branch_protection is not UNSET:
            field_dict["branch_protection"] = branch_protection
        if auto_merge_enabled is not UNSET:
            field_dict["auto_merge_enabled"] = auto_merge_enabled
        if delete_branch_on_merge is not UNSET:
            field_dict["delete_branch_on_merge"] = delete_branch_on_merge
        if allow_squash_merge is not UNSET:
            field_dict["allow_squash_merge"] = allow_squash_merge
        if allow_merge_commit is not UNSET:
            field_dict["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not UNSET:
            field_dict["allow_rebase_merge"] = allow_rebase_merge

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.branch_protection_policy_schema import BranchProtectionPolicySchema

        d = dict(src_dict)

        def _parse_branch_protection(data: object) -> BranchProtectionPolicySchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                branch_protection_type_0 = BranchProtectionPolicySchema.from_dict(data)

                return branch_protection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BranchProtectionPolicySchema | None | Unset, data)

        branch_protection = _parse_branch_protection(d.pop("branch_protection", UNSET))

        auto_merge_enabled = d.pop("auto_merge_enabled", UNSET)

        delete_branch_on_merge = d.pop("delete_branch_on_merge", UNSET)

        allow_squash_merge = d.pop("allow_squash_merge", UNSET)

        allow_merge_commit = d.pop("allow_merge_commit", UNSET)

        allow_rebase_merge = d.pop("allow_rebase_merge", UNSET)

        repository_policies_schema = cls(
            branch_protection=branch_protection,
            auto_merge_enabled=auto_merge_enabled,
            delete_branch_on_merge=delete_branch_on_merge,
            allow_squash_merge=allow_squash_merge,
            allow_merge_commit=allow_merge_commit,
            allow_rebase_merge=allow_rebase_merge,
        )

        repository_policies_schema.additional_properties = d
        return repository_policies_schema

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
