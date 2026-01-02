from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.onboarding_step_update_schema_step_data import OnboardingStepUpdateSchemaStepData


T = TypeVar("T", bound="OnboardingStepUpdateSchema")


@_attrs_define
class OnboardingStepUpdateSchema:
    """Generic schema for updating onboarding step progress.

    Attributes:
        step_data (OnboardingStepUpdateSchemaStepData | Unset):
        notes (None | str | Unset):
        skip_step (bool | Unset):  Default: False.
    """

    step_data: OnboardingStepUpdateSchemaStepData | Unset = UNSET
    notes: None | str | Unset = UNSET
    skip_step: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        step_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.step_data, Unset):
            step_data = self.step_data.to_dict()

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        skip_step = self.skip_step

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if step_data is not UNSET:
            field_dict["step_data"] = step_data
        if notes is not UNSET:
            field_dict["notes"] = notes
        if skip_step is not UNSET:
            field_dict["skip_step"] = skip_step

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.onboarding_step_update_schema_step_data import OnboardingStepUpdateSchemaStepData

        d = dict(src_dict)
        _step_data = d.pop("step_data", UNSET)
        step_data: OnboardingStepUpdateSchemaStepData | Unset
        if isinstance(_step_data, Unset):
            step_data = UNSET
        else:
            step_data = OnboardingStepUpdateSchemaStepData.from_dict(_step_data)

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        skip_step = d.pop("skip_step", UNSET)

        onboarding_step_update_schema = cls(
            step_data=step_data,
            notes=notes,
            skip_step=skip_step,
        )

        onboarding_step_update_schema.additional_properties = d
        return onboarding_step_update_schema

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
