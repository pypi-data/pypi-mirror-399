from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CompliancePreviewRequestSchema")


@_attrs_define
class CompliancePreviewRequestSchema:
    """Request schema for compliance preview.

    Attributes:
        template_bundle_id (str): Template bundle to preview
        frameworks (list[str]): Frameworks to evaluate
    """

    template_bundle_id: str
    frameworks: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        template_bundle_id = self.template_bundle_id

        frameworks = self.frameworks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "template_bundle_id": template_bundle_id,
                "frameworks": frameworks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        template_bundle_id = d.pop("template_bundle_id")

        frameworks = cast(list[str], d.pop("frameworks"))

        compliance_preview_request_schema = cls(
            template_bundle_id=template_bundle_id,
            frameworks=frameworks,
        )

        compliance_preview_request_schema.additional_properties = d
        return compliance_preview_request_schema

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
