from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plan_phase_schema_compliance_results_type_0 import PlanPhaseSchemaComplianceResultsType0
    from ..models.plan_phase_schema_plan_results import PlanPhaseSchemaPlanResults
    from ..models.plan_phase_schema_plan_summary_type_0 import PlanPhaseSchemaPlanSummaryType0


T = TypeVar("T", bound="PlanPhaseSchema")


@_attrs_define
class PlanPhaseSchema:
    """Schema for plan phase webhook.

    Attributes:
        run_id (str): Run ID from validation phase
        success (bool): Plan success status
        plan_results (PlanPhaseSchemaPlanResults | Unset): Terraform plan output
        plan_summary (None | PlanPhaseSchemaPlanSummaryType0 | Unset): Plan summary with resource changes
        plan_url (None | str | Unset): URL to stored plan file
        compliance_results (None | PlanPhaseSchemaComplianceResultsType0 | Unset): Optional compliance evaluation
            results
    """

    run_id: str
    success: bool
    plan_results: PlanPhaseSchemaPlanResults | Unset = UNSET
    plan_summary: None | PlanPhaseSchemaPlanSummaryType0 | Unset = UNSET
    plan_url: None | str | Unset = UNSET
    compliance_results: None | PlanPhaseSchemaComplianceResultsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.plan_phase_schema_compliance_results_type_0 import PlanPhaseSchemaComplianceResultsType0
        from ..models.plan_phase_schema_plan_summary_type_0 import PlanPhaseSchemaPlanSummaryType0

        run_id = self.run_id

        success = self.success

        plan_results: dict[str, Any] | Unset = UNSET
        if not isinstance(self.plan_results, Unset):
            plan_results = self.plan_results.to_dict()

        plan_summary: dict[str, Any] | None | Unset
        if isinstance(self.plan_summary, Unset):
            plan_summary = UNSET
        elif isinstance(self.plan_summary, PlanPhaseSchemaPlanSummaryType0):
            plan_summary = self.plan_summary.to_dict()
        else:
            plan_summary = self.plan_summary

        plan_url: None | str | Unset
        if isinstance(self.plan_url, Unset):
            plan_url = UNSET
        else:
            plan_url = self.plan_url

        compliance_results: dict[str, Any] | None | Unset
        if isinstance(self.compliance_results, Unset):
            compliance_results = UNSET
        elif isinstance(self.compliance_results, PlanPhaseSchemaComplianceResultsType0):
            compliance_results = self.compliance_results.to_dict()
        else:
            compliance_results = self.compliance_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_id": run_id,
                "success": success,
            }
        )
        if plan_results is not UNSET:
            field_dict["plan_results"] = plan_results
        if plan_summary is not UNSET:
            field_dict["plan_summary"] = plan_summary
        if plan_url is not UNSET:
            field_dict["plan_url"] = plan_url
        if compliance_results is not UNSET:
            field_dict["compliance_results"] = compliance_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plan_phase_schema_compliance_results_type_0 import PlanPhaseSchemaComplianceResultsType0
        from ..models.plan_phase_schema_plan_results import PlanPhaseSchemaPlanResults
        from ..models.plan_phase_schema_plan_summary_type_0 import PlanPhaseSchemaPlanSummaryType0

        d = dict(src_dict)
        run_id = d.pop("run_id")

        success = d.pop("success")

        _plan_results = d.pop("plan_results", UNSET)
        plan_results: PlanPhaseSchemaPlanResults | Unset
        if isinstance(_plan_results, Unset):
            plan_results = UNSET
        else:
            plan_results = PlanPhaseSchemaPlanResults.from_dict(_plan_results)

        def _parse_plan_summary(data: object) -> None | PlanPhaseSchemaPlanSummaryType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                plan_summary_type_0 = PlanPhaseSchemaPlanSummaryType0.from_dict(data)

                return plan_summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlanPhaseSchemaPlanSummaryType0 | Unset, data)

        plan_summary = _parse_plan_summary(d.pop("plan_summary", UNSET))

        def _parse_plan_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan_url = _parse_plan_url(d.pop("plan_url", UNSET))

        def _parse_compliance_results(data: object) -> None | PlanPhaseSchemaComplianceResultsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compliance_results_type_0 = PlanPhaseSchemaComplianceResultsType0.from_dict(data)

                return compliance_results_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlanPhaseSchemaComplianceResultsType0 | Unset, data)

        compliance_results = _parse_compliance_results(d.pop("compliance_results", UNSET))

        plan_phase_schema = cls(
            run_id=run_id,
            success=success,
            plan_results=plan_results,
            plan_summary=plan_summary,
            plan_url=plan_url,
            compliance_results=compliance_results,
        )

        plan_phase_schema.additional_properties = d
        return plan_phase_schema

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
