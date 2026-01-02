from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compliance_report_request_schema_date_range_type_0 import ComplianceReportRequestSchemaDateRangeType0


T = TypeVar("T", bound="ComplianceReportRequestSchema")


@_attrs_define
class ComplianceReportRequestSchema:
    """Request schema for compliance report generation.

    Attributes:
        stack_id (str): Stack identifier
        workspace_id (None | str | Unset): Workspace identifier
        report_type (str | Unset): Type of report to generate Default: 'summary'.
        frameworks (list[str] | None | Unset): Specific frameworks to include
        date_range (ComplianceReportRequestSchemaDateRangeType0 | None | Unset): Date range for report
        include_evidence (bool | Unset): Whether to include evidence in report Default: False.
        include_remediation (bool | Unset): Whether to include remediation recommendations Default: True.
        include_trends (bool | Unset): Whether to include trend analysis Default: False.
        include_history (bool | Unset): Whether to include historical data Default: False.
        format_ (str | Unset): Report format Default: 'json'.
    """

    stack_id: str
    workspace_id: None | str | Unset = UNSET
    report_type: str | Unset = "summary"
    frameworks: list[str] | None | Unset = UNSET
    date_range: ComplianceReportRequestSchemaDateRangeType0 | None | Unset = UNSET
    include_evidence: bool | Unset = False
    include_remediation: bool | Unset = True
    include_trends: bool | Unset = False
    include_history: bool | Unset = False
    format_: str | Unset = "json"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.compliance_report_request_schema_date_range_type_0 import (
            ComplianceReportRequestSchemaDateRangeType0,
        )

        stack_id = self.stack_id

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        report_type = self.report_type

        frameworks: list[str] | None | Unset
        if isinstance(self.frameworks, Unset):
            frameworks = UNSET
        elif isinstance(self.frameworks, list):
            frameworks = self.frameworks

        else:
            frameworks = self.frameworks

        date_range: dict[str, Any] | None | Unset
        if isinstance(self.date_range, Unset):
            date_range = UNSET
        elif isinstance(self.date_range, ComplianceReportRequestSchemaDateRangeType0):
            date_range = self.date_range.to_dict()
        else:
            date_range = self.date_range

        include_evidence = self.include_evidence

        include_remediation = self.include_remediation

        include_trends = self.include_trends

        include_history = self.include_history

        format_ = self.format_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if report_type is not UNSET:
            field_dict["report_type"] = report_type
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks
        if date_range is not UNSET:
            field_dict["date_range"] = date_range
        if include_evidence is not UNSET:
            field_dict["include_evidence"] = include_evidence
        if include_remediation is not UNSET:
            field_dict["include_remediation"] = include_remediation
        if include_trends is not UNSET:
            field_dict["include_trends"] = include_trends
        if include_history is not UNSET:
            field_dict["include_history"] = include_history
        if format_ is not UNSET:
            field_dict["format"] = format_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compliance_report_request_schema_date_range_type_0 import (
            ComplianceReportRequestSchemaDateRangeType0,
        )

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        report_type = d.pop("report_type", UNSET)

        def _parse_frameworks(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                frameworks_type_0 = cast(list[str], data)

                return frameworks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        frameworks = _parse_frameworks(d.pop("frameworks", UNSET))

        def _parse_date_range(data: object) -> ComplianceReportRequestSchemaDateRangeType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                date_range_type_0 = ComplianceReportRequestSchemaDateRangeType0.from_dict(data)

                return date_range_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ComplianceReportRequestSchemaDateRangeType0 | None | Unset, data)

        date_range = _parse_date_range(d.pop("date_range", UNSET))

        include_evidence = d.pop("include_evidence", UNSET)

        include_remediation = d.pop("include_remediation", UNSET)

        include_trends = d.pop("include_trends", UNSET)

        include_history = d.pop("include_history", UNSET)

        format_ = d.pop("format", UNSET)

        compliance_report_request_schema = cls(
            stack_id=stack_id,
            workspace_id=workspace_id,
            report_type=report_type,
            frameworks=frameworks,
            date_range=date_range,
            include_evidence=include_evidence,
            include_remediation=include_remediation,
            include_trends=include_trends,
            include_history=include_history,
            format_=format_,
        )

        compliance_report_request_schema.additional_properties = d
        return compliance_report_request_schema

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
