from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.monitoring_setup_request_schema_monitoring_config import MonitoringSetupRequestSchemaMonitoringConfig


T = TypeVar("T", bound="MonitoringSetupRequestSchema")


@_attrs_define
class MonitoringSetupRequestSchema:
    """Request schema for setting up compliance monitoring.

    Attributes:
        stack_id (str): Stack identifier
        monitoring_config (MonitoringSetupRequestSchemaMonitoringConfig): Monitoring configuration
        workspace_id (None | str | Unset): Workspace identifier
        check_interval_minutes (int | Unset): Check interval in minutes Default: 60.
        alert_threshold (float | Unset): Alert threshold (compliance score) Default: 80.0.
        frameworks (list[str] | Unset): Frameworks to monitor
        notification_channels (list[str] | Unset): Notification channels for alerts
        auto_remediation_enabled (bool | Unset): Whether to enable auto-remediation Default: False.
        evidence_collection_enabled (bool | Unset): Whether to enable evidence collection Default: True.
        evidence_collection_interval_hours (int | None | Unset): Evidence collection interval in hours
    """

    stack_id: str
    monitoring_config: MonitoringSetupRequestSchemaMonitoringConfig
    workspace_id: None | str | Unset = UNSET
    check_interval_minutes: int | Unset = 60
    alert_threshold: float | Unset = 80.0
    frameworks: list[str] | Unset = UNSET
    notification_channels: list[str] | Unset = UNSET
    auto_remediation_enabled: bool | Unset = False
    evidence_collection_enabled: bool | Unset = True
    evidence_collection_interval_hours: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        monitoring_config = self.monitoring_config.to_dict()

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        check_interval_minutes = self.check_interval_minutes

        alert_threshold = self.alert_threshold

        frameworks: list[str] | Unset = UNSET
        if not isinstance(self.frameworks, Unset):
            frameworks = self.frameworks

        notification_channels: list[str] | Unset = UNSET
        if not isinstance(self.notification_channels, Unset):
            notification_channels = self.notification_channels

        auto_remediation_enabled = self.auto_remediation_enabled

        evidence_collection_enabled = self.evidence_collection_enabled

        evidence_collection_interval_hours: int | None | Unset
        if isinstance(self.evidence_collection_interval_hours, Unset):
            evidence_collection_interval_hours = UNSET
        else:
            evidence_collection_interval_hours = self.evidence_collection_interval_hours

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "monitoring_config": monitoring_config,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if check_interval_minutes is not UNSET:
            field_dict["check_interval_minutes"] = check_interval_minutes
        if alert_threshold is not UNSET:
            field_dict["alert_threshold"] = alert_threshold
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks
        if notification_channels is not UNSET:
            field_dict["notification_channels"] = notification_channels
        if auto_remediation_enabled is not UNSET:
            field_dict["auto_remediation_enabled"] = auto_remediation_enabled
        if evidence_collection_enabled is not UNSET:
            field_dict["evidence_collection_enabled"] = evidence_collection_enabled
        if evidence_collection_interval_hours is not UNSET:
            field_dict["evidence_collection_interval_hours"] = evidence_collection_interval_hours

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.monitoring_setup_request_schema_monitoring_config import (
            MonitoringSetupRequestSchemaMonitoringConfig,
        )

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        monitoring_config = MonitoringSetupRequestSchemaMonitoringConfig.from_dict(d.pop("monitoring_config"))

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        check_interval_minutes = d.pop("check_interval_minutes", UNSET)

        alert_threshold = d.pop("alert_threshold", UNSET)

        frameworks = cast(list[str], d.pop("frameworks", UNSET))

        notification_channels = cast(list[str], d.pop("notification_channels", UNSET))

        auto_remediation_enabled = d.pop("auto_remediation_enabled", UNSET)

        evidence_collection_enabled = d.pop("evidence_collection_enabled", UNSET)

        def _parse_evidence_collection_interval_hours(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        evidence_collection_interval_hours = _parse_evidence_collection_interval_hours(
            d.pop("evidence_collection_interval_hours", UNSET)
        )

        monitoring_setup_request_schema = cls(
            stack_id=stack_id,
            monitoring_config=monitoring_config,
            workspace_id=workspace_id,
            check_interval_minutes=check_interval_minutes,
            alert_threshold=alert_threshold,
            frameworks=frameworks,
            notification_channels=notification_channels,
            auto_remediation_enabled=auto_remediation_enabled,
            evidence_collection_enabled=evidence_collection_enabled,
            evidence_collection_interval_hours=evidence_collection_interval_hours,
        )

        monitoring_setup_request_schema.additional_properties = d
        return monitoring_setup_request_schema

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
