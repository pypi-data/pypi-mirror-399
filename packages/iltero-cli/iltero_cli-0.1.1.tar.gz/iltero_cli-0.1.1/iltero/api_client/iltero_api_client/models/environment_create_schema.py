from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.compliance_policies_schema import CompliancePoliciesSchema
    from ..models.deployment_policies_schema import DeploymentPoliciesSchema
    from ..models.monitoring_policies_schema import MonitoringPoliciesSchema
    from ..models.repository_policies_schema import RepositoryPoliciesSchema
    from ..models.security_policies_schema import SecurityPoliciesSchema


T = TypeVar("T", bound="EnvironmentCreateSchema")


@_attrs_define
class EnvironmentCreateSchema:
    """Schema for environment creation.

    Attributes:
        name (str): Environment name
        key (None | str | Unset): URL-friendly identifier
        description (None | str | Unset): Environment description
        is_production (bool | Unset): Whether this is a production environment Default: False.
        is_default (bool | Unset): Whether this is the default environment Default: False.
        color (str | Unset): Color code for UI representation Default: '#9ca3af'.
        repo_ref_type (str | Unset): Type of Git reference for deployments Default: 'branch'.
        repo_ref_name (str | Unset): Git reference name for deployments Default: 'main'.
        git_environment (str | Unset): Git provider environment name Default: ''.
        show_in_dashboard (bool | Unset): Whether to show this environment in the dashboard Default: True.
        compliance_policies (CompliancePoliciesSchema | None | Unset): Compliance scanning and policy enforcement rules
        monitoring_policies (MonitoringPoliciesSchema | None | Unset): Monitoring, alerting, and drift detection
            policies
        repository_policies (None | RepositoryPoliciesSchema | Unset): Repository policies including branch protection
            rules
        security_policies (None | SecurityPoliciesSchema | Unset): Security and access control policies
        deployment_policies (DeploymentPoliciesSchema | None | Unset): Deployment automation and pipeline policies
    """

    name: str
    key: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    is_production: bool | Unset = False
    is_default: bool | Unset = False
    color: str | Unset = "#9ca3af"
    repo_ref_type: str | Unset = "branch"
    repo_ref_name: str | Unset = "main"
    git_environment: str | Unset = ""
    show_in_dashboard: bool | Unset = True
    compliance_policies: CompliancePoliciesSchema | None | Unset = UNSET
    monitoring_policies: MonitoringPoliciesSchema | None | Unset = UNSET
    repository_policies: None | RepositoryPoliciesSchema | Unset = UNSET
    security_policies: None | SecurityPoliciesSchema | Unset = UNSET
    deployment_policies: DeploymentPoliciesSchema | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.compliance_policies_schema import CompliancePoliciesSchema
        from ..models.deployment_policies_schema import DeploymentPoliciesSchema
        from ..models.monitoring_policies_schema import MonitoringPoliciesSchema
        from ..models.repository_policies_schema import RepositoryPoliciesSchema
        from ..models.security_policies_schema import SecurityPoliciesSchema

        name = self.name

        key: None | str | Unset
        if isinstance(self.key, Unset):
            key = UNSET
        else:
            key = self.key

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_production = self.is_production

        is_default = self.is_default

        color = self.color

        repo_ref_type = self.repo_ref_type

        repo_ref_name = self.repo_ref_name

        git_environment = self.git_environment

        show_in_dashboard = self.show_in_dashboard

        compliance_policies: dict[str, Any] | None | Unset
        if isinstance(self.compliance_policies, Unset):
            compliance_policies = UNSET
        elif isinstance(self.compliance_policies, CompliancePoliciesSchema):
            compliance_policies = self.compliance_policies.to_dict()
        else:
            compliance_policies = self.compliance_policies

        monitoring_policies: dict[str, Any] | None | Unset
        if isinstance(self.monitoring_policies, Unset):
            monitoring_policies = UNSET
        elif isinstance(self.monitoring_policies, MonitoringPoliciesSchema):
            monitoring_policies = self.monitoring_policies.to_dict()
        else:
            monitoring_policies = self.monitoring_policies

        repository_policies: dict[str, Any] | None | Unset
        if isinstance(self.repository_policies, Unset):
            repository_policies = UNSET
        elif isinstance(self.repository_policies, RepositoryPoliciesSchema):
            repository_policies = self.repository_policies.to_dict()
        else:
            repository_policies = self.repository_policies

        security_policies: dict[str, Any] | None | Unset
        if isinstance(self.security_policies, Unset):
            security_policies = UNSET
        elif isinstance(self.security_policies, SecurityPoliciesSchema):
            security_policies = self.security_policies.to_dict()
        else:
            security_policies = self.security_policies

        deployment_policies: dict[str, Any] | None | Unset
        if isinstance(self.deployment_policies, Unset):
            deployment_policies = UNSET
        elif isinstance(self.deployment_policies, DeploymentPoliciesSchema):
            deployment_policies = self.deployment_policies.to_dict()
        else:
            deployment_policies = self.deployment_policies

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if key is not UNSET:
            field_dict["key"] = key
        if description is not UNSET:
            field_dict["description"] = description
        if is_production is not UNSET:
            field_dict["is_production"] = is_production
        if is_default is not UNSET:
            field_dict["is_default"] = is_default
        if color is not UNSET:
            field_dict["color"] = color
        if repo_ref_type is not UNSET:
            field_dict["repo_ref_type"] = repo_ref_type
        if repo_ref_name is not UNSET:
            field_dict["repo_ref_name"] = repo_ref_name
        if git_environment is not UNSET:
            field_dict["git_environment"] = git_environment
        if show_in_dashboard is not UNSET:
            field_dict["show_in_dashboard"] = show_in_dashboard
        if compliance_policies is not UNSET:
            field_dict["compliance_policies"] = compliance_policies
        if monitoring_policies is not UNSET:
            field_dict["monitoring_policies"] = monitoring_policies
        if repository_policies is not UNSET:
            field_dict["repository_policies"] = repository_policies
        if security_policies is not UNSET:
            field_dict["security_policies"] = security_policies
        if deployment_policies is not UNSET:
            field_dict["deployment_policies"] = deployment_policies

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.compliance_policies_schema import CompliancePoliciesSchema
        from ..models.deployment_policies_schema import DeploymentPoliciesSchema
        from ..models.monitoring_policies_schema import MonitoringPoliciesSchema
        from ..models.repository_policies_schema import RepositoryPoliciesSchema
        from ..models.security_policies_schema import SecurityPoliciesSchema

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        key = _parse_key(d.pop("key", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        is_production = d.pop("is_production", UNSET)

        is_default = d.pop("is_default", UNSET)

        color = d.pop("color", UNSET)

        repo_ref_type = d.pop("repo_ref_type", UNSET)

        repo_ref_name = d.pop("repo_ref_name", UNSET)

        git_environment = d.pop("git_environment", UNSET)

        show_in_dashboard = d.pop("show_in_dashboard", UNSET)

        def _parse_compliance_policies(data: object) -> CompliancePoliciesSchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compliance_policies_type_0 = CompliancePoliciesSchema.from_dict(data)

                return compliance_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CompliancePoliciesSchema | None | Unset, data)

        compliance_policies = _parse_compliance_policies(d.pop("compliance_policies", UNSET))

        def _parse_monitoring_policies(data: object) -> MonitoringPoliciesSchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                monitoring_policies_type_0 = MonitoringPoliciesSchema.from_dict(data)

                return monitoring_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MonitoringPoliciesSchema | None | Unset, data)

        monitoring_policies = _parse_monitoring_policies(d.pop("monitoring_policies", UNSET))

        def _parse_repository_policies(data: object) -> None | RepositoryPoliciesSchema | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                repository_policies_type_0 = RepositoryPoliciesSchema.from_dict(data)

                return repository_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RepositoryPoliciesSchema | Unset, data)

        repository_policies = _parse_repository_policies(d.pop("repository_policies", UNSET))

        def _parse_security_policies(data: object) -> None | SecurityPoliciesSchema | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                security_policies_type_0 = SecurityPoliciesSchema.from_dict(data)

                return security_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SecurityPoliciesSchema | Unset, data)

        security_policies = _parse_security_policies(d.pop("security_policies", UNSET))

        def _parse_deployment_policies(data: object) -> DeploymentPoliciesSchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                deployment_policies_type_0 = DeploymentPoliciesSchema.from_dict(data)

                return deployment_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DeploymentPoliciesSchema | None | Unset, data)

        deployment_policies = _parse_deployment_policies(d.pop("deployment_policies", UNSET))

        environment_create_schema = cls(
            name=name,
            key=key,
            description=description,
            is_production=is_production,
            is_default=is_default,
            color=color,
            repo_ref_type=repo_ref_type,
            repo_ref_name=repo_ref_name,
            git_environment=git_environment,
            show_in_dashboard=show_in_dashboard,
            compliance_policies=compliance_policies,
            monitoring_policies=monitoring_policies,
            repository_policies=repository_policies,
            security_policies=security_policies,
            deployment_policies=deployment_policies,
        )

        environment_create_schema.additional_properties = d
        return environment_create_schema

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
