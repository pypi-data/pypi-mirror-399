from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RepositoryIndexResponse")


@_attrs_define
class RepositoryIndexResponse:
    """Response for indexing a repository.

    Attributes:
        message (str): Status message
        project_id (str): Created project ID
        repository (str): Repository identifier
        branch (str): Branch being indexed
        status (str): Current status
        is_global (bool | None | Unset): Whether using global deduplication
        global_source_id (None | str | Unset): Global source ID if applicable
    """

    message: str
    project_id: str
    repository: str
    branch: str
    status: str
    is_global: bool | None | Unset = UNSET
    global_source_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message

        project_id = self.project_id

        repository = self.repository

        branch = self.branch

        status = self.status

        is_global: bool | None | Unset
        if isinstance(self.is_global, Unset):
            is_global = UNSET
        else:
            is_global = self.is_global

        global_source_id: None | str | Unset
        if isinstance(self.global_source_id, Unset):
            global_source_id = UNSET
        else:
            global_source_id = self.global_source_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "project_id": project_id,
                "repository": repository,
                "branch": branch,
                "status": status,
            }
        )
        if is_global is not UNSET:
            field_dict["is_global"] = is_global
        if global_source_id is not UNSET:
            field_dict["global_source_id"] = global_source_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message = d.pop("message")

        project_id = d.pop("project_id")

        repository = d.pop("repository")

        branch = d.pop("branch")

        status = d.pop("status")

        def _parse_is_global(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_global = _parse_is_global(d.pop("is_global", UNSET))

        def _parse_global_source_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        global_source_id = _parse_global_source_id(d.pop("global_source_id", UNSET))

        repository_index_response = cls(
            message=message,
            project_id=project_id,
            repository=repository,
            branch=branch,
            status=status,
            is_global=is_global,
            global_source_id=global_source_id,
        )

        repository_index_response.additional_properties = d
        return repository_index_response

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
