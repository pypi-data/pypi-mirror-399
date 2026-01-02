from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.billing_period import BillingPeriod


T = TypeVar("T", bound="ApiUsageDetailsResponse")


@_attrs_define
class ApiUsageDetailsResponse:
    """
    Example:
        {'api_keys_count': 3, 'billing_period': {'end': '2023-06-30T23:59:59Z', 'start': '2023-06-01T00:00:00Z'},
            'current_usage': 150, 'has_payment_method': True, 'total_requests': 150, 'upcoming_charges': 15.0}

    Attributes:
        has_payment_method (bool): Whether the user has a payment method on file
        api_keys_count (int): Number of API keys the user has
        total_requests (int): Total number of API requests made this month
        upcoming_charges (float): Upcoming charges in dollars
        current_usage (int): Current usage count
        billing_period (BillingPeriod):
    """

    has_payment_method: bool
    api_keys_count: int
    total_requests: int
    upcoming_charges: float
    current_usage: int
    billing_period: BillingPeriod
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        has_payment_method = self.has_payment_method

        api_keys_count = self.api_keys_count

        total_requests = self.total_requests

        upcoming_charges = self.upcoming_charges

        current_usage = self.current_usage

        billing_period = self.billing_period.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "has_payment_method": has_payment_method,
                "api_keys_count": api_keys_count,
                "total_requests": total_requests,
                "upcoming_charges": upcoming_charges,
                "current_usage": current_usage,
                "billing_period": billing_period,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.billing_period import BillingPeriod

        d = dict(src_dict)
        has_payment_method = d.pop("has_payment_method")

        api_keys_count = d.pop("api_keys_count")

        total_requests = d.pop("total_requests")

        upcoming_charges = d.pop("upcoming_charges")

        current_usage = d.pop("current_usage")

        billing_period = BillingPeriod.from_dict(d.pop("billing_period"))

        api_usage_details_response = cls(
            has_payment_method=has_payment_method,
            api_keys_count=api_keys_count,
            total_requests=total_requests,
            upcoming_charges=upcoming_charges,
            current_usage=current_usage,
            billing_period=billing_period,
        )

        api_usage_details_response.additional_properties = d
        return api_usage_details_response

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
