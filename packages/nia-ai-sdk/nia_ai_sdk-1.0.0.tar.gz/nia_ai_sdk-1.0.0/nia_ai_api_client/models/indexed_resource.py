from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IndexedResource")


@_attrs_define
class IndexedResource:
    """Represents a NIA resource (repository or documentation) with context.

    Attributes:
        identifier (str): Repository (owner/repo) or documentation URL/ID
        resource_type (str): Type: 'repository' or 'documentation'
        purpose (str): Why this resource was used/referenced
        indexed_at (None | str | Unset): When it was indexed
    """

    identifier: str
    resource_type: str
    purpose: str
    indexed_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        identifier = self.identifier

        resource_type = self.resource_type

        purpose = self.purpose

        indexed_at: None | str | Unset
        if isinstance(self.indexed_at, Unset):
            indexed_at = UNSET
        else:
            indexed_at = self.indexed_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "identifier": identifier,
                "resource_type": resource_type,
                "purpose": purpose,
            }
        )
        if indexed_at is not UNSET:
            field_dict["indexed_at"] = indexed_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        identifier = d.pop("identifier")

        resource_type = d.pop("resource_type")

        purpose = d.pop("purpose")

        def _parse_indexed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        indexed_at = _parse_indexed_at(d.pop("indexed_at", UNSET))

        indexed_resource = cls(
            identifier=identifier,
            resource_type=resource_type,
            purpose=purpose,
            indexed_at=indexed_at,
        )

        indexed_resource.additional_properties = d
        return indexed_resource

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
