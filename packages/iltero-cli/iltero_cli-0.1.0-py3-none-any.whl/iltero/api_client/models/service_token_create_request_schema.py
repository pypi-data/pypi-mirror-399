from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceTokenCreateRequestSchema")


@_attrs_define
class ServiceTokenCreateRequestSchema:
    """Service account token creation request schema.

    Attributes:
        service_account_name (str): Name of the service account
        scopes (list[str]): List of scopes to grant to this token
        description (None | str | Unset): Human-readable description of token purpose Default: ''.
        expires_in (int | None | Unset): Token expiration in seconds (optional)
    """

    service_account_name: str
    scopes: list[str]
    description: None | str | Unset = ""
    expires_in: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        service_account_name = self.service_account_name

        scopes = self.scopes

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        expires_in: int | None | Unset
        if isinstance(self.expires_in, Unset):
            expires_in = UNSET
        else:
            expires_in = self.expires_in

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "service_account_name": service_account_name,
                "scopes": scopes,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if expires_in is not UNSET:
            field_dict["expires_in"] = expires_in

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        service_account_name = d.pop("service_account_name")

        scopes = cast(list[str], d.pop("scopes"))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_expires_in(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expires_in = _parse_expires_in(d.pop("expires_in", UNSET))

        service_token_create_request_schema = cls(
            service_account_name=service_account_name,
            scopes=scopes,
            description=description,
            expires_in=expires_in,
        )

        service_token_create_request_schema.additional_properties = d
        return service_token_create_request_schema

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
