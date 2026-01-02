from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="InstallationTokenRequestSchema")


@_attrs_define
class InstallationTokenRequestSchema:
    """Schema for GitHub App installation token request.

    Attributes:
        stack_id (str): Stack ID requesting the token
        repository (str): Repository name (owner/repo format)
    """

    stack_id: str
    repository: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        repository = self.repository

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "repository": repository,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        repository = d.pop("repository")

        installation_token_request_schema = cls(
            stack_id=stack_id,
            repository=repository,
        )

        installation_token_request_schema.additional_properties = d
        return installation_token_request_schema

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
