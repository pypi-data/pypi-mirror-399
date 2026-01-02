from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_share_response_metadata import ContextShareResponseMetadata
    from ..models.edited_file import EditedFile
    from ..models.nia_references import NiaReferences


T = TypeVar("T", bound="ContextShareResponse")


@_attrs_define
class ContextShareResponse:
    """Response model for context operations.

    Attributes:
        id (str):
        user_id (str):
        title (str):
        summary (str):
        content (str):
        tags (list[str]):
        agent_source (str):
        created_at (datetime.datetime):
        metadata (ContextShareResponseMetadata):
        organization_id (None | str | Unset):
        updated_at (datetime.datetime | None | Unset):
        nia_references (NiaReferences | None | Unset):
        edited_files (list[EditedFile] | Unset):
    """

    id: str
    user_id: str
    title: str
    summary: str
    content: str
    tags: list[str]
    agent_source: str
    created_at: datetime.datetime
    metadata: ContextShareResponseMetadata
    organization_id: None | str | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    nia_references: NiaReferences | None | Unset = UNSET
    edited_files: list[EditedFile] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.nia_references import NiaReferences

        id = self.id

        user_id = self.user_id

        title = self.title

        summary = self.summary

        content = self.content

        tags = self.tags

        agent_source = self.agent_source

        created_at = self.created_at.isoformat()

        metadata = self.metadata.to_dict()

        organization_id: None | str | Unset
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        nia_references: dict[str, Any] | None | Unset
        if isinstance(self.nia_references, Unset):
            nia_references = UNSET
        elif isinstance(self.nia_references, NiaReferences):
            nia_references = self.nia_references.to_dict()
        else:
            nia_references = self.nia_references

        edited_files: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.edited_files, Unset):
            edited_files = []
            for edited_files_item_data in self.edited_files:
                edited_files_item = edited_files_item_data.to_dict()
                edited_files.append(edited_files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "user_id": user_id,
                "title": title,
                "summary": summary,
                "content": content,
                "tags": tags,
                "agent_source": agent_source,
                "created_at": created_at,
                "metadata": metadata,
            }
        )
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if nia_references is not UNSET:
            field_dict["nia_references"] = nia_references
        if edited_files is not UNSET:
            field_dict["edited_files"] = edited_files

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_share_response_metadata import ContextShareResponseMetadata
        from ..models.edited_file import EditedFile
        from ..models.nia_references import NiaReferences

        d = dict(src_dict)
        id = d.pop("id")

        user_id = d.pop("user_id")

        title = d.pop("title")

        summary = d.pop("summary")

        content = d.pop("content")

        tags = cast(list[str], d.pop("tags"))

        agent_source = d.pop("agent_source")

        created_at = isoparse(d.pop("created_at"))

        metadata = ContextShareResponseMetadata.from_dict(d.pop("metadata"))

        def _parse_organization_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = isoparse(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        def _parse_nia_references(data: object) -> NiaReferences | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                nia_references_type_0 = NiaReferences.from_dict(data)

                return nia_references_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(NiaReferences | None | Unset, data)

        nia_references = _parse_nia_references(d.pop("nia_references", UNSET))

        _edited_files = d.pop("edited_files", UNSET)
        edited_files: list[EditedFile] | Unset = UNSET
        if _edited_files is not UNSET:
            edited_files = []
            for edited_files_item_data in _edited_files:
                edited_files_item = EditedFile.from_dict(edited_files_item_data)

                edited_files.append(edited_files_item)

        context_share_response = cls(
            id=id,
            user_id=user_id,
            title=title,
            summary=summary,
            content=content,
            tags=tags,
            agent_source=agent_source,
            created_at=created_at,
            metadata=metadata,
            organization_id=organization_id,
            updated_at=updated_at,
            nia_references=nia_references,
            edited_files=edited_files,
        )

        context_share_response.additional_properties = d
        return context_share_response

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
