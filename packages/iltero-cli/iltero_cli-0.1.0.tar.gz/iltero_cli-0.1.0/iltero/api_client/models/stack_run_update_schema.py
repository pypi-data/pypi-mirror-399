from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.stack_run_update_schema_run_output_type_0 import StackRunUpdateSchemaRunOutputType0


T = TypeVar("T", bound="StackRunUpdateSchema")


@_attrs_define
class StackRunUpdateSchema:
    """Schema used by internal processes (e.g., CI/CD webhook) to update run status.

    Attributes:
        status (Status):
        external_run_id (None | str | Unset): ID from the external CI/CD system.
        external_run_url (None | str | Unset): URL to the external CI/CD run.
        started_at (datetime.datetime | None | Unset): Timestamp when the run started.
        finished_at (datetime.datetime | None | Unset): Timestamp when the run finished.
        run_output (None | StackRunUpdateSchemaRunOutputType0 | Unset): Updated output or errors.
    """

    status: Status
    external_run_id: None | str | Unset = UNSET
    external_run_url: None | str | Unset = UNSET
    started_at: datetime.datetime | None | Unset = UNSET
    finished_at: datetime.datetime | None | Unset = UNSET
    run_output: None | StackRunUpdateSchemaRunOutputType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.stack_run_update_schema_run_output_type_0 import StackRunUpdateSchemaRunOutputType0

        status = self.status.value

        external_run_id: None | str | Unset
        if isinstance(self.external_run_id, Unset):
            external_run_id = UNSET
        else:
            external_run_id = self.external_run_id

        external_run_url: None | str | Unset
        if isinstance(self.external_run_url, Unset):
            external_run_url = UNSET
        else:
            external_run_url = self.external_run_url

        started_at: None | str | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        elif isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        finished_at: None | str | Unset
        if isinstance(self.finished_at, Unset):
            finished_at = UNSET
        elif isinstance(self.finished_at, datetime.datetime):
            finished_at = self.finished_at.isoformat()
        else:
            finished_at = self.finished_at

        run_output: dict[str, Any] | None | Unset
        if isinstance(self.run_output, Unset):
            run_output = UNSET
        elif isinstance(self.run_output, StackRunUpdateSchemaRunOutputType0):
            run_output = self.run_output.to_dict()
        else:
            run_output = self.run_output

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if external_run_id is not UNSET:
            field_dict["external_run_id"] = external_run_id
        if external_run_url is not UNSET:
            field_dict["external_run_url"] = external_run_url
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if finished_at is not UNSET:
            field_dict["finished_at"] = finished_at
        if run_output is not UNSET:
            field_dict["run_output"] = run_output

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stack_run_update_schema_run_output_type_0 import StackRunUpdateSchemaRunOutputType0

        d = dict(src_dict)
        status = Status(d.pop("status"))

        def _parse_external_run_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_run_id = _parse_external_run_id(d.pop("external_run_id", UNSET))

        def _parse_external_run_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        external_run_url = _parse_external_run_url(d.pop("external_run_url", UNSET))

        def _parse_started_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = isoparse(data)

                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        def _parse_finished_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finished_at_type_0 = isoparse(data)

                return finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        finished_at = _parse_finished_at(d.pop("finished_at", UNSET))

        def _parse_run_output(data: object) -> None | StackRunUpdateSchemaRunOutputType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                run_output_type_0 = StackRunUpdateSchemaRunOutputType0.from_dict(data)

                return run_output_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StackRunUpdateSchemaRunOutputType0 | Unset, data)

        run_output = _parse_run_output(d.pop("run_output", UNSET))

        stack_run_update_schema = cls(
            status=status,
            external_run_id=external_run_id,
            external_run_url=external_run_url,
            started_at=started_at,
            finished_at=finished_at,
            run_output=run_output,
        )

        stack_run_update_schema.additional_properties = d
        return stack_run_update_schema

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
