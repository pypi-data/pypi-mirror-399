from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.graph_link_properties import GraphLinkProperties


T = TypeVar("T", bound="GraphLink")


@_attrs_define
class GraphLink:
    """
    Attributes:
        id (int):
        source (int):
        target (int):
        type_ (str):
        properties (GraphLinkProperties | Unset):
    """

    id: int
    source: int
    target: int
    type_: str
    properties: GraphLinkProperties | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        source = self.source

        target = self.target

        type_ = self.type_

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "source": source,
                "target": target,
                "type": type_,
            }
        )
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_link_properties import GraphLinkProperties

        d = dict(src_dict)
        id = d.pop("id")

        source = d.pop("source")

        target = d.pop("target")

        type_ = d.pop("type")

        _properties = d.pop("properties", UNSET)
        properties: GraphLinkProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = GraphLinkProperties.from_dict(_properties)

        graph_link = cls(
            id=id,
            source=source,
            target=target,
            type_=type_,
            properties=properties,
        )

        graph_link.additional_properties = d
        return graph_link

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
