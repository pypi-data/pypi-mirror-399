from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CheckoutStartedRequest")


@_attrs_define
class CheckoutStartedRequest:
    """
    Attributes:
        user_id (str):
        user_email (str):
        plan (str):
        price (float):
        promo_code (None | str | Unset):
    """

    user_id: str
    user_email: str
    plan: str
    price: float
    promo_code: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        user_email = self.user_email

        plan = self.plan

        price = self.price

        promo_code: None | str | Unset
        if isinstance(self.promo_code, Unset):
            promo_code = UNSET
        else:
            promo_code = self.promo_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "user_email": user_email,
                "plan": plan,
                "price": price,
            }
        )
        if promo_code is not UNSET:
            field_dict["promo_code"] = promo_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        user_email = d.pop("user_email")

        plan = d.pop("plan")

        price = d.pop("price")

        def _parse_promo_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        promo_code = _parse_promo_code(d.pop("promo_code", UNSET))

        checkout_started_request = cls(
            user_id=user_id,
            user_email=user_email,
            plan=plan,
            price=price,
            promo_code=promo_code,
        )

        checkout_started_request.additional_properties = d
        return checkout_started_request

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
