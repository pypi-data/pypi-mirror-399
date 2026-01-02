from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EvidenceRequirementsSchema")


@_attrs_define
class EvidenceRequirementsSchema:
    """Schema for evidence requirements by phase.

    Attributes:
        pre_deployment (list[str] | Unset): Required evidence before deployment
        post_deployment (list[str] | Unset): Required evidence after deployment
        continuous (list[str] | Unset): Required evidence for continuous monitoring
    """

    pre_deployment: list[str] | Unset = UNSET
    post_deployment: list[str] | Unset = UNSET
    continuous: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pre_deployment: list[str] | Unset = UNSET
        if not isinstance(self.pre_deployment, Unset):
            pre_deployment = self.pre_deployment

        post_deployment: list[str] | Unset = UNSET
        if not isinstance(self.post_deployment, Unset):
            post_deployment = self.post_deployment

        continuous: list[str] | Unset = UNSET
        if not isinstance(self.continuous, Unset):
            continuous = self.continuous

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pre_deployment is not UNSET:
            field_dict["pre_deployment"] = pre_deployment
        if post_deployment is not UNSET:
            field_dict["post_deployment"] = post_deployment
        if continuous is not UNSET:
            field_dict["continuous"] = continuous

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pre_deployment = cast(list[str], d.pop("pre_deployment", UNSET))

        post_deployment = cast(list[str], d.pop("post_deployment", UNSET))

        continuous = cast(list[str], d.pop("continuous", UNSET))

        evidence_requirements_schema = cls(
            pre_deployment=pre_deployment,
            post_deployment=post_deployment,
            continuous=continuous,
        )

        evidence_requirements_schema.additional_properties = d
        return evidence_requirements_schema

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
