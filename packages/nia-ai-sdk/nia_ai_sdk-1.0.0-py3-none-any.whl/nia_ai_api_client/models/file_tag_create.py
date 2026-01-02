from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileTagCreate")


@_attrs_define
class FileTagCreate:
    """Model for creating file tags

    Attributes:
        tag_name (str):
        file_path (str):
        project_id (str):
        user_id (str):
        description (None | str | Unset):
    """

    tag_name: str
    file_path: str
    project_id: str
    user_id: str
    description: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tag_name = self.tag_name

        file_path = self.file_path

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
                "tag_name": tag_name,
                "file_path": file_path,
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
        tag_name = d.pop("tag_name")

        file_path = d.pop("file_path")

        project_id = d.pop("project_id")

        user_id = d.pop("user_id")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        file_tag_create = cls(
            tag_name=tag_name,
            file_path=file_path,
            project_id=project_id,
            user_id=user_id,
            description=description,
        )

        file_tag_create.additional_properties = d
        return file_tag_create

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
