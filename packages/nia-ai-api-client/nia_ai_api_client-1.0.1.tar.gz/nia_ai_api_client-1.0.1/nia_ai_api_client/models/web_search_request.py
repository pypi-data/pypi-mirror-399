from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchRequest")


@_attrs_define
class WebSearchRequest:
    """
    Attributes:
        query (str): Search query
        num_results (int | Unset): Number of results Default: 5.
        category (None | str | Unset): Filter by category: github, company, research, news, tweet, pdf, blog
        days_back (int | None | Unset): Only show results from last N days
        find_similar_to (None | str | Unset): URL to find similar content to
    """

    query: str
    num_results: int | Unset = 5
    category: None | str | Unset = UNSET
    days_back: int | None | Unset = UNSET
    find_similar_to: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        num_results = self.num_results

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        days_back: int | None | Unset
        if isinstance(self.days_back, Unset):
            days_back = UNSET
        else:
            days_back = self.days_back

        find_similar_to: None | str | Unset
        if isinstance(self.find_similar_to, Unset):
            find_similar_to = UNSET
        else:
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

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_days_back(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        days_back = _parse_days_back(d.pop("days_back", UNSET))

        def _parse_find_similar_to(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        find_similar_to = _parse_find_similar_to(d.pop("find_similar_to", UNSET))

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
