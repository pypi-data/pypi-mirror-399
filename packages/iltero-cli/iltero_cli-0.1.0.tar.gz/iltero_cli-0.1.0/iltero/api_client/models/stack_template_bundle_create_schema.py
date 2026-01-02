from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StackTemplateBundleCreateSchema")


@_attrs_define
class StackTemplateBundleCreateSchema:
    """Schema for creating Template Bundle integration.

    Example:
        {'business_use_case': 'HIPAA-compliant patient portal infrastructure', 'deployment_strategy':
            'uic_coordinated_sequential', 'marketplace_category': 'Healthcare', 'template_bundle_id':
            '550e8400-e29b-41d4-a716-446655440000', 'template_id': 'hipaa-core-aws', 'template_version': '2.1.0'}

    Attributes:
        template_bundle_id (str): ID of registry.TemplateBundle in public schema
        template_id (str): Template ID string (e.g., 'hipaa-core-aws')
        template_version (str): Template version (e.g., '2.1.0')
        marketplace_category (None | str | Unset): Marketplace category (Healthcare, Financial Services, etc.)
        business_use_case (None | str | Unset): Customer-facing business use case description
        deployment_strategy (str | Unset): Deployment strategy for infrastructure units Default:
            'uic_coordinated_sequential'.
    """

    template_bundle_id: str
    template_id: str
    template_version: str
    marketplace_category: None | str | Unset = UNSET
    business_use_case: None | str | Unset = UNSET
    deployment_strategy: str | Unset = "uic_coordinated_sequential"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        template_bundle_id = self.template_bundle_id

        template_id = self.template_id

        template_version = self.template_version

        marketplace_category: None | str | Unset
        if isinstance(self.marketplace_category, Unset):
            marketplace_category = UNSET
        else:
            marketplace_category = self.marketplace_category

        business_use_case: None | str | Unset
        if isinstance(self.business_use_case, Unset):
            business_use_case = UNSET
        else:
            business_use_case = self.business_use_case

        deployment_strategy = self.deployment_strategy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "template_bundle_id": template_bundle_id,
                "template_id": template_id,
                "template_version": template_version,
            }
        )
        if marketplace_category is not UNSET:
            field_dict["marketplace_category"] = marketplace_category
        if business_use_case is not UNSET:
            field_dict["business_use_case"] = business_use_case
        if deployment_strategy is not UNSET:
            field_dict["deployment_strategy"] = deployment_strategy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        template_bundle_id = d.pop("template_bundle_id")

        template_id = d.pop("template_id")

        template_version = d.pop("template_version")

        def _parse_marketplace_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        marketplace_category = _parse_marketplace_category(d.pop("marketplace_category", UNSET))

        def _parse_business_use_case(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        business_use_case = _parse_business_use_case(d.pop("business_use_case", UNSET))

        deployment_strategy = d.pop("deployment_strategy", UNSET)

        stack_template_bundle_create_schema = cls(
            template_bundle_id=template_bundle_id,
            template_id=template_id,
            template_version=template_version,
            marketplace_category=marketplace_category,
            business_use_case=business_use_case,
            deployment_strategy=deployment_strategy,
        )

        stack_template_bundle_create_schema.additional_properties = d
        return stack_template_bundle_create_schema

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
