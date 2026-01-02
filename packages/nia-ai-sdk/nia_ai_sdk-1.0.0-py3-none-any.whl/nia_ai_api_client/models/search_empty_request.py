from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchEmptyRequest")


@_attrs_define
class SearchEmptyRequest:
    """
    Attributes:
        user_id (str):
        user_email (str):
        query (str):
        repo_name (None | str | Unset):
    """

    user_id: str
    user_email: str
    query: str
    repo_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        user_email = self.user_email

        query = self.query

        repo_name: None | str | Unset
        if isinstance(self.repo_name, Unset):
            repo_name = UNSET
        else:
            repo_name = self.repo_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "user_email": user_email,
                "query": query,
            }
        )
        if repo_name is not UNSET:
            field_dict["repo_name"] = repo_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        user_email = d.pop("user_email")

        query = d.pop("query")

        def _parse_repo_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        repo_name = _parse_repo_name(d.pop("repo_name", UNSET))

        search_empty_request = cls(
            user_id=user_id,
            user_email=user_email,
            query=query,
            repo_name=repo_name,
        )

        search_empty_request.additional_properties = d
        return search_empty_request

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
