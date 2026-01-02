from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FileMetadataModel")


@_attrs_define
class FileMetadataModel:
    """File interaction metadata for context organization.

    Attributes:
        edited_files (list[str] | Unset): Paths of edited files
        read_files (list[str] | Unset): Paths of read files
        primary_directory (None | str | Unset): Main directory where work happened
        file_extensions (list[str] | Unset): File extensions involved
    """

    edited_files: list[str] | Unset = UNSET
    read_files: list[str] | Unset = UNSET
    primary_directory: None | str | Unset = UNSET
    file_extensions: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        edited_files: list[str] | Unset = UNSET
        if not isinstance(self.edited_files, Unset):
            edited_files = self.edited_files

        read_files: list[str] | Unset = UNSET
        if not isinstance(self.read_files, Unset):
            read_files = self.read_files

        primary_directory: None | str | Unset
        if isinstance(self.primary_directory, Unset):
            primary_directory = UNSET
        else:
            primary_directory = self.primary_directory

        file_extensions: list[str] | Unset = UNSET
        if not isinstance(self.file_extensions, Unset):
            file_extensions = self.file_extensions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if edited_files is not UNSET:
            field_dict["edited_files"] = edited_files
        if read_files is not UNSET:
            field_dict["read_files"] = read_files
        if primary_directory is not UNSET:
            field_dict["primary_directory"] = primary_directory
        if file_extensions is not UNSET:
            field_dict["file_extensions"] = file_extensions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        edited_files = cast(list[str], d.pop("edited_files", UNSET))

        read_files = cast(list[str], d.pop("read_files", UNSET))

        def _parse_primary_directory(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_directory = _parse_primary_directory(d.pop("primary_directory", UNSET))

        file_extensions = cast(list[str], d.pop("file_extensions", UNSET))

        file_metadata_model = cls(
            edited_files=edited_files,
            read_files=read_files,
            primary_directory=primary_directory,
            file_extensions=file_extensions,
        )

        file_metadata_model.additional_properties = d
        return file_metadata_model

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
