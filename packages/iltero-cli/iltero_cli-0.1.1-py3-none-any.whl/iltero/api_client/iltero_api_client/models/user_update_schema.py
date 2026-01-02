from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_update_schema_notification_preferences_type_0 import UserUpdateSchemaNotificationPreferencesType0
    from ..models.user_update_schema_security_settings_type_0 import UserUpdateSchemaSecuritySettingsType0


T = TypeVar("T", bound="UserUpdateSchema")


@_attrs_define
class UserUpdateSchema:
    """Enhanced schema for user updates.

    Attributes:
        name (None | str | Unset):
        email (None | str | Unset):
        phone_number (None | str | Unset):
        timezone (None | str | Unset):
        locale (None | str | Unset):
        avatar_url (None | str | Unset):
        notification_preferences (None | Unset | UserUpdateSchemaNotificationPreferencesType0):
        security_settings (None | Unset | UserUpdateSchemaSecuritySettingsType0):
    """

    name: None | str | Unset = UNSET
    email: None | str | Unset = UNSET
    phone_number: None | str | Unset = UNSET
    timezone: None | str | Unset = UNSET
    locale: None | str | Unset = UNSET
    avatar_url: None | str | Unset = UNSET
    notification_preferences: None | Unset | UserUpdateSchemaNotificationPreferencesType0 = UNSET
    security_settings: None | Unset | UserUpdateSchemaSecuritySettingsType0 = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.user_update_schema_notification_preferences_type_0 import (
            UserUpdateSchemaNotificationPreferencesType0,
        )
        from ..models.user_update_schema_security_settings_type_0 import UserUpdateSchemaSecuritySettingsType0

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        email: None | str | Unset
        if isinstance(self.email, Unset):
            email = UNSET
        else:
            email = self.email

        phone_number: None | str | Unset
        if isinstance(self.phone_number, Unset):
            phone_number = UNSET
        else:
            phone_number = self.phone_number

        timezone: None | str | Unset
        if isinstance(self.timezone, Unset):
            timezone = UNSET
        else:
            timezone = self.timezone

        locale: None | str | Unset
        if isinstance(self.locale, Unset):
            locale = UNSET
        else:
            locale = self.locale

        avatar_url: None | str | Unset
        if isinstance(self.avatar_url, Unset):
            avatar_url = UNSET
        else:
            avatar_url = self.avatar_url

        notification_preferences: dict[str, Any] | None | Unset
        if isinstance(self.notification_preferences, Unset):
            notification_preferences = UNSET
        elif isinstance(self.notification_preferences, UserUpdateSchemaNotificationPreferencesType0):
            notification_preferences = self.notification_preferences.to_dict()
        else:
            notification_preferences = self.notification_preferences

        security_settings: dict[str, Any] | None | Unset
        if isinstance(self.security_settings, Unset):
            security_settings = UNSET
        elif isinstance(self.security_settings, UserUpdateSchemaSecuritySettingsType0):
            security_settings = self.security_settings.to_dict()
        else:
            security_settings = self.security_settings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if email is not UNSET:
            field_dict["email"] = email
        if phone_number is not UNSET:
            field_dict["phone_number"] = phone_number
        if timezone is not UNSET:
            field_dict["timezone"] = timezone
        if locale is not UNSET:
            field_dict["locale"] = locale
        if avatar_url is not UNSET:
            field_dict["avatar_url"] = avatar_url
        if notification_preferences is not UNSET:
            field_dict["notification_preferences"] = notification_preferences
        if security_settings is not UNSET:
            field_dict["security_settings"] = security_settings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.user_update_schema_notification_preferences_type_0 import (
            UserUpdateSchemaNotificationPreferencesType0,
        )
        from ..models.user_update_schema_security_settings_type_0 import UserUpdateSchemaSecuritySettingsType0

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        email = _parse_email(d.pop("email", UNSET))

        def _parse_phone_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phone_number = _parse_phone_number(d.pop("phone_number", UNSET))

        def _parse_timezone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        timezone = _parse_timezone(d.pop("timezone", UNSET))

        def _parse_locale(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        locale = _parse_locale(d.pop("locale", UNSET))

        def _parse_avatar_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        avatar_url = _parse_avatar_url(d.pop("avatar_url", UNSET))

        def _parse_notification_preferences(
            data: object,
        ) -> None | Unset | UserUpdateSchemaNotificationPreferencesType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                notification_preferences_type_0 = UserUpdateSchemaNotificationPreferencesType0.from_dict(data)

                return notification_preferences_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UserUpdateSchemaNotificationPreferencesType0, data)

        notification_preferences = _parse_notification_preferences(d.pop("notification_preferences", UNSET))

        def _parse_security_settings(data: object) -> None | Unset | UserUpdateSchemaSecuritySettingsType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                security_settings_type_0 = UserUpdateSchemaSecuritySettingsType0.from_dict(data)

                return security_settings_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UserUpdateSchemaSecuritySettingsType0, data)

        security_settings = _parse_security_settings(d.pop("security_settings", UNSET))

        user_update_schema = cls(
            name=name,
            email=email,
            phone_number=phone_number,
            timezone=timezone,
            locale=locale,
            avatar_url=avatar_url,
            notification_preferences=notification_preferences,
            security_settings=security_settings,
        )

        user_update_schema.additional_properties = d
        return user_update_schema

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
