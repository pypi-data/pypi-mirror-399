from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyExceptionApprovalSchema")


@_attrs_define
class PolicyExceptionApprovalSchema:
    """Schema for approving/rejecting a policy exception.

    Attributes:
        exception_ref (str): Exception reference ID
        approved (bool): Whether exception is approved
        approver_id (str): InfoSec approver ID
        expiry_date (str): When exception expires (ISO format)
        conditions (list[str] | None | Unset): Conditions for approval
        notes (None | str | Unset): Approval/rejection notes
    """

    exception_ref: str
    approved: bool
    approver_id: str
    expiry_date: str
    conditions: list[str] | None | Unset = UNSET
    notes: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        exception_ref = self.exception_ref

        approved = self.approved

        approver_id = self.approver_id

        expiry_date = self.expiry_date

        conditions: list[str] | None | Unset
        if isinstance(self.conditions, Unset):
            conditions = UNSET
        elif isinstance(self.conditions, list):
            conditions = self.conditions

        else:
            conditions = self.conditions

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exception_ref": exception_ref,
                "approved": approved,
                "approver_id": approver_id,
                "expiry_date": expiry_date,
            }
        )
        if conditions is not UNSET:
            field_dict["conditions"] = conditions
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        exception_ref = d.pop("exception_ref")

        approved = d.pop("approved")

        approver_id = d.pop("approver_id")

        expiry_date = d.pop("expiry_date")

        def _parse_conditions(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                conditions_type_0 = cast(list[str], data)

                return conditions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        conditions = _parse_conditions(d.pop("conditions", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        policy_exception_approval_schema = cls(
            exception_ref=exception_ref,
            approved=approved,
            approver_id=approver_id,
            expiry_date=expiry_date,
            conditions=conditions,
            notes=notes,
        )

        policy_exception_approval_schema.additional_properties = d
        return policy_exception_approval_schema

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
