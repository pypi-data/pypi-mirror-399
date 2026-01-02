from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stack_additional_policies_schema_policy_parameters_type_0 import (
        StackAdditionalPoliciesSchemaPolicyParametersType0,
    )
    from ..models.stack_additional_policies_schema_workflow_parameters_type_0 import (
        StackAdditionalPoliciesSchemaWorkflowParametersType0,
    )


T = TypeVar("T", bound="StackAdditionalPoliciesSchema")


@_attrs_define
class StackAdditionalPoliciesSchema:
    """Schema for updating stack additional policies (Baseline + Additive model).

    Attributes:
        policy_sets (list[str] | None | Unset): Additional policy sets to ADD to environment baseline
        alert_channels (list[str] | None | Unset): Additional alert channels to ADD to environment baseline
        scan_types (list[str] | None | Unset): Additional scan types beyond environment baseline (e.g., ['sast',
            'dependency'])
        severity_threshold (None | str | Unset): Request stricter severity threshold (can only be stricter than
            baseline)
        policy_parameters (None | StackAdditionalPoliciesSchemaPolicyParametersType0 | Unset): Stack-specific policy
            parameters (e.g., allowed_regions, allowed_cidrs)
        workflow_parameters (None | StackAdditionalPoliciesSchemaWorkflowParametersType0 | Unset): Stack-specific
            workflow parameters within allowed bounds
    """

    policy_sets: list[str] | None | Unset = UNSET
    alert_channels: list[str] | None | Unset = UNSET
    scan_types: list[str] | None | Unset = UNSET
    severity_threshold: None | str | Unset = UNSET
    policy_parameters: None | StackAdditionalPoliciesSchemaPolicyParametersType0 | Unset = UNSET
    workflow_parameters: None | StackAdditionalPoliciesSchemaWorkflowParametersType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.stack_additional_policies_schema_policy_parameters_type_0 import (
            StackAdditionalPoliciesSchemaPolicyParametersType0,
        )
        from ..models.stack_additional_policies_schema_workflow_parameters_type_0 import (
            StackAdditionalPoliciesSchemaWorkflowParametersType0,
        )

        policy_sets: list[str] | None | Unset
        if isinstance(self.policy_sets, Unset):
            policy_sets = UNSET
        elif isinstance(self.policy_sets, list):
            policy_sets = self.policy_sets

        else:
            policy_sets = self.policy_sets

        alert_channels: list[str] | None | Unset
        if isinstance(self.alert_channels, Unset):
            alert_channels = UNSET
        elif isinstance(self.alert_channels, list):
            alert_channels = self.alert_channels

        else:
            alert_channels = self.alert_channels

        scan_types: list[str] | None | Unset
        if isinstance(self.scan_types, Unset):
            scan_types = UNSET
        elif isinstance(self.scan_types, list):
            scan_types = self.scan_types

        else:
            scan_types = self.scan_types

        severity_threshold: None | str | Unset
        if isinstance(self.severity_threshold, Unset):
            severity_threshold = UNSET
        else:
            severity_threshold = self.severity_threshold

        policy_parameters: dict[str, Any] | None | Unset
        if isinstance(self.policy_parameters, Unset):
            policy_parameters = UNSET
        elif isinstance(self.policy_parameters, StackAdditionalPoliciesSchemaPolicyParametersType0):
            policy_parameters = self.policy_parameters.to_dict()
        else:
            policy_parameters = self.policy_parameters

        workflow_parameters: dict[str, Any] | None | Unset
        if isinstance(self.workflow_parameters, Unset):
            workflow_parameters = UNSET
        elif isinstance(self.workflow_parameters, StackAdditionalPoliciesSchemaWorkflowParametersType0):
            workflow_parameters = self.workflow_parameters.to_dict()
        else:
            workflow_parameters = self.workflow_parameters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if policy_sets is not UNSET:
            field_dict["policy_sets"] = policy_sets
        if alert_channels is not UNSET:
            field_dict["alert_channels"] = alert_channels
        if scan_types is not UNSET:
            field_dict["scan_types"] = scan_types
        if severity_threshold is not UNSET:
            field_dict["severity_threshold"] = severity_threshold
        if policy_parameters is not UNSET:
            field_dict["policy_parameters"] = policy_parameters
        if workflow_parameters is not UNSET:
            field_dict["workflow_parameters"] = workflow_parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_additional_policies_schema_policy_parameters_type_0 import (
            StackAdditionalPoliciesSchemaPolicyParametersType0,
        )
        from ..models.stack_additional_policies_schema_workflow_parameters_type_0 import (
            StackAdditionalPoliciesSchemaWorkflowParametersType0,
        )

        d = dict(src_dict)

        def _parse_policy_sets(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                policy_sets_type_0 = cast(list[str], data)

                return policy_sets_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        policy_sets = _parse_policy_sets(d.pop("policy_sets", UNSET))

        def _parse_alert_channels(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                alert_channels_type_0 = cast(list[str], data)

                return alert_channels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        alert_channels = _parse_alert_channels(d.pop("alert_channels", UNSET))

        def _parse_scan_types(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                scan_types_type_0 = cast(list[str], data)

                return scan_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        scan_types = _parse_scan_types(d.pop("scan_types", UNSET))

        def _parse_severity_threshold(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        severity_threshold = _parse_severity_threshold(d.pop("severity_threshold", UNSET))

        def _parse_policy_parameters(data: object) -> None | StackAdditionalPoliciesSchemaPolicyParametersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                policy_parameters_type_0 = StackAdditionalPoliciesSchemaPolicyParametersType0.from_dict(data)

                return policy_parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackAdditionalPoliciesSchemaPolicyParametersType0 | Unset, data)

        policy_parameters = _parse_policy_parameters(d.pop("policy_parameters", UNSET))

        def _parse_workflow_parameters(
            data: object,
        ) -> None | StackAdditionalPoliciesSchemaWorkflowParametersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                workflow_parameters_type_0 = StackAdditionalPoliciesSchemaWorkflowParametersType0.from_dict(data)

                return workflow_parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackAdditionalPoliciesSchemaWorkflowParametersType0 | Unset, data)

        workflow_parameters = _parse_workflow_parameters(d.pop("workflow_parameters", UNSET))

        stack_additional_policies_schema = cls(
            policy_sets=policy_sets,
            alert_channels=alert_channels,
            scan_types=scan_types,
            severity_threshold=severity_threshold,
            policy_parameters=policy_parameters,
            workflow_parameters=workflow_parameters,
        )

        stack_additional_policies_schema.additional_properties = d
        return stack_additional_policies_schema

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
