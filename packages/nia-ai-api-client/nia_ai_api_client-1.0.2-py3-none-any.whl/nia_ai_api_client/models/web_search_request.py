from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.web_search_request_category import WebSearchRequestCategory
from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchRequest")


@_attrs_define
class WebSearchRequest:
    """
    Attributes:
        query (str): Search query Example: best practices for React hooks.
        num_results (int | Unset): Number of results to return Default: 5.
        category (WebSearchRequestCategory | Unset): Filter by content category
        days_back (int | Unset): Only show results from last N days
        find_similar_to (str | Unset): URL to find similar content to
    """

    query: str
    num_results: int | Unset = 5
    category: WebSearchRequestCategory | Unset = UNSET
    days_back: int | Unset = UNSET
    find_similar_to: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        num_results = self.num_results

        category: str | Unset = UNSET
        if not isinstance(self.category, Unset):
            category = self.category.value

        days_back = self.days_back

        find_similar_to = self.find_similar_to

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if num_results is not UNSET:
            field_dict["num_results"] = num_results
        if category is not UNSET:
            field_dict["category"] = category
        if days_back is not UNSET:
            field_dict["days_back"] = days_back
        if find_similar_to is not UNSET:
            field_dict["find_similar_to"] = find_similar_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        num_results = d.pop("num_results", UNSET)

        _category = d.pop("category", UNSET)
        category: WebSearchRequestCategory | Unset
        if isinstance(_category, Unset):
            category = UNSET
        else:
            category = WebSearchRequestCategory(_category)

        days_back = d.pop("days_back", UNSET)

        find_similar_to = d.pop("find_similar_to", UNSET)

        web_search_request = cls(
            query=query,
            num_results=num_results,
            category=category,
            days_back=days_back,
            find_similar_to=find_similar_to,
        )

        web_search_request.additional_properties = d
        return web_search_request

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
