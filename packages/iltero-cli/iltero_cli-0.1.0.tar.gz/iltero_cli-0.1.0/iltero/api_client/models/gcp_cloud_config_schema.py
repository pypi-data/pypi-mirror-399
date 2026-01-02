from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GCPCloudConfigSchema")


@_attrs_define
class GCPCloudConfigSchema:
    """Schema for GCP cloud provider configuration.

    Attributes:
        project_id (str): GCP project ID
        region (str): GCP region for resources
        service_account_email (str): Service account email for deployment
        plan_bucket (str): GCS bucket for storing Terraform plans
    """

    project_id: str
    region: str
    service_account_email: str
    plan_bucket: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        project_id = self.project_id

        region = self.region

        service_account_email = self.service_account_email

        plan_bucket = self.plan_bucket

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "project_id": project_id,
                "region": region,
                "service_account_email": service_account_email,
                "plan_bucket": plan_bucket,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        project_id = d.pop("project_id")

        region = d.pop("region")

        service_account_email = d.pop("service_account_email")

        plan_bucket = d.pop("plan_bucket")

        gcp_cloud_config_schema = cls(
            project_id=project_id,
            region=region,
            service_account_email=service_account_email,
            plan_bucket=plan_bucket,
        )

        gcp_cloud_config_schema.additional_properties = d
        return gcp_cloud_config_schema

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
