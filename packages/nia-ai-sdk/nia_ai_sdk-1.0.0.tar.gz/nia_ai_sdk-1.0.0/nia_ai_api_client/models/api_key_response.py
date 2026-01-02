from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.api_key_limits import ApiKeyLimits
    from ..models.api_key_response_metadata_type_0 import ApiKeyResponseMetadataType0
    from ..models.api_key_usage import ApiKeyUsage


T = TypeVar("T", bound="ApiKeyResponse")


@_attrs_define
class ApiKeyResponse:
    """
    Attributes:
        id (str):
        key (str):
        label (str):
        user_id (str):
        created_at (datetime.datetime):
        usage (ApiKeyUsage):
        last_used (datetime.datetime | None | Unset):
        limits (ApiKeyLimits | None | Unset):
        is_active (bool | Unset):  Default: True.
        billing_rate (float | Unset):  Default: 0.0.
        metadata (ApiKeyResponseMetadataType0 | None | Unset):
    """

    id: str
    key: str
    label: str
    user_id: str
    created_at: datetime.datetime
    usage: ApiKeyUsage
    last_used: datetime.datetime | None | Unset = UNSET
    limits: ApiKeyLimits | None | Unset = UNSET
    is_active: bool | Unset = True
    billing_rate: float | Unset = 0.0
    metadata: ApiKeyResponseMetadataType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.api_key_limits import ApiKeyLimits
        from ..models.api_key_response_metadata_type_0 import ApiKeyResponseMetadataType0

        id = self.id

        key = self.key

        label = self.label

        user_id = self.user_id

        created_at = self.created_at.isoformat()

        usage = self.usage.to_dict()

        last_used: None | str | Unset
        if isinstance(self.last_used, Unset):
            last_used = UNSET
        elif isinstance(self.last_used, datetime.datetime):
            last_used = self.last_used.isoformat()
        else:
            last_used = self.last_used

        limits: dict[str, Any] | None | Unset
        if isinstance(self.limits, Unset):
            limits = UNSET
        elif isinstance(self.limits, ApiKeyLimits):
            limits = self.limits.to_dict()
        else:
            limits = self.limits

        is_active = self.is_active

        billing_rate = self.billing_rate

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, ApiKeyResponseMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "key": key,
                "label": label,
                "user_id": user_id,
                "created_at": created_at,
                "usage": usage,
            }
        )
        if last_used is not UNSET:
            field_dict["last_used"] = last_used
        if limits is not UNSET:
            field_dict["limits"] = limits
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if billing_rate is not UNSET:
            field_dict["billing_rate"] = billing_rate
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.api_key_limits import ApiKeyLimits
        from ..models.api_key_response_metadata_type_0 import ApiKeyResponseMetadataType0
        from ..models.api_key_usage import ApiKeyUsage

        d = dict(src_dict)
        id = d.pop("id")

        key = d.pop("key")

        label = d.pop("label")

        user_id = d.pop("user_id")

        created_at = isoparse(d.pop("created_at"))

        usage = ApiKeyUsage.from_dict(d.pop("usage"))

        def _parse_last_used(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_used_type_0 = isoparse(data)

                return last_used_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_used = _parse_last_used(d.pop("last_used", UNSET))

        def _parse_limits(data: object) -> ApiKeyLimits | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                limits_type_0 = ApiKeyLimits.from_dict(data)

                return limits_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ApiKeyLimits | None | Unset, data)

        limits = _parse_limits(d.pop("limits", UNSET))

        is_active = d.pop("is_active", UNSET)

        billing_rate = d.pop("billing_rate", UNSET)

        def _parse_metadata(data: object) -> ApiKeyResponseMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = ApiKeyResponseMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ApiKeyResponseMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        api_key_response = cls(
            id=id,
            key=key,
            label=label,
            user_id=user_id,
            created_at=created_at,
            usage=usage,
            last_used=last_used,
            limits=limits,
            is_active=is_active,
            billing_rate=billing_rate,
            metadata=metadata,
        )

        api_key_response.additional_properties = d
        return api_key_response

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
