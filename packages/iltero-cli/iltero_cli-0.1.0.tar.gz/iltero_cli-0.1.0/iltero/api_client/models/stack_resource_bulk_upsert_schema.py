from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stack_resource_bulk_upsert_schema_resources_item import StackResourceBulkUpsertSchemaResourcesItem


T = TypeVar("T", bound="StackResourceBulkUpsertSchema")


@_attrs_define
class StackResourceBulkUpsertSchema:
    """Schema for bulk resource upsert operations.

    Attributes:
        resources (list[StackResourceBulkUpsertSchemaResourcesItem]): List of resources to upsert
        mark_missing_as_destroyed (bool | Unset): Mark existing resources not in the list as destroyed Default: False.
    """

    resources: list[StackResourceBulkUpsertSchemaResourcesItem]
    mark_missing_as_destroyed: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resources = []
        for resources_item_data in self.resources:
            resources_item = resources_item_data.to_dict()
            resources.append(resources_item)

        mark_missing_as_destroyed = self.mark_missing_as_destroyed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resources": resources,
            }
        )
        if mark_missing_as_destroyed is not UNSET:
            field_dict["mark_missing_as_destroyed"] = mark_missing_as_destroyed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_resource_bulk_upsert_schema_resources_item import StackResourceBulkUpsertSchemaResourcesItem

        d = dict(src_dict)
        resources = []
        _resources = d.pop("resources")
        for resources_item_data in _resources:
            resources_item = StackResourceBulkUpsertSchemaResourcesItem.from_dict(resources_item_data)

            resources.append(resources_item)

        mark_missing_as_destroyed = d.pop("mark_missing_as_destroyed", UNSET)

        stack_resource_bulk_upsert_schema = cls(
            resources=resources,
            mark_missing_as_destroyed=mark_missing_as_destroyed,
        )

        stack_resource_bulk_upsert_schema.additional_properties = d
        return stack_resource_bulk_upsert_schema

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
