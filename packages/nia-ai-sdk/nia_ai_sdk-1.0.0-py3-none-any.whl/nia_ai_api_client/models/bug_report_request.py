from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BugReportRequest")


@_attrs_define
class BugReportRequest:
    """Request model for bug reports

    Attributes:
        description (str): Bug description or feature request
        bug_type (str | Unset): Type: 'bug', 'feature-request', 'improvement', or 'other' Default: 'bug'.
        additional_context (None | str | Unset): Additional context or steps to reproduce
    """

    description: str
    bug_type: str | Unset = "bug"
    additional_context: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        bug_type = self.bug_type

        additional_context: None | str | Unset
        if isinstance(self.additional_context, Unset):
            additional_context = UNSET
        else:
            additional_context = self.additional_context

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
            }
        )
        if bug_type is not UNSET:
            field_dict["bug_type"] = bug_type
        if additional_context is not UNSET:
            field_dict["additional_context"] = additional_context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description")

        bug_type = d.pop("bug_type", UNSET)

        def _parse_additional_context(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        additional_context = _parse_additional_context(d.pop("additional_context", UNSET))

        bug_report_request = cls(
            description=description,
            bug_type=bug_type,
            additional_context=additional_context,
        )

        bug_report_request.additional_properties = d
        return bug_report_request

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
