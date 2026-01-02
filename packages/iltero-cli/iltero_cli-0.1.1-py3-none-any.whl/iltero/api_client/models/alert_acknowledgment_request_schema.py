from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="AlertAcknowledgmentRequestSchema")


@_attrs_define
class AlertAcknowledgmentRequestSchema:
    """Request schema for acknowledging an alert.

    Attributes:
        stack_id (str): Stack identifier
        workspace_id (None | str | Unset): Workspace identifier
        acknowledgment_note (None | str | Unset): Optional note for the acknowledgment
        action_taken (None | str | Unset): Action taken or to be taken
        assign_to (None | str | Unset): User ID to assign the alert to
        estimated_resolution_time (datetime.datetime | None | Unset): Estimated time for resolution
    """

    stack_id: str
    workspace_id: None | str | Unset = UNSET
    acknowledgment_note: None | str | Unset = UNSET
    action_taken: None | str | Unset = UNSET
    assign_to: None | str | Unset = UNSET
    estimated_resolution_time: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        acknowledgment_note: None | str | Unset
        if isinstance(self.acknowledgment_note, Unset):
            acknowledgment_note = UNSET
        else:
            acknowledgment_note = self.acknowledgment_note

        action_taken: None | str | Unset
        if isinstance(self.action_taken, Unset):
            action_taken = UNSET
        else:
            action_taken = self.action_taken

        assign_to: None | str | Unset
        if isinstance(self.assign_to, Unset):
            assign_to = UNSET
        else:
            assign_to = self.assign_to

        estimated_resolution_time: None | str | Unset
        if isinstance(self.estimated_resolution_time, Unset):
            estimated_resolution_time = UNSET
        elif isinstance(self.estimated_resolution_time, datetime.datetime):
            estimated_resolution_time = self.estimated_resolution_time.isoformat()
        else:
            estimated_resolution_time = self.estimated_resolution_time

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if acknowledgment_note is not UNSET:
            field_dict["acknowledgment_note"] = acknowledgment_note
        if action_taken is not UNSET:
            field_dict["action_taken"] = action_taken
        if assign_to is not UNSET:
            field_dict["assign_to"] = assign_to
        if estimated_resolution_time is not UNSET:
            field_dict["estimated_resolution_time"] = estimated_resolution_time

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        def _parse_acknowledgment_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        acknowledgment_note = _parse_acknowledgment_note(d.pop("acknowledgment_note", UNSET))

        def _parse_action_taken(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_taken = _parse_action_taken(d.pop("action_taken", UNSET))

        def _parse_assign_to(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        assign_to = _parse_assign_to(d.pop("assign_to", UNSET))

        def _parse_estimated_resolution_time(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                estimated_resolution_time_type_0 = isoparse(data)

                return estimated_resolution_time_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        estimated_resolution_time = _parse_estimated_resolution_time(d.pop("estimated_resolution_time", UNSET))

        alert_acknowledgment_request_schema = cls(
            stack_id=stack_id,
            workspace_id=workspace_id,
            acknowledgment_note=acknowledgment_note,
            action_taken=action_taken,
            assign_to=assign_to,
            estimated_resolution_time=estimated_resolution_time,
        )

        alert_acknowledgment_request_schema.additional_properties = d
        return alert_acknowledgment_request_schema

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
