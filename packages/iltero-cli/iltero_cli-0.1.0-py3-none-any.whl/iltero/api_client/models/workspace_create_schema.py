from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceCreateSchema")


@_attrs_define
class WorkspaceCreateSchema:
    """Schema for workspace creation with multi-environment support.

    Attributes:
        name (str): Workspace name
        description (None | str | Unset): Workspace description
        slug (None | str | Unset): URL-friendly version of the name
        environment_ids (list[str] | None | Unset): List of environment IDs for the workspace. If not provided, uses
            org's default environment.
        default_environment_id (None | str | Unset): Default environment ID (must be in environment_ids list). If not
            provided, first environment will be default.
    """

    name: str
    description: None | str | Unset = UNSET
    slug: None | str | Unset = UNSET
    environment_ids: list[str] | None | Unset = UNSET
    default_environment_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        slug: None | str | Unset
        if isinstance(self.slug, Unset):
            slug = UNSET
        else:
            slug = self.slug

        environment_ids: list[str] | None | Unset
        if isinstance(self.environment_ids, Unset):
            environment_ids = UNSET
        elif isinstance(self.environment_ids, list):
            environment_ids = self.environment_ids

        else:
            environment_ids = self.environment_ids

        default_environment_id: None | str | Unset
        if isinstance(self.default_environment_id, Unset):
            default_environment_id = UNSET
        else:
            default_environment_id = self.default_environment_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if slug is not UNSET:
            field_dict["slug"] = slug
        if environment_ids is not UNSET:
            field_dict["environment_ids"] = environment_ids
        if default_environment_id is not UNSET:
            field_dict["default_environment_id"] = default_environment_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_slug(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        slug = _parse_slug(d.pop("slug", UNSET))

        def _parse_environment_ids(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                environment_ids_type_0 = cast(list[str], data)

                return environment_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        environment_ids = _parse_environment_ids(d.pop("environment_ids", UNSET))

        def _parse_default_environment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        default_environment_id = _parse_default_environment_id(d.pop("default_environment_id", UNSET))

        workspace_create_schema = cls(
            name=name,
            description=description,
            slug=slug,
            environment_ids=environment_ids,
            default_environment_id=default_environment_id,
        )

        workspace_create_schema.additional_properties = d
        return workspace_create_schema

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
