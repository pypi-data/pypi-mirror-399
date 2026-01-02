from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsageCategory")


@_attrs_define
class UsageCategory:
    """Usage for a single category.

    Attributes:
        used (int | Unset): Amount used Default: 0.
        limit (int | Unset): Usage limit Default: 0.
        remaining (int | Unset): Remaining allowance Default: 0.
    """

    used: int | Unset = 0
    limit: int | Unset = 0
    remaining: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        used = self.used

        limit = self.limit

        remaining = self.remaining

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if used is not UNSET:
            field_dict["used"] = used
        if limit is not UNSET:
            field_dict["limit"] = limit
        if remaining is not UNSET:
            field_dict["remaining"] = remaining

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        used = d.pop("used", UNSET)

        limit = d.pop("limit", UNSET)

        remaining = d.pop("remaining", UNSET)

        usage_category = cls(
            used=used,
            limit=limit,
            remaining=remaining,
        )

        usage_category.additional_properties = d
        return usage_category

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
