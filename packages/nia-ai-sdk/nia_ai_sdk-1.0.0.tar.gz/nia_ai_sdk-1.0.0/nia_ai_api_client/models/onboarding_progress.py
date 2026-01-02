from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OnboardingProgress")


@_attrs_define
class OnboardingProgress:
    """
    Attributes:
        current_step (int):
        completed_steps (list[int] | Unset):
        org_id (None | str | Unset):
        github_connected (bool | Unset):  Default: False.
        mcp_configured (bool | Unset):  Default: False.
    """

    current_step: int
    completed_steps: list[int] | Unset = UNSET
    org_id: None | str | Unset = UNSET
    github_connected: bool | Unset = False
    mcp_configured: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        current_step = self.current_step

        completed_steps: list[int] | Unset = UNSET
        if not isinstance(self.completed_steps, Unset):
            completed_steps = self.completed_steps

        org_id: None | str | Unset
        if isinstance(self.org_id, Unset):
            org_id = UNSET
        else:
            org_id = self.org_id

        github_connected = self.github_connected

        mcp_configured = self.mcp_configured

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_step": current_step,
            }
        )
        if completed_steps is not UNSET:
            field_dict["completed_steps"] = completed_steps
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if github_connected is not UNSET:
            field_dict["github_connected"] = github_connected
        if mcp_configured is not UNSET:
            field_dict["mcp_configured"] = mcp_configured

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        current_step = d.pop("current_step")

        completed_steps = cast(list[int], d.pop("completed_steps", UNSET))

        def _parse_org_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        org_id = _parse_org_id(d.pop("org_id", UNSET))

        github_connected = d.pop("github_connected", UNSET)

        mcp_configured = d.pop("mcp_configured", UNSET)

        onboarding_progress = cls(
            current_step=current_step,
            completed_steps=completed_steps,
            org_id=org_id,
            github_connected=github_connected,
            mcp_configured=mcp_configured,
        )

        onboarding_progress.additional_properties = d
        return onboarding_progress

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
