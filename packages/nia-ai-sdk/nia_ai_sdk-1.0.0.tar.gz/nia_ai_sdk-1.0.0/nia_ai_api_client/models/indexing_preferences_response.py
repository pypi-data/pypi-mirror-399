from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="IndexingPreferencesResponse")


@_attrs_define
class IndexingPreferencesResponse:
    """
    Attributes:
        codebases (bool):
        documentation (bool):
    """

    codebases: bool
    documentation: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        codebases = self.codebases

        documentation = self.documentation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "codebases": codebases,
                "documentation": documentation,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        codebases = d.pop("codebases")

        documentation = d.pop("documentation")

        indexing_preferences_response = cls(
            codebases=codebases,
            documentation=documentation,
        )

        indexing_preferences_response.additional_properties = d
        return indexing_preferences_response

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
