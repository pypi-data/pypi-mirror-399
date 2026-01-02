from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ComplianceFrameworkSchema")


@_attrs_define
class ComplianceFrameworkSchema:
    """Schema for compliance framework configuration.

    Attributes:
        name (str): Framework name (e.g., SOC2, ISO27001, HIPAA)
        enabled (bool | Unset): Whether framework is enabled Default: True.
        scan_on_pr (bool | Unset): Scan on pull request Default: True.
        scan_on_merge (bool | Unset): Scan on merge to main Default: True.
        block_on_violations (bool | Unset): Block deployment on violations Default: True.
        severity_threshold (str | Unset): Minimum severity to block Default: 'high'.
        evidence_collection (bool | Unset): Enable evidence collection Default: True.
    """

    name: str
    enabled: bool | Unset = True
    scan_on_pr: bool | Unset = True
    scan_on_merge: bool | Unset = True
    block_on_violations: bool | Unset = True
    severity_threshold: str | Unset = "high"
    evidence_collection: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        enabled = self.enabled

        scan_on_pr = self.scan_on_pr

        scan_on_merge = self.scan_on_merge

        block_on_violations = self.block_on_violations

        severity_threshold = self.severity_threshold

        evidence_collection = self.evidence_collection

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if scan_on_pr is not UNSET:
            field_dict["scan_on_pr"] = scan_on_pr
        if scan_on_merge is not UNSET:
            field_dict["scan_on_merge"] = scan_on_merge
        if block_on_violations is not UNSET:
            field_dict["block_on_violations"] = block_on_violations
        if severity_threshold is not UNSET:
            field_dict["severity_threshold"] = severity_threshold
        if evidence_collection is not UNSET:
            field_dict["evidence_collection"] = evidence_collection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        enabled = d.pop("enabled", UNSET)

        scan_on_pr = d.pop("scan_on_pr", UNSET)

        scan_on_merge = d.pop("scan_on_merge", UNSET)

        block_on_violations = d.pop("block_on_violations", UNSET)

        severity_threshold = d.pop("severity_threshold", UNSET)

        evidence_collection = d.pop("evidence_collection", UNSET)

        compliance_framework_schema = cls(
            name=name,
            enabled=enabled,
            scan_on_pr=scan_on_pr,
            scan_on_merge=scan_on_merge,
            block_on_violations=block_on_violations,
            severity_threshold=severity_threshold,
            evidence_collection=evidence_collection,
        )

        compliance_framework_schema.additional_properties = d
        return compliance_framework_schema

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
