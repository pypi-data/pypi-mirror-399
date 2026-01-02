from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.approval_request_schema_compliance_summary import ApprovalRequestSchemaComplianceSummary
    from ..models.approval_request_schema_plan_summary import ApprovalRequestSchemaPlanSummary


T = TypeVar("T", bound="ApprovalRequestSchema")


@_attrs_define
class ApprovalRequestSchema:
    """Schema for creating an approval request.

    Attributes:
        run_id (str): ID of the stack run requiring approval
        reason (str | Unset): Reason for the approval request Default: ''.
        priority (str | Unset): Priority level (LOW, MEDIUM, HIGH, CRITICAL) Default: 'MEDIUM'.
        required_approvers (list[str] | Unset): List of required approver emails
        expires_in_hours (int | Unset): Hours until approval expires Default: 24.
        plan_summary (ApprovalRequestSchemaPlanSummary | Unset): Terraform plan summary
        compliance_summary (ApprovalRequestSchemaComplianceSummary | Unset): Compliance check summary
        risk_score (int | Unset): Calculated risk score (0-100) Default: 0.
    """

    run_id: str
    reason: str | Unset = ""
    priority: str | Unset = "MEDIUM"
    required_approvers: list[str] | Unset = UNSET
    expires_in_hours: int | Unset = 24
    plan_summary: ApprovalRequestSchemaPlanSummary | Unset = UNSET
    compliance_summary: ApprovalRequestSchemaComplianceSummary | Unset = UNSET
    risk_score: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        run_id = self.run_id

        reason = self.reason

        priority = self.priority

        required_approvers: list[str] | Unset = UNSET
        if not isinstance(self.required_approvers, Unset):
            required_approvers = self.required_approvers

        expires_in_hours = self.expires_in_hours

        plan_summary: dict[str, Any] | Unset = UNSET
        if not isinstance(self.plan_summary, Unset):
            plan_summary = self.plan_summary.to_dict()

        compliance_summary: dict[str, Any] | Unset = UNSET
        if not isinstance(self.compliance_summary, Unset):
            compliance_summary = self.compliance_summary.to_dict()

        risk_score = self.risk_score

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_id": run_id,
            }
        )
        if reason is not UNSET:
            field_dict["reason"] = reason
        if priority is not UNSET:
            field_dict["priority"] = priority
        if required_approvers is not UNSET:
            field_dict["required_approvers"] = required_approvers
        if expires_in_hours is not UNSET:
            field_dict["expires_in_hours"] = expires_in_hours
        if plan_summary is not UNSET:
            field_dict["plan_summary"] = plan_summary
        if compliance_summary is not UNSET:
            field_dict["compliance_summary"] = compliance_summary
        if risk_score is not UNSET:
            field_dict["risk_score"] = risk_score

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.approval_request_schema_compliance_summary import ApprovalRequestSchemaComplianceSummary
        from ..models.approval_request_schema_plan_summary import ApprovalRequestSchemaPlanSummary

        d = dict(src_dict)
        run_id = d.pop("run_id")

        reason = d.pop("reason", UNSET)

        priority = d.pop("priority", UNSET)

        required_approvers = cast(list[str], d.pop("required_approvers", UNSET))

        expires_in_hours = d.pop("expires_in_hours", UNSET)

        _plan_summary = d.pop("plan_summary", UNSET)
        plan_summary: ApprovalRequestSchemaPlanSummary | Unset
        if isinstance(_plan_summary, Unset):
            plan_summary = UNSET
        else:
            plan_summary = ApprovalRequestSchemaPlanSummary.from_dict(_plan_summary)

        _compliance_summary = d.pop("compliance_summary", UNSET)
        compliance_summary: ApprovalRequestSchemaComplianceSummary | Unset
        if isinstance(_compliance_summary, Unset):
            compliance_summary = UNSET
        else:
            compliance_summary = ApprovalRequestSchemaComplianceSummary.from_dict(_compliance_summary)

        risk_score = d.pop("risk_score", UNSET)

        approval_request_schema = cls(
            run_id=run_id,
            reason=reason,
            priority=priority,
            required_approvers=required_approvers,
            expires_in_hours=expires_in_hours,
            plan_summary=plan_summary,
            compliance_summary=compliance_summary,
            risk_score=risk_score,
        )

        approval_request_schema.additional_properties = d
        return approval_request_schema

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
