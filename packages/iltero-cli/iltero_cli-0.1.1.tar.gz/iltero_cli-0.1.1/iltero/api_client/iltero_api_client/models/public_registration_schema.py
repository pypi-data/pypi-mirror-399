from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PublicRegistrationSchema")


@_attrs_define
class PublicRegistrationSchema:
    """Schema for user registration.

    Attributes:
        email (str):
        name (str):
        password (str):
        confirm_password (str): Password confirmation
        invite_token (None | str | Unset):
    """

    email: str
    name: str
    password: str
    confirm_password: str
    invite_token: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        password = self.password

        confirm_password = self.confirm_password

        invite_token: None | str | Unset
        if isinstance(self.invite_token, Unset):
            invite_token = UNSET
        else:
            invite_token = self.invite_token

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "name": name,
                "password": password,
                "confirm_password": confirm_password,
            }
        )
        if invite_token is not UNSET:
            field_dict["invite_token"] = invite_token

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        password = d.pop("password")

        confirm_password = d.pop("confirm_password")

        def _parse_invite_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        invite_token = _parse_invite_token(d.pop("invite_token", UNSET))

        public_registration_schema = cls(
            email=email,
            name=name,
            password=password,
            confirm_password=confirm_password,
            invite_token=invite_token,
        )

        public_registration_schema.additional_properties = d
        return public_registration_schema

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
