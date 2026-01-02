from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.drift_detection_result_schema_drift_summary import DriftDetectionResultSchemaDriftSummary
    from ..models.drift_detection_result_schema_impact_analysis import DriftDetectionResultSchemaImpactAnalysis
    from ..models.drift_detection_result_schema_remediation_plan import DriftDetectionResultSchemaRemediationPlan


T = TypeVar("T", bound="DriftDetectionResultSchema")


@_attrs_define
class DriftDetectionResultSchema:
    """Schema for drift detection results.

    Attributes:
        drift_detected (bool): Whether drift was detected
        drift_summary (DriftDetectionResultSchemaDriftSummary): Summary of detected drift
        drifted_resources (list[Any]): List of resources with drift
        terraform_plan_output (str | Unset): Raw Terraform plan output Default: ''.
        impact_analysis (DriftDetectionResultSchemaImpactAnalysis | Unset): Impact analysis
        security_implications (list[Any] | Unset): Security implications
        compliance_impact (list[Any] | Unset): Compliance impact
        remediation_plan (DriftDetectionResultSchemaRemediationPlan | Unset): Remediation plan
    """

    drift_detected: bool
    drift_summary: DriftDetectionResultSchemaDriftSummary
    drifted_resources: list[Any]
    terraform_plan_output: str | Unset = ""
    impact_analysis: DriftDetectionResultSchemaImpactAnalysis | Unset = UNSET
    security_implications: list[Any] | Unset = UNSET
    compliance_impact: list[Any] | Unset = UNSET
    remediation_plan: DriftDetectionResultSchemaRemediationPlan | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        drift_detected = self.drift_detected

        drift_summary = self.drift_summary.to_dict()

        drifted_resources = self.drifted_resources

        terraform_plan_output = self.terraform_plan_output

        impact_analysis: dict[str, Any] | Unset = UNSET
        if not isinstance(self.impact_analysis, Unset):
            impact_analysis = self.impact_analysis.to_dict()

        security_implications: list[Any] | Unset = UNSET
        if not isinstance(self.security_implications, Unset):
            security_implications = self.security_implications

        compliance_impact: list[Any] | Unset = UNSET
        if not isinstance(self.compliance_impact, Unset):
            compliance_impact = self.compliance_impact

        remediation_plan: dict[str, Any] | Unset = UNSET
        if not isinstance(self.remediation_plan, Unset):
            remediation_plan = self.remediation_plan.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "drift_detected": drift_detected,
                "drift_summary": drift_summary,
                "drifted_resources": drifted_resources,
            }
        )
        if terraform_plan_output is not UNSET:
            field_dict["terraform_plan_output"] = terraform_plan_output
        if impact_analysis is not UNSET:
            field_dict["impact_analysis"] = impact_analysis
        if security_implications is not UNSET:
            field_dict["security_implications"] = security_implications
        if compliance_impact is not UNSET:
            field_dict["compliance_impact"] = compliance_impact
        if remediation_plan is not UNSET:
            field_dict["remediation_plan"] = remediation_plan

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.drift_detection_result_schema_drift_summary import DriftDetectionResultSchemaDriftSummary
        from ..models.drift_detection_result_schema_impact_analysis import DriftDetectionResultSchemaImpactAnalysis
        from ..models.drift_detection_result_schema_remediation_plan import DriftDetectionResultSchemaRemediationPlan

        d = dict(src_dict)
        drift_detected = d.pop("drift_detected")

        drift_summary = DriftDetectionResultSchemaDriftSummary.from_dict(d.pop("drift_summary"))

        drifted_resources = cast(list[Any], d.pop("drifted_resources"))

        terraform_plan_output = d.pop("terraform_plan_output", UNSET)

        _impact_analysis = d.pop("impact_analysis", UNSET)
        impact_analysis: DriftDetectionResultSchemaImpactAnalysis | Unset
        if isinstance(_impact_analysis, Unset):
            impact_analysis = UNSET
        else:
            impact_analysis = DriftDetectionResultSchemaImpactAnalysis.from_dict(_impact_analysis)

        security_implications = cast(list[Any], d.pop("security_implications", UNSET))

        compliance_impact = cast(list[Any], d.pop("compliance_impact", UNSET))

        _remediation_plan = d.pop("remediation_plan", UNSET)
        remediation_plan: DriftDetectionResultSchemaRemediationPlan | Unset
        if isinstance(_remediation_plan, Unset):
            remediation_plan = UNSET
        else:
            remediation_plan = DriftDetectionResultSchemaRemediationPlan.from_dict(_remediation_plan)

        drift_detection_result_schema = cls(
            drift_detected=drift_detected,
            drift_summary=drift_summary,
            drifted_resources=drifted_resources,
            terraform_plan_output=terraform_plan_output,
            impact_analysis=impact_analysis,
            security_implications=security_implications,
            compliance_impact=compliance_impact,
            remediation_plan=remediation_plan,
        )

        drift_detection_result_schema.additional_properties = d
        return drift_detection_result_schema

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
