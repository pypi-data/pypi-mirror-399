from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationMetadata")


@_attrs_define
class OrganizationMetadata:
    """
    Attributes:
        company_size (None | str | Unset):
        company_website (None | str | Unset):
        how_heard (None | str | Unset):
    """

    company_size: None | str | Unset = UNSET
    company_website: None | str | Unset = UNSET
    how_heard: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        company_size: None | str | Unset
        if isinstance(self.company_size, Unset):
            company_size = UNSET
        else:
            company_size = self.company_size

        company_website: None | str | Unset
        if isinstance(self.company_website, Unset):
            company_website = UNSET
        else:
            company_website = self.company_website

        how_heard: None | str | Unset
        if isinstance(self.how_heard, Unset):
            how_heard = UNSET
        else:
            how_heard = self.how_heard

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if company_size is not UNSET:
            field_dict["company_size"] = company_size
        if company_website is not UNSET:
            field_dict["company_website"] = company_website
        if how_heard is not UNSET:
            field_dict["how_heard"] = how_heard

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_company_size(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        company_size = _parse_company_size(d.pop("company_size", UNSET))

        def _parse_company_website(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        company_website = _parse_company_website(d.pop("company_website", UNSET))

        def _parse_how_heard(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        how_heard = _parse_how_heard(d.pop("how_heard", UNSET))

        organization_metadata = cls(
            company_size=company_size,
            company_website=company_website,
            how_heard=how_heard,
        )

        organization_metadata.additional_properties = d
        return organization_metadata

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
