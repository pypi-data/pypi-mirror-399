from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StackVariableUpdateSchema")


@_attrs_define
class StackVariableUpdateSchema:
    """Schema for updating an existing stack variable. All fields are optional.

    Attributes:
        key (str): Variable key (name).
        value (None | str | Unset): New variable value.
        is_secret (bool | None | Unset): New secret status.
        description (None | str | Unset): New description.
        category (str | Unset): Variable category: 'env' or 'terraform'. Default: 'env'.
        unit_name (None | str | Unset): Deployment unit name for terraform variables.
        var_type (None | str | Unset): Terraform variable type.
        default_value (Any | None | Unset): Default value for terraform variables.
    """

    key: str
    value: None | str | Unset = UNSET
    is_secret: bool | None | Unset = UNSET
    description: None | str | Unset = UNSET
    category: str | Unset = "env"
    unit_name: None | str | Unset = UNSET
    var_type: None | str | Unset = UNSET
    default_value: Any | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key = self.key

        value: None | str | Unset
        if isinstance(self.value, Unset):
            value = UNSET
        else:
            value = self.value

        is_secret: bool | None | Unset
        if isinstance(self.is_secret, Unset):
            is_secret = UNSET
        else:
            is_secret = self.is_secret

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        category = self.category

        unit_name: None | str | Unset
        if isinstance(self.unit_name, Unset):
            unit_name = UNSET
        else:
            unit_name = self.unit_name

        var_type: None | str | Unset
        if isinstance(self.var_type, Unset):
            var_type = UNSET
        else:
            var_type = self.var_type

        default_value: Any | None | Unset
        if isinstance(self.default_value, Unset):
            default_value = UNSET
        else:
            default_value = self.default_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "key": key,
            }
        )
        if value is not UNSET:
            field_dict["value"] = value
        if is_secret is not UNSET:
            field_dict["is_secret"] = is_secret
        if description is not UNSET:
            field_dict["description"] = description
        if category is not UNSET:
            field_dict["category"] = category
        if unit_name is not UNSET:
            field_dict["unit_name"] = unit_name
        if var_type is not UNSET:
            field_dict["var_type"] = var_type
        if default_value is not UNSET:
            field_dict["default_value"] = default_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        key = d.pop("key")

        def _parse_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        value = _parse_value(d.pop("value", UNSET))

        def _parse_is_secret(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_secret = _parse_is_secret(d.pop("is_secret", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        category = d.pop("category", UNSET)

        def _parse_unit_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        unit_name = _parse_unit_name(d.pop("unit_name", UNSET))

        def _parse_var_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        var_type = _parse_var_type(d.pop("var_type", UNSET))

        def _parse_default_value(data: object) -> Any | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Any | None | Unset, data)

        default_value = _parse_default_value(d.pop("default_value", UNSET))

        stack_variable_update_schema = cls(
            key=key,
            value=value,
            is_secret=is_secret,
            description=description,
            category=category,
            unit_name=unit_name,
            var_type=var_type,
            default_value=default_value,
        )

        stack_variable_update_schema.additional_properties = d
        return stack_variable_update_schema

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
