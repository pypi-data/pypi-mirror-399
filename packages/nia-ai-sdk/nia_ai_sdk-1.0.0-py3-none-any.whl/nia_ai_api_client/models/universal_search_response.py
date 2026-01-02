from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.universal_search_result_item import UniversalSearchResultItem


T = TypeVar("T", bound="UniversalSearchResponse")


@_attrs_define
class UniversalSearchResponse:
    """Response from universal search.

    Attributes:
        results (list[UniversalSearchResultItem]):
        sources_searched (int):
        query_time_ms (int):
        errors (list[str] | None | Unset):
        answer (None | str | Unset):
    """

    results: list[UniversalSearchResultItem]
    sources_searched: int
    query_time_ms: int
    errors: list[str] | None | Unset = UNSET
    answer: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        sources_searched = self.sources_searched

        query_time_ms = self.query_time_ms

        errors: list[str] | None | Unset
        if isinstance(self.errors, Unset):
            errors = UNSET
        elif isinstance(self.errors, list):
            errors = self.errors

        else:
            errors = self.errors

        answer: None | str | Unset
        if isinstance(self.answer, Unset):
            answer = UNSET
        else:
            answer = self.answer

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "results": results,
                "sources_searched": sources_searched,
                "query_time_ms": query_time_ms,
            }
        )
        if errors is not UNSET:
            field_dict["errors"] = errors
        if answer is not UNSET:
            field_dict["answer"] = answer

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.universal_search_result_item import UniversalSearchResultItem

        d = dict(src_dict)
        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = UniversalSearchResultItem.from_dict(results_item_data)

            results.append(results_item)

        sources_searched = d.pop("sources_searched")

        query_time_ms = d.pop("query_time_ms")

        def _parse_errors(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                errors_type_0 = cast(list[str], data)

                return errors_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        errors = _parse_errors(d.pop("errors", UNSET))

        def _parse_answer(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        answer = _parse_answer(d.pop("answer", UNSET))

        universal_search_response = cls(
            results=results,
            sources_searched=sources_searched,
            query_time_ms=query_time_ms,
            errors=errors,
            answer=answer,
        )

        universal_search_response.additional_properties = d
        return universal_search_response

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
