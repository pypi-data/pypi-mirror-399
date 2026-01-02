from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization_metadata import OrganizationMetadata


T = TypeVar("T", bound="OrganizationResponse")


@_attrs_define
class OrganizationResponse:
    """
    Attributes:
        id (str):
        name (str):
        created_at (str):
        updated_at (str):
        slug (None | str | Unset):
        metadata (None | OrganizationMetadata | Unset):
        members_count (int | None | Unset):
        subscription_tier (None | str | Unset):
        subscription_status (None | str | Unset):
    """

    id: str
    name: str
    created_at: str
    updated_at: str
    slug: None | str | Unset = UNSET
    metadata: None | OrganizationMetadata | Unset = UNSET
    members_count: int | None | Unset = UNSET
    subscription_tier: None | str | Unset = UNSET
    subscription_status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.organization_metadata import OrganizationMetadata

        id = self.id

        name = self.name

        created_at = self.created_at

        updated_at = self.updated_at

        slug: None | str | Unset
        if isinstance(self.slug, Unset):
            slug = UNSET
        else:
            slug = self.slug

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, OrganizationMetadata):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        members_count: int | None | Unset
        if isinstance(self.members_count, Unset):
            members_count = UNSET
        else:
            members_count = self.members_count

        subscription_tier: None | str | Unset
        if isinstance(self.subscription_tier, Unset):
            subscription_tier = UNSET
        else:
            subscription_tier = self.subscription_tier

        subscription_status: None | str | Unset
        if isinstance(self.subscription_status, Unset):
            subscription_status = UNSET
        else:
            subscription_status = self.subscription_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if slug is not UNSET:
            field_dict["slug"] = slug
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if members_count is not UNSET:
            field_dict["members_count"] = members_count
        if subscription_tier is not UNSET:
            field_dict["subscription_tier"] = subscription_tier
        if subscription_status is not UNSET:
            field_dict["subscription_status"] = subscription_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.organization_metadata import OrganizationMetadata

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_slug(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        slug = _parse_slug(d.pop("slug", UNSET))

        def _parse_metadata(data: object) -> None | OrganizationMetadata | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = OrganizationMetadata.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OrganizationMetadata | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        def _parse_members_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        members_count = _parse_members_count(d.pop("members_count", UNSET))

        def _parse_subscription_tier(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        subscription_tier = _parse_subscription_tier(d.pop("subscription_tier", UNSET))

        def _parse_subscription_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        subscription_status = _parse_subscription_status(d.pop("subscription_status", UNSET))

        organization_response = cls(
            id=id,
            name=name,
            created_at=created_at,
            updated_at=updated_at,
            slug=slug,
            metadata=metadata,
            members_count=members_count,
            subscription_tier=subscription_tier,
            subscription_status=subscription_status,
        )

        organization_response.additional_properties = d
        return organization_response

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
