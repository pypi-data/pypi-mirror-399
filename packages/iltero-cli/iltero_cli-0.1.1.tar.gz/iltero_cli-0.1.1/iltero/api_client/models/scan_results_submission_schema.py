from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.scan_results_submission_schema_scan_results import ScanResultsSubmissionSchemaScanResults


T = TypeVar("T", bound="ScanResultsSubmissionSchema")


@_attrs_define
class ScanResultsSubmissionSchema:
    """Schema for submitting scan results from CI/CD pipeline.

    Attributes:
        scan_results (ScanResultsSubmissionSchemaScanResults): Raw scan results from Checkov/OPA scanner
        scanner_version (None | str | Unset): Version of scanner that produced results
        pipeline_url (None | str | Unset): URL to the CI/CD pipeline run
        commit_sha (None | str | Unset): Git commit SHA that was scanned
        branch (None | str | Unset): Git branch that was scanned
    """

    scan_results: ScanResultsSubmissionSchemaScanResults
    scanner_version: None | str | Unset = UNSET
    pipeline_url: None | str | Unset = UNSET
    commit_sha: None | str | Unset = UNSET
    branch: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        scan_results = self.scan_results.to_dict()

        scanner_version: None | str | Unset
        if isinstance(self.scanner_version, Unset):
            scanner_version = UNSET
        else:
            scanner_version = self.scanner_version

        pipeline_url: None | str | Unset
        if isinstance(self.pipeline_url, Unset):
            pipeline_url = UNSET
        else:
            pipeline_url = self.pipeline_url

        commit_sha: None | str | Unset
        if isinstance(self.commit_sha, Unset):
            commit_sha = UNSET
        else:
            commit_sha = self.commit_sha

        branch: None | str | Unset
        if isinstance(self.branch, Unset):
            branch = UNSET
        else:
            branch = self.branch

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "scan_results": scan_results,
            }
        )
        if scanner_version is not UNSET:
            field_dict["scanner_version"] = scanner_version
        if pipeline_url is not UNSET:
            field_dict["pipeline_url"] = pipeline_url
        if commit_sha is not UNSET:
            field_dict["commit_sha"] = commit_sha
        if branch is not UNSET:
            field_dict["branch"] = branch

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scan_results_submission_schema_scan_results import ScanResultsSubmissionSchemaScanResults

        d = dict(src_dict)
        scan_results = ScanResultsSubmissionSchemaScanResults.from_dict(d.pop("scan_results"))

        def _parse_scanner_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        scanner_version = _parse_scanner_version(d.pop("scanner_version", UNSET))

        def _parse_pipeline_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pipeline_url = _parse_pipeline_url(d.pop("pipeline_url", UNSET))

        def _parse_commit_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_sha = _parse_commit_sha(d.pop("commit_sha", UNSET))

        def _parse_branch(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        branch = _parse_branch(d.pop("branch", UNSET))

        scan_results_submission_schema = cls(
            scan_results=scan_results,
            scanner_version=scanner_version,
            pipeline_url=pipeline_url,
            commit_sha=commit_sha,
            branch=branch,
        )

        scan_results_submission_schema.additional_properties = d
        return scan_results_submission_schema

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
