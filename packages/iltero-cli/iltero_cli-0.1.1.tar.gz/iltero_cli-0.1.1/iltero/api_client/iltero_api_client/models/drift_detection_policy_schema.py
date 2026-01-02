from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DriftDetectionPolicySchema")


@_attrs_define
class DriftDetectionPolicySchema:
    """Schema for drift detection policies.

    Attributes:
        enabled (bool | Unset): Enable drift detection Default: True.
        schedule (str | Unset): Cron schedule for drift detection Default: '0 */4 * * *'.
        auto_remediate (bool | Unset): Automatically fix detected drift Default: False.
        notification_channels (list[str] | Unset): Notification channels
    """

    enabled: bool | Unset = True
    schedule: str | Unset = "0 */4 * * *"
    auto_remediate: bool | Unset = False
    notification_channels: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        schedule = self.schedule

        auto_remediate = self.auto_remediate

        notification_channels: list[str] | Unset = UNSET
        if not isinstance(self.notification_channels, Unset):
            notification_channels = self.notification_channels

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if schedule is not UNSET:
            field_dict["schedule"] = schedule
        if auto_remediate is not UNSET:
            field_dict["auto_remediate"] = auto_remediate
        if notification_channels is not UNSET:
            field_dict["notification_channels"] = notification_channels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        schedule = d.pop("schedule", UNSET)

        auto_remediate = d.pop("auto_remediate", UNSET)

        notification_channels = cast(list[str], d.pop("notification_channels", UNSET))

        drift_detection_policy_schema = cls(
            enabled=enabled,
            schedule=schedule,
            auto_remediate=auto_remediate,
            notification_channels=notification_channels,
        )

        drift_detection_policy_schema.additional_properties = d
        return drift_detection_policy_schema

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
