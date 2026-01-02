from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.indexed_resource import IndexedResource
    from ..models.search_query import SearchQuery


T = TypeVar("T", bound="NiaReferences")


@_attrs_define
class NiaReferences:
    """Structured tracking of NIA resources used during conversation.

    Attributes:
        indexed_resources (list[IndexedResource] | Unset):
        search_queries (list[SearchQuery] | Unset):
        session_summary (None | str | Unset):
    """

    indexed_resources: list[IndexedResource] | Unset = UNSET
    search_queries: list[SearchQuery] | Unset = UNSET
    session_summary: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        indexed_resources: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.indexed_resources, Unset):
            indexed_resources = []
            for indexed_resources_item_data in self.indexed_resources:
                indexed_resources_item = indexed_resources_item_data.to_dict()
                indexed_resources.append(indexed_resources_item)

        search_queries: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.search_queries, Unset):
            search_queries = []
            for search_queries_item_data in self.search_queries:
                search_queries_item = search_queries_item_data.to_dict()
                search_queries.append(search_queries_item)

        session_summary: None | str | Unset
        if isinstance(self.session_summary, Unset):
            session_summary = UNSET
        else:
            session_summary = self.session_summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if indexed_resources is not UNSET:
            field_dict["indexed_resources"] = indexed_resources
        if search_queries is not UNSET:
            field_dict["search_queries"] = search_queries
        if session_summary is not UNSET:
            field_dict["session_summary"] = session_summary

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.indexed_resource import IndexedResource
        from ..models.search_query import SearchQuery

        d = dict(src_dict)
        _indexed_resources = d.pop("indexed_resources", UNSET)
        indexed_resources: list[IndexedResource] | Unset = UNSET
        if _indexed_resources is not UNSET:
            indexed_resources = []
            for indexed_resources_item_data in _indexed_resources:
                indexed_resources_item = IndexedResource.from_dict(indexed_resources_item_data)

                indexed_resources.append(indexed_resources_item)

        _search_queries = d.pop("search_queries", UNSET)
        search_queries: list[SearchQuery] | Unset = UNSET
        if _search_queries is not UNSET:
            search_queries = []
            for search_queries_item_data in _search_queries:
                search_queries_item = SearchQuery.from_dict(search_queries_item_data)

                search_queries.append(search_queries_item)

        def _parse_session_summary(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        session_summary = _parse_session_summary(d.pop("session_summary", UNSET))

        nia_references = cls(
            indexed_resources=indexed_resources,
            search_queries=search_queries,
            session_summary=session_summary,
        )

        nia_references.additional_properties = d
        return nia_references

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
