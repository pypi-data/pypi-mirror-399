from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.post_deployment_validation_request_schema_deployment_results import (
        PostDeploymentValidationRequestSchemaDeploymentResults,
    )


T = TypeVar("T", bound="PostDeploymentValidationRequestSchema")


@_attrs_define
class PostDeploymentValidationRequestSchema:
    """Request schema for post-deployment compliance validation.

    Attributes:
        stack_id (str): Stack identifier
        deployment_results (PostDeploymentValidationRequestSchemaDeploymentResults): Deployment results including
            terraform state
        workspace_id (None | str | Unset): Workspace identifier
        deployment_id (None | str | Unset): Deployment ID for context
        validate_runtime (bool | Unset): Whether to validate runtime configuration Default: True.
        collect_evidence (bool | Unset): Whether to collect compliance evidence Default: True.
        setup_monitoring (bool | Unset): Whether to setup continuous monitoring Default: True.
    """

    stack_id: str
    deployment_results: PostDeploymentValidationRequestSchemaDeploymentResults
    workspace_id: None | str | Unset = UNSET
    deployment_id: None | str | Unset = UNSET
    validate_runtime: bool | Unset = True
    collect_evidence: bool | Unset = True
    setup_monitoring: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        stack_id = self.stack_id

        deployment_results = self.deployment_results.to_dict()

        workspace_id: None | str | Unset
        if isinstance(self.workspace_id, Unset):
            workspace_id = UNSET
        else:
            workspace_id = self.workspace_id

        deployment_id: None | str | Unset
        if isinstance(self.deployment_id, Unset):
            deployment_id = UNSET
        else:
            deployment_id = self.deployment_id

        validate_runtime = self.validate_runtime

        collect_evidence = self.collect_evidence

        setup_monitoring = self.setup_monitoring

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "stack_id": stack_id,
                "deployment_results": deployment_results,
            }
        )
        if workspace_id is not UNSET:
            field_dict["workspace_id"] = workspace_id
        if deployment_id is not UNSET:
            field_dict["deployment_id"] = deployment_id
        if validate_runtime is not UNSET:
            field_dict["validate_runtime"] = validate_runtime
        if collect_evidence is not UNSET:
            field_dict["collect_evidence"] = collect_evidence
        if setup_monitoring is not UNSET:
            field_dict["setup_monitoring"] = setup_monitoring

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.post_deployment_validation_request_schema_deployment_results import (
            PostDeploymentValidationRequestSchemaDeploymentResults,
        )

        d = dict(src_dict)
        stack_id = d.pop("stack_id")

        deployment_results = PostDeploymentValidationRequestSchemaDeploymentResults.from_dict(
            d.pop("deployment_results")
        )

        def _parse_workspace_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        workspace_id = _parse_workspace_id(d.pop("workspace_id", UNSET))

        def _parse_deployment_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        deployment_id = _parse_deployment_id(d.pop("deployment_id", UNSET))

        validate_runtime = d.pop("validate_runtime", UNSET)

        collect_evidence = d.pop("collect_evidence", UNSET)

        setup_monitoring = d.pop("setup_monitoring", UNSET)

        post_deployment_validation_request_schema = cls(
            stack_id=stack_id,
            deployment_results=deployment_results,
            workspace_id=workspace_id,
            deployment_id=deployment_id,
            validate_runtime=validate_runtime,
            collect_evidence=collect_evidence,
            setup_monitoring=setup_monitoring,
        )

        post_deployment_validation_request_schema.additional_properties = d
        return post_deployment_validation_request_schema

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
