from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ContextSemanticSearchSuggestions")


@_attrs_define
class ContextSemanticSearchSuggestions:
    """Suggestions from semantic search.

    Attributes:
        related_tags (list[str] | Unset): Related tags
        workspaces (list[str] | Unset): Related workspaces
        tips (list[str] | Unset): Search tips
    """

    related_tags: list[str] | Unset = UNSET
    workspaces: list[str] | Unset = UNSET
    tips: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        related_tags: list[str] | Unset = UNSET
        if not isinstance(self.related_tags, Unset):
            related_tags = self.related_tags

        workspaces: list[str] | Unset = UNSET
        if not isinstance(self.workspaces, Unset):
            workspaces = self.workspaces

        tips: list[str] | Unset = UNSET
        if not isinstance(self.tips, Unset):
            tips = self.tips

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if related_tags is not UNSET:
            field_dict["related_tags"] = related_tags
        if workspaces is not UNSET:
            field_dict["workspaces"] = workspaces
        if tips is not UNSET:
            field_dict["tips"] = tips

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        related_tags = cast(list[str], d.pop("related_tags", UNSET))

        workspaces = cast(list[str], d.pop("workspaces", UNSET))

        tips = cast(list[str], d.pop("tips", UNSET))

        context_semantic_search_suggestions = cls(
            related_tags=related_tags,
            workspaces=workspaces,
            tips=tips,
        )

        context_semantic_search_suggestions.additional_properties = d
        return context_semantic_search_suggestions

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
