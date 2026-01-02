from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResearchPaperResponse")


@_attrs_define
class ResearchPaperResponse:
    """Response model for research paper indexing.

    Attributes:
        id (str):
        arxiv_id (str):
        title (str):
        authors (list[str]):
        abstract (str):
        categories (list[str]):
        primary_category (str):
        status (str):
        created_at (str):
        updated_at (str):
        pdf_url (str):
        abs_url (str):
        chunk_count (int | Unset):  Default: 0.
        doi (None | str | Unset):
        published_date (None | str | Unset):
        error (None | str | Unset):
    """

    id: str
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    categories: list[str]
    primary_category: str
    status: str
    created_at: str
    updated_at: str
    pdf_url: str
    abs_url: str
    chunk_count: int | Unset = 0
    doi: None | str | Unset = UNSET
    published_date: None | str | Unset = UNSET
    error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        arxiv_id = self.arxiv_id

        title = self.title

        authors = self.authors

        abstract = self.abstract

        categories = self.categories

        primary_category = self.primary_category

        status = self.status

        created_at = self.created_at

        updated_at = self.updated_at

        pdf_url = self.pdf_url

        abs_url = self.abs_url

        chunk_count = self.chunk_count

        doi: None | str | Unset
        if isinstance(self.doi, Unset):
            doi = UNSET
        else:
            doi = self.doi

        published_date: None | str | Unset
        if isinstance(self.published_date, Unset):
            published_date = UNSET
        else:
            published_date = self.published_date

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "categories": categories,
                "primary_category": primary_category,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
                "pdf_url": pdf_url,
                "abs_url": abs_url,
            }
        )
        if chunk_count is not UNSET:
            field_dict["chunk_count"] = chunk_count
        if doi is not UNSET:
            field_dict["doi"] = doi
        if published_date is not UNSET:
            field_dict["published_date"] = published_date
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        arxiv_id = d.pop("arxiv_id")

        title = d.pop("title")

        authors = cast(list[str], d.pop("authors"))

        abstract = d.pop("abstract")

        categories = cast(list[str], d.pop("categories"))

        primary_category = d.pop("primary_category")

        status = d.pop("status")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        pdf_url = d.pop("pdf_url")

        abs_url = d.pop("abs_url")

        chunk_count = d.pop("chunk_count", UNSET)

        def _parse_doi(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        doi = _parse_doi(d.pop("doi", UNSET))

        def _parse_published_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        published_date = _parse_published_date(d.pop("published_date", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        research_paper_response = cls(
            id=id,
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            categories=categories,
            primary_category=primary_category,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            pdf_url=pdf_url,
            abs_url=abs_url,
            chunk_count=chunk_count,
            doi=doi,
            published_date=published_date,
            error=error,
        )

        research_paper_response.additional_properties = d
        return research_paper_response

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
