from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.apply_phase_schema_apply_results import ApplyPhaseSchemaApplyResults


T = TypeVar("T", bound="ApplyPhaseSchema")


@_attrs_define
class ApplyPhaseSchema:
    """Schema for apply phase webhook.

    Attributes:
        run_id (str): Run ID from previous phases
        success (bool): Apply success status
        apply_results (ApplyPhaseSchemaApplyResults | Unset): Terraform apply output
        schedule_drift_detection (bool | Unset): Whether to schedule drift detection after apply Default: False.
    """

    run_id: str
    success: bool
    apply_results: ApplyPhaseSchemaApplyResults | Unset = UNSET
    schedule_drift_detection: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        run_id = self.run_id

        success = self.success

        apply_results: dict[str, Any] | Unset = UNSET
        if not isinstance(self.apply_results, Unset):
            apply_results = self.apply_results.to_dict()

        schedule_drift_detection = self.schedule_drift_detection

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "run_id": run_id,
                "success": success,
            }
        )
        if apply_results is not UNSET:
            field_dict["apply_results"] = apply_results
        if schedule_drift_detection is not UNSET:
            field_dict["schedule_drift_detection"] = schedule_drift_detection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.apply_phase_schema_apply_results import ApplyPhaseSchemaApplyResults

        d = dict(src_dict)
        run_id = d.pop("run_id")

        success = d.pop("success")

        _apply_results = d.pop("apply_results", UNSET)
        apply_results: ApplyPhaseSchemaApplyResults | Unset
        if isinstance(_apply_results, Unset):
            apply_results = UNSET
        else:
            apply_results = ApplyPhaseSchemaApplyResults.from_dict(_apply_results)

        schedule_drift_detection = d.pop("schedule_drift_detection", UNSET)

        apply_phase_schema = cls(
            run_id=run_id,
            success=success,
            apply_results=apply_results,
            schedule_drift_detection=schedule_drift_detection,
        )

        apply_phase_schema.additional_properties = d
        return apply_phase_schema

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
