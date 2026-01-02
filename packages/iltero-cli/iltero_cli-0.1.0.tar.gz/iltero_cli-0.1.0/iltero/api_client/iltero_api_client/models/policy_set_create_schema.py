from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicySetCreateSchema")


@_attrs_define
class PolicySetCreateSchema:
    """Schema for policy set creation.

    Attributes:
        name (str): Name of the policy set
        source_type (str): Type of policy source
        description (None | str | Unset): Description of the policy set
        source_location (None | str | Unset): Git repository URL containing policy definitions
        version (None | str | Unset): Git commit hash/tag/branch
        policy_bundle_keys (list[str] | Unset): List of GlobalPolicyBundle keys this PolicySet imports from. Example:
            ['cis_aws_v1_6', 'iltero_aws_v1']. Links tenant policies back to global catalog.
        is_active (bool | Unset): Whether this policy set is active Default: True.
    """

    name: str
    source_type: str
    description: None | str | Unset = UNSET
    source_location: None | str | Unset = UNSET
    version: None | str | Unset = UNSET
    policy_bundle_keys: list[str] | Unset = UNSET
    is_active: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        source_type = self.source_type

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        source_location: None | str | Unset
        if isinstance(self.source_location, Unset):
            source_location = UNSET
        else:
            source_location = self.source_location

        version: None | str | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        policy_bundle_keys: list[str] | Unset = UNSET
        if not isinstance(self.policy_bundle_keys, Unset):
            policy_bundle_keys = self.policy_bundle_keys

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "source_type": source_type,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if source_location is not UNSET:
            field_dict["source_location"] = source_location
        if version is not UNSET:
            field_dict["version"] = version
        if policy_bundle_keys is not UNSET:
            field_dict["policy_bundle_keys"] = policy_bundle_keys
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        source_type = d.pop("source_type")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_source_location(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_location = _parse_source_location(d.pop("source_location", UNSET))

        def _parse_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        policy_bundle_keys = cast(list[str], d.pop("policy_bundle_keys", UNSET))

        is_active = d.pop("is_active", UNSET)

        policy_set_create_schema = cls(
            name=name,
            source_type=source_type,
            description=description,
            source_location=source_location,
            version=version,
            policy_bundle_keys=policy_bundle_keys,
            is_active=is_active,
        )

        policy_set_create_schema.additional_properties = d
        return policy_set_create_schema

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
