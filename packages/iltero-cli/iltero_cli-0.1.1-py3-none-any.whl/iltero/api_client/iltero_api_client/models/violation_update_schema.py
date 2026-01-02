from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ViolationUpdateSchema")


@_attrs_define
class ViolationUpdateSchema:
    """Schema for updating violation status.

    Attributes:
        status (str): New status for the violation
        comment (None | str | Unset): Optional comment explaining the status change
        create_remediation (bool | Unset): Whether to create a remediation action Default: False.
        remediation_type (None | str | Unset): Type of remediation to create (MANUAL or AUTOMATIC)
    """

    status: str
    comment: None | str | Unset = UNSET
    create_remediation: bool | Unset = False
    remediation_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        comment: None | str | Unset
        if isinstance(self.comment, Unset):
            comment = UNSET
        else:
            comment = self.comment

        create_remediation = self.create_remediation

        remediation_type: None | str | Unset
        if isinstance(self.remediation_type, Unset):
            remediation_type = UNSET
        else:
            remediation_type = self.remediation_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if comment is not UNSET:
            field_dict["comment"] = comment
        if create_remediation is not UNSET:
            field_dict["create_remediation"] = create_remediation
        if remediation_type is not UNSET:
            field_dict["remediation_type"] = remediation_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        def _parse_comment(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        comment = _parse_comment(d.pop("comment", UNSET))

        create_remediation = d.pop("create_remediation", UNSET)

        def _parse_remediation_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        remediation_type = _parse_remediation_type(d.pop("remediation_type", UNSET))

        violation_update_schema = cls(
            status=status,
            comment=comment,
            create_remediation=create_remediation,
            remediation_type=remediation_type,
        )

        violation_update_schema.additional_properties = d
        return violation_update_schema

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
