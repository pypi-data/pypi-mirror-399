from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.approval_policy_schema import ApprovalPolicySchema


T = TypeVar("T", bound="DeploymentPoliciesSchema")


@_attrs_define
class DeploymentPoliciesSchema:
    """Schema for deployment policies API endpoints.

    Attributes:
        require_approval (bool | Unset): Require approval before deployment Default: False.
        approval_policy (ApprovalPolicySchema | None | Unset): Detailed approval policy configuration
        auto_apply_on_merge (bool | Unset): Auto-apply changes on merge Default: False.
        terraform_version (str | Unset): Terraform version to use Default: 'latest'.
        max_parallel_deployments (int | Unset): Max parallel deployments Default: 5.
        deployment_timeout (int | Unset): Deployment timeout in seconds Default: 3600.
        allowed_resource_types (list[str] | Unset): Allowed Terraform resources
        blocked_resource_types (list[str] | Unset): Blocked Terraform resources
        cost_threshold (float | None | Unset): Max cost increase per deployment
    """

    require_approval: bool | Unset = False
    approval_policy: ApprovalPolicySchema | None | Unset = UNSET
    auto_apply_on_merge: bool | Unset = False
    terraform_version: str | Unset = "latest"
    max_parallel_deployments: int | Unset = 5
    deployment_timeout: int | Unset = 3600
    allowed_resource_types: list[str] | Unset = UNSET
    blocked_resource_types: list[str] | Unset = UNSET
    cost_threshold: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.approval_policy_schema import ApprovalPolicySchema

        require_approval = self.require_approval

        approval_policy: dict[str, Any] | None | Unset
        if isinstance(self.approval_policy, Unset):
            approval_policy = UNSET
        elif isinstance(self.approval_policy, ApprovalPolicySchema):
            approval_policy = self.approval_policy.to_dict()
        else:
            approval_policy = self.approval_policy

        auto_apply_on_merge = self.auto_apply_on_merge

        terraform_version = self.terraform_version

        max_parallel_deployments = self.max_parallel_deployments

        deployment_timeout = self.deployment_timeout

        allowed_resource_types: list[str] | Unset = UNSET
        if not isinstance(self.allowed_resource_types, Unset):
            allowed_resource_types = self.allowed_resource_types

        blocked_resource_types: list[str] | Unset = UNSET
        if not isinstance(self.blocked_resource_types, Unset):
            blocked_resource_types = self.blocked_resource_types

        cost_threshold: float | None | Unset
        if isinstance(self.cost_threshold, Unset):
            cost_threshold = UNSET
        else:
            cost_threshold = self.cost_threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if require_approval is not UNSET:
            field_dict["require_approval"] = require_approval
        if approval_policy is not UNSET:
            field_dict["approval_policy"] = approval_policy
        if auto_apply_on_merge is not UNSET:
            field_dict["auto_apply_on_merge"] = auto_apply_on_merge
        if terraform_version is not UNSET:
            field_dict["terraform_version"] = terraform_version
        if max_parallel_deployments is not UNSET:
            field_dict["max_parallel_deployments"] = max_parallel_deployments
        if deployment_timeout is not UNSET:
            field_dict["deployment_timeout"] = deployment_timeout
        if allowed_resource_types is not UNSET:
            field_dict["allowed_resource_types"] = allowed_resource_types
        if blocked_resource_types is not UNSET:
            field_dict["blocked_resource_types"] = blocked_resource_types
        if cost_threshold is not UNSET:
            field_dict["cost_threshold"] = cost_threshold

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.approval_policy_schema import ApprovalPolicySchema

        d = dict(src_dict)
        require_approval = d.pop("require_approval", UNSET)

        def _parse_approval_policy(data: object) -> ApprovalPolicySchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                approval_policy_type_0 = ApprovalPolicySchema.from_dict(data)

                return approval_policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ApprovalPolicySchema | None | Unset, data)

        approval_policy = _parse_approval_policy(d.pop("approval_policy", UNSET))

        auto_apply_on_merge = d.pop("auto_apply_on_merge", UNSET)

        terraform_version = d.pop("terraform_version", UNSET)

        max_parallel_deployments = d.pop("max_parallel_deployments", UNSET)

        deployment_timeout = d.pop("deployment_timeout", UNSET)

        allowed_resource_types = cast(list[str], d.pop("allowed_resource_types", UNSET))

        blocked_resource_types = cast(list[str], d.pop("blocked_resource_types", UNSET))

        def _parse_cost_threshold(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cost_threshold = _parse_cost_threshold(d.pop("cost_threshold", UNSET))

        deployment_policies_schema = cls(
            require_approval=require_approval,
            approval_policy=approval_policy,
            auto_apply_on_merge=auto_apply_on_merge,
            terraform_version=terraform_version,
            max_parallel_deployments=max_parallel_deployments,
            deployment_timeout=deployment_timeout,
            allowed_resource_types=allowed_resource_types,
            blocked_resource_types=blocked_resource_types,
            cost_threshold=cost_threshold,
        )

        deployment_policies_schema.additional_properties = d
        return deployment_policies_schema

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
