from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CheckoutSessionRequest")


@_attrs_define
class CheckoutSessionRequest:
    """
    Attributes:
        user_id (str):
        price_id (str):
        user_email (str):
        user_name (None | str | Unset):
        promotion_code (None | str | Unset):
    """

    user_id: str
    price_id: str
    user_email: str
    user_name: None | str | Unset = UNSET
    promotion_code: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        price_id = self.price_id

        user_email = self.user_email

        user_name: None | str | Unset
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        promotion_code: None | str | Unset
        if isinstance(self.promotion_code, Unset):
            promotion_code = UNSET
        else:
            promotion_code = self.promotion_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "price_id": price_id,
                "user_email": user_email,
            }
        )
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if promotion_code is not UNSET:
            field_dict["promotion_code"] = promotion_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        price_id = d.pop("price_id")

        user_email = d.pop("user_email")

        def _parse_user_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_name = _parse_user_name(d.pop("user_name", UNSET))

        def _parse_promotion_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        promotion_code = _parse_promotion_code(d.pop("promotion_code", UNSET))

        checkout_session_request = cls(
            user_id=user_id,
            price_id=price_id,
            user_email=user_email,
            user_name=user_name,
            promotion_code=promotion_code,
        )

        checkout_session_request.additional_properties = d
        return checkout_session_request

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
