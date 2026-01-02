from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.body_execute_cypher_query_graph_project_id_query_post_params_type_0 import (
        BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0,
    )


T = TypeVar("T", bound="BodyExecuteCypherQueryGraphProjectIdQueryPost")


@_attrs_define
class BodyExecuteCypherQueryGraphProjectIdQueryPost:
    """
    Attributes:
        query (str): Cypher query to execute
        params (BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0 | None | Unset): Query parameters
    """

    query: str
    params: BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.body_execute_cypher_query_graph_project_id_query_post_params_type_0 import (
            BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0,
        )

        query = self.query

        params: dict[str, Any] | None | Unset
        if isinstance(self.params, Unset):
            params = UNSET
        elif isinstance(self.params, BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0):
            params = self.params.to_dict()
        else:
            params = self.params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.body_execute_cypher_query_graph_project_id_query_post_params_type_0 import (
            BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0,
        )

        d = dict(src_dict)
        query = d.pop("query")

        def _parse_params(data: object) -> BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_0 = BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0.from_dict(data)

                return params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BodyExecuteCypherQueryGraphProjectIdQueryPostParamsType0 | None | Unset, data)

        params = _parse_params(d.pop("params", UNSET))

        body_execute_cypher_query_graph_project_id_query_post = cls(
            query=query,
            params=params,
        )

        body_execute_cypher_query_graph_project_id_query_post.additional_properties = d
        return body_execute_cypher_query_graph_project_id_query_post

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
