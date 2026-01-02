from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.universal_search_result_source import UniversalSearchResultSource


T = TypeVar("T", bound="UniversalSearchResultItem")


@_attrs_define
class UniversalSearchResultItem:
    """A single search result.

    Attributes:
        content (str):
        score (float):
        source (UniversalSearchResultSource): Source info for a search result.
    """

    content: str
    score: float
    source: UniversalSearchResultSource
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        score = self.score

        source = self.source.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
                "score": score,
                "source": source,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.universal_search_result_source import UniversalSearchResultSource

        d = dict(src_dict)
        content = d.pop("content")

        score = d.pop("score")

        source = UniversalSearchResultSource.from_dict(d.pop("source"))

        universal_search_result_item = cls(
            content=content,
            score=score,
            source=source,
        )

        universal_search_result_item.additional_properties = d
        return universal_search_result_item

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
