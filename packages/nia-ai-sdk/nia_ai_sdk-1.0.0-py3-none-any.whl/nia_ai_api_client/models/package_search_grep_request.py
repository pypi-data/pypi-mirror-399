from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchGrepRequest")


@_attrs_define
class PackageSearchGrepRequest:
    """Request model for package grep search

    Attributes:
        registry (str): Registry: crates_io, golang_proxy, npm, py_pi, or ruby_gems
        package_name (str): Package name
        pattern (str): Regex pattern to search
        version (None | str | Unset): Package version
        language (None | str | Unset): Language filter
        filename_sha256 (None | str | Unset): File SHA256 filter
        a (int | None | Unset): Lines after match
        b (int | None | Unset): Lines before match
        c (int | None | Unset): Lines before and after match
        head_limit (int | None | Unset): Limit results
        output_mode (str | Unset): Output mode: content, files_with_matches, or count Default: 'content'.
    """

    registry: str
    package_name: str
    pattern: str
    version: None | str | Unset = UNSET
    language: None | str | Unset = UNSET
    filename_sha256: None | str | Unset = UNSET
    a: int | None | Unset = UNSET
    b: int | None | Unset = UNSET
    c: int | None | Unset = UNSET
    head_limit: int | None | Unset = UNSET
    output_mode: str | Unset = "content"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registry = self.registry

        package_name = self.package_name

        pattern = self.pattern

        version: None | str | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        language: None | str | Unset
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        filename_sha256: None | str | Unset
        if isinstance(self.filename_sha256, Unset):
            filename_sha256 = UNSET
        else:
            filename_sha256 = self.filename_sha256

        a: int | None | Unset
        if isinstance(self.a, Unset):
            a = UNSET
        else:
            a = self.a

        b: int | None | Unset
        if isinstance(self.b, Unset):
            b = UNSET
        else:
            b = self.b

        c: int | None | Unset
        if isinstance(self.c, Unset):
            c = UNSET
        else:
            c = self.c

        head_limit: int | None | Unset
        if isinstance(self.head_limit, Unset):
            head_limit = UNSET
        else:
            head_limit = self.head_limit

        output_mode = self.output_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registry": registry,
                "package_name": package_name,
                "pattern": pattern,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if language is not UNSET:
            field_dict["language"] = language
        if filename_sha256 is not UNSET:
            field_dict["filename_sha256"] = filename_sha256
        if a is not UNSET:
            field_dict["a"] = a
        if b is not UNSET:
            field_dict["b"] = b
        if c is not UNSET:
            field_dict["c"] = c
        if head_limit is not UNSET:
            field_dict["head_limit"] = head_limit
        if output_mode is not UNSET:
            field_dict["output_mode"] = output_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        registry = d.pop("registry")

        package_name = d.pop("package_name")

        pattern = d.pop("pattern")

        def _parse_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        def _parse_language(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        language = _parse_language(d.pop("language", UNSET))

        def _parse_filename_sha256(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename_sha256 = _parse_filename_sha256(d.pop("filename_sha256", UNSET))

        def _parse_a(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        a = _parse_a(d.pop("a", UNSET))

        def _parse_b(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        b = _parse_b(d.pop("b", UNSET))

        def _parse_c(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        c = _parse_c(d.pop("c", UNSET))

        def _parse_head_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        head_limit = _parse_head_limit(d.pop("head_limit", UNSET))

        output_mode = d.pop("output_mode", UNSET)

        package_search_grep_request = cls(
            registry=registry,
            package_name=package_name,
            pattern=pattern,
            version=version,
            language=language,
            filename_sha256=filename_sha256,
            a=a,
            b=b,
            c=c,
            head_limit=head_limit,
            output_mode=output_mode,
        )

        package_search_grep_request.additional_properties = d
        return package_search_grep_request

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
