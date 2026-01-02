from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evidence_collection_request_schema_metadata_type_0 import EvidenceCollectionRequestSchemaMetadataType0


T = TypeVar("T", bound="EvidenceCollectionRequestSchema")


@_attrs_define
class EvidenceCollectionRequestSchema:
    """Request schema for evidence collection.

    Attributes:
        stack_id (str): Stack identifier
        evidence_types (list[str]): Types of evidence to collect
        workspace_id (None | str | Unset): Workspace identifier
        collection_reason (str | Unset): Reason for evidence collection Default: 'manual'.
        compress (bool | Unset): Whether to compress evidence Default: True.
        encrypt (bool | Unset): Whether to encrypt evidence Default: True.
        retention_override_days (int | None | Unset): Override default retention period
        metadata (EvidenceCollectionRequestSchemaMetadataType0 | None | Unset): Additional metadata for evidence
    """

    stack_id: str
    evidence_types: list[str]
    workspace_id: None | str | Unset = UNSET
    collection_reason: str | Unset = "manual"
    compress: bool | Unset = True
    encrypt: bool | Unset = True
    retention_override_days: int | None | Unset = UNSET
    metadata: EvidenceCollectionRequestSchemaMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.evidence_collection_request_schema_metadata_type_0 import (
            EvidenceCollectionRequestSchemaMetadataType0,
        )

        stack_id = self.stack_id

        evidence_types = self.evidence_types

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        collection_reason = self.collection_reason

        compress = self.compress

        encrypt = self.encrypt

        retention_override_days: int | None | Unset
        if isinstance(self.retention_override_days, Unset):
            retention_override_days = UNSET
        else:
            retention_override_days = self.retention_override_days

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, EvidenceCollectionRequestSchemaMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "evidence_types": evidence_types,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if collection_reason is not UNSET:
            field_dict["collection_reason"] = collection_reason
        if compress is not UNSET:
            field_dict["compress"] = compress
        if encrypt is not UNSET:
            field_dict["encrypt"] = encrypt
        if retention_override_days is not UNSET:
            field_dict["retention_override_days"] = retention_override_days
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evidence_collection_request_schema_metadata_type_0 import (
            EvidenceCollectionRequestSchemaMetadataType0,
        )

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        evidence_types = cast(list[str], d.pop("evidence_types"))

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        collection_reason = d.pop("collection_reason", UNSET)

        compress = d.pop("compress", UNSET)

        encrypt = d.pop("encrypt", UNSET)

        def _parse_retention_override_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        retention_override_days = _parse_retention_override_days(d.pop("retention_override_days", UNSET))

        def _parse_metadata(data: object) -> EvidenceCollectionRequestSchemaMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = EvidenceCollectionRequestSchemaMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EvidenceCollectionRequestSchemaMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        evidence_collection_request_schema = cls(
            stack_id=stack_id,
            evidence_types=evidence_types,
            workspace_id=workspace_id,
            collection_reason=collection_reason,
            compress=compress,
            encrypt=encrypt,
            retention_override_days=retention_override_days,
            metadata=metadata,
        )

        evidence_collection_request_schema.additional_properties = d
        return evidence_collection_request_schema

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
