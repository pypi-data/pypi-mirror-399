from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.score_threshold_alerts_schema import ScoreThresholdAlertsSchema


T = TypeVar("T", bound="ComplianceMonitoringSchema")


@_attrs_define
class ComplianceMonitoringSchema:
    """Schema for compliance monitoring policies.

    Attributes:
        real_time_monitoring (bool | Unset): Enable real-time monitoring Default: False.
        alert_on_violations (bool | Unset): Send alerts for violations Default: True.
        alert_channels (list[str] | Unset): Alert notification channels
        monitoring_schedule (str | Unset): Cron schedule for monitoring checks Default: '0 0 * * *'.
        track_compliance_score (bool | Unset): Track compliance score over time Default: True.
        score_threshold_alerts (ScoreThresholdAlertsSchema | Unset): Schema for compliance score alert thresholds.
    """

    real_time_monitoring: bool | Unset = False
    alert_on_violations: bool | Unset = True
    alert_channels: list[str] | Unset = UNSET
    monitoring_schedule: str | Unset = "0 0 * * *"
    track_compliance_score: bool | Unset = True
    score_threshold_alerts: ScoreThresholdAlertsSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        real_time_monitoring = self.real_time_monitoring

        alert_on_violations = self.alert_on_violations

        alert_channels: list[str] | Unset = UNSET
        if not isinstance(self.alert_channels, Unset):
            alert_channels = self.alert_channels

        monitoring_schedule = self.monitoring_schedule

        track_compliance_score = self.track_compliance_score

        score_threshold_alerts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.score_threshold_alerts, Unset):
            score_threshold_alerts = self.score_threshold_alerts.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if real_time_monitoring is not UNSET:
            field_dict["real_time_monitoring"] = real_time_monitoring
        if alert_on_violations is not UNSET:
            field_dict["alert_on_violations"] = alert_on_violations
        if alert_channels is not UNSET:
            field_dict["alert_channels"] = alert_channels
        if monitoring_schedule is not UNSET:
            field_dict["monitoring_schedule"] = monitoring_schedule
        if track_compliance_score is not UNSET:
            field_dict["track_compliance_score"] = track_compliance_score
        if score_threshold_alerts is not UNSET:
            field_dict["score_threshold_alerts"] = score_threshold_alerts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.score_threshold_alerts_schema import ScoreThresholdAlertsSchema

        d = dict(src_dict)
        real_time_monitoring = d.pop("real_time_monitoring", UNSET)

        alert_on_violations = d.pop("alert_on_violations", UNSET)

        alert_channels = cast(list[str], d.pop("alert_channels", UNSET))

        monitoring_schedule = d.pop("monitoring_schedule", UNSET)

        track_compliance_score = d.pop("track_compliance_score", UNSET)

        _score_threshold_alerts = d.pop("score_threshold_alerts", UNSET)
        score_threshold_alerts: ScoreThresholdAlertsSchema | Unset
        if isinstance(_score_threshold_alerts, Unset):
            score_threshold_alerts = UNSET
        else:
            score_threshold_alerts = ScoreThresholdAlertsSchema.from_dict(_score_threshold_alerts)

        compliance_monitoring_schema = cls(
            real_time_monitoring=real_time_monitoring,
            alert_on_violations=alert_on_violations,
            alert_channels=alert_channels,
            monitoring_schedule=monitoring_schedule,
            track_compliance_score=track_compliance_score,
            score_threshold_alerts=score_threshold_alerts,
        )

        compliance_monitoring_schema.additional_properties = d
        return compliance_monitoring_schema

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
