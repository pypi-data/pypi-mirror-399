from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resource_item_metadata import ResourceItemMetadata


T = TypeVar("T", bound="ResourceItem")


@_attrs_define
class ResourceItem:
    """Schema for an individual resource in the inventory.

    Attributes:
        resource_type (str): Type of the resource (e.g., 'aws_s3_bucket', 'aws_vpc')
        resource_id (str): Provider-specific resource identifier
        cloud_provider (str): Cloud provider (e.g., 'aws', 'azure', 'gcp')
        resource_name (None | str | Unset): Human-readable name for the resource
        metadata (ResourceItemMetadata | Unset): Resource metadata, properties and tags
    """

    resource_type: str
    resource_id: str
    cloud_provider: str
    resource_name: None | str | Unset = UNSET
    metadata: ResourceItemMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resource_type = self.resource_type

        resource_id = self.resource_id

        cloud_provider = self.cloud_provider

        resource_name: None | str | Unset
        if isinstance(self.resource_name, Unset):
            resource_name = UNSET
        else:
            resource_name = self.resource_name

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resource_type": resource_type,
                "resource_id": resource_id,
                "cloud_provider": cloud_provider,
            }
        )
        if resource_name is not UNSET:
            field_dict["resource_name"] = resource_name
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_item_metadata import ResourceItemMetadata

        d = dict(src_dict)
        resource_type = d.pop("resource_type")

        resource_id = d.pop("resource_id")

        cloud_provider = d.pop("cloud_provider")

        def _parse_resource_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resource_name = _parse_resource_name(d.pop("resource_name", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: ResourceItemMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ResourceItemMetadata.from_dict(_metadata)

        resource_item = cls(
            resource_type=resource_type,
            resource_id=resource_id,
            cloud_provider=cloud_provider,
            resource_name=resource_name,
            metadata=metadata,
        )

        resource_item.additional_properties = d
        return resource_item

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
