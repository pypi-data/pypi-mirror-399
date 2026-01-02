from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.registry_module_version_create_schema_compliance_status_type_0 import (
        RegistryModuleVersionCreateSchemaComplianceStatusType0,
    )
    from ..models.registry_module_version_create_schema_metadata_type_0 import (
        RegistryModuleVersionCreateSchemaMetadataType0,
    )


T = TypeVar("T", bound="RegistryModuleVersionCreateSchema")


@_attrs_define
class RegistryModuleVersionCreateSchema:
    """Schema for Registry module version creation.

    Attributes:
        version (str): Version number (SemVer format)
        module_id (str): ID of the module
        storage_path (str): Path to the module archive in storage
        metadata (None | RegistryModuleVersionCreateSchemaMetadataType0 | Unset): Module metadata (inputs, outputs,
            dependencies, etc.)
        compliance_status (None | RegistryModuleVersionCreateSchemaComplianceStatusType0 | Unset): Compliance scan
            results
    """

    version: str
    module_id: str
    storage_path: str
    metadata: None | RegistryModuleVersionCreateSchemaMetadataType0 | Unset = UNSET
    compliance_status: None | RegistryModuleVersionCreateSchemaComplianceStatusType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.registry_module_version_create_schema_compliance_status_type_0 import (
            RegistryModuleVersionCreateSchemaComplianceStatusType0,
        )
        from ..models.registry_module_version_create_schema_metadata_type_0 import (
            RegistryModuleVersionCreateSchemaMetadataType0,
        )

        version = self.version

        module_id = str(self.module_id)

        storage_path = self.storage_path

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, RegistryModuleVersionCreateSchemaMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        compliance_status: dict[str, Any] | None | Unset
        if isinstance(self.compliance_status, Unset):
            compliance_status = UNSET
        elif isinstance(self.compliance_status, RegistryModuleVersionCreateSchemaComplianceStatusType0):
            compliance_status = self.compliance_status.to_dict()
        else:
            compliance_status = self.compliance_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "module_id": module_id,
                "storage_path": storage_path,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if compliance_status is not UNSET:
            field_dict["compliance_status"] = compliance_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.registry_module_version_create_schema_compliance_status_type_0 import (
            RegistryModuleVersionCreateSchemaComplianceStatusType0,
        )
        from ..models.registry_module_version_create_schema_metadata_type_0 import (
            RegistryModuleVersionCreateSchemaMetadataType0,
        )

        d = dict(src_dict)
        version = d.pop("version")

        module_id = UUID(d.pop("module_id"))

        storage_path = d.pop("storage_path")

        def _parse_metadata(data: object) -> None | RegistryModuleVersionCreateSchemaMetadataType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = RegistryModuleVersionCreateSchemaMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryModuleVersionCreateSchemaMetadataType0 | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_compliance_status(
            data: object,
        ) -> None | RegistryModuleVersionCreateSchemaComplianceStatusType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compliance_status_type_0 = RegistryModuleVersionCreateSchemaComplianceStatusType0.from_dict(data)

                return compliance_status_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RegistryModuleVersionCreateSchemaComplianceStatusType0 | Unset, data)

        compliance_status = _parse_compliance_status(d.pop("compliance_status", UNSET))

        registry_module_version_create_schema = cls(
            version=version,
            module_id=module_id,
            storage_path=storage_path,
            metadata=metadata,
            compliance_status=compliance_status,
        )

        registry_module_version_create_schema.additional_properties = d
        return registry_module_version_create_schema

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
