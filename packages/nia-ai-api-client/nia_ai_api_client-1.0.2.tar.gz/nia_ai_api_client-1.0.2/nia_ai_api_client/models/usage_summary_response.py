from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.usage_summary_response_subscription_tier import UsageSummaryResponseSubscriptionTier
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.usage_summary_response_usage import UsageSummaryResponseUsage


T = TypeVar("T", bound="UsageSummaryResponse")


@_attrs_define
class UsageSummaryResponse:
    """
    Attributes:
        user_id (str | Unset): User identifier
        organization_id (None | str | Unset): Organization identifier (if applicable)
        subscription_tier (UsageSummaryResponseSubscriptionTier | Unset): Current subscription tier
        billing_period_start (datetime.datetime | Unset): Start of current billing period
        billing_period_end (datetime.datetime | Unset): End of current billing period
        usage (UsageSummaryResponseUsage | Unset): Usage breakdown by operation type
    """

    user_id: str | Unset = UNSET
    organization_id: None | str | Unset = UNSET
    subscription_tier: UsageSummaryResponseSubscriptionTier | Unset = UNSET
    billing_period_start: datetime.datetime | Unset = UNSET
    billing_period_end: datetime.datetime | Unset = UNSET
    usage: UsageSummaryResponseUsage | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        organization_id: None | str | Unset
        if isinstance(self.organization_id, Unset):
            organization_id = UNSET
        else:
            organization_id = self.organization_id

        subscription_tier: str | Unset = UNSET
        if not isinstance(self.subscription_tier, Unset):
            subscription_tier = self.subscription_tier.value

        billing_period_start: str | Unset = UNSET
        if not isinstance(self.billing_period_start, Unset):
            billing_period_start = self.billing_period_start.isoformat()

        billing_period_end: str | Unset = UNSET
        if not isinstance(self.billing_period_end, Unset):
            billing_period_end = self.billing_period_end.isoformat()

        usage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage, Unset):
            usage = self.usage.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if subscription_tier is not UNSET:
            field_dict["subscription_tier"] = subscription_tier
        if billing_period_start is not UNSET:
            field_dict["billing_period_start"] = billing_period_start
        if billing_period_end is not UNSET:
            field_dict["billing_period_end"] = billing_period_end
        if usage is not UNSET:
            field_dict["usage"] = usage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.usage_summary_response_usage import UsageSummaryResponseUsage

        d = dict(src_dict)
        user_id = d.pop("user_id", UNSET)

        def _parse_organization_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        organization_id = _parse_organization_id(d.pop("organization_id", UNSET))

        _subscription_tier = d.pop("subscription_tier", UNSET)
        subscription_tier: UsageSummaryResponseSubscriptionTier | Unset
        if isinstance(_subscription_tier, Unset):
            subscription_tier = UNSET
        else:
            subscription_tier = UsageSummaryResponseSubscriptionTier(_subscription_tier)

        _billing_period_start = d.pop("billing_period_start", UNSET)
        billing_period_start: datetime.datetime | Unset
        if isinstance(_billing_period_start, Unset):
            billing_period_start = UNSET
        else:
            billing_period_start = isoparse(_billing_period_start)

        _billing_period_end = d.pop("billing_period_end", UNSET)
        billing_period_end: datetime.datetime | Unset
        if isinstance(_billing_period_end, Unset):
            billing_period_end = UNSET
        else:
            billing_period_end = isoparse(_billing_period_end)

        _usage = d.pop("usage", UNSET)
        usage: UsageSummaryResponseUsage | Unset
        if isinstance(_usage, Unset):
            usage = UNSET
        else:
            usage = UsageSummaryResponseUsage.from_dict(_usage)

        usage_summary_response = cls(
            user_id=user_id,
            organization_id=organization_id,
            subscription_tier=subscription_tier,
            billing_period_start=billing_period_start,
            billing_period_end=billing_period_end,
            usage=usage,
        )

        usage_summary_response.additional_properties = d
        return usage_summary_response

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
