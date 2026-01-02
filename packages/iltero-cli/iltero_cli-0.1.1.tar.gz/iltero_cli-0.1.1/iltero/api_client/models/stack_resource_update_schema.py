from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stack_resource_update_schema_drift_details_type_0 import StackResourceUpdateSchemaDriftDetailsType0
    from ..models.stack_resource_update_schema_metadata_type_0 import StackResourceUpdateSchemaMetadataType0
    from ..models.stack_resource_update_schema_terraform_state_type_0 import (
        StackResourceUpdateSchemaTerraformStateType0,
    )


T = TypeVar("T", bound="StackResourceUpdateSchema")


@_attrs_define
class StackResourceUpdateSchema:
    """Schema for stack resource updates.

    Attributes:
        resource_name (None | str | Unset): Human-readable resource name
        lifecycle_status (None | str | Unset): Lifecycle status update
        terraform_state (None | StackResourceUpdateSchemaTerraformStateType0 | Unset): Updated Terraform state
        terraform_address (None | str | Unset): Updated Terraform address
        metadata (None | StackResourceUpdateSchemaMetadataType0 | Unset): Updated metadata
        drift_detected (bool | None | Unset): Drift detection status
        drift_details (None | StackResourceUpdateSchemaDriftDetailsType0 | Unset): Drift details if detected
    """

    resource_name: None | str | Unset = UNSET
    lifecycle_status: None | str | Unset = UNSET
    terraform_state: None | StackResourceUpdateSchemaTerraformStateType0 | Unset = UNSET
    terraform_address: None | str | Unset = UNSET
    metadata: None | StackResourceUpdateSchemaMetadataType0 | Unset = UNSET
    drift_detected: bool | None | Unset = UNSET
    drift_details: None | StackResourceUpdateSchemaDriftDetailsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.stack_resource_update_schema_drift_details_type_0 import (
            StackResourceUpdateSchemaDriftDetailsType0,
        )
        from ..models.stack_resource_update_schema_metadata_type_0 import StackResourceUpdateSchemaMetadataType0
        from ..models.stack_resource_update_schema_terraform_state_type_0 import (
            StackResourceUpdateSchemaTerraformStateType0,
        )

        resource_name: None | str | Unset
        if isinstance(self.resource_name, Unset):
            resource_name = UNSET
        else:
            resource_name = self.resource_name

        lifecycle_status: None | str | Unset
        if isinstance(self.lifecycle_status, Unset):
            lifecycle_status = UNSET
        else:
            lifecycle_status = self.lifecycle_status

        terraform_state: dict[str, Any] | None | Unset
        if isinstance(self.terraform_state, Unset):
            terraform_state = UNSET
        elif isinstance(self.terraform_state, StackResourceUpdateSchemaTerraformStateType0):
            terraform_state = self.terraform_state.to_dict()
        else:
            terraform_state = self.terraform_state

        terraform_address: None | str | Unset
        if isinstance(self.terraform_address, Unset):
            terraform_address = UNSET
        else:
            terraform_address = self.terraform_address

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, StackResourceUpdateSchemaMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        drift_detected: bool | None | Unset
        if isinstance(self.drift_detected, Unset):
            drift_detected = UNSET
        else:
            drift_detected = self.drift_detected

        drift_details: dict[str, Any] | None | Unset
        if isinstance(self.drift_details, Unset):
            drift_details = UNSET
        elif isinstance(self.drift_details, StackResourceUpdateSchemaDriftDetailsType0):
            drift_details = self.drift_details.to_dict()
        else:
            drift_details = self.drift_details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if resource_name is not UNSET:
            field_dict["resource_name"] = resource_name
        if lifecycle_status is not UNSET:
            field_dict["lifecycle_status"] = lifecycle_status
        if terraform_state is not UNSET:
            field_dict["terraform_state"] = terraform_state
        if terraform_address is not UNSET:
            field_dict["terraform_address"] = terraform_address
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if drift_detected is not UNSET:
            field_dict["drift_detected"] = drift_detected
        if drift_details is not UNSET:
            field_dict["drift_details"] = drift_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_resource_update_schema_drift_details_type_0 import (
            StackResourceUpdateSchemaDriftDetailsType0,
        )
        from ..models.stack_resource_update_schema_metadata_type_0 import StackResourceUpdateSchemaMetadataType0
        from ..models.stack_resource_update_schema_terraform_state_type_0 import (
            StackResourceUpdateSchemaTerraformStateType0,
        )

        d = dict(src_dict)

        def _parse_resource_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resource_name = _parse_resource_name(d.pop("resource_name", UNSET))

        def _parse_lifecycle_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        lifecycle_status = _parse_lifecycle_status(d.pop("lifecycle_status", UNSET))

        def _parse_terraform_state(data: object) -> None | StackResourceUpdateSchemaTerraformStateType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                terraform_state_type_0 = StackResourceUpdateSchemaTerraformStateType0.from_dict(data)

                return terraform_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackResourceUpdateSchemaTerraformStateType0 | Unset, data)

        terraform_state = _parse_terraform_state(d.pop("terraform_state", UNSET))

        def _parse_terraform_address(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        terraform_address = _parse_terraform_address(d.pop("terraform_address", UNSET))

        def _parse_metadata(data: object) -> None | StackResourceUpdateSchemaMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = StackResourceUpdateSchemaMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackResourceUpdateSchemaMetadataType0 | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_drift_detected(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        drift_detected = _parse_drift_detected(d.pop("drift_detected", UNSET))

        def _parse_drift_details(data: object) -> None | StackResourceUpdateSchemaDriftDetailsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                drift_details_type_0 = StackResourceUpdateSchemaDriftDetailsType0.from_dict(data)

                return drift_details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackResourceUpdateSchemaDriftDetailsType0 | Unset, data)

        drift_details = _parse_drift_details(d.pop("drift_details", UNSET))

        stack_resource_update_schema = cls(
            resource_name=resource_name,
            lifecycle_status=lifecycle_status,
            terraform_state=terraform_state,
            terraform_address=terraform_address,
            metadata=metadata,
            drift_detected=drift_detected,
            drift_details=drift_details,
        )

        stack_resource_update_schema.additional_properties = d
        return stack_resource_update_schema

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
