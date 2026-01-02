from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AWSCloudConfigSchema")


@_attrs_define
class AWSCloudConfigSchema:
    """Schema for AWS cloud provider configuration.

    Attributes:
        aws_region (str): AWS region for resources
        aws_role_arn (str): AWS IAM role ARN to assume for deployment
        plan_bucket (str): S3 bucket for storing Terraform plans
    """

    aws_region: str
    aws_role_arn: str
    plan_bucket: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        aws_region = self.aws_region

        aws_role_arn = self.aws_role_arn

        plan_bucket = self.plan_bucket

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aws_region": aws_region,
                "aws_role_arn": aws_role_arn,
                "plan_bucket": plan_bucket,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        aws_region = d.pop("aws_region")

        aws_role_arn = d.pop("aws_role_arn")

        plan_bucket = d.pop("plan_bucket")

        aws_cloud_config_schema = cls(
            aws_region=aws_region,
            aws_role_arn=aws_role_arn,
            plan_bucket=plan_bucket,
        )

        aws_cloud_config_schema.additional_properties = d
        return aws_cloud_config_schema

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
