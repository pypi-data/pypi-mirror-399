from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OnboardingReviewSchema")


@_attrs_define
class OnboardingReviewSchema:
    """Schema for onboarding review step.

    Attributes:
        confirm_setup (bool): Confirm the setup is correct
        enable_monitoring (bool | Unset):  Default: True.
        enable_notifications (bool | Unset):  Default: True.
        subscribe_to_updates (bool | Unset):  Default: True.
        feedback (None | str | Unset):
    """

    confirm_setup: bool
    enable_monitoring: bool | Unset = True
    enable_notifications: bool | Unset = True
    subscribe_to_updates: bool | Unset = True
    feedback: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        confirm_setup = self.confirm_setup

        enable_monitoring = self.enable_monitoring

        enable_notifications = self.enable_notifications

        subscribe_to_updates = self.subscribe_to_updates

        feedback: None | str | Unset
        if isinstance(self.feedback, Unset):
            feedback = UNSET
        else:
            feedback = self.feedback

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "confirm_setup": confirm_setup,
            }
        )
        if enable_monitoring is not UNSET:
            field_dict["enable_monitoring"] = enable_monitoring
        if enable_notifications is not UNSET:
            field_dict["enable_notifications"] = enable_notifications
        if subscribe_to_updates is not UNSET:
            field_dict["subscribe_to_updates"] = subscribe_to_updates
        if feedback is not UNSET:
            field_dict["feedback"] = feedback

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        confirm_setup = d.pop("confirm_setup")

        enable_monitoring = d.pop("enable_monitoring", UNSET)

        enable_notifications = d.pop("enable_notifications", UNSET)

        subscribe_to_updates = d.pop("subscribe_to_updates", UNSET)

        def _parse_feedback(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        feedback = _parse_feedback(d.pop("feedback", UNSET))

        onboarding_review_schema = cls(
            confirm_setup=confirm_setup,
            enable_monitoring=enable_monitoring,
            enable_notifications=enable_notifications,
            subscribe_to_updates=subscribe_to_updates,
            feedback=feedback,
        )

        onboarding_review_schema.additional_properties = d
        return onboarding_review_schema

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
