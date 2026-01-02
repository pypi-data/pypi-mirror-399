from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RemediationPlanRequestSchema")


@_attrs_define
class RemediationPlanRequestSchema:
    """Request schema for creating remediation plans.

    Attributes:
        stack_id (str): Stack identifier
        validation_id (str): Validation ID with violations
        workspace_id (None | str | Unset): Workspace identifier
        violations_to_remediate (list[str] | None | Unset): Specific violation IDs to remediate
        remediation_strategy (str | Unset): Remediation strategy Default: 'manual'.
        priority_order (str | Unset): Priority order for remediation Default: 'severity'.
        auto_apply (bool | Unset): Whether to automatically apply remediation Default: False.
        notification_on_completion (bool | Unset): Send notification when remediation completes Default: True.
    """

    stack_id: str
    validation_id: str
    workspace_id: None | str | Unset = UNSET
    violations_to_remediate: list[str] | None | Unset = UNSET
    remediation_strategy: str | Unset = "manual"
    priority_order: str | Unset = "severity"
    auto_apply: bool | Unset = False
    notification_on_completion: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        validation_id = self.validation_id

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        violations_to_remediate: list[str] | None | Unset
        if isinstance(self.violations_to_remediate, Unset):
            violations_to_remediate = UNSET
        elif isinstance(self.violations_to_remediate, list):
            violations_to_remediate = self.violations_to_remediate

        else:
            violations_to_remediate = self.violations_to_remediate

        remediation_strategy = self.remediation_strategy

        priority_order = self.priority_order

        auto_apply = self.auto_apply

        notification_on_completion = self.notification_on_completion

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "validation_id": validation_id,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if violations_to_remediate is not UNSET:
            field_dict["violations_to_remediate"] = violations_to_remediate
        if remediation_strategy is not UNSET:
            field_dict["remediation_strategy"] = remediation_strategy
        if priority_order is not UNSET:
            field_dict["priority_order"] = priority_order
        if auto_apply is not UNSET:
            field_dict["auto_apply"] = auto_apply
        if notification_on_completion is not UNSET:
            field_dict["notification_on_completion"] = notification_on_completion

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        validation_id = d.pop("validation_id")

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        def _parse_violations_to_remediate(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                violations_to_remediate_type_0 = cast(list[str], data)

                return violations_to_remediate_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        violations_to_remediate = _parse_violations_to_remediate(d.pop("violations_to_remediate", UNSET))

        remediation_strategy = d.pop("remediation_strategy", UNSET)

        priority_order = d.pop("priority_order", UNSET)

        auto_apply = d.pop("auto_apply", UNSET)

        notification_on_completion = d.pop("notification_on_completion", UNSET)

        remediation_plan_request_schema = cls(
            stack_id=stack_id,
            validation_id=validation_id,
            workspace_id=workspace_id,
            violations_to_remediate=violations_to_remediate,
            remediation_strategy=remediation_strategy,
            priority_order=priority_order,
            auto_apply=auto_apply,
            notification_on_completion=notification_on_completion,
        )

        remediation_plan_request_schema.additional_properties = d
        return remediation_plan_request_schema

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
