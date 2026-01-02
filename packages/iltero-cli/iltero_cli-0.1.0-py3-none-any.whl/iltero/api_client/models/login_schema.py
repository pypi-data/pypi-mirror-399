from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoginSchema")


@_attrs_define
class LoginSchema:
    """Login request schema.

    Attributes:
        email (str): User's email address
        password (str): User's password
        remember_me (bool | Unset): Whether to remember the login Default: False.
        two_factor_code (None | str | Unset):
    """

    email: str
    password: str
    remember_me: bool | Unset = False
    two_factor_code: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        password = self.password

        remember_me = self.remember_me

        two_factor_code: None | str | Unset
        if isinstance(self.two_factor_code, Unset):
            two_factor_code = UNSET
        else:
            two_factor_code = self.two_factor_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "password": password,
            }
        )
        if remember_me is not UNSET:
            field_dict["remember_me"] = remember_me
        if two_factor_code is not UNSET:
            field_dict["two_factor_code"] = two_factor_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        password = d.pop("password")

        remember_me = d.pop("remember_me", UNSET)

        def _parse_two_factor_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        two_factor_code = _parse_two_factor_code(d.pop("two_factor_code", UNSET))

        login_schema = cls(
            email=email,
            password=password,
            remember_me=remember_me,
            two_factor_code=two_factor_code,
        )

        login_schema.additional_properties = d
        return login_schema

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
