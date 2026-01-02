from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IndexingPreferencesUpdateRequest")


@_attrs_define
class IndexingPreferencesUpdateRequest:
    """
    Attributes:
        codebases (bool | None | Unset):
        documentation (bool | None | Unset):
    """

    codebases: bool | None | Unset = UNSET
    documentation: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        codebases: bool | None | Unset
        if isinstance(self.codebases, Unset):
            codebases = UNSET
        else:
            codebases = self.codebases

        documentation: bool | None | Unset
        if isinstance(self.documentation, Unset):
            documentation = UNSET
        else:
            documentation = self.documentation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if codebases is not UNSET:
            field_dict["codebases"] = codebases
        if documentation is not UNSET:
            field_dict["documentation"] = documentation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_codebases(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        codebases = _parse_codebases(d.pop("codebases", UNSET))

        def _parse_documentation(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        documentation = _parse_documentation(d.pop("documentation", UNSET))

        indexing_preferences_update_request = cls(
            codebases=codebases,
            documentation=documentation,
        )

        indexing_preferences_update_request.additional_properties = d
        return indexing_preferences_update_request

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
