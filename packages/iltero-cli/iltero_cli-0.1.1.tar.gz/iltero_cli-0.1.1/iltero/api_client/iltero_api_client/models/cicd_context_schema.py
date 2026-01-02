from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CICDContextSchema")


@_attrs_define
class CICDContextSchema:
    """CI/CD pipeline context for evidence collection.

    Captures comprehensive metadata from CI/CD pipelines to support:
    - SOC 2 / ISO 27001 audit trails
    - Change management linkage (commits, PRs, approvals)
    - Evidence of code review and segregation of duties
    - Complete deployment provenance chain

        Attributes:
            repository_url (None | str | Unset): Full repository URL (e.g., https://github.com/org/repo)
            repository_name (None | str | Unset): Repository name in owner/repo format
            commit_sha (None | str | Unset): Full Git commit SHA being deployed
            commit_message (None | str | Unset): Commit message for context
            branch (None | str | Unset): Source branch name
            base_branch (None | str | Unset): Target/base branch for PRs (e.g., main)
            pull_request_number (int | None | Unset): PR number if this deployment is from a PR
            pull_request_url (None | str | Unset): Full URL to the pull request
            pull_request_title (None | str | Unset): PR title for audit context
            triggered_by (None | str | Unset): Username/actor who triggered the pipeline
            triggered_by_email (None | str | Unset): Email of the triggering user if available
            pipeline_name (None | str | Unset): Name of the workflow/pipeline
            pipeline_run_number (int | None | Unset): Sequential run number of the pipeline
            job_name (None | str | Unset): Name of the current job within the pipeline
            pr_approvers (list[str] | None | Unset): List of users who approved the PR
            pr_reviewers (list[str] | None | Unset): List of users who reviewed the PR
            required_approvals (int | None | Unset): Number of approvals required by branch protection
            approval_count (int | None | Unset): Actual number of approvals received
            provider (None | str | Unset): CI/CD provider (github, gitlab, bitbucket, azure_devops)
            provider_event (None | str | Unset): Event type that triggered the pipeline (push, pull_request, etc.)
            runner_os (None | str | Unset): OS of the CI/CD runner
            runner_name (None | str | Unset): Name/ID of the CI/CD runner
    """

    repository_url: None | str | Unset = UNSET
    repository_name: None | str | Unset = UNSET
    commit_sha: None | str | Unset = UNSET
    commit_message: None | str | Unset = UNSET
    branch: None | str | Unset = UNSET
    base_branch: None | str | Unset = UNSET
    pull_request_number: int | None | Unset = UNSET
    pull_request_url: None | str | Unset = UNSET
    pull_request_title: None | str | Unset = UNSET
    triggered_by: None | str | Unset = UNSET
    triggered_by_email: None | str | Unset = UNSET
    pipeline_name: None | str | Unset = UNSET
    pipeline_run_number: int | None | Unset = UNSET
    job_name: None | str | Unset = UNSET
    pr_approvers: list[str] | None | Unset = UNSET
    pr_reviewers: list[str] | None | Unset = UNSET
    required_approvals: int | None | Unset = UNSET
    approval_count: int | None | Unset = UNSET
    provider: None | str | Unset = UNSET
    provider_event: None | str | Unset = UNSET
    runner_os: None | str | Unset = UNSET
    runner_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository_url: None | str | Unset
        if isinstance(self.repository_url, Unset):
            repository_url = UNSET
        else:
            repository_url = self.repository_url

        repository_name: None | str | Unset
        if isinstance(self.repository_name, Unset):
            repository_name = UNSET
        else:
            repository_name = self.repository_name

        commit_sha: None | str | Unset
        if isinstance(self.commit_sha, Unset):
            commit_sha = UNSET
        else:
            commit_sha = self.commit_sha

        commit_message: None | str | Unset
        if isinstance(self.commit_message, Unset):
            commit_message = UNSET
        else:
            commit_message = self.commit_message

        branch: None | str | Unset
        if isinstance(self.branch, Unset):
            branch = UNSET
        else:
            branch = self.branch

        base_branch: None | str | Unset
        if isinstance(self.base_branch, Unset):
            base_branch = UNSET
        else:
            base_branch = self.base_branch

        pull_request_number: int | None | Unset
        if isinstance(self.pull_request_number, Unset):
            pull_request_number = UNSET
        else:
            pull_request_number = self.pull_request_number

        pull_request_url: None | str | Unset
        if isinstance(self.pull_request_url, Unset):
            pull_request_url = UNSET
        else:
            pull_request_url = self.pull_request_url

        pull_request_title: None | str | Unset
        if isinstance(self.pull_request_title, Unset):
            pull_request_title = UNSET
        else:
            pull_request_title = self.pull_request_title

        triggered_by: None | str | Unset
        if isinstance(self.triggered_by, Unset):
            triggered_by = UNSET
        else:
            triggered_by = self.triggered_by

        triggered_by_email: None | str | Unset
        if isinstance(self.triggered_by_email, Unset):
            triggered_by_email = UNSET
        else:
            triggered_by_email = self.triggered_by_email

        pipeline_name: None | str | Unset
        if isinstance(self.pipeline_name, Unset):
            pipeline_name = UNSET
        else:
            pipeline_name = self.pipeline_name

        pipeline_run_number: int | None | Unset
        if isinstance(self.pipeline_run_number, Unset):
            pipeline_run_number = UNSET
        else:
            pipeline_run_number = self.pipeline_run_number

        job_name: None | str | Unset
        if isinstance(self.job_name, Unset):
            job_name = UNSET
        else:
            job_name = self.job_name

        pr_approvers: list[str] | None | Unset
        if isinstance(self.pr_approvers, Unset):
            pr_approvers = UNSET
        elif isinstance(self.pr_approvers, list):
            pr_approvers = self.pr_approvers

        else:
            pr_approvers = self.pr_approvers

        pr_reviewers: list[str] | None | Unset
        if isinstance(self.pr_reviewers, Unset):
            pr_reviewers = UNSET
        elif isinstance(self.pr_reviewers, list):
            pr_reviewers = self.pr_reviewers

        else:
            pr_reviewers = self.pr_reviewers

        required_approvals: int | None | Unset
        if isinstance(self.required_approvals, Unset):
            required_approvals = UNSET
        else:
            required_approvals = self.required_approvals

        approval_count: int | None | Unset
        if isinstance(self.approval_count, Unset):
            approval_count = UNSET
        else:
            approval_count = self.approval_count

        provider: None | str | Unset
        if isinstance(self.provider, Unset):
            provider = UNSET
        else:
            provider = self.provider

        provider_event: None | str | Unset
        if isinstance(self.provider_event, Unset):
            provider_event = UNSET
        else:
            provider_event = self.provider_event

        runner_os: None | str | Unset
        if isinstance(self.runner_os, Unset):
            runner_os = UNSET
        else:
            runner_os = self.runner_os

        runner_name: None | str | Unset
        if isinstance(self.runner_name, Unset):
            runner_name = UNSET
        else:
            runner_name = self.runner_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository_url is not UNSET:
            field_dict["repository_url"] = repository_url
        if repository_name is not UNSET:
            field_dict["repository_name"] = repository_name
        if commit_sha is not UNSET:
            field_dict["commit_sha"] = commit_sha
        if commit_message is not UNSET:
            field_dict["commit_message"] = commit_message
        if branch is not UNSET:
            field_dict["branch"] = branch
        if base_branch is not UNSET:
            field_dict["base_branch"] = base_branch
        if pull_request_number is not UNSET:
            field_dict["pull_request_number"] = pull_request_number
        if pull_request_url is not UNSET:
            field_dict["pull_request_url"] = pull_request_url
        if pull_request_title is not UNSET:
            field_dict["pull_request_title"] = pull_request_title
        if triggered_by is not UNSET:
            field_dict["triggered_by"] = triggered_by
        if triggered_by_email is not UNSET:
            field_dict["triggered_by_email"] = triggered_by_email
        if pipeline_name is not UNSET:
            field_dict["pipeline_name"] = pipeline_name
        if pipeline_run_number is not UNSET:
            field_dict["pipeline_run_number"] = pipeline_run_number
        if job_name is not UNSET:
            field_dict["job_name"] = job_name
        if pr_approvers is not UNSET:
            field_dict["pr_approvers"] = pr_approvers
        if pr_reviewers is not UNSET:
            field_dict["pr_reviewers"] = pr_reviewers
        if required_approvals is not UNSET:
            field_dict["required_approvals"] = required_approvals
        if approval_count is not UNSET:
            field_dict["approval_count"] = approval_count
        if provider is not UNSET:
            field_dict["provider"] = provider
        if provider_event is not UNSET:
            field_dict["provider_event"] = provider_event
        if runner_os is not UNSET:
            field_dict["runner_os"] = runner_os
        if runner_name is not UNSET:
            field_dict["runner_name"] = runner_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_repository_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_url = _parse_repository_url(d.pop("repository_url", UNSET))

        def _parse_repository_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repository_name = _parse_repository_name(d.pop("repository_name", UNSET))

        def _parse_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_sha = _parse_commit_sha(d.pop("commit_sha", UNSET))

        def _parse_commit_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_message = _parse_commit_message(d.pop("commit_message", UNSET))

        def _parse_branch(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        branch = _parse_branch(d.pop("branch", UNSET))

        def _parse_base_branch(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_branch = _parse_base_branch(d.pop("base_branch", UNSET))

        def _parse_pull_request_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pull_request_number = _parse_pull_request_number(d.pop("pull_request_number", UNSET))

        def _parse_pull_request_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_url = _parse_pull_request_url(d.pop("pull_request_url", UNSET))

        def _parse_pull_request_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pull_request_title = _parse_pull_request_title(d.pop("pull_request_title", UNSET))

        def _parse_triggered_by(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        triggered_by = _parse_triggered_by(d.pop("triggered_by", UNSET))

        def _parse_triggered_by_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        triggered_by_email = _parse_triggered_by_email(d.pop("triggered_by_email", UNSET))

        def _parse_pipeline_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pipeline_name = _parse_pipeline_name(d.pop("pipeline_name", UNSET))

        def _parse_pipeline_run_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        pipeline_run_number = _parse_pipeline_run_number(d.pop("pipeline_run_number", UNSET))

        def _parse_job_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        job_name = _parse_job_name(d.pop("job_name", UNSET))

        def _parse_pr_approvers(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                pr_approvers_type_0 = cast(list[str], data)

                return pr_approvers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        pr_approvers = _parse_pr_approvers(d.pop("pr_approvers", UNSET))

        def _parse_pr_reviewers(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                pr_reviewers_type_0 = cast(list[str], data)

                return pr_reviewers_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        pr_reviewers = _parse_pr_reviewers(d.pop("pr_reviewers", UNSET))

        def _parse_required_approvals(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        required_approvals = _parse_required_approvals(d.pop("required_approvals", UNSET))

        def _parse_approval_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        approval_count = _parse_approval_count(d.pop("approval_count", UNSET))

        def _parse_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider = _parse_provider(d.pop("provider", UNSET))

        def _parse_provider_event(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider_event = _parse_provider_event(d.pop("provider_event", UNSET))

        def _parse_runner_os(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        runner_os = _parse_runner_os(d.pop("runner_os", UNSET))

        def _parse_runner_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        runner_name = _parse_runner_name(d.pop("runner_name", UNSET))

        cicd_context_schema = cls(
            repository_url=repository_url,
            repository_name=repository_name,
            commit_sha=commit_sha,
            commit_message=commit_message,
            branch=branch,
            base_branch=base_branch,
            pull_request_number=pull_request_number,
            pull_request_url=pull_request_url,
            pull_request_title=pull_request_title,
            triggered_by=triggered_by,
            triggered_by_email=triggered_by_email,
            pipeline_name=pipeline_name,
            pipeline_run_number=pipeline_run_number,
            job_name=job_name,
            pr_approvers=pr_approvers,
            pr_reviewers=pr_reviewers,
            required_approvals=required_approvals,
            approval_count=approval_count,
            provider=provider,
            provider_event=provider_event,
            runner_os=runner_os,
            runner_name=runner_name,
        )

        cicd_context_schema.additional_properties = d
        return cicd_context_schema

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
