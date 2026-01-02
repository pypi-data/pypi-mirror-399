from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ContextSemanticSearchMetadata")


@_attrs_define
class ContextSemanticSearchMetadata:
    """Metadata for semantic search.

    Attributes:
        search_type (str | Unset): Type of search performed Default: 'semantic'.
        total_results (int | Unset): Number of results Default: 0.
        vector_matches (int | Unset): Number of vector matches Default: 0.
        mongodb_matches (int | Unset): Number of MongoDB matches Default: 0.
    """

    search_type: str | Unset = "semantic"
    total_results: int | Unset = 0
    vector_matches: int | Unset = 0
    mongodb_matches: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        search_type = self.search_type

        total_results = self.total_results

        vector_matches = self.vector_matches

        mongodb_matches = self.mongodb_matches

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if search_type is not UNSET:
            field_dict["search_type"] = search_type
        if total_results is not UNSET:
            field_dict["total_results"] = total_results
        if vector_matches is not UNSET:
            field_dict["vector_matches"] = vector_matches
        if mongodb_matches is not UNSET:
            field_dict["mongodb_matches"] = mongodb_matches

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        search_type = d.pop("search_type", UNSET)

        total_results = d.pop("total_results", UNSET)

        vector_matches = d.pop("vector_matches", UNSET)

        mongodb_matches = d.pop("mongodb_matches", UNSET)

        context_semantic_search_metadata = cls(
            search_type=search_type,
            total_results=total_results,
            vector_matches=vector_matches,
            mongodb_matches=mongodb_matches,
        )

        context_semantic_search_metadata.additional_properties = d
        return context_semantic_search_metadata

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
