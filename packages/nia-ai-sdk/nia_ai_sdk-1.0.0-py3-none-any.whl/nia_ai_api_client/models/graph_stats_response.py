from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.graph_stats_response_node_counts import GraphStatsResponseNodeCounts
    from ..models.graph_stats_response_relationship_counts import GraphStatsResponseRelationshipCounts


T = TypeVar("T", bound="GraphStatsResponse")


@_attrs_define
class GraphStatsResponse:
    """
    Attributes:
        total_nodes (int):
        total_relationships (int):
        node_counts (GraphStatsResponseNodeCounts):
        relationship_counts (GraphStatsResponseRelationshipCounts):
        is_empty (bool):
    """

    total_nodes: int
    total_relationships: int
    node_counts: GraphStatsResponseNodeCounts
    relationship_counts: GraphStatsResponseRelationshipCounts
    is_empty: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_nodes = self.total_nodes

        total_relationships = self.total_relationships

        node_counts = self.node_counts.to_dict()

        relationship_counts = self.relationship_counts.to_dict()

        is_empty = self.is_empty

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_nodes": total_nodes,
                "total_relationships": total_relationships,
                "node_counts": node_counts,
                "relationship_counts": relationship_counts,
                "is_empty": is_empty,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_stats_response_node_counts import GraphStatsResponseNodeCounts
        from ..models.graph_stats_response_relationship_counts import GraphStatsResponseRelationshipCounts

        d = dict(src_dict)
        total_nodes = d.pop("total_nodes")

        total_relationships = d.pop("total_relationships")

        node_counts = GraphStatsResponseNodeCounts.from_dict(d.pop("node_counts"))

        relationship_counts = GraphStatsResponseRelationshipCounts.from_dict(d.pop("relationship_counts"))

        is_empty = d.pop("is_empty")

        graph_stats_response = cls(
            total_nodes=total_nodes,
            total_relationships=total_relationships,
            node_counts=node_counts,
            relationship_counts=relationship_counts,
            is_empty=is_empty,
        )

        graph_stats_response.additional_properties = d
        return graph_stats_response

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
