from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_resolution import EventResolution
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventLogUpdateSchema")


@_attrs_define
class EventLogUpdateSchema:
    """Schema for updating event logs.

    Attributes:
        resolution_status (EventResolution): Event resolution statuses.
        resolution_notes (None | str | Unset): Notes on event resolution
        resolved_by (None | str | Unset): Who resolved the event
    """

    resolution_status: EventResolution
    resolution_notes: None | str | Unset = UNSET
    resolved_by: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resolution_status = self.resolution_status.value

        resolution_notes: None | str | Unset
        if isinstance(self.resolution_notes, Unset):
            resolution_notes = UNSET
        else:
            resolution_notes = self.resolution_notes

        resolved_by: None | str | Unset
        if isinstance(self.resolved_by, Unset):
            resolved_by = UNSET
        else:
            resolved_by = self.resolved_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resolution_status": resolution_status,
            }
        )
        if resolution_notes is not UNSET:
            field_dict["resolution_notes"] = resolution_notes
        if resolved_by is not UNSET:
            field_dict["resolved_by"] = resolved_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resolution_status = EventResolution(d.pop("resolution_status"))

        def _parse_resolution_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolution_notes = _parse_resolution_notes(d.pop("resolution_notes", UNSET))

        def _parse_resolved_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolved_by = _parse_resolved_by(d.pop("resolved_by", UNSET))

        event_log_update_schema = cls(
            resolution_status=resolution_status,
            resolution_notes=resolution_notes,
            resolved_by=resolved_by,
        )

        event_log_update_schema.additional_properties = d
        return event_log_update_schema

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
