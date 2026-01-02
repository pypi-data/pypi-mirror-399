from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocGrepMatch")


@_attrs_define
class DocGrepMatch:
    """A grep match in documentation.

    Attributes:
        path (str): Virtual path
        snippet (str): Matching snippet
        title (None | str | Unset): Page title
        url (None | str | Unset): Original URL
        line_number (int | None | Unset): Line number if applicable
    """

    path: str
    snippet: str
    title: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    line_number: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        snippet = self.snippet

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        line_number: int | None | Unset
        if isinstance(self.line_number, Unset):
            line_number = UNSET
        else:
            line_number = self.line_number

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "snippet": snippet,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title
        if url is not UNSET:
            field_dict["url"] = url
        if line_number is not UNSET:
            field_dict["line_number"] = line_number

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        snippet = d.pop("snippet")

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        def _parse_line_number(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        line_number = _parse_line_number(d.pop("line_number", UNSET))

        doc_grep_match = cls(
            path=path,
            snippet=snippet,
            title=title,
            url=url,
            line_number=line_number,
        )

        doc_grep_match.additional_properties = d
        return doc_grep_match

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
