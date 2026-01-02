from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PolicyOverrideRequestSchema")


@_attrs_define
class PolicyOverrideRequestSchema:
    """Request schema for policy override.

    Attributes:
        stack_id (str): Stack identifier
        policy_rule (str): Policy rule to override
        override_reason (str): Reason for override
        workspace_id (None | str | Unset): Workspace identifier
        risk_acceptance (None | str | Unset): Risk acceptance statement
        compensating_controls (list[str] | None | Unset): Compensating controls in place
        expiration_days (int | None | Unset): Days until override expires
        approval_required (bool | Unset): Whether approval is required Default: True.
        notification_on_expiry (bool | Unset): Send notification before expiry Default: True.
    """

    stack_id: str
    policy_rule: str
    override_reason: str
    workspace_id: None | str | Unset = UNSET
    risk_acceptance: None | str | Unset = UNSET
    compensating_controls: list[str] | None | Unset = UNSET
    expiration_days: int | None | Unset = UNSET
    approval_required: bool | Unset = True
    notification_on_expiry: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        policy_rule = self.policy_rule

        override_reason = self.override_reason

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        risk_acceptance: None | str | Unset
        if isinstance(self.risk_acceptance, Unset):
            risk_acceptance = UNSET
        else:
            risk_acceptance = self.risk_acceptance

        compensating_controls: list[str] | None | Unset
        if isinstance(self.compensating_controls, Unset):
            compensating_controls = UNSET
        elif isinstance(self.compensating_controls, list):
            compensating_controls = self.compensating_controls

        else:
            compensating_controls = self.compensating_controls

        expiration_days: int | None | Unset
        if isinstance(self.expiration_days, Unset):
            expiration_days = UNSET
        else:
            expiration_days = self.expiration_days

        approval_required = self.approval_required

        notification_on_expiry = self.notification_on_expiry

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "policy_rule": policy_rule,
                "override_reason": override_reason,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if risk_acceptance is not UNSET:
            field_dict["risk_acceptance"] = risk_acceptance
        if compensating_controls is not UNSET:
            field_dict["compensating_controls"] = compensating_controls
        if expiration_days is not UNSET:
            field_dict["expiration_days"] = expiration_days
        if approval_required is not UNSET:
            field_dict["approval_required"] = approval_required
        if notification_on_expiry is not UNSET:
            field_dict["notification_on_expiry"] = notification_on_expiry

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        policy_rule = d.pop("policy_rule")

        override_reason = d.pop("override_reason")

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        def _parse_risk_acceptance(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        risk_acceptance = _parse_risk_acceptance(d.pop("risk_acceptance", UNSET))

        def _parse_compensating_controls(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                compensating_controls_type_0 = cast(list[str], data)

                return compensating_controls_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        compensating_controls = _parse_compensating_controls(d.pop("compensating_controls", UNSET))

        def _parse_expiration_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        expiration_days = _parse_expiration_days(d.pop("expiration_days", UNSET))

        approval_required = d.pop("approval_required", UNSET)

        notification_on_expiry = d.pop("notification_on_expiry", UNSET)

        policy_override_request_schema = cls(
            stack_id=stack_id,
            policy_rule=policy_rule,
            override_reason=override_reason,
            workspace_id=workspace_id,
            risk_acceptance=risk_acceptance,
            compensating_controls=compensating_controls,
            expiration_days=expiration_days,
            approval_required=approval_required,
            notification_on_expiry=notification_on_expiry,
        )

        policy_override_request_schema.additional_properties = d
        return policy_override_request_schema

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
