from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkResolveSchema")


@_attrs_define
class BulkResolveSchema:
    """Schema for bulk resolving events.

    Attributes:
        event_ids (list[UUID]): List of event IDs to resolve
        notes (None | str | Unset): Resolution notes
        resolved_by (None | str | Unset): Who resolved the events
    """

    event_ids: list[UUID]
    notes: None | str | Unset = UNSET
    resolved_by: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_ids = []
        for event_ids_item_data in self.event_ids:
            event_ids_item = str(event_ids_item_data)
            event_ids.append(event_ids_item)

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        resolved_by: None | str | Unset
        if isinstance(self.resolved_by, Unset):
            resolved_by = UNSET
        else:
            resolved_by = self.resolved_by

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_ids": event_ids,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes
        if resolved_by is not UNSET:
            field_dict["resolved_by"] = resolved_by

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        event_ids = []
        _event_ids = d.pop("event_ids")
        for event_ids_item_data in _event_ids:
            event_ids_item = UUID(event_ids_item_data)

            event_ids.append(event_ids_item)

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_resolved_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolved_by = _parse_resolved_by(d.pop("resolved_by", UNSET))

        bulk_resolve_schema = cls(
            event_ids=event_ids,
            notes=notes,
            resolved_by=resolved_by,
        )

        bulk_resolve_schema.additional_properties = d
        return bulk_resolve_schema

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
