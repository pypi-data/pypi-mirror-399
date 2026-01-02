from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.member_usage_response_usage import MemberUsageResponseUsage


T = TypeVar("T", bound="MemberUsageResponse")


@_attrs_define
class MemberUsageResponse:
    """
    Attributes:
        user_id (str):
        role (str):
        pro_enabled (bool):
        usage (MemberUsageResponseUsage):
        user_name (None | str | Unset):
        user_email (None | str | Unset):
    """

    user_id: str
    role: str
    pro_enabled: bool
    usage: MemberUsageResponseUsage
    user_name: None | str | Unset = UNSET
    user_email: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        role = self.role

        pro_enabled = self.pro_enabled

        usage = self.usage.to_dict()

        user_name: None | str | Unset
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        user_email: None | str | Unset
        if isinstance(self.user_email, Unset):
            user_email = UNSET
        else:
            user_email = self.user_email

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "role": role,
                "pro_enabled": pro_enabled,
                "usage": usage,
            }
        )
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if user_email is not UNSET:
            field_dict["user_email"] = user_email

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_usage_response_usage import MemberUsageResponseUsage

        d = dict(src_dict)
        user_id = d.pop("user_id")

        role = d.pop("role")

        pro_enabled = d.pop("pro_enabled")

        usage = MemberUsageResponseUsage.from_dict(d.pop("usage"))

        def _parse_user_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_name = _parse_user_name(d.pop("user_name", UNSET))

        def _parse_user_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_email = _parse_user_email(d.pop("user_email", UNSET))

        member_usage_response = cls(
            user_id=user_id,
            role=role,
            pro_enabled=pro_enabled,
            usage=usage,
            user_name=user_name,
            user_email=user_email,
        )

        member_usage_response.additional_properties = d
        return member_usage_response

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
