from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyCreateUserProjectProjectsPost")


@_attrs_define
class BodyCreateUserProjectProjectsPost:
    """
    Attributes:
        name (str):
        repo_url (str):
        user_id (str):
        status (str | Unset):  Default: 'new'.
        organization_id (str | Unset):
    """

    name: str
    repo_url: str
    user_id: str
    status: str | Unset = "new"
    organization_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        repo_url = self.repo_url

        user_id = self.user_id

        status = self.status

        organization_id = self.organization_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "repoUrl": repo_url,
                "user_id": user_id,
            }
        )
        if status is not UNSET:
            field_dict["status"] = status
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        repo_url = d.pop("repoUrl")

        user_id = d.pop("user_id")

        status = d.pop("status", UNSET)

        organization_id = d.pop("organization_id", UNSET)

        body_create_user_project_projects_post = cls(
            name=name,
            repo_url=repo_url,
            user_id=user_id,
            status=status,
            organization_id=organization_id,
        )

        body_create_user_project_projects_post.additional_properties = d
        return body_create_user_project_projects_post

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
