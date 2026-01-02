from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.member_usage_response import MemberUsageResponse
    from ..models.organization_usage_analytics_response_totals import OrganizationUsageAnalyticsResponseTotals


T = TypeVar("T", bound="OrganizationUsageAnalyticsResponse")


@_attrs_define
class OrganizationUsageAnalyticsResponse:
    """
    Attributes:
        org_id (str):
        org_name (str):
        period (str):
        tier (str):
        totals (OrganizationUsageAnalyticsResponseTotals):
        members (list[MemberUsageResponse]):
        member_count (int):
        active_seats (int):
    """

    org_id: str
    org_name: str
    period: str
    tier: str
    totals: OrganizationUsageAnalyticsResponseTotals
    members: list[MemberUsageResponse]
    member_count: int
    active_seats: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        org_id = self.org_id

        org_name = self.org_name

        period = self.period

        tier = self.tier

        totals = self.totals.to_dict()

        members = []
        for members_item_data in self.members:
            members_item = members_item_data.to_dict()
            members.append(members_item)

        member_count = self.member_count

        active_seats = self.active_seats

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "org_id": org_id,
                "org_name": org_name,
                "period": period,
                "tier": tier,
                "totals": totals,
                "members": members,
                "member_count": member_count,
                "active_seats": active_seats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.member_usage_response import MemberUsageResponse
        from ..models.organization_usage_analytics_response_totals import OrganizationUsageAnalyticsResponseTotals

        d = dict(src_dict)
        org_id = d.pop("org_id")

        org_name = d.pop("org_name")

        period = d.pop("period")

        tier = d.pop("tier")

        totals = OrganizationUsageAnalyticsResponseTotals.from_dict(d.pop("totals"))

        members = []
        _members = d.pop("members")
        for members_item_data in _members:
            members_item = MemberUsageResponse.from_dict(members_item_data)

            members.append(members_item)

        member_count = d.pop("member_count")

        active_seats = d.pop("active_seats")

        organization_usage_analytics_response = cls(
            org_id=org_id,
            org_name=org_name,
            period=period,
            tier=tier,
            totals=totals,
            members=members,
            member_count=member_count,
            active_seats=active_seats,
        )

        organization_usage_analytics_response.additional_properties = d
        return organization_usage_analytics_response

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
