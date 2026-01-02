from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tree_item import TreeItem


T = TypeVar("T", bound="RepositoryTreeResponse")


@_attrs_define
class RepositoryTreeResponse:
    """Response for repository tree endpoints.

    Attributes:
        tree (list[TreeItem] | Unset): Tree items
        formatted_tree (None | str | Unset): Human-readable tree structure
        total_items (int | Unset): Total number of items Default: 0.
        max_depth (int | Unset): Maximum tree depth Default: 0.
        truncated (bool | Unset): Whether the tree was truncated Default: False.
    """

    tree: list[TreeItem] | Unset = UNSET
    formatted_tree: None | str | Unset = UNSET
    total_items: int | Unset = 0
    max_depth: int | Unset = 0
    truncated: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tree: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tree, Unset):
            tree = []
            for tree_item_data in self.tree:
                tree_item = tree_item_data.to_dict()
                tree.append(tree_item)

        formatted_tree: None | str | Unset
        if isinstance(self.formatted_tree, Unset):
            formatted_tree = UNSET
        else:
            formatted_tree = self.formatted_tree

        total_items = self.total_items

        max_depth = self.max_depth

        truncated = self.truncated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tree is not UNSET:
            field_dict["tree"] = tree
        if formatted_tree is not UNSET:
            field_dict["formatted_tree"] = formatted_tree
        if total_items is not UNSET:
            field_dict["total_items"] = total_items
        if max_depth is not UNSET:
            field_dict["max_depth"] = max_depth
        if truncated is not UNSET:
            field_dict["truncated"] = truncated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tree_item import TreeItem

        d = dict(src_dict)
        _tree = d.pop("tree", UNSET)
        tree: list[TreeItem] | Unset = UNSET
        if _tree is not UNSET:
            tree = []
            for tree_item_data in _tree:
                tree_item = TreeItem.from_dict(tree_item_data)

                tree.append(tree_item)

        def _parse_formatted_tree(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        formatted_tree = _parse_formatted_tree(d.pop("formatted_tree", UNSET))

        total_items = d.pop("total_items", UNSET)

        max_depth = d.pop("max_depth", UNSET)

        truncated = d.pop("truncated", UNSET)

        repository_tree_response = cls(
            tree=tree,
            formatted_tree=formatted_tree,
            total_items=total_items,
            max_depth=max_depth,
            truncated=truncated,
        )

        repository_tree_response.additional_properties = d
        return repository_tree_response

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
