from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.data_source_response import DataSourceResponse


T = TypeVar("T", bound="GetDataSourcesBatchDataSourcesBatchPostResponseGetDataSourcesBatchDataSourcesBatchPost")


@_attrs_define
class GetDataSourcesBatchDataSourcesBatchPostResponseGetDataSourcesBatchDataSourcesBatchPost:
    """ """

    additional_properties: dict[str, DataSourceResponse] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_source_response import DataSourceResponse

        d = dict(src_dict)
        get_data_sources_batch_data_sources_batch_post_response_get_data_sources_batch_data_sources_batch_post = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = DataSourceResponse.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        get_data_sources_batch_data_sources_batch_post_response_get_data_sources_batch_data_sources_batch_post.additional_properties = additional_properties
        return get_data_sources_batch_data_sources_batch_post_response_get_data_sources_batch_data_sources_batch_post

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> DataSourceResponse:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: DataSourceResponse) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
