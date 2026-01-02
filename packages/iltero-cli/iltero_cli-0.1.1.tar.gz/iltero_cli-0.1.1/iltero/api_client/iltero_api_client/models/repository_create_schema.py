from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repository_config_schema import RepositoryConfigSchema


T = TypeVar("T", bound="RepositoryCreateSchema")


@_attrs_define
class RepositoryCreateSchema:
    """Schema for repository creation with compliance options.

    Attributes:
        provider (str): Git provider (github, gitlab, etc)
        config (RepositoryConfigSchema):
        option (str): Option selected for repository creation
        url (str): Repository URL
        name (str): Repository name
        cloud_provider (None | str | Unset): Optional cloud provider enforcement
        visibility (str | Unset): Repository visibility (private, public, internal) Default: 'private'.
        description (None | str | Unset): Repository description
        enable_compliance_scanning (bool | Unset): Enable compliance scanning workflow Default: True.
        enable_monitoring (bool | Unset): Enable continuous monitoring webhook Default: True.
    """

    provider: str
    config: RepositoryConfigSchema
    option: str
    url: str
    name: str
    cloud_provider: None | str | Unset = UNSET
    visibility: str | Unset = "private"
    description: None | str | Unset = UNSET
    enable_compliance_scanning: bool | Unset = True
    enable_monitoring: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider = self.provider

        config = self.config.to_dict()

        option = self.option

        url = self.url

        name = self.name

        cloud_provider: None | str | Unset
        if isinstance(self.cloud_provider, Unset):
            cloud_provider = UNSET
        else:
            cloud_provider = self.cloud_provider

        visibility = self.visibility

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        enable_compliance_scanning = self.enable_compliance_scanning

        enable_monitoring = self.enable_monitoring

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider": provider,
                "config": config,
                "option": option,
                "url": url,
                "name": name,
            }
        )
        if cloud_provider is not UNSET:
            field_dict["cloud_provider"] = cloud_provider
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if description is not UNSET:
            field_dict["description"] = description
        if enable_compliance_scanning is not UNSET:
            field_dict["enable_compliance_scanning"] = enable_compliance_scanning
        if enable_monitoring is not UNSET:
            field_dict["enable_monitoring"] = enable_monitoring

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repository_config_schema import RepositoryConfigSchema

        d = dict(src_dict)
        provider = d.pop("provider")

        config = RepositoryConfigSchema.from_dict(d.pop("config"))

        option = d.pop("option")

        url = d.pop("url")

        name = d.pop("name")

        def _parse_cloud_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        cloud_provider = _parse_cloud_provider(d.pop("cloud_provider", UNSET))

        visibility = d.pop("visibility", UNSET)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        enable_compliance_scanning = d.pop("enable_compliance_scanning", UNSET)

        enable_monitoring = d.pop("enable_monitoring", UNSET)

        repository_create_schema = cls(
            provider=provider,
            config=config,
            option=option,
            url=url,
            name=name,
            cloud_provider=cloud_provider,
            visibility=visibility,
            description=description,
            enable_compliance_scanning=enable_compliance_scanning,
            enable_monitoring=enable_monitoring,
        )

        repository_create_schema.additional_properties = d
        return repository_create_schema

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
