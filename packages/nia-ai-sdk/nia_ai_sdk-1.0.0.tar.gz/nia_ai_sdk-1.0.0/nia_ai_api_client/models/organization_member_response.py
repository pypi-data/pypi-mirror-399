from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OrganizationMemberResponse")


@_attrs_define
class OrganizationMemberResponse:
    """
    Attributes:
        id (str):
        organization_id (str):
        user_id (str):
        role (str):
        pro_enabled (bool):
        joined_at (str):
        user_email (None | str | Unset):
        user_name (None | str | Unset):
        seat_assigned_at (None | str | Unset):
        seat_last_used_at (None | str | Unset):
        seat_status (None | str | Unset):
    """

    id: str
    organization_id: str
    user_id: str
    role: str
    pro_enabled: bool
    joined_at: str
    user_email: None | str | Unset = UNSET
    user_name: None | str | Unset = UNSET
    seat_assigned_at: None | str | Unset = UNSET
    seat_last_used_at: None | str | Unset = UNSET
    seat_status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        organization_id = self.organization_id

        user_id = self.user_id

        role = self.role

        pro_enabled = self.pro_enabled

        joined_at = self.joined_at

        user_email: None | str | Unset
        if isinstance(self.user_email, Unset):
            user_email = UNSET
        else:
            user_email = self.user_email

        user_name: None | str | Unset
        if isinstance(self.user_name, Unset):
            user_name = UNSET
        else:
            user_name = self.user_name

        seat_assigned_at: None | str | Unset
        if isinstance(self.seat_assigned_at, Unset):
            seat_assigned_at = UNSET
        else:
            seat_assigned_at = self.seat_assigned_at

        seat_last_used_at: None | str | Unset
        if isinstance(self.seat_last_used_at, Unset):
            seat_last_used_at = UNSET
        else:
            seat_last_used_at = self.seat_last_used_at

        seat_status: None | str | Unset
        if isinstance(self.seat_status, Unset):
            seat_status = UNSET
        else:
            seat_status = self.seat_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "organization_id": organization_id,
                "user_id": user_id,
                "role": role,
                "pro_enabled": pro_enabled,
                "joined_at": joined_at,
            }
        )
        if user_email is not UNSET:
            field_dict["user_email"] = user_email
        if user_name is not UNSET:
            field_dict["user_name"] = user_name
        if seat_assigned_at is not UNSET:
            field_dict["seat_assigned_at"] = seat_assigned_at
        if seat_last_used_at is not UNSET:
            field_dict["seat_last_used_at"] = seat_last_used_at
        if seat_status is not UNSET:
            field_dict["seat_status"] = seat_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        organization_id = d.pop("organization_id")

        user_id = d.pop("user_id")

        role = d.pop("role")

        pro_enabled = d.pop("pro_enabled")

        joined_at = d.pop("joined_at")

        def _parse_user_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_email = _parse_user_email(d.pop("user_email", UNSET))

        def _parse_user_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        user_name = _parse_user_name(d.pop("user_name", UNSET))

        def _parse_seat_assigned_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seat_assigned_at = _parse_seat_assigned_at(d.pop("seat_assigned_at", UNSET))

        def _parse_seat_last_used_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seat_last_used_at = _parse_seat_last_used_at(d.pop("seat_last_used_at", UNSET))

        def _parse_seat_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        seat_status = _parse_seat_status(d.pop("seat_status", UNSET))

        organization_member_response = cls(
            id=id,
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            pro_enabled=pro_enabled,
            joined_at=joined_at,
            user_email=user_email,
            user_name=user_name,
            seat_assigned_at=seat_assigned_at,
            seat_last_used_at=seat_last_used_at,
            seat_status=seat_status,
        )

        organization_member_response.additional_properties = d
        return organization_member_response

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
