from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SubscriptionFeatures")


@_attrs_define
class SubscriptionFeatures:
    """
    Attributes:
        max_repo_size (int):
        private_repos (bool):
        multi_repo_querying (bool):
        unlimited_chat (bool):
        integrations (list[str]):
        indexing_limit (int | None | Unset):
        indexing_is_lifetime (bool | None | Unset):
        queries_limit (int | None | Unset):
        deep_research_limit (int | None | Unset):
        web_search_limit (int | None | Unset):
        package_search_limit (int | None | Unset):
        contexts_limit (int | None | Unset):
        oracle_limit (int | None | Unset):
    """

    max_repo_size: int
    private_repos: bool
    multi_repo_querying: bool
    unlimited_chat: bool
    integrations: list[str]
    indexing_limit: int | None | Unset = UNSET
    indexing_is_lifetime: bool | None | Unset = UNSET
    queries_limit: int | None | Unset = UNSET
    deep_research_limit: int | None | Unset = UNSET
    web_search_limit: int | None | Unset = UNSET
    package_search_limit: int | None | Unset = UNSET
    contexts_limit: int | None | Unset = UNSET
    oracle_limit: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_repo_size = self.max_repo_size

        private_repos = self.private_repos

        multi_repo_querying = self.multi_repo_querying

        unlimited_chat = self.unlimited_chat

        integrations = self.integrations

        indexing_limit: int | None | Unset
        if isinstance(self.indexing_limit, Unset):
            indexing_limit = UNSET
        else:
            indexing_limit = self.indexing_limit

        indexing_is_lifetime: bool | None | Unset
        if isinstance(self.indexing_is_lifetime, Unset):
            indexing_is_lifetime = UNSET
        else:
            indexing_is_lifetime = self.indexing_is_lifetime

        queries_limit: int | None | Unset
        if isinstance(self.queries_limit, Unset):
            queries_limit = UNSET
        else:
            queries_limit = self.queries_limit

        deep_research_limit: int | None | Unset
        if isinstance(self.deep_research_limit, Unset):
            deep_research_limit = UNSET
        else:
            deep_research_limit = self.deep_research_limit

        web_search_limit: int | None | Unset
        if isinstance(self.web_search_limit, Unset):
            web_search_limit = UNSET
        else:
            web_search_limit = self.web_search_limit

        package_search_limit: int | None | Unset
        if isinstance(self.package_search_limit, Unset):
            package_search_limit = UNSET
        else:
            package_search_limit = self.package_search_limit

        contexts_limit: int | None | Unset
        if isinstance(self.contexts_limit, Unset):
            contexts_limit = UNSET
        else:
            contexts_limit = self.contexts_limit

        oracle_limit: int | None | Unset
        if isinstance(self.oracle_limit, Unset):
            oracle_limit = UNSET
        else:
            oracle_limit = self.oracle_limit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "maxRepoSize": max_repo_size,
                "privateRepos": private_repos,
                "multiRepoQuerying": multi_repo_querying,
                "unlimitedChat": unlimited_chat,
                "integrations": integrations,
            }
        )
        if indexing_limit is not UNSET:
            field_dict["indexingLimit"] = indexing_limit
        if indexing_is_lifetime is not UNSET:
            field_dict["indexingIsLifetime"] = indexing_is_lifetime
        if queries_limit is not UNSET:
            field_dict["queriesLimit"] = queries_limit
        if deep_research_limit is not UNSET:
            field_dict["deepResearchLimit"] = deep_research_limit
        if web_search_limit is not UNSET:
            field_dict["webSearchLimit"] = web_search_limit
        if package_search_limit is not UNSET:
            field_dict["packageSearchLimit"] = package_search_limit
        if contexts_limit is not UNSET:
            field_dict["contextsLimit"] = contexts_limit
        if oracle_limit is not UNSET:
            field_dict["oracleLimit"] = oracle_limit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_repo_size = d.pop("maxRepoSize")

        private_repos = d.pop("privateRepos")

        multi_repo_querying = d.pop("multiRepoQuerying")

        unlimited_chat = d.pop("unlimitedChat")

        integrations = cast(list[str], d.pop("integrations"))

        def _parse_indexing_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        indexing_limit = _parse_indexing_limit(d.pop("indexingLimit", UNSET))

        def _parse_indexing_is_lifetime(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        indexing_is_lifetime = _parse_indexing_is_lifetime(d.pop("indexingIsLifetime", UNSET))

        def _parse_queries_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        queries_limit = _parse_queries_limit(d.pop("queriesLimit", UNSET))

        def _parse_deep_research_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        deep_research_limit = _parse_deep_research_limit(d.pop("deepResearchLimit", UNSET))

        def _parse_web_search_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        web_search_limit = _parse_web_search_limit(d.pop("webSearchLimit", UNSET))

        def _parse_package_search_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        package_search_limit = _parse_package_search_limit(d.pop("packageSearchLimit", UNSET))

        def _parse_contexts_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        contexts_limit = _parse_contexts_limit(d.pop("contextsLimit", UNSET))

        def _parse_oracle_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        oracle_limit = _parse_oracle_limit(d.pop("oracleLimit", UNSET))

        subscription_features = cls(
            max_repo_size=max_repo_size,
            private_repos=private_repos,
            multi_repo_querying=multi_repo_querying,
            unlimited_chat=unlimited_chat,
            integrations=integrations,
            indexing_limit=indexing_limit,
            indexing_is_lifetime=indexing_is_lifetime,
            queries_limit=queries_limit,
            deep_research_limit=deep_research_limit,
            web_search_limit=web_search_limit,
            package_search_limit=package_search_limit,
            contexts_limit=contexts_limit,
            oracle_limit=oracle_limit,
        )

        subscription_features.additional_properties = d
        return subscription_features

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
