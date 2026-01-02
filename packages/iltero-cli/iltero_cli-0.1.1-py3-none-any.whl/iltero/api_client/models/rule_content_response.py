from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RuleContentResponse")


@_attrs_define
class RuleContentResponse:
    """Response schema for rule content preview.

    Attributes:
        rule_id (str):
        bundle_key (str):
        rego_content (None | str | Unset):
        yaml_content (None | str | Unset):
        python_content (None | str | Unset):
    """

    rule_id: str
    bundle_key: str
    rego_content: None | str | Unset = UNSET
    yaml_content: None | str | Unset = UNSET
    python_content: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rule_id = self.rule_id

        bundle_key = self.bundle_key

        rego_content: None | str | Unset
        if isinstance(self.rego_content, Unset):
            rego_content = UNSET
        else:
            rego_content = self.rego_content

        yaml_content: None | str | Unset
        if isinstance(self.yaml_content, Unset):
            yaml_content = UNSET
        else:
            yaml_content = self.yaml_content

        python_content: None | str | Unset
        if isinstance(self.python_content, Unset):
            python_content = UNSET
        else:
            python_content = self.python_content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rule_id": rule_id,
                "bundle_key": bundle_key,
            }
        )
        if rego_content is not UNSET:
            field_dict["rego_content"] = rego_content
        if yaml_content is not UNSET:
            field_dict["yaml_content"] = yaml_content
        if python_content is not UNSET:
            field_dict["python_content"] = python_content

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rule_id = d.pop("rule_id")

        bundle_key = d.pop("bundle_key")

        def _parse_rego_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rego_content = _parse_rego_content(d.pop("rego_content", UNSET))

        def _parse_yaml_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        yaml_content = _parse_yaml_content(d.pop("yaml_content", UNSET))

        def _parse_python_content(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        python_content = _parse_python_content(d.pop("python_content", UNSET))

        rule_content_response = cls(
            rule_id=rule_id,
            bundle_key=bundle_key,
            rego_content=rego_content,
            yaml_content=yaml_content,
            python_content=python_content,
        )

        rule_content_response.additional_properties = d
        return rule_content_response

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
