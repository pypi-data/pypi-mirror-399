from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OnboardingRegistrationSchema")


@_attrs_define
class OnboardingRegistrationSchema:
    """Schema for user registration with organization creation intent.

    Attributes:
        email (str):
        name (str):
        password (str):
        confirm_password (str): Password confirmation
        organization_name (str): Name of the organization to create
        invite_token (None | str | Unset):
        industry (None | str | Unset): Industry classification for intelligent defaults
        compliance_framework (None | str | Unset): Primary compliance framework (e.g., 'hipaa', 'sox', 'soc2')
    """

    email: str
    name: str
    password: str
    confirm_password: str
    organization_name: str
    invite_token: None | str | Unset = UNSET
    industry: None | str | Unset = UNSET
    compliance_framework: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        email = self.email

        name = self.name

        password = self.password

        confirm_password = self.confirm_password

        organization_name = self.organization_name

        invite_token: None | str | Unset
        if isinstance(self.invite_token, Unset):
            invite_token = UNSET
        else:
            invite_token = self.invite_token

        industry: None | str | Unset
        if isinstance(self.industry, Unset):
            industry = UNSET
        else:
            industry = self.industry

        compliance_framework: None | str | Unset
        if isinstance(self.compliance_framework, Unset):
            compliance_framework = UNSET
        else:
            compliance_framework = self.compliance_framework

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "email": email,
                "name": name,
                "password": password,
                "confirm_password": confirm_password,
                "organization_name": organization_name,
            }
        )
        if invite_token is not UNSET:
            field_dict["invite_token"] = invite_token
        if industry is not UNSET:
            field_dict["industry"] = industry
        if compliance_framework is not UNSET:
            field_dict["compliance_framework"] = compliance_framework

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        email = d.pop("email")

        name = d.pop("name")

        password = d.pop("password")

        confirm_password = d.pop("confirm_password")

        organization_name = d.pop("organization_name")

        def _parse_invite_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        invite_token = _parse_invite_token(d.pop("invite_token", UNSET))

        def _parse_industry(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        industry = _parse_industry(d.pop("industry", UNSET))

        def _parse_compliance_framework(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        compliance_framework = _parse_compliance_framework(d.pop("compliance_framework", UNSET))

        onboarding_registration_schema = cls(
            email=email,
            name=name,
            password=password,
            confirm_password=confirm_password,
            organization_name=organization_name,
            invite_token=invite_token,
            industry=industry,
            compliance_framework=compliance_framework,
        )

        onboarding_registration_schema.additional_properties = d
        return onboarding_registration_schema

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
