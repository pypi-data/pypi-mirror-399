from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.subscription_tier import SubscriptionTier
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.subscription_features import SubscriptionFeatures


T = TypeVar("T", bound="SubscriptionResponse")


@_attrs_define
class SubscriptionResponse:
    """
    Attributes:
        tier (SubscriptionTier):
        status (str):
        current_period_end (str):
        features (SubscriptionFeatures):
        api_requests_used (int | None | str | Unset):
        api_requests_limit (int | None | str | Unset):
        api_requests_remaining (int | None | str | Unset):
        edu_verified (bool | None | Unset):
        edu_institution (None | str | Unset):
        edu_email (None | str | Unset):
        edu_days_remaining (int | None | Unset):
    """

    tier: SubscriptionTier
    status: str
    current_period_end: str
    features: SubscriptionFeatures
    api_requests_used: int | None | str | Unset = UNSET
    api_requests_limit: int | None | str | Unset = UNSET
    api_requests_remaining: int | None | str | Unset = UNSET
    edu_verified: bool | None | Unset = UNSET
    edu_institution: None | str | Unset = UNSET
    edu_email: None | str | Unset = UNSET
    edu_days_remaining: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tier = self.tier.value

        status = self.status

        current_period_end = self.current_period_end

        features = self.features.to_dict()

        api_requests_used: int | None | str | Unset
        if isinstance(self.api_requests_used, Unset):
            api_requests_used = UNSET
        else:
            api_requests_used = self.api_requests_used

        api_requests_limit: int | None | str | Unset
        if isinstance(self.api_requests_limit, Unset):
            api_requests_limit = UNSET
        else:
            api_requests_limit = self.api_requests_limit

        api_requests_remaining: int | None | str | Unset
        if isinstance(self.api_requests_remaining, Unset):
            api_requests_remaining = UNSET
        else:
            api_requests_remaining = self.api_requests_remaining

        edu_verified: bool | None | Unset
        if isinstance(self.edu_verified, Unset):
            edu_verified = UNSET
        else:
            edu_verified = self.edu_verified

        edu_institution: None | str | Unset
        if isinstance(self.edu_institution, Unset):
            edu_institution = UNSET
        else:
            edu_institution = self.edu_institution

        edu_email: None | str | Unset
        if isinstance(self.edu_email, Unset):
            edu_email = UNSET
        else:
            edu_email = self.edu_email

        edu_days_remaining: int | None | Unset
        if isinstance(self.edu_days_remaining, Unset):
            edu_days_remaining = UNSET
        else:
            edu_days_remaining = self.edu_days_remaining

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tier": tier,
                "status": status,
                "currentPeriodEnd": current_period_end,
                "features": features,
            }
        )
        if api_requests_used is not UNSET:
            field_dict["apiRequestsUsed"] = api_requests_used
        if api_requests_limit is not UNSET:
            field_dict["apiRequestsLimit"] = api_requests_limit
        if api_requests_remaining is not UNSET:
            field_dict["apiRequestsRemaining"] = api_requests_remaining
        if edu_verified is not UNSET:
            field_dict["eduVerified"] = edu_verified
        if edu_institution is not UNSET:
            field_dict["eduInstitution"] = edu_institution
        if edu_email is not UNSET:
            field_dict["eduEmail"] = edu_email
        if edu_days_remaining is not UNSET:
            field_dict["eduDaysRemaining"] = edu_days_remaining

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.subscription_features import SubscriptionFeatures

        d = dict(src_dict)
        tier = SubscriptionTier(d.pop("tier"))

        status = d.pop("status")

        current_period_end = d.pop("currentPeriodEnd")

        features = SubscriptionFeatures.from_dict(d.pop("features"))

        def _parse_api_requests_used(data: object) -> int | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | str | Unset, data)

        api_requests_used = _parse_api_requests_used(d.pop("apiRequestsUsed", UNSET))

        def _parse_api_requests_limit(data: object) -> int | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | str | Unset, data)

        api_requests_limit = _parse_api_requests_limit(d.pop("apiRequestsLimit", UNSET))

        def _parse_api_requests_remaining(data: object) -> int | None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | str | Unset, data)

        api_requests_remaining = _parse_api_requests_remaining(d.pop("apiRequestsRemaining", UNSET))

        def _parse_edu_verified(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        edu_verified = _parse_edu_verified(d.pop("eduVerified", UNSET))

        def _parse_edu_institution(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        edu_institution = _parse_edu_institution(d.pop("eduInstitution", UNSET))

        def _parse_edu_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        edu_email = _parse_edu_email(d.pop("eduEmail", UNSET))

        def _parse_edu_days_remaining(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        edu_days_remaining = _parse_edu_days_remaining(d.pop("eduDaysRemaining", UNSET))

        subscription_response = cls(
            tier=tier,
            status=status,
            current_period_end=current_period_end,
            features=features,
            api_requests_used=api_requests_used,
            api_requests_limit=api_requests_limit,
            api_requests_remaining=api_requests_remaining,
            edu_verified=edu_verified,
            edu_institution=edu_institution,
            edu_email=edu_email,
            edu_days_remaining=edu_days_remaining,
        )

        subscription_response.additional_properties = d
        return subscription_response

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
