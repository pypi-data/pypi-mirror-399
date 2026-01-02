from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_semantic_search_metadata import ContextSemanticSearchMetadata
    from ..models.context_semantic_search_response_results_item import ContextSemanticSearchResponseResultsItem
    from ..models.context_semantic_search_suggestions import ContextSemanticSearchSuggestions


T = TypeVar("T", bound="ContextSemanticSearchResponse")


@_attrs_define
class ContextSemanticSearchResponse:
    """Response for semantic search in contexts.

    Attributes:
        search_query (str): The search query used
        search_metadata (ContextSemanticSearchMetadata): Metadata for semantic search.
        suggestions (ContextSemanticSearchSuggestions): Suggestions from semantic search.
        results (list[ContextSemanticSearchResponseResultsItem] | Unset): Search results with scores
    """

    search_query: str
    search_metadata: ContextSemanticSearchMetadata
    suggestions: ContextSemanticSearchSuggestions
    results: list[ContextSemanticSearchResponseResultsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        search_query = self.search_query

        search_metadata = self.search_metadata.to_dict()

        suggestions = self.suggestions.to_dict()

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "search_query": search_query,
                "search_metadata": search_metadata,
                "suggestions": suggestions,
            }
        )
        if results is not UNSET:
            field_dict["results"] = results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_semantic_search_metadata import ContextSemanticSearchMetadata
        from ..models.context_semantic_search_response_results_item import ContextSemanticSearchResponseResultsItem
        from ..models.context_semantic_search_suggestions import ContextSemanticSearchSuggestions

        d = dict(src_dict)
        search_query = d.pop("search_query")

        search_metadata = ContextSemanticSearchMetadata.from_dict(d.pop("search_metadata"))

        suggestions = ContextSemanticSearchSuggestions.from_dict(d.pop("suggestions"))

        _results = d.pop("results", UNSET)
        results: list[ContextSemanticSearchResponseResultsItem] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = ContextSemanticSearchResponseResultsItem.from_dict(results_item_data)

                results.append(results_item)

        context_semantic_search_response = cls(
            search_query=search_query,
            search_metadata=search_metadata,
            suggestions=suggestions,
            results=results,
        )

        context_semantic_search_response.additional_properties = d
        return context_semantic_search_response

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
