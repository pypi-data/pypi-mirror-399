from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.global_source_response import GlobalSourceResponse


T = TypeVar("T", bound="GlobalSourceListResponse")


@_attrs_define
class GlobalSourceListResponse:
    """
    Attributes:
        sources (list[GlobalSourceResponse]):
        total (int):
        limit (int):
        offset (int):
    """

    sources: list[GlobalSourceResponse]
    total: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        total = self.total

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sources": sources,
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.global_source_response import GlobalSourceResponse

        d = dict(src_dict)
        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = GlobalSourceResponse.from_dict(sources_item_data)

            sources.append(sources_item)

        total = d.pop("total")

        limit = d.pop("limit")

        offset = d.pop("offset")

        global_source_list_response = cls(
            sources=sources,
            total=total,
            limit=limit,
            offset=offset,
        )

        global_source_list_response.additional_properties = d
        return global_source_list_response

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
