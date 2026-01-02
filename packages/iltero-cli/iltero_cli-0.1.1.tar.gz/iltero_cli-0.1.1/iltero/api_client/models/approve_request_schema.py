from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.approve_request_schema_policy_overrides import ApproveRequestSchemaPolicyOverrides


T = TypeVar("T", bound="ApproveRequestSchema")


@_attrs_define
class ApproveRequestSchema:
    """Schema for approving a deployment.

    Attributes:
        comment (str | Unset): Optional comment with the approval Default: ''.
        policy_overrides (ApproveRequestSchemaPolicyOverrides | Unset): Optional policy overrides to grant
    """

    comment: str | Unset = ""
    policy_overrides: ApproveRequestSchemaPolicyOverrides | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        comment = self.comment

        policy_overrides: dict[str, Any] | Unset = UNSET
        if not isinstance(self.policy_overrides, Unset):
            policy_overrides = self.policy_overrides.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if comment is not UNSET:
            field_dict["comment"] = comment
        if policy_overrides is not UNSET:
            field_dict["policy_overrides"] = policy_overrides

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.approve_request_schema_policy_overrides import ApproveRequestSchemaPolicyOverrides

        d = dict(src_dict)
        comment = d.pop("comment", UNSET)

        _policy_overrides = d.pop("policy_overrides", UNSET)
        policy_overrides: ApproveRequestSchemaPolicyOverrides | Unset
        if isinstance(_policy_overrides, Unset):
            policy_overrides = UNSET
        else:
            policy_overrides = ApproveRequestSchemaPolicyOverrides.from_dict(_policy_overrides)

        approve_request_schema = cls(
            comment=comment,
            policy_overrides=policy_overrides,
        )

        approve_request_schema.additional_properties = d
        return approve_request_schema

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
