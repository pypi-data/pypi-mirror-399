from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.stack_resource_drift_detection_schema_drift_details import (
        StackResourceDriftDetectionSchemaDriftDetails,
    )


T = TypeVar("T", bound="StackResourceDriftDetectionSchema")


@_attrs_define
class StackResourceDriftDetectionSchema:
    """Schema for marking drift detection results.

    Attributes:
        resource_type (str): Resource type
        resource_id (str): Resource identifier
        drift_details (StackResourceDriftDetectionSchemaDriftDetails): Details of detected drift
    """

    resource_type: str
    resource_id: str
    drift_details: StackResourceDriftDetectionSchemaDriftDetails
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_type = self.resource_type

        resource_id = self.resource_id

        drift_details = self.drift_details.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "drift_details": drift_details,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_resource_drift_detection_schema_drift_details import (
            StackResourceDriftDetectionSchemaDriftDetails,
        )

        d = dict(src_dict)
        resource_type = d.pop("resource_type")

        resource_id = d.pop("resource_id")

        drift_details = StackResourceDriftDetectionSchemaDriftDetails.from_dict(d.pop("drift_details"))

        stack_resource_drift_detection_schema = cls(
            resource_type=resource_type,
            resource_id=resource_id,
            drift_details=drift_details,
        )

        stack_resource_drift_detection_schema.additional_properties = d
        return stack_resource_drift_detection_schema

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
