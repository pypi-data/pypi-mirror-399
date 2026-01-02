from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.event_category import EventCategory
from ..models.event_resolution import EventResolution
from ..models.event_severity import EventSeverity
from ..models.event_source import EventSource
from ..models.event_type import EventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="EventLogFilterSchema")


@_attrs_define
class EventLogFilterSchema:
    """Schema for filtering event logs.

    Attributes:
        event_types (list[EventType] | None | Unset): Filter by event types
        categories (list[EventCategory] | None | Unset): Filter by categories
        severities (list[EventSeverity] | None | Unset): Filter by severities
        sources (list[EventSource] | None | Unset): Filter by sources
        user_ids (list[str] | None | Unset): Filter by user IDs
        is_threat (bool | None | Unset): Filter by threat status
        resolution_statuses (list[EventResolution] | None | Unset): Filter by resolution statuses
        start_date (datetime.datetime | None | Unset): Filter by start date
        end_date (datetime.datetime | None | Unset): Filter by end date
        limit (int | Unset): Limit results Default: 100.
        offset (int | Unset): Offset results Default: 0.
    """

    event_types: list[EventType] | None | Unset = UNSET
    categories: list[EventCategory] | None | Unset = UNSET
    severities: list[EventSeverity] | None | Unset = UNSET
    sources: list[EventSource] | None | Unset = UNSET
    user_ids: list[str] | None | Unset = UNSET
    is_threat: bool | None | Unset = UNSET
    resolution_statuses: list[EventResolution] | None | Unset = UNSET
    start_date: datetime.datetime | None | Unset = UNSET
    end_date: datetime.datetime | None | Unset = UNSET
    limit: int | Unset = 100
    offset: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        event_types: list[str] | None | Unset
        if isinstance(self.event_types, Unset):
            event_types = UNSET
        elif isinstance(self.event_types, list):
            event_types = []
            for event_types_type_0_item_data in self.event_types:
                event_types_type_0_item = event_types_type_0_item_data.value
                event_types.append(event_types_type_0_item)

        else:
            event_types = self.event_types

        categories: list[str] | None | Unset
        if isinstance(self.categories, Unset):
            categories = UNSET
        elif isinstance(self.categories, list):
            categories = []
            for categories_type_0_item_data in self.categories:
                categories_type_0_item = categories_type_0_item_data.value
                categories.append(categories_type_0_item)

        else:
            categories = self.categories

        severities: list[str] | None | Unset
        if isinstance(self.severities, Unset):
            severities = UNSET
        elif isinstance(self.severities, list):
            severities = []
            for severities_type_0_item_data in self.severities:
                severities_type_0_item = severities_type_0_item_data.value
                severities.append(severities_type_0_item)

        else:
            severities = self.severities

        sources: list[str] | None | Unset
        if isinstance(self.sources, Unset):
            sources = UNSET
        elif isinstance(self.sources, list):
            sources = []
            for sources_type_0_item_data in self.sources:
                sources_type_0_item = sources_type_0_item_data.value
                sources.append(sources_type_0_item)

        else:
            sources = self.sources

        user_ids: list[str] | None | Unset
        if isinstance(self.user_ids, Unset):
            user_ids = UNSET
        elif isinstance(self.user_ids, list):
            user_ids = self.user_ids

        else:
            user_ids = self.user_ids

        is_threat: bool | None | Unset
        if isinstance(self.is_threat, Unset):
            is_threat = UNSET
        else:
            is_threat = self.is_threat

        resolution_statuses: list[str] | None | Unset
        if isinstance(self.resolution_statuses, Unset):
            resolution_statuses = UNSET
        elif isinstance(self.resolution_statuses, list):
            resolution_statuses = []
            for resolution_statuses_type_0_item_data in self.resolution_statuses:
                resolution_statuses_type_0_item = resolution_statuses_type_0_item_data.value
                resolution_statuses.append(resolution_statuses_type_0_item)

        else:
            resolution_statuses = self.resolution_statuses

        start_date: None | str | Unset
        if isinstance(self.start_date, Unset):
            start_date = UNSET
        elif isinstance(self.start_date, datetime.datetime):
            start_date = self.start_date.isoformat()
        else:
            start_date = self.start_date

        end_date: None | str | Unset
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.datetime):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if event_types is not UNSET:
            field_dict["event_types"] = event_types
        if categories is not UNSET:
            field_dict["categories"] = categories
        if severities is not UNSET:
            field_dict["severities"] = severities
        if sources is not UNSET:
            field_dict["sources"] = sources
        if user_ids is not UNSET:
            field_dict["user_ids"] = user_ids
        if is_threat is not UNSET:
            field_dict["is_threat"] = is_threat
        if resolution_statuses is not UNSET:
            field_dict["resolution_statuses"] = resolution_statuses
        if start_date is not UNSET:
            field_dict["start_date"] = start_date
        if end_date is not UNSET:
            field_dict["end_date"] = end_date
        if limit is not UNSET:
            field_dict["limit"] = limit
        if offset is not UNSET:
            field_dict["offset"] = offset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_event_types(data: object) -> list[EventType] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                event_types_type_0 = []
                _event_types_type_0 = data
                for event_types_type_0_item_data in _event_types_type_0:
                    event_types_type_0_item = EventType(event_types_type_0_item_data)

                    event_types_type_0.append(event_types_type_0_item)

                return event_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EventType] | None | Unset, data)

        event_types = _parse_event_types(d.pop("event_types", UNSET))

        def _parse_categories(data: object) -> list[EventCategory] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                categories_type_0 = []
                _categories_type_0 = data
                for categories_type_0_item_data in _categories_type_0:
                    categories_type_0_item = EventCategory(categories_type_0_item_data)

                    categories_type_0.append(categories_type_0_item)

                return categories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EventCategory] | None | Unset, data)

        categories = _parse_categories(d.pop("categories", UNSET))

        def _parse_severities(data: object) -> list[EventSeverity] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                severities_type_0 = []
                _severities_type_0 = data
                for severities_type_0_item_data in _severities_type_0:
                    severities_type_0_item = EventSeverity(severities_type_0_item_data)

                    severities_type_0.append(severities_type_0_item)

                return severities_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EventSeverity] | None | Unset, data)

        severities = _parse_severities(d.pop("severities", UNSET))

        def _parse_sources(data: object) -> list[EventSource] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sources_type_0 = []
                _sources_type_0 = data
                for sources_type_0_item_data in _sources_type_0:
                    sources_type_0_item = EventSource(sources_type_0_item_data)

                    sources_type_0.append(sources_type_0_item)

                return sources_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EventSource] | None | Unset, data)

        sources = _parse_sources(d.pop("sources", UNSET))

        def _parse_user_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                user_ids_type_0 = cast(list[str], data)

                return user_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        user_ids = _parse_user_ids(d.pop("user_ids", UNSET))

        def _parse_is_threat(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_threat = _parse_is_threat(d.pop("is_threat", UNSET))

        def _parse_resolution_statuses(data: object) -> list[EventResolution] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                resolution_statuses_type_0 = []
                _resolution_statuses_type_0 = data
                for resolution_statuses_type_0_item_data in _resolution_statuses_type_0:
                    resolution_statuses_type_0_item = EventResolution(resolution_statuses_type_0_item_data)

                    resolution_statuses_type_0.append(resolution_statuses_type_0_item)

                return resolution_statuses_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[EventResolution] | None | Unset, data)

        resolution_statuses = _parse_resolution_statuses(d.pop("resolution_statuses", UNSET))

        def _parse_start_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_date_type_0 = isoparse(data)

                return start_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        start_date = _parse_start_date(d.pop("start_date", UNSET))

        def _parse_end_date(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = isoparse(data)

                return end_date_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        end_date = _parse_end_date(d.pop("end_date", UNSET))

        limit = d.pop("limit", UNSET)

        offset = d.pop("offset", UNSET)

        event_log_filter_schema = cls(
            event_types=event_types,
            categories=categories,
            severities=severities,
            sources=sources,
            user_ids=user_ids,
            is_threat=is_threat,
            resolution_statuses=resolution_statuses,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        event_log_filter_schema.additional_properties = d
        return event_log_filter_schema

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
