from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.collection_rule_schema import CollectionRuleSchema
    from ..models.evidence_requirements_schema import EvidenceRequirementsSchema


T = TypeVar("T", bound="EvidenceCollectionPolicySchema")


@_attrs_define
class EvidenceCollectionPolicySchema:
    """Schema for evidence collection policies.

    Attributes:
        enabled (bool | Unset): Enable evidence collection Default: True.
        default_frequency (str | Unset): Default collection frequency Default: 'DAILY'.
        required_evidence_types (list[str] | Unset): Required evidence types
        retention_days (int | Unset): Default retention period Default: 90.
        storage_backend (str | Unset): Storage backend (s3, azure, gcs) Default: 's3'.
        encryption_required (bool | Unset): Require encryption for stored evidence Default: True.
        compress_evidence (bool | Unset): Compress evidence before storage Default: True.
        collection_rules (list[CollectionRuleSchema] | Unset): Specific collection rules per evidence type
        evidence_requirements (EvidenceRequirementsSchema | Unset): Schema for evidence requirements by phase.
    """

    enabled: bool | Unset = True
    default_frequency: str | Unset = "DAILY"
    required_evidence_types: list[str] | Unset = UNSET
    retention_days: int | Unset = 90
    storage_backend: str | Unset = "s3"
    encryption_required: bool | Unset = True
    compress_evidence: bool | Unset = True
    collection_rules: list[CollectionRuleSchema] | Unset = UNSET
    evidence_requirements: EvidenceRequirementsSchema | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        default_frequency = self.default_frequency

        required_evidence_types: list[str] | Unset = UNSET
        if not isinstance(self.required_evidence_types, Unset):
            required_evidence_types = self.required_evidence_types

        retention_days = self.retention_days

        storage_backend = self.storage_backend

        encryption_required = self.encryption_required

        compress_evidence = self.compress_evidence

        collection_rules: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.collection_rules, Unset):
            collection_rules = []
            for collection_rules_item_data in self.collection_rules:
                collection_rules_item = collection_rules_item_data.to_dict()
                collection_rules.append(collection_rules_item)

        evidence_requirements: dict[str, Any] | Unset = UNSET
        if not isinstance(self.evidence_requirements, Unset):
            evidence_requirements = self.evidence_requirements.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if default_frequency is not UNSET:
            field_dict["default_frequency"] = default_frequency
        if required_evidence_types is not UNSET:
            field_dict["required_evidence_types"] = required_evidence_types
        if retention_days is not UNSET:
            field_dict["retention_days"] = retention_days
        if storage_backend is not UNSET:
            field_dict["storage_backend"] = storage_backend
        if encryption_required is not UNSET:
            field_dict["encryption_required"] = encryption_required
        if compress_evidence is not UNSET:
            field_dict["compress_evidence"] = compress_evidence
        if collection_rules is not UNSET:
            field_dict["collection_rules"] = collection_rules
        if evidence_requirements is not UNSET:
            field_dict["evidence_requirements"] = evidence_requirements

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.collection_rule_schema import CollectionRuleSchema
        from ..models.evidence_requirements_schema import EvidenceRequirementsSchema

        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        default_frequency = d.pop("default_frequency", UNSET)

        required_evidence_types = cast(list[str], d.pop("required_evidence_types", UNSET))

        retention_days = d.pop("retention_days", UNSET)

        storage_backend = d.pop("storage_backend", UNSET)

        encryption_required = d.pop("encryption_required", UNSET)

        compress_evidence = d.pop("compress_evidence", UNSET)

        _collection_rules = d.pop("collection_rules", UNSET)
        collection_rules: list[CollectionRuleSchema] | Unset = UNSET
        if _collection_rules is not UNSET:
            collection_rules = []
            for collection_rules_item_data in _collection_rules:
                collection_rules_item = CollectionRuleSchema.from_dict(collection_rules_item_data)

                collection_rules.append(collection_rules_item)

        _evidence_requirements = d.pop("evidence_requirements", UNSET)
        evidence_requirements: EvidenceRequirementsSchema | Unset
        if isinstance(_evidence_requirements, Unset):
            evidence_requirements = UNSET
        else:
            evidence_requirements = EvidenceRequirementsSchema.from_dict(_evidence_requirements)

        evidence_collection_policy_schema = cls(
            enabled=enabled,
            default_frequency=default_frequency,
            required_evidence_types=required_evidence_types,
            retention_days=retention_days,
            storage_backend=storage_backend,
            encryption_required=encryption_required,
            compress_evidence=compress_evidence,
            collection_rules=collection_rules,
            evidence_requirements=evidence_requirements,
        )

        evidence_collection_policy_schema.additional_properties = d
        return evidence_collection_policy_schema

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
