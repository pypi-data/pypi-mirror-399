from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.event_category import EventCategory
from ..models.event_severity import EventSeverity
from ..models.event_source import EventSource
from ..models.event_type import EventType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.event_log_create_schema_details_type_0 import EventLogCreateSchemaDetailsType0


T = TypeVar("T", bound="EventLogCreateSchema")


@_attrs_define
class EventLogCreateSchema:
    """Schema for creating event logs.

    Attributes:
        event_type (EventType): Event types.
        category (EventCategory | Unset): Event categories. Default: EventCategory.SECURITY.
        severity (EventSeverity | Unset): Event severity levels. Default: EventSeverity.INFO.
        source (EventSource | Unset): Event sources. Default: EventSource.SYSTEM.
        user_id (None | str | Unset): ID of the user associated with the event
        ip_address (None | str | Unset): IP address of the request
        user_agent (None | str | Unset): User agent string from the request
        device_id (None | str | Unset): Device ID if available
        details (EventLogCreateSchemaDetailsType0 | None | Unset): Additional event details
        is_threat (bool | Unset): Whether the event is considered a threat Default: False.
    """

    event_type: EventType
    category: EventCategory | Unset = EventCategory.SECURITY
    severity: EventSeverity | Unset = EventSeverity.INFO
    source: EventSource | Unset = EventSource.SYSTEM
    user_id: None | str | Unset = UNSET
    ip_address: None | str | Unset = UNSET
    user_agent: None | str | Unset = UNSET
    device_id: None | str | Unset = UNSET
    details: EventLogCreateSchemaDetailsType0 | None | Unset = UNSET
    is_threat: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.event_log_create_schema_details_type_0 import EventLogCreateSchemaDetailsType0

        event_type = self.event_type.value

        category: str | Unset = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        severity: str | Unset = UNSET
        if not isinstance(self.severity, Unset):
            severity = self.severity.value

        source: str | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.value

        user_id: None | str | Unset
        if isinstance(self.user_id, Unset):
            user_id = UNSET
        else:
            user_id = self.user_id

        ip_address: None | str | Unset
        if isinstance(self.ip_address, Unset):
            ip_address = UNSET
        else:
            ip_address = self.ip_address

        user_agent: None | str | Unset
        if isinstance(self.user_agent, Unset):
            user_agent = UNSET
        else:
            user_agent = self.user_agent

        device_id: None | str | Unset
        if isinstance(self.device_id, Unset):
            device_id = UNSET
        else:
            device_id = self.device_id

        details: dict[str, Any] | None | Unset
        if isinstance(self.details, Unset):
            details = UNSET
        elif isinstance(self.details, EventLogCreateSchemaDetailsType0):
            details = self.details.to_dict()
        else:
            details = self.details

        is_threat = self.is_threat

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "event_type": event_type,
            }
        )
        if category is not UNSET:
            field_dict["category"] = category
        if severity is not UNSET:
            field_dict["severity"] = severity
        if source is not UNSET:
            field_dict["source"] = source
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if ip_address is not UNSET:
            field_dict["ip_address"] = ip_address
        if user_agent is not UNSET:
            field_dict["user_agent"] = user_agent
        if device_id is not UNSET:
            field_dict["device_id"] = device_id
        if details is not UNSET:
            field_dict["details"] = details
        if is_threat is not UNSET:
            field_dict["is_threat"] = is_threat

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.event_log_create_schema_details_type_0 import EventLogCreateSchemaDetailsType0

        d = dict(src_dict)
        event_type = EventType(d.pop("event_type"))

        _category = d.pop("category", UNSET)
        category: EventCategory | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = EventCategory(_category)

        _severity = d.pop("severity", UNSET)
        severity: EventSeverity | Unset
        if isinstance(_severity, Unset):
            severity = UNSET
        else:
            severity = EventSeverity(_severity)

        _source = d.pop("source", UNSET)
        source: EventSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = EventSource(_source)

        def _parse_user_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_id = _parse_user_id(d.pop("user_id", UNSET))

        def _parse_ip_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ip_address = _parse_ip_address(d.pop("ip_address", UNSET))

        def _parse_user_agent(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_agent = _parse_user_agent(d.pop("user_agent", UNSET))

        def _parse_device_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        device_id = _parse_device_id(d.pop("device_id", UNSET))

        def _parse_details(data: object) -> EventLogCreateSchemaDetailsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                details_type_0 = EventLogCreateSchemaDetailsType0.from_dict(data)

                return details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EventLogCreateSchemaDetailsType0 | None | Unset, data)

        details = _parse_details(d.pop("details", UNSET))

        is_threat = d.pop("is_threat", UNSET)

        event_log_create_schema = cls(
            event_type=event_type,
            category=category,
            severity=severity,
            source=source,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            details=details,
            is_threat=is_threat,
        )

        event_log_create_schema.additional_properties = d
        return event_log_create_schema

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
