from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RemediationCreateSchema")


@_attrs_define
class RemediationCreateSchema:
    """Schema for creating a remediation action.

    Attributes:
        violation_id (str): ID of the violation to remediate
        action_type (str): Type of remediation action (MANUAL or AUTOMATIC)
        details (None | str | Unset): Details or description of the remediation action
    """

    violation_id: str
    action_type: str
    details: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        violation_id = self.violation_id

        action_type = self.action_type

        details: None | str | Unset
        if isinstance(self.details, Unset):
            details = UNSET
        else:
            details = self.details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "violation_id": violation_id,
                "action_type": action_type,
            }
        )
        if details is not UNSET:
            field_dict["details"] = details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        violation_id = d.pop("violation_id")

        action_type = d.pop("action_type")

        def _parse_details(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        details = _parse_details(d.pop("details", UNSET))

        remediation_create_schema = cls(
            violation_id=violation_id,
            action_type=action_type,
            details=details,
        )

        remediation_create_schema.additional_properties = d
        return remediation_create_schema

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
