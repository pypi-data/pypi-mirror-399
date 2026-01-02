from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.audit_category import AuditCategory
from ..models.audit_event_type import AuditEventType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AudittrailSearchAuditLogsF45B25E2BodyParams")


@_attrs_define
class AudittrailSearchAuditLogsF45B25E2BodyParams:
    """
    Attributes:
        categories (list[AuditCategory] | None | Unset):
        event_types (list[AuditEventType] | None | Unset):
        resource_types (list[str] | None | Unset):
        user_identifiers (list[str] | None | Unset):
    """

    categories: list[AuditCategory] | None | Unset = UNSET
    event_types: list[AuditEventType] | None | Unset = UNSET
    resource_types: list[str] | None | Unset = UNSET
    user_identifiers: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        categories: list[str] | None | Unset
        if isinstance(self.categories, Unset):
            categories = UNSET
        elif isinstance(self.categories, list):
            categories = []
            for categories_type_0_item_data in self.categories:
                categories_type_0_item = categories_type_0_item_data.value
                categories.append(categories_type_0_item)

        else:
            categories = self.categories

        event_types: list[str] | None | Unset
        if isinstance(self.event_types, Unset):
            event_types = UNSET
        elif isinstance(self.event_types, list):
            event_types = []
            for event_types_type_0_item_data in self.event_types:
                event_types_type_0_item = event_types_type_0_item_data.value
                event_types.append(event_types_type_0_item)

        else:
            event_types = self.event_types

        resource_types: list[str] | None | Unset
        if isinstance(self.resource_types, Unset):
            resource_types = UNSET
        elif isinstance(self.resource_types, list):
            resource_types = self.resource_types

        else:
            resource_types = self.resource_types

        user_identifiers: list[str] | None | Unset
        if isinstance(self.user_identifiers, Unset):
            user_identifiers = UNSET
        elif isinstance(self.user_identifiers, list):
            user_identifiers = self.user_identifiers

        else:
            user_identifiers = self.user_identifiers

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if categories is not UNSET:
            field_dict["categories"] = categories
        if event_types is not UNSET:
            field_dict["event_types"] = event_types
        if resource_types is not UNSET:
            field_dict["resource_types"] = resource_types
        if user_identifiers is not UNSET:
            field_dict["user_identifiers"] = user_identifiers

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_categories(data: object) -> list[AuditCategory] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                categories_type_0 = []
                _categories_type_0 = data
                for categories_type_0_item_data in _categories_type_0:
                    categories_type_0_item = AuditCategory(categories_type_0_item_data)

                    categories_type_0.append(categories_type_0_item)

                return categories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AuditCategory] | None | Unset, data)

        categories = _parse_categories(d.pop("categories", UNSET))

        def _parse_event_types(data: object) -> list[AuditEventType] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                event_types_type_0 = []
                _event_types_type_0 = data
                for event_types_type_0_item_data in _event_types_type_0:
                    event_types_type_0_item = AuditEventType(event_types_type_0_item_data)

                    event_types_type_0.append(event_types_type_0_item)

                return event_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AuditEventType] | None | Unset, data)

        event_types = _parse_event_types(d.pop("event_types", UNSET))

        def _parse_resource_types(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                resource_types_type_0 = cast(list[str], data)

                return resource_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        resource_types = _parse_resource_types(d.pop("resource_types", UNSET))

        def _parse_user_identifiers(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                user_identifiers_type_0 = cast(list[str], data)

                return user_identifiers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        user_identifiers = _parse_user_identifiers(d.pop("user_identifiers", UNSET))

        audittrail_search_audit_logs_f45b25e2_body_params = cls(
            categories=categories,
            event_types=event_types,
            resource_types=resource_types,
            user_identifiers=user_identifiers,
        )

        audittrail_search_audit_logs_f45b25e2_body_params.additional_properties = d
        return audittrail_search_audit_logs_f45b25e2_body_params

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
