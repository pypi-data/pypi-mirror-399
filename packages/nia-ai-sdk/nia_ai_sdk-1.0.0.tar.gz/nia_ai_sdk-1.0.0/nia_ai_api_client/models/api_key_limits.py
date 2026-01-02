from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKeyLimits")


@_attrs_define
class ApiKeyLimits:
    """
    Attributes:
        monthly_request_limit (int | None | Unset):
        rate_limit_requests (int | Unset):  Default: 100.
        rate_limit_window (int | Unset):  Default: 60.
    """

    monthly_request_limit: int | None | Unset = UNSET
    rate_limit_requests: int | Unset = 100
    rate_limit_window: int | Unset = 60
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        monthly_request_limit: int | None | Unset
        if isinstance(self.monthly_request_limit, Unset):
            monthly_request_limit = UNSET
        else:
            monthly_request_limit = self.monthly_request_limit

        rate_limit_requests = self.rate_limit_requests

        rate_limit_window = self.rate_limit_window

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if monthly_request_limit is not UNSET:
            field_dict["monthly_request_limit"] = monthly_request_limit
        if rate_limit_requests is not UNSET:
            field_dict["rate_limit_requests"] = rate_limit_requests
        if rate_limit_window is not UNSET:
            field_dict["rate_limit_window"] = rate_limit_window

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_monthly_request_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        monthly_request_limit = _parse_monthly_request_limit(d.pop("monthly_request_limit", UNSET))

        rate_limit_requests = d.pop("rate_limit_requests", UNSET)

        rate_limit_window = d.pop("rate_limit_window", UNSET)

        api_key_limits = cls(
            monthly_request_limit=monthly_request_limit,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
        )

        api_key_limits.additional_properties = d
        return api_key_limits

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
