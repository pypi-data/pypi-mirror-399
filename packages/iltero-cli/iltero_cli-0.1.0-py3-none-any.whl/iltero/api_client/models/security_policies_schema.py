from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SecurityPoliciesSchema")


@_attrs_define
class SecurityPoliciesSchema:
    """Schema for security policies API endpoints.

    Attributes:
        enforce_signed_commits (bool | Unset): Require signed commits Default: False.
        vulnerability_scanning_enabled (bool | Unset): Enable vulnerability scanning Default: True.
        secret_scanning_enabled (bool | Unset): Enable secret scanning Default: True.
        dependency_scanning_enabled (bool | Unset): Enable dependency scanning Default: True.
        security_severity_threshold (str | Unset): Minimum severity to block deployment Default: 'high'.
        allowed_licenses (list[str] | Unset): Allowed software licenses
    """

    enforce_signed_commits: bool | Unset = False
    vulnerability_scanning_enabled: bool | Unset = True
    secret_scanning_enabled: bool | Unset = True
    dependency_scanning_enabled: bool | Unset = True
    security_severity_threshold: str | Unset = "high"
    allowed_licenses: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enforce_signed_commits = self.enforce_signed_commits

        vulnerability_scanning_enabled = self.vulnerability_scanning_enabled

        secret_scanning_enabled = self.secret_scanning_enabled

        dependency_scanning_enabled = self.dependency_scanning_enabled

        security_severity_threshold = self.security_severity_threshold

        allowed_licenses: list[str] | Unset = UNSET
        if not isinstance(self.allowed_licenses, Unset):
            allowed_licenses = self.allowed_licenses

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enforce_signed_commits is not UNSET:
            field_dict["enforce_signed_commits"] = enforce_signed_commits
        if vulnerability_scanning_enabled is not UNSET:
            field_dict["vulnerability_scanning_enabled"] = vulnerability_scanning_enabled
        if secret_scanning_enabled is not UNSET:
            field_dict["secret_scanning_enabled"] = secret_scanning_enabled
        if dependency_scanning_enabled is not UNSET:
            field_dict["dependency_scanning_enabled"] = dependency_scanning_enabled
        if security_severity_threshold is not UNSET:
            field_dict["security_severity_threshold"] = security_severity_threshold
        if allowed_licenses is not UNSET:
            field_dict["allowed_licenses"] = allowed_licenses

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enforce_signed_commits = d.pop("enforce_signed_commits", UNSET)

        vulnerability_scanning_enabled = d.pop("vulnerability_scanning_enabled", UNSET)

        secret_scanning_enabled = d.pop("secret_scanning_enabled", UNSET)

        dependency_scanning_enabled = d.pop("dependency_scanning_enabled", UNSET)

        security_severity_threshold = d.pop("security_severity_threshold", UNSET)

        allowed_licenses = cast(list[str], d.pop("allowed_licenses", UNSET))

        security_policies_schema = cls(
            enforce_signed_commits=enforce_signed_commits,
            vulnerability_scanning_enabled=vulnerability_scanning_enabled,
            secret_scanning_enabled=secret_scanning_enabled,
            dependency_scanning_enabled=dependency_scanning_enabled,
            security_severity_threshold=security_severity_threshold,
            allowed_licenses=allowed_licenses,
        )

        security_policies_schema.additional_properties = d
        return security_policies_schema

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
