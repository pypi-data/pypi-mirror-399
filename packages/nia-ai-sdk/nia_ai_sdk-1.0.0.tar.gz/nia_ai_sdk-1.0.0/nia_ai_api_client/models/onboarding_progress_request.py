from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.onboarding_progress import OnboardingProgress


T = TypeVar("T", bound="OnboardingProgressRequest")


@_attrs_define
class OnboardingProgressRequest:
    """
    Attributes:
        user_id (str):
        progress (OnboardingProgress):
    """

    user_id: str
    progress: OnboardingProgress
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        progress = self.progress.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "progress": progress,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.onboarding_progress import OnboardingProgress

        d = dict(src_dict)
        user_id = d.pop("user_id")

        progress = OnboardingProgress.from_dict(d.pop("progress"))

        onboarding_progress_request = cls(
            user_id=user_id,
            progress=progress,
        )

        onboarding_progress_request.additional_properties = d
        return onboarding_progress_request

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
