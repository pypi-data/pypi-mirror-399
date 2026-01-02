from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchGitHubRepo")


@_attrs_define
class WebSearchGitHubRepo:
    """A GitHub repository from web search.

    Attributes:
        url (str): Repository URL
        owner_repo (str): owner/repo identifier
        title (str): Repository title
        summary (str | Unset): Repository summary Default: ''.
        highlights (list[str] | Unset): Search highlights
        published_date (None | str | Unset): Publication date
    """

    url: str
    owner_repo: str
    title: str
    summary: str | Unset = ""
    highlights: list[str] | Unset = UNSET
    published_date: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        owner_repo = self.owner_repo

        title = self.title

        summary = self.summary

        highlights: list[str] | Unset = UNSET
        if not isinstance(self.highlights, Unset):
            highlights = self.highlights

        published_date: None | str | Unset
        if isinstance(self.published_date, Unset):
            published_date = UNSET
        else:
            published_date = self.published_date

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "owner_repo": owner_repo,
                "title": title,
            }
        )
        if summary is not UNSET:
            field_dict["summary"] = summary
        if highlights is not UNSET:
            field_dict["highlights"] = highlights
        if published_date is not UNSET:
            field_dict["published_date"] = published_date

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        owner_repo = d.pop("owner_repo")

        title = d.pop("title")

        summary = d.pop("summary", UNSET)

        highlights = cast(list[str], d.pop("highlights", UNSET))

        def _parse_published_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        published_date = _parse_published_date(d.pop("published_date", UNSET))

        web_search_git_hub_repo = cls(
            url=url,
            owner_repo=owner_repo,
            title=title,
            summary=summary,
            highlights=highlights,
            published_date=published_date,
        )

        web_search_git_hub_repo.additional_properties = d
        return web_search_git_hub_repo

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
