from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AzureCloudConfigSchema")


@_attrs_define
class AzureCloudConfigSchema:
    """Schema for Azure cloud provider configuration.

    Attributes:
        subscription_id (str): Azure subscription ID
        tenant_id (str): Azure tenant ID
        client_id (str): Azure client ID for service principal
        resource_group (str): Azure resource group
        location (str): Azure location for resources
        plan_storage_account (str): Storage account for storing Terraform plans
        plan_container (str): Storage container for Terraform plans
    """

    subscription_id: str
    tenant_id: str
    client_id: str
    resource_group: str
    location: str
    plan_storage_account: str
    plan_container: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        subscription_id = self.subscription_id

        tenant_id = self.tenant_id

        client_id = self.client_id

        resource_group = self.resource_group

        location = self.location

        plan_storage_account = self.plan_storage_account

        plan_container = self.plan_container

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "subscription_id": subscription_id,
                "tenant_id": tenant_id,
                "client_id": client_id,
                "resource_group": resource_group,
                "location": location,
                "plan_storage_account": plan_storage_account,
                "plan_container": plan_container,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        subscription_id = d.pop("subscription_id")

        tenant_id = d.pop("tenant_id")

        client_id = d.pop("client_id")

        resource_group = d.pop("resource_group")

        location = d.pop("location")

        plan_storage_account = d.pop("plan_storage_account")

        plan_container = d.pop("plan_container")

        azure_cloud_config_schema = cls(
            subscription_id=subscription_id,
            tenant_id=tenant_id,
            client_id=client_id,
            resource_group=resource_group,
            location=location,
            plan_storage_account=plan_storage_account,
            plan_container=plan_container,
        )

        azure_cloud_config_schema.additional_properties = d
        return azure_cloud_config_schema

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
