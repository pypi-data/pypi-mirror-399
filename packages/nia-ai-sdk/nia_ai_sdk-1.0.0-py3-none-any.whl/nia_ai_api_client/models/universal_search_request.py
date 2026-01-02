from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UniversalSearchRequest")


@_attrs_define
class UniversalSearchRequest:
    """Request body for internal universal search.

    Attributes:
        query (str): Search query
        user_id (str): Authenticated user ID
        top_k (int | Unset): Number of results Default: 20.
        include_repos (bool | Unset): Include repositories Default: True.
        include_docs (bool | Unset): Include documentation Default: True.
        alpha (float | Unset): Vector vs BM25 weight Default: 0.7.
        compress_output (bool | Unset): Use AI to compress results Default: False.
        max_sources (int | Unset): Max source namespaces to deep search Default: 5.
        sources_for_answer (int | Unset): Number of results to use for AI answer Default: 10.
        model (None | str | Unset): Model to use for AI answer (frontend only)
        thinking_enabled (bool | Unset): Enable extended thinking (frontend only) Default: False.
        thinking_budget (int | None | Unset): Thinking token budget
    """

    query: str
    user_id: str
    top_k: int | Unset = 20
    include_repos: bool | Unset = True
    include_docs: bool | Unset = True
    alpha: float | Unset = 0.7
    compress_output: bool | Unset = False
    max_sources: int | Unset = 5
    sources_for_answer: int | Unset = 10
    model: None | str | Unset = UNSET
    thinking_enabled: bool | Unset = False
    thinking_budget: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        user_id = self.user_id

        top_k = self.top_k

        include_repos = self.include_repos

        include_docs = self.include_docs

        alpha = self.alpha

        compress_output = self.compress_output

        max_sources = self.max_sources

        sources_for_answer = self.sources_for_answer

        model: None | str | Unset
        if isinstance(self.model, Unset):
            model = UNSET
        else:
            model = self.model

        thinking_enabled = self.thinking_enabled

        thinking_budget: int | None | Unset
        if isinstance(self.thinking_budget, Unset):
            thinking_budget = UNSET
        else:
            thinking_budget = self.thinking_budget

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
                "user_id": user_id,
            }
        )
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if include_repos is not UNSET:
            field_dict["include_repos"] = include_repos
        if include_docs is not UNSET:
            field_dict["include_docs"] = include_docs
        if alpha is not UNSET:
            field_dict["alpha"] = alpha
        if compress_output is not UNSET:
            field_dict["compress_output"] = compress_output
        if max_sources is not UNSET:
            field_dict["max_sources"] = max_sources
        if sources_for_answer is not UNSET:
            field_dict["sources_for_answer"] = sources_for_answer
        if model is not UNSET:
            field_dict["model"] = model
        if thinking_enabled is not UNSET:
            field_dict["thinking_enabled"] = thinking_enabled
        if thinking_budget is not UNSET:
            field_dict["thinking_budget"] = thinking_budget

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        user_id = d.pop("user_id")

        top_k = d.pop("top_k", UNSET)

        include_repos = d.pop("include_repos", UNSET)

        include_docs = d.pop("include_docs", UNSET)

        alpha = d.pop("alpha", UNSET)

        compress_output = d.pop("compress_output", UNSET)

        max_sources = d.pop("max_sources", UNSET)

        sources_for_answer = d.pop("sources_for_answer", UNSET)

        def _parse_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model = _parse_model(d.pop("model", UNSET))

        thinking_enabled = d.pop("thinking_enabled", UNSET)

        def _parse_thinking_budget(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        thinking_budget = _parse_thinking_budget(d.pop("thinking_budget", UNSET))

        universal_search_request = cls(
            query=query,
            user_id=user_id,
            top_k=top_k,
            include_repos=include_repos,
            include_docs=include_docs,
            alpha=alpha,
            compress_output=compress_output,
            max_sources=max_sources,
            sources_for_answer=sources_for_answer,
            model=model,
            thinking_enabled=thinking_enabled,
            thinking_budget=thinking_budget,
        )

        universal_search_request.additional_properties = d
        return universal_search_request

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
