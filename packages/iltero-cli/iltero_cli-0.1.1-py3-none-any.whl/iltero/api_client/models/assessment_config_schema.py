from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.assessment_config_schema_metadata_type_0 import AssessmentConfigSchemaMetadataType0


T = TypeVar("T", bound="AssessmentConfigSchema")


@_attrs_define
class AssessmentConfigSchema:
    """Request schema for assessment configuration.

    Attributes:
        include_validation (bool | Unset): Include validation in assessment Default: True.
        include_evidence (bool | Unset): Include evidence collection Default: True.
        include_monitoring (bool | Unset): Include monitoring setup Default: True.
        frameworks (list[str] | None | Unset): Specific frameworks to assess
        validation_mode (str | Unset): Validation mode: FULL, QUICK, or CUSTOM Default: 'FULL'.
        evidence_types (list[str] | None | Unset): Types of evidence to collect
        auto_remediate (bool | Unset): Enable auto-remediation for violations Default: False.
        notification_channels (list[str] | None | Unset): Notification channels for results
        metadata (AssessmentConfigSchemaMetadataType0 | None | Unset): Additional metadata for assessment
    """

    include_validation: bool | Unset = True
    include_evidence: bool | Unset = True
    include_monitoring: bool | Unset = True
    frameworks: list[str] | None | Unset = UNSET
    validation_mode: str | Unset = "FULL"
    evidence_types: list[str] | None | Unset = UNSET
    auto_remediate: bool | Unset = False
    notification_channels: list[str] | None | Unset = UNSET
    metadata: AssessmentConfigSchemaMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.assessment_config_schema_metadata_type_0 import AssessmentConfigSchemaMetadataType0

        include_validation = self.include_validation

        include_evidence = self.include_evidence

        include_monitoring = self.include_monitoring

        frameworks: list[str] | None | Unset
        if isinstance(self.frameworks, Unset):
            frameworks = UNSET
        elif isinstance(self.frameworks, list):
            frameworks = self.frameworks

        else:
            frameworks = self.frameworks

        validation_mode = self.validation_mode

        evidence_types: list[str] | None | Unset
        if isinstance(self.evidence_types, Unset):
            evidence_types = UNSET
        elif isinstance(self.evidence_types, list):
            evidence_types = self.evidence_types

        else:
            evidence_types = self.evidence_types

        auto_remediate = self.auto_remediate

        notification_channels: list[str] | None | Unset
        if isinstance(self.notification_channels, Unset):
            notification_channels = UNSET
        elif isinstance(self.notification_channels, list):
            notification_channels = self.notification_channels

        else:
            notification_channels = self.notification_channels

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, AssessmentConfigSchemaMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if include_validation is not UNSET:
            field_dict["include_validation"] = include_validation
        if include_evidence is not UNSET:
            field_dict["include_evidence"] = include_evidence
        if include_monitoring is not UNSET:
            field_dict["include_monitoring"] = include_monitoring
        if frameworks is not UNSET:
            field_dict["frameworks"] = frameworks
        if validation_mode is not UNSET:
            field_dict["validation_mode"] = validation_mode
        if evidence_types is not UNSET:
            field_dict["evidence_types"] = evidence_types
        if auto_remediate is not UNSET:
            field_dict["auto_remediate"] = auto_remediate
        if notification_channels is not UNSET:
            field_dict["notification_channels"] = notification_channels
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.assessment_config_schema_metadata_type_0 import AssessmentConfigSchemaMetadataType0

        d = dict(src_dict)
        include_validation = d.pop("include_validation", UNSET)

        include_evidence = d.pop("include_evidence", UNSET)

        include_monitoring = d.pop("include_monitoring", UNSET)

        def _parse_frameworks(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                frameworks_type_0 = cast(list[str], data)

                return frameworks_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        frameworks = _parse_frameworks(d.pop("frameworks", UNSET))

        validation_mode = d.pop("validation_mode", UNSET)

        def _parse_evidence_types(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                evidence_types_type_0 = cast(list[str], data)

                return evidence_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        evidence_types = _parse_evidence_types(d.pop("evidence_types", UNSET))

        auto_remediate = d.pop("auto_remediate", UNSET)

        def _parse_notification_channels(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                notification_channels_type_0 = cast(list[str], data)

                return notification_channels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        notification_channels = _parse_notification_channels(d.pop("notification_channels", UNSET))

        def _parse_metadata(data: object) -> AssessmentConfigSchemaMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = AssessmentConfigSchemaMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AssessmentConfigSchemaMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        assessment_config_schema = cls(
            include_validation=include_validation,
            include_evidence=include_evidence,
            include_monitoring=include_monitoring,
            frameworks=frameworks,
            validation_mode=validation_mode,
            evidence_types=evidence_types,
            auto_remediate=auto_remediate,
            notification_channels=notification_channels,
            metadata=metadata,
        )

        assessment_config_schema.additional_properties = d
        return assessment_config_schema

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
