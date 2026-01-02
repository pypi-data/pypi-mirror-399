from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.update_history_response_update_settings_type_0 import UpdateHistoryResponseUpdateSettingsType0
    from ..models.update_history_response_update_state_type_0 import UpdateHistoryResponseUpdateStateType0


T = TypeVar("T", bound="UpdateHistoryResponse")


@_attrs_define
class UpdateHistoryResponse:
    """
    Attributes:
        canonical_id (str):
        status (str):
        indexed_at (None | str | Unset):
        update_settings (None | Unset | UpdateHistoryResponseUpdateSettingsType0):
        update_state (None | Unset | UpdateHistoryResponseUpdateStateType0):
    """

    canonical_id: str
    status: str
    indexed_at: None | str | Unset = UNSET
    update_settings: None | Unset | UpdateHistoryResponseUpdateSettingsType0 = UNSET
    update_state: None | Unset | UpdateHistoryResponseUpdateStateType0 = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.update_history_response_update_settings_type_0 import UpdateHistoryResponseUpdateSettingsType0
        from ..models.update_history_response_update_state_type_0 import UpdateHistoryResponseUpdateStateType0

        canonical_id = self.canonical_id

        status = self.status

        indexed_at: None | str | Unset
        if isinstance(self.indexed_at, Unset):
            indexed_at = UNSET
        else:
            indexed_at = self.indexed_at

        update_settings: dict[str, Any] | None | Unset
        if isinstance(self.update_settings, Unset):
            update_settings = UNSET
        elif isinstance(self.update_settings, UpdateHistoryResponseUpdateSettingsType0):
            update_settings = self.update_settings.to_dict()
        else:
            update_settings = self.update_settings

        update_state: dict[str, Any] | None | Unset
        if isinstance(self.update_state, Unset):
            update_state = UNSET
        elif isinstance(self.update_state, UpdateHistoryResponseUpdateStateType0):
            update_state = self.update_state.to_dict()
        else:
            update_state = self.update_state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "canonical_id": canonical_id,
                "status": status,
            }
        )
        if indexed_at is not UNSET:
            field_dict["indexed_at"] = indexed_at
        if update_settings is not UNSET:
            field_dict["update_settings"] = update_settings
        if update_state is not UNSET:
            field_dict["update_state"] = update_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.update_history_response_update_settings_type_0 import UpdateHistoryResponseUpdateSettingsType0
        from ..models.update_history_response_update_state_type_0 import UpdateHistoryResponseUpdateStateType0

        d = dict(src_dict)
        canonical_id = d.pop("canonical_id")

        status = d.pop("status")

        def _parse_indexed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        indexed_at = _parse_indexed_at(d.pop("indexed_at", UNSET))

        def _parse_update_settings(data: object) -> None | Unset | UpdateHistoryResponseUpdateSettingsType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                update_settings_type_0 = UpdateHistoryResponseUpdateSettingsType0.from_dict(data)

                return update_settings_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdateHistoryResponseUpdateSettingsType0, data)

        update_settings = _parse_update_settings(d.pop("update_settings", UNSET))

        def _parse_update_state(data: object) -> None | Unset | UpdateHistoryResponseUpdateStateType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                update_state_type_0 = UpdateHistoryResponseUpdateStateType0.from_dict(data)

                return update_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UpdateHistoryResponseUpdateStateType0, data)

        update_state = _parse_update_state(d.pop("update_state", UNSET))

        update_history_response = cls(
            canonical_id=canonical_id,
            status=status,
            indexed_at=indexed_at,
            update_settings=update_settings,
            update_state=update_state,
        )

        update_history_response.additional_properties = d
        return update_history_response

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
