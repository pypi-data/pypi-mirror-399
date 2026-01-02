from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compliance_policies_schema_framework_configs import CompliancePoliciesSchemaFrameworkConfigs


T = TypeVar("T", bound="CompliancePoliciesSchema")


@_attrs_define
class CompliancePoliciesSchema:
    """Schema for compliance policies API endpoints.

    Attributes:
        enable_compliance_scanning (bool | Unset): Enable compliance scanning Default: True.
        policy_sets (list[str] | Unset): Active policy sets
        auto_policy_scan (bool | Unset): Automatically scan on changes Default: True.
        block_on_violations (bool | Unset): Block deployment on violations Default: True.
        scan_types (list[str] | Unset): Types of compliance scans to run
        compliance_frameworks (list[str] | Unset): Compliance frameworks to validate against
        framework_configs (CompliancePoliciesSchemaFrameworkConfigs | Unset): Per-framework configuration
    """

    enable_compliance_scanning: bool | Unset = True
    policy_sets: list[str] | Unset = UNSET
    auto_policy_scan: bool | Unset = True
    block_on_violations: bool | Unset = True
    scan_types: list[str] | Unset = UNSET
    compliance_frameworks: list[str] | Unset = UNSET
    framework_configs: CompliancePoliciesSchemaFrameworkConfigs | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable_compliance_scanning = self.enable_compliance_scanning

        policy_sets: list[str] | Unset = UNSET
        if not isinstance(self.policy_sets, Unset):
            policy_sets = self.policy_sets

        auto_policy_scan = self.auto_policy_scan

        block_on_violations = self.block_on_violations

        scan_types: list[str] | Unset = UNSET
        if not isinstance(self.scan_types, Unset):
            scan_types = self.scan_types

        compliance_frameworks: list[str] | Unset = UNSET
        if not isinstance(self.compliance_frameworks, Unset):
            compliance_frameworks = self.compliance_frameworks

        framework_configs: dict[str, Any] | Unset = UNSET
        if not isinstance(self.framework_configs, Unset):
            framework_configs = self.framework_configs.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable_compliance_scanning is not UNSET:
            field_dict["enable_compliance_scanning"] = enable_compliance_scanning
        if policy_sets is not UNSET:
            field_dict["policy_sets"] = policy_sets
        if auto_policy_scan is not UNSET:
            field_dict["auto_policy_scan"] = auto_policy_scan
        if block_on_violations is not UNSET:
            field_dict["block_on_violations"] = block_on_violations
        if scan_types is not UNSET:
            field_dict["scan_types"] = scan_types
        if compliance_frameworks is not UNSET:
            field_dict["compliance_frameworks"] = compliance_frameworks
        if framework_configs is not UNSET:
            field_dict["framework_configs"] = framework_configs

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compliance_policies_schema_framework_configs import CompliancePoliciesSchemaFrameworkConfigs

        d = dict(src_dict)
        enable_compliance_scanning = d.pop("enable_compliance_scanning", UNSET)

        policy_sets = cast(list[str], d.pop("policy_sets", UNSET))

        auto_policy_scan = d.pop("auto_policy_scan", UNSET)

        block_on_violations = d.pop("block_on_violations", UNSET)

        scan_types = cast(list[str], d.pop("scan_types", UNSET))

        compliance_frameworks = cast(list[str], d.pop("compliance_frameworks", UNSET))

        _framework_configs = d.pop("framework_configs", UNSET)
        framework_configs: CompliancePoliciesSchemaFrameworkConfigs | Unset
        if isinstance(_framework_configs, Unset):
            framework_configs = UNSET
        else:
            framework_configs = CompliancePoliciesSchemaFrameworkConfigs.from_dict(_framework_configs)

        compliance_policies_schema = cls(
            enable_compliance_scanning=enable_compliance_scanning,
            policy_sets=policy_sets,
            auto_policy_scan=auto_policy_scan,
            block_on_violations=block_on_violations,
            scan_types=scan_types,
            compliance_frameworks=compliance_frameworks,
            framework_configs=framework_configs,
        )

        compliance_policies_schema.additional_properties = d
        return compliance_policies_schema

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
