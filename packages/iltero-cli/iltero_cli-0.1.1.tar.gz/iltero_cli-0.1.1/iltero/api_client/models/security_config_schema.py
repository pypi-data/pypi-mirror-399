from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SecurityConfigSchema")


@_attrs_define
class SecurityConfigSchema:
    """Schema for security configuration.

    Attributes:
        branch (str): Branch to protect
        required_reviews (int | Unset): Required review count Default: 2.
        enforce_admins (bool | Unset): Enforce for administrators Default: True.
        dismiss_stale_reviews (bool | Unset): Dismiss stale reviews Default: True.
    """

    branch: str
    required_reviews: int | Unset = 2
    enforce_admins: bool | Unset = True
    dismiss_stale_reviews: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        branch = self.branch

        required_reviews = self.required_reviews

        enforce_admins = self.enforce_admins

        dismiss_stale_reviews = self.dismiss_stale_reviews

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "branch": branch,
            }
        )
        if required_reviews is not UNSET:
            field_dict["required_reviews"] = required_reviews
        if enforce_admins is not UNSET:
            field_dict["enforce_admins"] = enforce_admins
        if dismiss_stale_reviews is not UNSET:
            field_dict["dismiss_stale_reviews"] = dismiss_stale_reviews

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        branch = d.pop("branch")

        required_reviews = d.pop("required_reviews", UNSET)

        enforce_admins = d.pop("enforce_admins", UNSET)

        dismiss_stale_reviews = d.pop("dismiss_stale_reviews", UNSET)

        security_config_schema = cls(
            branch=branch,
            required_reviews=required_reviews,
            enforce_admins=enforce_admins,
            dismiss_stale_reviews=dismiss_stale_reviews,
        )

        security_config_schema.additional_properties = d
        return security_config_schema

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
