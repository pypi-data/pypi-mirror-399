from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApiKeyUsage")


@_attrs_define
class ApiKeyUsage:
    """
    Attributes:
        last_reset (datetime.datetime):
        current_minute_start (datetime.datetime):
        monthly_requests (int | Unset):  Default: 0.
        monthly_tokens (int | Unset):  Default: 0.
        current_minute_requests (int | Unset):  Default: 0.
    """

    last_reset: datetime.datetime
    current_minute_start: datetime.datetime
    monthly_requests: int | Unset = 0
    monthly_tokens: int | Unset = 0
    current_minute_requests: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        last_reset = self.last_reset.isoformat()

        current_minute_start = self.current_minute_start.isoformat()

        monthly_requests = self.monthly_requests

        monthly_tokens = self.monthly_tokens

        current_minute_requests = self.current_minute_requests

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "last_reset": last_reset,
                "current_minute_start": current_minute_start,
            }
        )
        if monthly_requests is not UNSET:
            field_dict["monthly_requests"] = monthly_requests
        if monthly_tokens is not UNSET:
            field_dict["monthly_tokens"] = monthly_tokens
        if current_minute_requests is not UNSET:
            field_dict["current_minute_requests"] = current_minute_requests

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        last_reset = isoparse(d.pop("last_reset"))

        current_minute_start = isoparse(d.pop("current_minute_start"))

        monthly_requests = d.pop("monthly_requests", UNSET)

        monthly_tokens = d.pop("monthly_tokens", UNSET)

        current_minute_requests = d.pop("current_minute_requests", UNSET)

        api_key_usage = cls(
            last_reset=last_reset,
            current_minute_start=current_minute_start,
            monthly_requests=monthly_requests,
            monthly_tokens=monthly_tokens,
            current_minute_requests=current_minute_requests,
        )

        api_key_usage.additional_properties = d
        return api_key_usage

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
