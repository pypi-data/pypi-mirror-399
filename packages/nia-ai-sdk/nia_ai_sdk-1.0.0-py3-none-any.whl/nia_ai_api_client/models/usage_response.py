from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_category import UsageCategory


T = TypeVar("T", bound="UsageResponse")


@_attrs_define
class UsageResponse:
    """Response for usage summary.

    Attributes:
        user_id (str): User ID
        billing_period_start (datetime.datetime): Start of billing period
        billing_period_end (datetime.datetime): End of billing period
        queries (UsageCategory): Usage for a single category.
        deep_research (UsageCategory): Usage for a single category.
        web_search (UsageCategory): Usage for a single category.
        package_search (UsageCategory): Usage for a single category.
        oracle (UsageCategory): Usage for a single category.
        contexts (UsageCategory): Usage for a single category.
        indexing (UsageCategory): Usage for a single category.
        subscription_tier (str | Unset): Subscription tier Default: 'free'.
    """

    user_id: str
    billing_period_start: datetime.datetime
    billing_period_end: datetime.datetime
    queries: UsageCategory
    deep_research: UsageCategory
    web_search: UsageCategory
    package_search: UsageCategory
    oracle: UsageCategory
    contexts: UsageCategory
    indexing: UsageCategory
    subscription_tier: str | Unset = "free"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        billing_period_start = self.billing_period_start.isoformat()

        billing_period_end = self.billing_period_end.isoformat()

        queries = self.queries.to_dict()

        deep_research = self.deep_research.to_dict()

        web_search = self.web_search.to_dict()

        package_search = self.package_search.to_dict()

        oracle = self.oracle.to_dict()

        contexts = self.contexts.to_dict()

        indexing = self.indexing.to_dict()

        subscription_tier = self.subscription_tier

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "billing_period_start": billing_period_start,
                "billing_period_end": billing_period_end,
                "queries": queries,
                "deep_research": deep_research,
                "web_search": web_search,
                "package_search": package_search,
                "oracle": oracle,
                "contexts": contexts,
                "indexing": indexing,
            }
        )
        if subscription_tier is not UNSET:
            field_dict["subscription_tier"] = subscription_tier

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_category import UsageCategory

        d = dict(src_dict)
        user_id = d.pop("user_id")

        billing_period_start = isoparse(d.pop("billing_period_start"))

        billing_period_end = isoparse(d.pop("billing_period_end"))

        queries = UsageCategory.from_dict(d.pop("queries"))

        deep_research = UsageCategory.from_dict(d.pop("deep_research"))

        web_search = UsageCategory.from_dict(d.pop("web_search"))

        package_search = UsageCategory.from_dict(d.pop("package_search"))

        oracle = UsageCategory.from_dict(d.pop("oracle"))

        contexts = UsageCategory.from_dict(d.pop("contexts"))

        indexing = UsageCategory.from_dict(d.pop("indexing"))

        subscription_tier = d.pop("subscription_tier", UNSET)

        usage_response = cls(
            user_id=user_id,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
            queries=queries,
            deep_research=deep_research,
            web_search=web_search,
            package_search=package_search,
            oracle=oracle,
            contexts=contexts,
            indexing=indexing,
            subscription_tier=subscription_tier,
        )

        usage_response.additional_properties = d
        return usage_response

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
