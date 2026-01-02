from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileTagResponse")


@_attrs_define
class FileTagResponse:
    """Model for file tag response

    Attributes:
        id (str):
        tag_name (str):
        file_path (str):
        created_at (datetime.datetime):
        project_id (str):
        user_id (str):
        description (None | str | Unset):
    """

    id: str
    tag_name: str
    file_path: str
    created_at: datetime.datetime
    project_id: str
    user_id: str
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        tag_name = self.tag_name

        file_path = self.file_path

        created_at = self.created_at.isoformat()

        project_id = self.project_id

        user_id = self.user_id

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "tag_name": tag_name,
                "file_path": file_path,
                "created_at": created_at,
                "project_id": project_id,
                "user_id": user_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        tag_name = d.pop("tag_name")

        file_path = d.pop("file_path")

        created_at = isoparse(d.pop("created_at"))

        project_id = d.pop("project_id")

        user_id = d.pop("user_id")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        file_tag_response = cls(
            id=id,
            tag_name=tag_name,
            file_path=file_path,
            created_at=created_at,
            project_id=project_id,
            user_id=user_id,
            description=description,
        )

        file_tag_response.additional_properties = d
        return file_tag_response

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
