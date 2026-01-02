from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsageSummaryResponseUsageAdditionalProperty")


@_attrs_define
class UsageSummaryResponseUsageAdditionalProperty:
    """
    Attributes:
        used (int | Unset): Number of operations used this period
        limit (int | Unset): Maximum allowed operations (0 if unlimited)
        unlimited (bool | Unset): Whether this operation type is unlimited
    """

    used: int | Unset = UNSET
    limit: int | Unset = UNSET
    unlimited: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        used = self.used

        limit = self.limit

        unlimited = self.unlimited

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if used is not UNSET:
            field_dict["used"] = used
        if limit is not UNSET:
            field_dict["limit"] = limit
        if unlimited is not UNSET:
            field_dict["unlimited"] = unlimited

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        used = d.pop("used", UNSET)

        limit = d.pop("limit", UNSET)

        unlimited = d.pop("unlimited", UNSET)

        usage_summary_response_usage_additional_property = cls(
            used=used,
            limit=limit,
            unlimited=unlimited,
        )

        usage_summary_response_usage_additional_property.additional_properties = d
        return usage_summary_response_usage_additional_property

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
