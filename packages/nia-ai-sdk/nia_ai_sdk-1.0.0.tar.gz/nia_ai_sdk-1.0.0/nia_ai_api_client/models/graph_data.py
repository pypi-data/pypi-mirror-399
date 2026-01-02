from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.graph_data_stats import GraphDataStats
    from ..models.graph_link import GraphLink
    from ..models.graph_node import GraphNode


T = TypeVar("T", bound="GraphData")


@_attrs_define
class GraphData:
    """
    Attributes:
        nodes (list[GraphNode]):
        links (list[GraphLink]):
        stats (GraphDataStats):
    """

    nodes: list[GraphNode]
    links: list[GraphLink]
    stats: GraphDataStats
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        nodes = []
        for nodes_item_data in self.nodes:
            nodes_item = nodes_item_data.to_dict()
            nodes.append(nodes_item)

        links = []
        for links_item_data in self.links:
            links_item = links_item_data.to_dict()
            links.append(links_item)

        stats = self.stats.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nodes": nodes,
                "links": links,
                "stats": stats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_data_stats import GraphDataStats
        from ..models.graph_link import GraphLink
        from ..models.graph_node import GraphNode

        d = dict(src_dict)
        nodes = []
        _nodes = d.pop("nodes")
        for nodes_item_data in _nodes:
            nodes_item = GraphNode.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        links = []
        _links = d.pop("links")
        for links_item_data in _links:
            links_item = GraphLink.from_dict(links_item_data)

            links.append(links_item)

        stats = GraphDataStats.from_dict(d.pop("stats"))

        graph_data = cls(
            nodes=nodes,
            links=links,
            stats=stats,
        )

        graph_data.additional_properties = d
        return graph_data

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
