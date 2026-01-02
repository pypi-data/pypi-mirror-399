from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DashboardFilterSchema")


@_attrs_define
class DashboardFilterSchema:
    """Request schema for dashboard filters.

    Attributes:
        time_range (str | Unset): Time range for dashboard data (e.g., 7d, 30d, 90d) Default: '30d'.
        frameworks (list[str] | None | Unset): Filter by specific frameworks
        include_trends (bool | Unset): Include trend data Default: True.
        include_alerts (bool | Unset): Include active alerts Default: True.
        include_activities (bool | Unset): Include recent activities Default: True.
        max_activities (int | Unset): Maximum number of activities to return Default: 10.
        max_alerts (int | Unset): Maximum number of alerts to return Default: 5.
    """

    time_range: str | Unset = "30d"
    frameworks: list[str] | None | Unset = UNSET
    include_trends: bool | Unset = True
    include_alerts: bool | Unset = True
    include_activities: bool | Unset = True
    max_activities: int | Unset = 10
    max_alerts: int | Unset = 5
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time_range = self.time_range

        frameworks: list[str] | None | Unset
        if isinstance(self.frameworks, Unset):
            frameworks = UNSET
        elif isinstance(self.frameworks, list):
            frameworks = self.frameworks

        else:
            frameworks = self.frameworks

        include_trends = self.include_trends

        include_alerts = self.include_alerts

        include_activities = self.include_activities

        max_activities = self.max_activities

        max_alerts = self.max_alerts

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if time_range is not UNSET:
            field_dict["time_range"] = time_range
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks
        if include_trends is not UNSET:
            field_dict["include_trends"] = include_trends
        if include_alerts is not UNSET:
            field_dict["include_alerts"] = include_alerts
        if include_activities is not UNSET:
            field_dict["include_activities"] = include_activities
        if max_activities is not UNSET:
            field_dict["max_activities"] = max_activities
        if max_alerts is not UNSET:
            field_dict["max_alerts"] = max_alerts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        time_range = d.pop("time_range", UNSET)

        def _parse_frameworks(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                frameworks_type_0 = cast(list[str], data)

                return frameworks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        frameworks = _parse_frameworks(d.pop("frameworks", UNSET))

        include_trends = d.pop("include_trends", UNSET)

        include_alerts = d.pop("include_alerts", UNSET)

        include_activities = d.pop("include_activities", UNSET)

        max_activities = d.pop("max_activities", UNSET)

        max_alerts = d.pop("max_alerts", UNSET)

        dashboard_filter_schema = cls(
            time_range=time_range,
            frameworks=frameworks,
            include_trends=include_trends,
            include_alerts=include_alerts,
            include_activities=include_activities,
            max_activities=max_activities,
            max_alerts=max_alerts,
        )

        dashboard_filter_schema.additional_properties = d
        return dashboard_filter_schema

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
