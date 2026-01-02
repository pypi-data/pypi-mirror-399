from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyExceptionRequestSchema")


@_attrs_define
class PolicyExceptionRequestSchema:
    """Schema for requesting a policy exception (requires InfoSec approval).

    Attributes:
        stack_id (str): Stack ID requesting exception
        justification (str): Business justification for exception
        scope (list[str]): Specific rules/checks to exempt
        duration_days (int): Requested duration in days (must be time-boxed)
        risk_mitigation (str): How risks will be mitigated
        approver_notes (None | str | Unset): Notes from InfoSec approver
    """

    stack_id: str
    justification: str
    scope: list[str]
    duration_days: int
    risk_mitigation: str
    approver_notes: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        justification = self.justification

        scope = self.scope

        duration_days = self.duration_days

        risk_mitigation = self.risk_mitigation

        approver_notes: None | str | Unset
        if isinstance(self.approver_notes, Unset):
            approver_notes = UNSET
        else:
            approver_notes = self.approver_notes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "justification": justification,
                "scope": scope,
                "duration_days": duration_days,
                "risk_mitigation": risk_mitigation,
            }
        )
        if approver_notes is not UNSET:
            field_dict["approver_notes"] = approver_notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        justification = d.pop("justification")

        scope = cast(list[str], d.pop("scope"))

        duration_days = d.pop("duration_days")

        risk_mitigation = d.pop("risk_mitigation")

        def _parse_approver_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        approver_notes = _parse_approver_notes(d.pop("approver_notes", UNSET))

        policy_exception_request_schema = cls(
            stack_id=stack_id,
            justification=justification,
            scope=scope,
            duration_days=duration_days,
            risk_mitigation=risk_mitigation,
            approver_notes=approver_notes,
        )

        policy_exception_request_schema.additional_properties = d
        return policy_exception_request_schema

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
