from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserCreateSchema")


@_attrs_define
class UserCreateSchema:
    """Enhanced schema for user creation with org context.

    Attributes:
        email (str):
        name (str):
        password (str):
        is_org_creator (bool | Unset):  Default: False.
        org_id (None | str | Unset):
        role_id (None | str | Unset):
    """

    email: str
    name: str
    password: str
    is_org_creator: bool | Unset = False
    org_id: None | str | Unset = UNSET
    role_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        password = self.password

        is_org_creator = self.is_org_creator

        org_id: None | str | Unset
        if isinstance(self.org_id, Unset):
            org_id = UNSET
        else:
            org_id = self.org_id

        role_id: None | str | Unset
        if isinstance(self.role_id, Unset):
            role_id = UNSET
        else:
            role_id = self.role_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "name": name,
                "password": password,
            }
        )
        if is_org_creator is not UNSET:
            field_dict["is_org_creator"] = is_org_creator
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if role_id is not UNSET:
            field_dict["role_id"] = role_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        password = d.pop("password")

        is_org_creator = d.pop("is_org_creator", UNSET)

        def _parse_org_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        org_id = _parse_org_id(d.pop("org_id", UNSET))

        def _parse_role_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        role_id = _parse_role_id(d.pop("role_id", UNSET))

        user_create_schema = cls(
            email=email,
            name=name,
            password=password,
            is_org_creator=is_org_creator,
            org_id=org_id,
            role_id=role_id,
        )

        user_create_schema.additional_properties = d
        return user_create_schema

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
