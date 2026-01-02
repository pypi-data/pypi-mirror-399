from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateBranchRequestSchema")


@_attrs_define
class CreateBranchRequestSchema:
    """Schema for creating a new branch.

    Attributes:
        branch_name (str): Name of the new branch to create
        source_branch (str | Unset): Source branch to create from (default: main) Default: 'main'.
    """

    branch_name: str
    source_branch: str | Unset = "main"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        branch_name = self.branch_name

        source_branch = self.source_branch

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "branch_name": branch_name,
            }
        )
        if source_branch is not UNSET:
            field_dict["source_branch"] = source_branch

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        branch_name = d.pop("branch_name")

        source_branch = d.pop("source_branch", UNSET)

        create_branch_request_schema = cls(
            branch_name=branch_name,
            source_branch=source_branch,
        )

        create_branch_request_schema.additional_properties = d
        return create_branch_request_schema

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
