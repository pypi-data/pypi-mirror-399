from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ManifestGenerateRequestSchema")


@_attrs_define
class ManifestGenerateRequestSchema:
    """Schema for generating a compliance manifest.

    Attributes:
        bundle_id (str): Template bundle ID to generate manifest for
        frameworks (list[str] | None | Unset): Optional list of frameworks to include (e.g., ['CIS_AWS', 'SOC2'])
    """

    bundle_id: str
    frameworks: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bundle_id = self.bundle_id

        frameworks: list[str] | None | Unset
        if isinstance(self.frameworks, Unset):
            frameworks = UNSET
        elif isinstance(self.frameworks, list):
            frameworks = self.frameworks

        else:
            frameworks = self.frameworks

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bundle_id": bundle_id,
            }
        )
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bundle_id = d.pop("bundle_id")

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

        manifest_generate_request_schema = cls(
            bundle_id=bundle_id,
            frameworks=frameworks,
        )

        manifest_generate_request_schema.additional_properties = d
        return manifest_generate_request_schema

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
