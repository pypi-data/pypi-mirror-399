from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ComplianceValidationRequestSchema")


@_attrs_define
class ComplianceValidationRequestSchema:
    """Request schema for Template Bundle compliance validation.

    Attributes:
        frameworks (list[str]): Frameworks to validate against
        environment (str | Unset): Target environment Default: 'production'.
        validation_level (str | Unset): Validation strictness Default: 'strict'.
    """

    frameworks: list[str]
    environment: str | Unset = "production"
    validation_level: str | Unset = "strict"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        frameworks = self.frameworks

        environment = self.environment

        validation_level = self.validation_level

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "frameworks": frameworks,
            }
        )
        if environment is not UNSET:
            field_dict["environment"] = environment
        if validation_level is not UNSET:
            field_dict["validation_level"] = validation_level

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        frameworks = cast(list[str], d.pop("frameworks"))

        environment = d.pop("environment", UNSET)

        validation_level = d.pop("validation_level", UNSET)

        compliance_validation_request_schema = cls(
            frameworks=frameworks,
            environment=environment,
            validation_level=validation_level,
        )

        compliance_validation_request_schema.additional_properties = d
        return compliance_validation_request_schema

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
