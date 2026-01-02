from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DeviceExchangeRequest")


@_attrs_define
class DeviceExchangeRequest:
    """
    Attributes:
        authorization_session_id (str):
        user_code (str):
    """

    authorization_session_id: str
    user_code: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authorization_session_id = self.authorization_session_id

        user_code = self.user_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authorization_session_id": authorization_session_id,
                "user_code": user_code,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        authorization_session_id = d.pop("authorization_session_id")

        user_code = d.pop("user_code")

        device_exchange_request = cls(
            authorization_session_id=authorization_session_id,
            user_code=user_code,
        )

        device_exchange_request.additional_properties = d
        return device_exchange_request

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
