from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserSignupRequest")


@_attrs_define
class UserSignupRequest:
    """
    Attributes:
        user_id (str):
        user_email (str):
        signup_source (None | str | Unset):
    """

    user_id: str
    user_email: str
    signup_source: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        user_email = self.user_email

        signup_source: None | str | Unset
        if isinstance(self.signup_source, Unset):
            signup_source = UNSET
        else:
            signup_source = self.signup_source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "user_email": user_email,
            }
        )
        if signup_source is not UNSET:
            field_dict["signup_source"] = signup_source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        user_email = d.pop("user_email")

        def _parse_signup_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        signup_source = _parse_signup_source(d.pop("signup_source", UNSET))

        user_signup_request = cls(
            user_id=user_id,
            user_email=user_email,
            signup_source=signup_source,
        )

        user_signup_request.additional_properties = d
        return user_signup_request

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
