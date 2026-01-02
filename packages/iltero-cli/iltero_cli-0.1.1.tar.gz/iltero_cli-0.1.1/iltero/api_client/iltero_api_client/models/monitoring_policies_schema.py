from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compliance_monitoring_schema import ComplianceMonitoringSchema
    from ..models.drift_detection_policy_schema import DriftDetectionPolicySchema


T = TypeVar("T", bound="MonitoringPoliciesSchema")


@_attrs_define
class MonitoringPoliciesSchema:
    """Schema for monitoring policies API endpoints.

    Attributes:
        drift_detection (DriftDetectionPolicySchema | None | Unset): Drift detection policies
        compliance_monitoring (ComplianceMonitoringSchema | None | Unset): Compliance monitoring configuration
        alert_channels (list[str] | Unset): Alert notification channels
        metrics_enabled (bool | Unset): Enable metrics collection Default: True.
        log_retention_days (int | Unset): Log retention in days Default: 30.
    """

    drift_detection: DriftDetectionPolicySchema | None | Unset = UNSET
    compliance_monitoring: ComplianceMonitoringSchema | None | Unset = UNSET
    alert_channels: list[str] | Unset = UNSET
    metrics_enabled: bool | Unset = True
    log_retention_days: int | Unset = 30
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.compliance_monitoring_schema import ComplianceMonitoringSchema
        from ..models.drift_detection_policy_schema import DriftDetectionPolicySchema

        drift_detection: dict[str, Any] | None | Unset
        if isinstance(self.drift_detection, Unset):
            drift_detection = UNSET
        elif isinstance(self.drift_detection, DriftDetectionPolicySchema):
            drift_detection = self.drift_detection.to_dict()
        else:
            drift_detection = self.drift_detection

        compliance_monitoring: dict[str, Any] | None | Unset
        if isinstance(self.compliance_monitoring, Unset):
            compliance_monitoring = UNSET
        elif isinstance(self.compliance_monitoring, ComplianceMonitoringSchema):
            compliance_monitoring = self.compliance_monitoring.to_dict()
        else:
            compliance_monitoring = self.compliance_monitoring

        alert_channels: list[str] | Unset = UNSET
        if not isinstance(self.alert_channels, Unset):
            alert_channels = self.alert_channels

        metrics_enabled = self.metrics_enabled

        log_retention_days = self.log_retention_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if drift_detection is not UNSET:
            field_dict["drift_detection"] = drift_detection
        if compliance_monitoring is not UNSET:
            field_dict["compliance_monitoring"] = compliance_monitoring
        if alert_channels is not UNSET:
            field_dict["alert_channels"] = alert_channels
        if metrics_enabled is not UNSET:
            field_dict["metrics_enabled"] = metrics_enabled
        if log_retention_days is not UNSET:
            field_dict["log_retention_days"] = log_retention_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compliance_monitoring_schema import ComplianceMonitoringSchema
        from ..models.drift_detection_policy_schema import DriftDetectionPolicySchema

        d = dict(src_dict)

        def _parse_drift_detection(data: object) -> DriftDetectionPolicySchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                drift_detection_type_0 = DriftDetectionPolicySchema.from_dict(data)

                return drift_detection_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DriftDetectionPolicySchema | None | Unset, data)

        drift_detection = _parse_drift_detection(d.pop("drift_detection", UNSET))

        def _parse_compliance_monitoring(data: object) -> ComplianceMonitoringSchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compliance_monitoring_type_0 = ComplianceMonitoringSchema.from_dict(data)

                return compliance_monitoring_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ComplianceMonitoringSchema | None | Unset, data)

        compliance_monitoring = _parse_compliance_monitoring(d.pop("compliance_monitoring", UNSET))

        alert_channels = cast(list[str], d.pop("alert_channels", UNSET))

        metrics_enabled = d.pop("metrics_enabled", UNSET)

        log_retention_days = d.pop("log_retention_days", UNSET)

        monitoring_policies_schema = cls(
            drift_detection=drift_detection,
            compliance_monitoring=compliance_monitoring,
            alert_channels=alert_channels,
            metrics_enabled=metrics_enabled,
            log_retention_days=log_retention_days,
        )

        monitoring_policies_schema.additional_properties = d
        return monitoring_policies_schema

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
