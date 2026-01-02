from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_list_response_contexts_item import ContextListResponseContextsItem
    from ..models.pagination_info import PaginationInfo


T = TypeVar("T", bound="ContextListResponse")


@_attrs_define
class ContextListResponse:
    """Response for listing contexts.

    Attributes:
        pagination (PaginationInfo): Pagination metadata.
        contexts (list[ContextListResponseContextsItem] | Unset): List of contexts
    """

    pagination: PaginationInfo
    contexts: list[ContextListResponseContextsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pagination = self.pagination.to_dict()

        contexts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.contexts, Unset):
            contexts = []
            for contexts_item_data in self.contexts:
                contexts_item = contexts_item_data.to_dict()
                contexts.append(contexts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pagination": pagination,
            }
        )
        if contexts is not UNSET:
            field_dict["contexts"] = contexts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_list_response_contexts_item import ContextListResponseContextsItem
        from ..models.pagination_info import PaginationInfo

        d = dict(src_dict)
        pagination = PaginationInfo.from_dict(d.pop("pagination"))

        _contexts = d.pop("contexts", UNSET)
        contexts: list[ContextListResponseContextsItem] | Unset = UNSET
        if _contexts is not UNSET:
            contexts = []
            for contexts_item_data in _contexts:
                contexts_item = ContextListResponseContextsItem.from_dict(contexts_item_data)

                contexts.append(contexts_item)

        context_list_response = cls(
            pagination=pagination,
            contexts=contexts,
        )

        context_list_response.additional_properties = d
        return context_list_response

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
