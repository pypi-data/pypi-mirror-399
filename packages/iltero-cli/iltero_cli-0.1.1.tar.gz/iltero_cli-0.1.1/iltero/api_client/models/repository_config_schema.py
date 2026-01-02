from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepositoryConfigSchema")


@_attrs_define
class RepositoryConfigSchema:
    """
    Attributes:
        enable_issues (bool | Unset): Enable issues Default: True.
        enable_wiki (bool | Unset): Enable wiki Default: True.
        enable_projects (bool | Unset): Enable projects Default: True.
        enable_vulnerability_alerts (bool | Unset): Enable vulnerability alerts Default: True.
        allow_squash_merge (bool | Unset): Allow squash merge Default: True.
        allow_merge_commit (bool | Unset): Allow merge commit Default: True.
        allow_rebase_merge (bool | Unset): Allow rebase merge Default: True.
        delete_branch_on_merge (bool | Unset): Delete branch on merge Default: False.
    """

    enable_issues: bool | Unset = True
    enable_wiki: bool | Unset = True
    enable_projects: bool | Unset = True
    enable_vulnerability_alerts: bool | Unset = True
    allow_squash_merge: bool | Unset = True
    allow_merge_commit: bool | Unset = True
    allow_rebase_merge: bool | Unset = True
    delete_branch_on_merge: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable_issues = self.enable_issues

        enable_wiki = self.enable_wiki

        enable_projects = self.enable_projects

        enable_vulnerability_alerts = self.enable_vulnerability_alerts

        allow_squash_merge = self.allow_squash_merge

        allow_merge_commit = self.allow_merge_commit

        allow_rebase_merge = self.allow_rebase_merge

        delete_branch_on_merge = self.delete_branch_on_merge

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_issues is not UNSET:
            field_dict["enable_issues"] = enable_issues
        if enable_wiki is not UNSET:
            field_dict["enable_wiki"] = enable_wiki
        if enable_projects is not UNSET:
            field_dict["enable_projects"] = enable_projects
        if enable_vulnerability_alerts is not UNSET:
            field_dict["enable_vulnerability_alerts"] = enable_vulnerability_alerts
        if allow_squash_merge is not UNSET:
            field_dict["allow_squash_merge"] = allow_squash_merge
        if allow_merge_commit is not UNSET:
            field_dict["allow_merge_commit"] = allow_merge_commit
        if allow_rebase_merge is not UNSET:
            field_dict["allow_rebase_merge"] = allow_rebase_merge
        if delete_branch_on_merge is not UNSET:
            field_dict["delete_branch_on_merge"] = delete_branch_on_merge

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable_issues = d.pop("enable_issues", UNSET)

        enable_wiki = d.pop("enable_wiki", UNSET)

        enable_projects = d.pop("enable_projects", UNSET)

        enable_vulnerability_alerts = d.pop("enable_vulnerability_alerts", UNSET)

        allow_squash_merge = d.pop("allow_squash_merge", UNSET)

        allow_merge_commit = d.pop("allow_merge_commit", UNSET)

        allow_rebase_merge = d.pop("allow_rebase_merge", UNSET)

        delete_branch_on_merge = d.pop("delete_branch_on_merge", UNSET)

        repository_config_schema = cls(
            enable_issues=enable_issues,
            enable_wiki=enable_wiki,
            enable_projects=enable_projects,
            enable_vulnerability_alerts=enable_vulnerability_alerts,
            allow_squash_merge=allow_squash_merge,
            allow_merge_commit=allow_merge_commit,
            allow_rebase_merge=allow_rebase_merge,
            delete_branch_on_merge=delete_branch_on_merge,
        )

        repository_config_schema.additional_properties = d
        return repository_config_schema

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
