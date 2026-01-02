from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OracleResearchRequest")


@_attrs_define
class OracleResearchRequest:
    """
    Attributes:
        query (str): Research question to investigate
        repositories (list[str] | None | Unset): Optional list of repository identifiers
        data_sources (list[str] | None | Unset): Optional list of documentation source identifiers
        output_format (None | str | Unset): Optional output format specification
        model (None | str | Unset): Model to use: claude-opus-4-5-20251101 or claude-sonnet-4-5-20250929
    """

    query: str
    repositories: list[str] | None | Unset = UNSET
    data_sources: list[str] | None | Unset = UNSET
    output_format: None | str | Unset = UNSET
    model: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        repositories: list[str] | None | Unset
        if isinstance(self.repositories, Unset):
            repositories = UNSET
        elif isinstance(self.repositories, list):
            repositories = self.repositories

        else:
            repositories = self.repositories

        data_sources: list[str] | None | Unset
        if isinstance(self.data_sources, Unset):
            data_sources = UNSET
        elif isinstance(self.data_sources, list):
            data_sources = self.data_sources

        else:
            data_sources = self.data_sources

        output_format: None | str | Unset
        if isinstance(self.output_format, Unset):
            output_format = UNSET
        else:
            output_format = self.output_format

        model: None | str | Unset
        if isinstance(self.model, Unset):
            model = UNSET
        else:
            model = self.model

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if repositories is not UNSET:
            field_dict["repositories"] = repositories
        if data_sources is not UNSET:
            field_dict["data_sources"] = data_sources
        if output_format is not UNSET:
            field_dict["output_format"] = output_format
        if model is not UNSET:
            field_dict["model"] = model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        def _parse_repositories(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                repositories_type_0 = cast(list[str], data)

                return repositories_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        repositories = _parse_repositories(d.pop("repositories", UNSET))

        def _parse_data_sources(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_sources_type_0 = cast(list[str], data)

                return data_sources_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        data_sources = _parse_data_sources(d.pop("data_sources", UNSET))

        def _parse_output_format(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_format = _parse_output_format(d.pop("output_format", UNSET))

        def _parse_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model = _parse_model(d.pop("model", UNSET))

        oracle_research_request = cls(
            query=query,
            repositories=repositories,
            data_sources=data_sources,
            output_format=output_format,
            model=model,
        )

        oracle_research_request.additional_properties = d
        return oracle_research_request

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
