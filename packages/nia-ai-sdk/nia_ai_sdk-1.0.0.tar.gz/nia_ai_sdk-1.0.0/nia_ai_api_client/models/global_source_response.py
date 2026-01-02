from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.global_source_response_metadata import GlobalSourceResponseMetadata
    from ..models.global_source_response_update_settings_type_0 import GlobalSourceResponseUpdateSettingsType0
    from ..models.global_source_response_update_state_type_0 import GlobalSourceResponseUpdateStateType0


T = TypeVar("T", bound="GlobalSourceResponse")


@_attrs_define
class GlobalSourceResponse:
    """
    Attributes:
        canonical_id (str):
        canonical_url (str):
        source_type (str):
        status (str):
        namespace (str):
        subscriber_count (int | Unset):  Default: 0.
        indexed_at (None | str | Unset):
        created_at (None | str | Unset):
        metadata (GlobalSourceResponseMetadata | Unset):
        display_name (None | str | Unset):
        tokens (int | None | Unset):
        snippets (int | None | Unset):
        update_settings (GlobalSourceResponseUpdateSettingsType0 | None | Unset):
        update_state (GlobalSourceResponseUpdateStateType0 | None | Unset):
    """

    canonical_id: str
    canonical_url: str
    source_type: str
    status: str
    namespace: str
    subscriber_count: int | Unset = 0
    indexed_at: None | str | Unset = UNSET
    created_at: None | str | Unset = UNSET
    metadata: GlobalSourceResponseMetadata | Unset = UNSET
    display_name: None | str | Unset = UNSET
    tokens: int | None | Unset = UNSET
    snippets: int | None | Unset = UNSET
    update_settings: GlobalSourceResponseUpdateSettingsType0 | None | Unset = UNSET
    update_state: GlobalSourceResponseUpdateStateType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.global_source_response_update_settings_type_0 import GlobalSourceResponseUpdateSettingsType0
        from ..models.global_source_response_update_state_type_0 import GlobalSourceResponseUpdateStateType0

        canonical_id = self.canonical_id

        canonical_url = self.canonical_url

        source_type = self.source_type

        status = self.status

        namespace = self.namespace

        subscriber_count = self.subscriber_count

        indexed_at: None | str | Unset
        if isinstance(self.indexed_at, Unset):
            indexed_at = UNSET
        else:
            indexed_at = self.indexed_at

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        tokens: int | None | Unset
        if isinstance(self.tokens, Unset):
            tokens = UNSET
        else:
            tokens = self.tokens

        snippets: int | None | Unset
        if isinstance(self.snippets, Unset):
            snippets = UNSET
        else:
            snippets = self.snippets

        update_settings: dict[str, Any] | None | Unset
        if isinstance(self.update_settings, Unset):
            update_settings = UNSET
        elif isinstance(self.update_settings, GlobalSourceResponseUpdateSettingsType0):
            update_settings = self.update_settings.to_dict()
        else:
            update_settings = self.update_settings

        update_state: dict[str, Any] | None | Unset
        if isinstance(self.update_state, Unset):
            update_state = UNSET
        elif isinstance(self.update_state, GlobalSourceResponseUpdateStateType0):
            update_state = self.update_state.to_dict()
        else:
            update_state = self.update_state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "canonical_id": canonical_id,
                "canonical_url": canonical_url,
                "source_type": source_type,
                "status": status,
                "namespace": namespace,
            }
        )
        if subscriber_count is not UNSET:
            field_dict["subscriber_count"] = subscriber_count
        if indexed_at is not UNSET:
            field_dict["indexed_at"] = indexed_at
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if tokens is not UNSET:
            field_dict["tokens"] = tokens
        if snippets is not UNSET:
            field_dict["snippets"] = snippets
        if update_settings is not UNSET:
            field_dict["update_settings"] = update_settings
        if update_state is not UNSET:
            field_dict["update_state"] = update_state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.global_source_response_metadata import GlobalSourceResponseMetadata
        from ..models.global_source_response_update_settings_type_0 import GlobalSourceResponseUpdateSettingsType0
        from ..models.global_source_response_update_state_type_0 import GlobalSourceResponseUpdateStateType0

        d = dict(src_dict)
        canonical_id = d.pop("canonical_id")

        canonical_url = d.pop("canonical_url")

        source_type = d.pop("source_type")

        status = d.pop("status")

        namespace = d.pop("namespace")

        subscriber_count = d.pop("subscriber_count", UNSET)

        def _parse_indexed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        indexed_at = _parse_indexed_at(d.pop("indexed_at", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: GlobalSourceResponseMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = GlobalSourceResponseMetadata.from_dict(_metadata)

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_tokens(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        tokens = _parse_tokens(d.pop("tokens", UNSET))

        def _parse_snippets(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        snippets = _parse_snippets(d.pop("snippets", UNSET))

        def _parse_update_settings(data: object) -> GlobalSourceResponseUpdateSettingsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                update_settings_type_0 = GlobalSourceResponseUpdateSettingsType0.from_dict(data)

                return update_settings_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GlobalSourceResponseUpdateSettingsType0 | None | Unset, data)

        update_settings = _parse_update_settings(d.pop("update_settings", UNSET))

        def _parse_update_state(data: object) -> GlobalSourceResponseUpdateStateType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                update_state_type_0 = GlobalSourceResponseUpdateStateType0.from_dict(data)

                return update_state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GlobalSourceResponseUpdateStateType0 | None | Unset, data)

        update_state = _parse_update_state(d.pop("update_state", UNSET))

        global_source_response = cls(
            canonical_id=canonical_id,
            canonical_url=canonical_url,
            source_type=source_type,
            status=status,
            namespace=namespace,
            subscriber_count=subscriber_count,
            indexed_at=indexed_at,
            created_at=created_at,
            metadata=metadata,
            display_name=display_name,
            tokens=tokens,
            snippets=snippets,
            update_settings=update_settings,
            update_state=update_state,
        )

        global_source_response.additional_properties = d
        return global_source_response

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
