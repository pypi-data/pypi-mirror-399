from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScoreThresholdAlertsSchema")


@_attrs_define
class ScoreThresholdAlertsSchema:
    """Schema for compliance score alert thresholds.

    Attributes:
        warning (int | Unset): Warning threshold percentage Default: 85.
        critical (int | Unset): Critical threshold percentage Default: 70.
    """

    warning: int | Unset = 85
    critical: int | Unset = 70
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        warning = self.warning

        critical = self.critical

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if warning is not UNSET:
            field_dict["warning"] = warning
        if critical is not UNSET:
            field_dict["critical"] = critical

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        warning = d.pop("warning", UNSET)

        critical = d.pop("critical", UNSET)

        score_threshold_alerts_schema = cls(
            warning=warning,
            critical=critical,
        )

        score_threshold_alerts_schema.additional_properties = d
        return score_threshold_alerts_schema

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
