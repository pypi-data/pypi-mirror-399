from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DriftRemediationRequestSchema")


@_attrs_define
class DriftRemediationRequestSchema:
    """Schema for marking drift as remediated.

    Attributes:
        remediation_run_id (str): ID of the run that remediated the drift
    """

    remediation_run_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        remediation_run_id = self.remediation_run_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "remediation_run_id": remediation_run_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        remediation_run_id = d.pop("remediation_run_id")

        drift_remediation_request_schema = cls(
            remediation_run_id=remediation_run_id,
        )

        drift_remediation_request_schema.additional_properties = d
        return drift_remediation_request_schema

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
