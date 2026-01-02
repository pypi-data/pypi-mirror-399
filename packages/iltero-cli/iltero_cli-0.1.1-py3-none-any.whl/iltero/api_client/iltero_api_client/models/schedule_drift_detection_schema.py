from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schedule_drift_detection_schema_detection_config import ScheduleDriftDetectionSchemaDetectionConfig


T = TypeVar("T", bound="ScheduleDriftDetectionSchema")


@_attrs_define
class ScheduleDriftDetectionSchema:
    """Schema for scheduling drift detection.

    Attributes:
        stack_id (str): ID of the stack to check for drift
        scheduled_at (datetime.datetime | None | Unset): When to run the detection (defaults to now)
        detection_config (ScheduleDriftDetectionSchemaDetectionConfig | Unset): Configuration for drift detection
        ignore_patterns (list[str] | Unset): Resource patterns to ignore during detection
        remediation_strategy (str | Unset): Strategy for handling detected drift Default: 'NOTIFY_ONLY'.
    """

    stack_id: str
    scheduled_at: datetime.datetime | None | Unset = UNSET
    detection_config: ScheduleDriftDetectionSchemaDetectionConfig | Unset = UNSET
    ignore_patterns: list[str] | Unset = UNSET
    remediation_strategy: str | Unset = "NOTIFY_ONLY"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        scheduled_at: None | str | Unset
        if isinstance(self.scheduled_at, Unset):
            scheduled_at = UNSET
        elif isinstance(self.scheduled_at, datetime.datetime):
            scheduled_at = self.scheduled_at.isoformat()
        else:
            scheduled_at = self.scheduled_at

        detection_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.detection_config, Unset):
            detection_config = self.detection_config.to_dict()

        ignore_patterns: list[str] | Unset = UNSET
        if not isinstance(self.ignore_patterns, Unset):
            ignore_patterns = self.ignore_patterns

        remediation_strategy = self.remediation_strategy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
            }
        )
        if scheduled_at is not UNSET:
            field_dict["scheduled_at"] = scheduled_at
        if detection_config is not UNSET:
            field_dict["detection_config"] = detection_config
        if ignore_patterns is not UNSET:
            field_dict["ignore_patterns"] = ignore_patterns
        if remediation_strategy is not UNSET:
            field_dict["remediation_strategy"] = remediation_strategy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schedule_drift_detection_schema_detection_config import (
            ScheduleDriftDetectionSchemaDetectionConfig,
        )

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        def _parse_scheduled_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                scheduled_at_type_0 = isoparse(data)

                return scheduled_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        scheduled_at = _parse_scheduled_at(d.pop("scheduled_at", UNSET))

        _detection_config = d.pop("detection_config", UNSET)
        detection_config: ScheduleDriftDetectionSchemaDetectionConfig | Unset
        if isinstance(_detection_config, Unset):
            detection_config = UNSET
        else:
            detection_config = ScheduleDriftDetectionSchemaDetectionConfig.from_dict(_detection_config)

        ignore_patterns = cast(list[str], d.pop("ignore_patterns", UNSET))

        remediation_strategy = d.pop("remediation_strategy", UNSET)

        schedule_drift_detection_schema = cls(
            stack_id=stack_id,
            scheduled_at=scheduled_at,
            detection_config=detection_config,
            ignore_patterns=ignore_patterns,
            remediation_strategy=remediation_strategy,
        )

        schedule_drift_detection_schema.additional_properties = d
        return schedule_drift_detection_schema

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
