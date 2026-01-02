from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.resource_item import ResourceItem


T = TypeVar("T", bound="InventoryUpdateRequestSchema")


@_attrs_define
class InventoryUpdateRequestSchema:
    """Schema for resource inventory update request.

    Attributes:
        stack_id (str): ID of the stack to update inventory for
        resources (list[ResourceItem]): List of resources to update in the inventory
        run_id (None | Unset | str): ID of the stack run that triggered this update (if any)
        operation (str | Unset): Operation to perform: 'upsert' (update or insert) or 'replace' (replace all) Default:
            'upsert'.
    """

    stack_id: str
    resources: list[ResourceItem]
    run_id: None | Unset | UUID = UNSET
    operation: str | Unset = "upsert"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = str(self.stack_id)

        resources = []
        for resources_item_data in self.resources:
            resources_item = resources_item_data.to_dict()
            resources.append(resources_item)

        run_id: None | str | Unset
        if isinstance(self.run_id, Unset):
            run_id = UNSET
        elif isinstance(self.run_id, str):
            run_id = str(self.run_id)
        else:
            run_id = self.run_id

        operation = self.operation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "resources": resources,
            }
        )
        if run_id is not UNSET:
            field_dict["run_id"] = run_id
        if operation is not UNSET:
            field_dict["operation"] = operation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.resource_item import ResourceItem

        d = dict(src_dict)
        stack_id = UUID(d.pop("stack_id"))

        resources = []
        _resources = d.pop("resources")
        for resources_item_data in _resources:
            resources_item = ResourceItem.from_dict(resources_item_data)

            resources.append(resources_item)

        def _parse_run_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                run_id_type_0 = UUID(data)

                return run_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        run_id = _parse_run_id(d.pop("run_id", UNSET))

        operation = d.pop("operation", UNSET)

        inventory_update_request_schema = cls(
            stack_id=stack_id,
            resources=resources,
            run_id=run_id,
            operation=operation,
        )

        inventory_update_request_schema.additional_properties = d
        return inventory_update_request_schema

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
