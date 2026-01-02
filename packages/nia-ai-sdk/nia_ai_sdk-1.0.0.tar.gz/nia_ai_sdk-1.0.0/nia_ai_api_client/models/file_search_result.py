from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.file_search_result_metadata import FileSearchResultMetadata


T = TypeVar("T", bound="FileSearchResult")


@_attrs_define
class FileSearchResult:
    """Model for file search results

    Attributes:
        file_path (str):
        score (float):
        tags (list[str] | Unset):
        description (None | str | Unset):
        metadata (FileSearchResultMetadata | Unset):
    """

    file_path: str
    score: float
    tags: list[str] | Unset = UNSET
    description: None | str | Unset = UNSET
    metadata: FileSearchResultMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_path = self.file_path

        score = self.score

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_path": file_path,
                "score": score,
            }
        )
        if tags is not UNSET:
            field_dict["tags"] = tags
        if description is not UNSET:
            field_dict["description"] = description
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.file_search_result_metadata import FileSearchResultMetadata

        d = dict(src_dict)
        file_path = d.pop("file_path")

        score = d.pop("score")

        tags = cast(list[str], d.pop("tags", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: FileSearchResultMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = FileSearchResultMetadata.from_dict(_metadata)

        file_search_result = cls(
            file_path=file_path,
            score=score,
            tags=tags,
            description=description,
            metadata=metadata,
        )

        file_search_result.additional_properties = d
        return file_search_result

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
