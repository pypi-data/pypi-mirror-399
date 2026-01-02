from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CollectionRuleSchema")


@_attrs_define
class CollectionRuleSchema:
    """Schema for evidence collection rule.

    Attributes:
        type_ (str): Evidence type (e.g., terraform_state, audit_logs)
        frequency (str): Collection frequency (DAILY, HOURLY, ON_CHANGE)
        retention_days (int | Unset): Retention period in days Default: 90.
        priority (str | Unset): Collection priority (high, medium, low) Default: 'medium'.
    """

    type_: str
    frequency: str
    retention_days: int | Unset = 90
    priority: str | Unset = "medium"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        frequency = self.frequency

        retention_days = self.retention_days

        priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "frequency": frequency,
            }
        )
        if retention_days is not UNSET:
            field_dict["retention_days"] = retention_days
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        type_ = d.pop("type")

        frequency = d.pop("frequency")

        retention_days = d.pop("retention_days", UNSET)

        priority = d.pop("priority", UNSET)

        collection_rule_schema = cls(
            type_=type_,
            frequency=frequency,
            retention_days=retention_days,
            priority=priority,
        )

        collection_rule_schema.additional_properties = d
        return collection_rule_schema

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
