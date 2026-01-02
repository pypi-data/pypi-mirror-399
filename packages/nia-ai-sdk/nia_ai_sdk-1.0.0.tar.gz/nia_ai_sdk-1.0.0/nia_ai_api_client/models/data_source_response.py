from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_source_response_details_type_0 import DataSourceResponseDetailsType0


T = TypeVar("T", bound="DataSourceResponse")


@_attrs_define
class DataSourceResponse:
    """
    Attributes:
        id (str):
        status (str):
        created_at (str):
        updated_at (str):
        user_id (str):
        source_type (str):
        url (None | str | Unset):
        page_count (int | Unset):  Default: 0.
        chunk_count (int | Unset):  Default: 0.
        project_id (None | str | Unset):
        is_active (bool | Unset):  Default: True.
        file_name (None | str | Unset):
        display_name (None | str | Unset):
        progress (int | None | Unset):
        message (None | str | Unset):
        details (DataSourceResponseDetailsType0 | None | Unset):
        error (None | str | Unset):
        error_code (None | str | Unset):
        global_source_id (None | str | Unset):
        global_namespace (None | str | Unset):
    """

    id: str
    status: str
    created_at: str
    updated_at: str
    user_id: str
    source_type: str
    url: None | str | Unset = UNSET
    page_count: int | Unset = 0
    chunk_count: int | Unset = 0
    project_id: None | str | Unset = UNSET
    is_active: bool | Unset = True
    file_name: None | str | Unset = UNSET
    display_name: None | str | Unset = UNSET
    progress: int | None | Unset = UNSET
    message: None | str | Unset = UNSET
    details: DataSourceResponseDetailsType0 | None | Unset = UNSET
    error: None | str | Unset = UNSET
    error_code: None | str | Unset = UNSET
    global_source_id: None | str | Unset = UNSET
    global_namespace: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_source_response_details_type_0 import DataSourceResponseDetailsType0

        id = self.id

        status = self.status

        created_at = self.created_at

        updated_at = self.updated_at

        user_id = self.user_id

        source_type = self.source_type

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        page_count = self.page_count

        chunk_count = self.chunk_count

        project_id: None | str | Unset
        if isinstance(self.project_id, Unset):
            project_id = UNSET
        else:
            project_id = self.project_id

        is_active = self.is_active

        file_name: None | str | Unset
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        progress: int | None | Unset
        if isinstance(self.progress, Unset):
            progress = UNSET
        else:
            progress = self.progress

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        details: dict[str, Any] | None | Unset
        if isinstance(self.details, Unset):
            details = UNSET
        elif isinstance(self.details, DataSourceResponseDetailsType0):
            details = self.details.to_dict()
        else:
            details = self.details

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        error_code: None | str | Unset
        if isinstance(self.error_code, Unset):
            error_code = UNSET
        else:
            error_code = self.error_code

        global_source_id: None | str | Unset
        if isinstance(self.global_source_id, Unset):
            global_source_id = UNSET
        else:
            global_source_id = self.global_source_id

        global_namespace: None | str | Unset
        if isinstance(self.global_namespace, Unset):
            global_namespace = UNSET
        else:
            global_namespace = self.global_namespace

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
                "user_id": user_id,
                "source_type": source_type,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url
        if page_count is not UNSET:
            field_dict["page_count"] = page_count
        if chunk_count is not UNSET:
            field_dict["chunk_count"] = chunk_count
        if project_id is not UNSET:
            field_dict["project_id"] = project_id
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if progress is not UNSET:
            field_dict["progress"] = progress
        if message is not UNSET:
            field_dict["message"] = message
        if details is not UNSET:
            field_dict["details"] = details
        if error is not UNSET:
            field_dict["error"] = error
        if error_code is not UNSET:
            field_dict["error_code"] = error_code
        if global_source_id is not UNSET:
            field_dict["global_source_id"] = global_source_id
        if global_namespace is not UNSET:
            field_dict["global_namespace"] = global_namespace

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_source_response_details_type_0 import DataSourceResponseDetailsType0

        d = dict(src_dict)
        id = d.pop("id")

        status = d.pop("status")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        user_id = d.pop("user_id")

        source_type = d.pop("source_type")

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        page_count = d.pop("page_count", UNSET)

        chunk_count = d.pop("chunk_count", UNSET)

        def _parse_project_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_id = _parse_project_id(d.pop("project_id", UNSET))

        is_active = d.pop("is_active", UNSET)

        def _parse_file_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_name = _parse_file_name(d.pop("file_name", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_progress(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        progress = _parse_progress(d.pop("progress", UNSET))

        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_details(data: object) -> DataSourceResponseDetailsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                details_type_0 = DataSourceResponseDetailsType0.from_dict(data)

                return details_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataSourceResponseDetailsType0 | None | Unset, data)

        details = _parse_details(d.pop("details", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_error_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_code = _parse_error_code(d.pop("error_code", UNSET))

        def _parse_global_source_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        global_source_id = _parse_global_source_id(d.pop("global_source_id", UNSET))

        def _parse_global_namespace(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        global_namespace = _parse_global_namespace(d.pop("global_namespace", UNSET))

        data_source_response = cls(
            id=id,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            user_id=user_id,
            source_type=source_type,
            url=url,
            page_count=page_count,
            chunk_count=chunk_count,
            project_id=project_id,
            is_active=is_active,
            file_name=file_name,
            display_name=display_name,
            progress=progress,
            message=message,
            details=details,
            error=error,
            error_code=error_code,
            global_source_id=global_source_id,
            global_namespace=global_namespace,
        )

        data_source_response.additional_properties = d
        return data_source_response

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
