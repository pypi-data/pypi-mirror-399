from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.onboarding_status_response_progress_type_0 import OnboardingStatusResponseProgressType0


T = TypeVar("T", bound="OnboardingStatusResponse")


@_attrs_define
class OnboardingStatusResponse:
    """
    Attributes:
        progress (None | OnboardingStatusResponseProgressType0):
        is_invited (bool):
        onboarding_complete (bool):
        organization_name (None | str | Unset):
    """

    progress: None | OnboardingStatusResponseProgressType0
    is_invited: bool
    onboarding_complete: bool
    organization_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.onboarding_status_response_progress_type_0 import OnboardingStatusResponseProgressType0

        progress: dict[str, Any] | None
        if isinstance(self.progress, OnboardingStatusResponseProgressType0):
            progress = self.progress.to_dict()
        else:
            progress = self.progress

        is_invited = self.is_invited

        onboarding_complete = self.onboarding_complete

        organization_name: None | str | Unset
        if isinstance(self.organization_name, Unset):
            organization_name = UNSET
        else:
            organization_name = self.organization_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "progress": progress,
                "is_invited": is_invited,
                "onboarding_complete": onboarding_complete,
            }
        )
        if organization_name is not UNSET:
            field_dict["organization_name"] = organization_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.onboarding_status_response_progress_type_0 import OnboardingStatusResponseProgressType0

        d = dict(src_dict)

        def _parse_progress(data: object) -> None | OnboardingStatusResponseProgressType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                progress_type_0 = OnboardingStatusResponseProgressType0.from_dict(data)

                return progress_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OnboardingStatusResponseProgressType0, data)

        progress = _parse_progress(d.pop("progress"))

        is_invited = d.pop("is_invited")

        onboarding_complete = d.pop("onboarding_complete")

        def _parse_organization_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_name = _parse_organization_name(d.pop("organization_name", UNSET))

        onboarding_status_response = cls(
            progress=progress,
            is_invited=is_invited,
            onboarding_complete=onboarding_complete,
            organization_name=organization_name,
        )

        onboarding_status_response.additional_properties = d
        return onboarding_status_response

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
