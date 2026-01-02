from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TerraformBackendConfigSchema")


@_attrs_define
class TerraformBackendConfigSchema:
    """Schema for Terraform backend configuration.

    Attributes:
        bucket (str): Name of the storage bucket for Terraform state
        region (str): Region for the backend
        encrypt (bool | None | Unset): Whether to enable encryption for the backend state Default: True.
        kms_key_id (None | str | Unset): Optional KMS key ID for encryption
        dynamodb_table (None | str | Unset): Optional DynamoDB table for state locking
    """

    bucket: str
    region: str
    encrypt: bool | None | Unset = True
    kms_key_id: None | str | Unset = UNSET
    dynamodb_table: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bucket = self.bucket

        region = self.region

        encrypt: bool | None | Unset
        if isinstance(self.encrypt, Unset):
            encrypt = UNSET
        else:
            encrypt = self.encrypt

        kms_key_id: None | str | Unset
        if isinstance(self.kms_key_id, Unset):
            kms_key_id = UNSET
        else:
            kms_key_id = self.kms_key_id

        dynamodb_table: None | str | Unset
        if isinstance(self.dynamodb_table, Unset):
            dynamodb_table = UNSET
        else:
            dynamodb_table = self.dynamodb_table

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bucket": bucket,
                "region": region,
            }
        )
        if encrypt is not UNSET:
            field_dict["encrypt"] = encrypt
        if kms_key_id is not UNSET:
            field_dict["kms_key_id"] = kms_key_id
        if dynamodb_table is not UNSET:
            field_dict["dynamodb_table"] = dynamodb_table

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bucket = d.pop("bucket")

        region = d.pop("region")

        def _parse_encrypt(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        encrypt = _parse_encrypt(d.pop("encrypt", UNSET))

        def _parse_kms_key_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kms_key_id = _parse_kms_key_id(d.pop("kms_key_id", UNSET))

        def _parse_dynamodb_table(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dynamodb_table = _parse_dynamodb_table(d.pop("dynamodb_table", UNSET))

        terraform_backend_config_schema = cls(
            bucket=bucket,
            region=region,
            encrypt=encrypt,
            kms_key_id=kms_key_id,
            dynamodb_table=dynamodb_table,
        )

        terraform_backend_config_schema.additional_properties = d
        return terraform_backend_config_schema

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
