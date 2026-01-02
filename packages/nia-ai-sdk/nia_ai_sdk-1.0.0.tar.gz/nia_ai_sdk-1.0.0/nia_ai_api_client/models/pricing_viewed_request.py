from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PricingViewedRequest")


@_attrs_define
class PricingViewedRequest:
    """
    Attributes:
        user_id (str):
        user_email (str):
        subscription_tier (str):
        has_payment_method (bool):
    """

    user_id: str
    user_email: str
    subscription_tier: str
    has_payment_method: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        user_email = self.user_email

        subscription_tier = self.subscription_tier

        has_payment_method = self.has_payment_method

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "user_email": user_email,
                "subscription_tier": subscription_tier,
                "has_payment_method": has_payment_method,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        user_email = d.pop("user_email")

        subscription_tier = d.pop("subscription_tier")

        has_payment_method = d.pop("has_payment_method")

        pricing_viewed_request = cls(
            user_id=user_id,
            user_email=user_email,
            subscription_tier=subscription_tier,
            has_payment_method=has_payment_method,
        )

        pricing_viewed_request.additional_properties = d
        return pricing_viewed_request

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
