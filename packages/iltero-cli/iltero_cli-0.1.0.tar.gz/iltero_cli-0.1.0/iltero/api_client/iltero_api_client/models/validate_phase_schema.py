from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cicd_context_schema import CICDContextSchema
    from ..models.validate_phase_schema_compliance_scan_type_0 import ValidatePhaseSchemaComplianceScanType0
    from ..models.validate_phase_schema_validation_results import ValidatePhaseSchemaValidationResults


T = TypeVar("T", bound="ValidatePhaseSchema")


@_attrs_define
class ValidatePhaseSchema:
    """Schema for validation phase webhook.

    Attributes:
        stack_id (str): Stack ID
        success (bool): Validation success status
        run_id (None | str | Unset): Existing run ID if continuing
        external_run_id (None | str | Unset): External CI/CD run ID
        external_run_url (None | str | Unset): External CI/CD run URL
        validation_results (ValidatePhaseSchemaValidationResults | Unset): Terraform validation output
        compliance_scan (None | Unset | ValidatePhaseSchemaComplianceScanType0): Optional compliance scan results
        cicd_context (CICDContextSchema | None | Unset): CI/CD pipeline context for evidence collection
    """

    stack_id: str
    success: bool
    run_id: None | str | Unset = UNSET
    external_run_id: None | str | Unset = UNSET
    external_run_url: None | str | Unset = UNSET
    validation_results: ValidatePhaseSchemaValidationResults | Unset = UNSET
    compliance_scan: None | Unset | ValidatePhaseSchemaComplianceScanType0 = UNSET
    cicd_context: CICDContextSchema | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.cicd_context_schema import CICDContextSchema
        from ..models.validate_phase_schema_compliance_scan_type_0 import ValidatePhaseSchemaComplianceScanType0

        stack_id = self.stack_id

        success = self.success

        run_id: None | str | Unset
        if isinstance(self.run_id, Unset):
            run_id = UNSET
        else:
            run_id = self.run_id

        external_run_id: None | str | Unset
        if isinstance(self.external_run_id, Unset):
            external_run_id = UNSET
        else:
            external_run_id = self.external_run_id

        external_run_url: None | str | Unset
        if isinstance(self.external_run_url, Unset):
            external_run_url = UNSET
        else:
            external_run_url = self.external_run_url

        validation_results: dict[str, Any] | Unset = UNSET
        if not isinstance(self.validation_results, Unset):
            validation_results = self.validation_results.to_dict()

        compliance_scan: dict[str, Any] | None | Unset
        if isinstance(self.compliance_scan, Unset):
            compliance_scan = UNSET
        elif isinstance(self.compliance_scan, ValidatePhaseSchemaComplianceScanType0):
            compliance_scan = self.compliance_scan.to_dict()
        else:
            compliance_scan = self.compliance_scan

        cicd_context: dict[str, Any] | None | Unset
        if isinstance(self.cicd_context, Unset):
            cicd_context = UNSET
        elif isinstance(self.cicd_context, CICDContextSchema):
            cicd_context = self.cicd_context.to_dict()
        else:
            cicd_context = self.cicd_context

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "success": success,
            }
        )
        if run_id is not UNSET:
            field_dict["run_id"] = run_id
        if external_run_id is not UNSET:
            field_dict["external_run_id"] = external_run_id
        if external_run_url is not UNSET:
            field_dict["external_run_url"] = external_run_url
        if validation_results is not UNSET:
            field_dict["validation_results"] = validation_results
        if compliance_scan is not UNSET:
            field_dict["compliance_scan"] = compliance_scan
        if cicd_context is not UNSET:
            field_dict["cicd_context"] = cicd_context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cicd_context_schema import CICDContextSchema
        from ..models.validate_phase_schema_compliance_scan_type_0 import ValidatePhaseSchemaComplianceScanType0
        from ..models.validate_phase_schema_validation_results import ValidatePhaseSchemaValidationResults

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        success = d.pop("success")

        def _parse_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        run_id = _parse_run_id(d.pop("run_id", UNSET))

        def _parse_external_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_run_id = _parse_external_run_id(d.pop("external_run_id", UNSET))

        def _parse_external_run_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_run_url = _parse_external_run_url(d.pop("external_run_url", UNSET))

        _validation_results = d.pop("validation_results", UNSET)
        validation_results: ValidatePhaseSchemaValidationResults | Unset
        if isinstance(_validation_results, Unset):
            validation_results = UNSET
        else:
            validation_results = ValidatePhaseSchemaValidationResults.from_dict(_validation_results)

        def _parse_compliance_scan(data: object) -> None | Unset | ValidatePhaseSchemaComplianceScanType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compliance_scan_type_0 = ValidatePhaseSchemaComplianceScanType0.from_dict(data)

                return compliance_scan_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | ValidatePhaseSchemaComplianceScanType0, data)

        compliance_scan = _parse_compliance_scan(d.pop("compliance_scan", UNSET))

        def _parse_cicd_context(data: object) -> CICDContextSchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                cicd_context_type_0 = CICDContextSchema.from_dict(data)

                return cicd_context_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CICDContextSchema | None | Unset, data)

        cicd_context = _parse_cicd_context(d.pop("cicd_context", UNSET))

        validate_phase_schema = cls(
            stack_id=stack_id,
            success=success,
            run_id=run_id,
            external_run_id=external_run_id,
            external_run_url=external_run_url,
            validation_results=validation_results,
            compliance_scan=compliance_scan,
            cicd_context=cicd_context,
        )

        validate_phase_schema.additional_properties = d
        return validate_phase_schema

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
