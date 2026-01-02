from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.policy_validation_request_schema_compliance_policies_type_0 import (
        PolicyValidationRequestSchemaCompliancePoliciesType0,
    )
    from ..models.policy_validation_request_schema_deployment_policies_type_0 import (
        PolicyValidationRequestSchemaDeploymentPoliciesType0,
    )
    from ..models.policy_validation_request_schema_monitoring_policies_type_0 import (
        PolicyValidationRequestSchemaMonitoringPoliciesType0,
    )
    from ..models.policy_validation_request_schema_repository_policies_type_0 import (
        PolicyValidationRequestSchemaRepositoryPoliciesType0,
    )
    from ..models.policy_validation_request_schema_security_policies_type_0 import (
        PolicyValidationRequestSchemaSecurityPoliciesType0,
    )


T = TypeVar("T", bound="PolicyValidationRequestSchema")


@_attrs_define
class PolicyValidationRequestSchema:
    """Request schema for policy validation.

    Attributes:
        compliance_policies (None | PolicyValidationRequestSchemaCompliancePoliciesType0 | Unset): Compliance policies
            to validate
        monitoring_policies (None | PolicyValidationRequestSchemaMonitoringPoliciesType0 | Unset): Monitoring policies
            to validate
        repository_policies (None | PolicyValidationRequestSchemaRepositoryPoliciesType0 | Unset): Repository policies
            to validate
        security_policies (None | PolicyValidationRequestSchemaSecurityPoliciesType0 | Unset): Security policies to
            validate
        deployment_policies (None | PolicyValidationRequestSchemaDeploymentPoliciesType0 | Unset): Deployment policies
            to validate
    """

    compliance_policies: None | PolicyValidationRequestSchemaCompliancePoliciesType0 | Unset = UNSET
    monitoring_policies: None | PolicyValidationRequestSchemaMonitoringPoliciesType0 | Unset = UNSET
    repository_policies: None | PolicyValidationRequestSchemaRepositoryPoliciesType0 | Unset = UNSET
    security_policies: None | PolicyValidationRequestSchemaSecurityPoliciesType0 | Unset = UNSET
    deployment_policies: None | PolicyValidationRequestSchemaDeploymentPoliciesType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.policy_validation_request_schema_compliance_policies_type_0 import (
            PolicyValidationRequestSchemaCompliancePoliciesType0,
        )
        from ..models.policy_validation_request_schema_deployment_policies_type_0 import (
            PolicyValidationRequestSchemaDeploymentPoliciesType0,
        )
        from ..models.policy_validation_request_schema_monitoring_policies_type_0 import (
            PolicyValidationRequestSchemaMonitoringPoliciesType0,
        )
        from ..models.policy_validation_request_schema_repository_policies_type_0 import (
            PolicyValidationRequestSchemaRepositoryPoliciesType0,
        )
        from ..models.policy_validation_request_schema_security_policies_type_0 import (
            PolicyValidationRequestSchemaSecurityPoliciesType0,
        )

        compliance_policies: dict[str, Any] | None | Unset
        if isinstance(self.compliance_policies, Unset):
            compliance_policies = UNSET
        elif isinstance(self.compliance_policies, PolicyValidationRequestSchemaCompliancePoliciesType0):
            compliance_policies = self.compliance_policies.to_dict()
        else:
            compliance_policies = self.compliance_policies

        monitoring_policies: dict[str, Any] | None | Unset
        if isinstance(self.monitoring_policies, Unset):
            monitoring_policies = UNSET
        elif isinstance(self.monitoring_policies, PolicyValidationRequestSchemaMonitoringPoliciesType0):
            monitoring_policies = self.monitoring_policies.to_dict()
        else:
            monitoring_policies = self.monitoring_policies

        repository_policies: dict[str, Any] | None | Unset
        if isinstance(self.repository_policies, Unset):
            repository_policies = UNSET
        elif isinstance(self.repository_policies, PolicyValidationRequestSchemaRepositoryPoliciesType0):
            repository_policies = self.repository_policies.to_dict()
        else:
            repository_policies = self.repository_policies

        security_policies: dict[str, Any] | None | Unset
        if isinstance(self.security_policies, Unset):
            security_policies = UNSET
        elif isinstance(self.security_policies, PolicyValidationRequestSchemaSecurityPoliciesType0):
            security_policies = self.security_policies.to_dict()
        else:
            security_policies = self.security_policies

        deployment_policies: dict[str, Any] | None | Unset
        if isinstance(self.deployment_policies, Unset):
            deployment_policies = UNSET
        elif isinstance(self.deployment_policies, PolicyValidationRequestSchemaDeploymentPoliciesType0):
            deployment_policies = self.deployment_policies.to_dict()
        else:
            deployment_policies = self.deployment_policies

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        from ..models.policy_validation_request_schema_compliance_policies_type_0 import (
            PolicyValidationRequestSchemaCompliancePoliciesType0,
        )
        from ..models.policy_validation_request_schema_deployment_policies_type_0 import (
            PolicyValidationRequestSchemaDeploymentPoliciesType0,
        )
        from ..models.policy_validation_request_schema_monitoring_policies_type_0 import (
            PolicyValidationRequestSchemaMonitoringPoliciesType0,
        )
        from ..models.policy_validation_request_schema_repository_policies_type_0 import (
            PolicyValidationRequestSchemaRepositoryPoliciesType0,
        )
        from ..models.policy_validation_request_schema_security_policies_type_0 import (
            PolicyValidationRequestSchemaSecurityPoliciesType0,
        )

        d = dict(src_dict)

        def _parse_compliance_policies(
            data: object,
        ) -> None | PolicyValidationRequestSchemaCompliancePoliciesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                compliance_policies_type_0 = PolicyValidationRequestSchemaCompliancePoliciesType0.from_dict(data)

                return compliance_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PolicyValidationRequestSchemaCompliancePoliciesType0 | Unset, data)

        compliance_policies = _parse_compliance_policies(d.pop("compliance_policies", UNSET))

        def _parse_monitoring_policies(
            data: object,
        ) -> None | PolicyValidationRequestSchemaMonitoringPoliciesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                monitoring_policies_type_0 = PolicyValidationRequestSchemaMonitoringPoliciesType0.from_dict(data)

                return monitoring_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PolicyValidationRequestSchemaMonitoringPoliciesType0 | Unset, data)

        monitoring_policies = _parse_monitoring_policies(d.pop("monitoring_policies", UNSET))

        def _parse_repository_policies(
            data: object,
        ) -> None | PolicyValidationRequestSchemaRepositoryPoliciesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                repository_policies_type_0 = PolicyValidationRequestSchemaRepositoryPoliciesType0.from_dict(data)

                return repository_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PolicyValidationRequestSchemaRepositoryPoliciesType0 | Unset, data)

        repository_policies = _parse_repository_policies(d.pop("repository_policies", UNSET))

        def _parse_security_policies(data: object) -> None | PolicyValidationRequestSchemaSecurityPoliciesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                security_policies_type_0 = PolicyValidationRequestSchemaSecurityPoliciesType0.from_dict(data)

                return security_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PolicyValidationRequestSchemaSecurityPoliciesType0 | Unset, data)

        security_policies = _parse_security_policies(d.pop("security_policies", UNSET))

        def _parse_deployment_policies(
            data: object,
        ) -> None | PolicyValidationRequestSchemaDeploymentPoliciesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                deployment_policies_type_0 = PolicyValidationRequestSchemaDeploymentPoliciesType0.from_dict(data)

                return deployment_policies_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PolicyValidationRequestSchemaDeploymentPoliciesType0 | Unset, data)

        deployment_policies = _parse_deployment_policies(d.pop("deployment_policies", UNSET))

        policy_validation_request_schema = cls(
            compliance_policies=compliance_policies,
            monitoring_policies=monitoring_policies,
            repository_policies=repository_policies,
            security_policies=security_policies,
            deployment_policies=deployment_policies,
        )

        policy_validation_request_schema.additional_properties = d
        return policy_validation_request_schema

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
