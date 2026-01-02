from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicySetUpdateSchema")


@_attrs_define
class PolicySetUpdateSchema:
    """Schema for policy set updates.

    Attributes:
        name (None | str | Unset): Name of the policy set
        description (None | str | Unset): Description of the policy set
        source_type (None | str | Unset): Type of policy source
        source_location (None | str | Unset): Git repository URL containing policy definitions
        version (None | str | Unset): Git commit hash/tag/branch
        is_active (bool | None | Unset): Whether this policy set is active
        policy_bundle_keys (list[str] | None | Unset): List of GlobalPolicyBundle keys this PolicySet imports from.
            Example: ['cis_aws_v1_6', 'iltero_aws_v1'].
    """

    name: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    source_type: None | str | Unset = UNSET
    source_location: None | str | Unset = UNSET
    version: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    policy_bundle_keys: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        source_type: None | str | Unset
        if isinstance(self.source_type, Unset):
            source_type = UNSET
        else:
            source_type = self.source_type

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

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        policy_bundle_keys: list[str] | None | Unset
        if isinstance(self.policy_bundle_keys, Unset):
            policy_bundle_keys = UNSET
        elif isinstance(self.policy_bundle_keys, list):
            policy_bundle_keys = self.policy_bundle_keys

        else:
            policy_bundle_keys = self.policy_bundle_keys

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if source_type is not UNSET:
            field_dict["source_type"] = source_type
        if source_location is not UNSET:
            field_dict["source_location"] = source_location
        if version is not UNSET:
            field_dict["version"] = version
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if policy_bundle_keys is not UNSET:
            field_dict["policy_bundle_keys"] = policy_bundle_keys

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_source_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_type = _parse_source_type(d.pop("source_type", UNSET))

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

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_policy_bundle_keys(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                policy_bundle_keys_type_0 = cast(list[str], data)

                return policy_bundle_keys_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        policy_bundle_keys = _parse_policy_bundle_keys(d.pop("policy_bundle_keys", UNSET))

        policy_set_update_schema = cls(
            name=name,
            description=description,
            source_type=source_type,
            source_location=source_location,
            version=version,
            is_active=is_active,
            policy_bundle_keys=policy_bundle_keys,
        )

        policy_set_update_schema.additional_properties = d
        return policy_set_update_schema

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
