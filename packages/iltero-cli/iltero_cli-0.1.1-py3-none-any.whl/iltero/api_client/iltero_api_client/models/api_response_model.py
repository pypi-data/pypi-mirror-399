from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_response_model_data_type_0 import APIResponseModelDataType0
    from ..models.api_response_model_metadata_type_0 import APIResponseModelMetadataType0


T = TypeVar("T", bound="APIResponseModel")


@_attrs_define
class APIResponseModel:
    """Pydantic model for API response validation.
    Used for OpenAPI schema generation and validation.

        Attributes:
            status (str | Unset):  Default: 'success'.
            status_code (int | Unset):  Default: 200.
            data (Any | APIResponseModelDataType0 | None | Unset):
            message (None | str | Unset):
            error (None | str | Unset):
            metadata (APIResponseModelMetadataType0 | None | Unset):
    """

    status: str | Unset = "success"
    status_code: int | Unset = 200
    data: Any | APIResponseModelDataType0 | None | Unset = UNSET
    message: None | str | Unset = UNSET
    error: None | str | Unset = UNSET
    metadata: APIResponseModelMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.api_response_model_data_type_0 import APIResponseModelDataType0
        from ..models.api_response_model_metadata_type_0 import APIResponseModelMetadataType0

        status = self.status

        status_code = self.status_code

        data: Any | dict[str, Any] | None | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, APIResponseModelDataType0):
            data = self.data.to_dict()
        else:
            data = self.data

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, APIResponseModelMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if status is not UNSET:
            field_dict["status"] = status
        if status_code is not UNSET:
            field_dict["status_code"] = status_code
        if data is not UNSET:
            field_dict["data"] = data
        if message is not UNSET:
            field_dict["message"] = message
        if error is not UNSET:
            field_dict["error"] = error
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_response_model_data_type_0 import APIResponseModelDataType0
        from ..models.api_response_model_metadata_type_0 import APIResponseModelMetadataType0

        d = dict(src_dict)
        status = d.pop("status", UNSET)

        status_code = d.pop("status_code", UNSET)

        def _parse_data(data: object) -> Any | APIResponseModelDataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = APIResponseModelDataType0.from_dict(data)

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(Any | APIResponseModelDataType0 | None | Unset, data)

        data = _parse_data(d.pop("data", UNSET))

        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_metadata(data: object) -> APIResponseModelMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = APIResponseModelMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(APIResponseModelMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        api_response_model = cls(
            status=status,
            status_code=status_code,
            data=data,
            message=message,
            error=error,
            metadata=metadata,
        )

        api_response_model.additional_properties = d
        return api_response_model

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
