from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.regex_search_response_results_item import RegexSearchResponseResultsItem


T = TypeVar("T", bound="RegexSearchResponse")


@_attrs_define
class RegexSearchResponse:
    """
    Attributes:
        query (str | Unset): The search query used
        pattern_used (str | Unset): The regex pattern that was executed
        total_matches (int | Unset): Total number of matches found
        repositories_searched (list[str] | Unset): Repositories that were searched
        results (list[RegexSearchResponseResultsItem] | Unset):
        truncated (bool | Unset): Whether results were truncated due to max_results limit
    """

    query: str | Unset = UNSET
    pattern_used: str | Unset = UNSET
    total_matches: int | Unset = UNSET
    repositories_searched: list[str] | Unset = UNSET
    results: list[RegexSearchResponseResultsItem] | Unset = UNSET
    truncated: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        pattern_used = self.pattern_used

        total_matches = self.total_matches

        repositories_searched: list[str] | Unset = UNSET
        if not isinstance(self.repositories_searched, Unset):
            repositories_searched = self.repositories_searched

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        truncated = self.truncated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if query is not UNSET:
            field_dict["query"] = query
        if pattern_used is not UNSET:
            field_dict["pattern_used"] = pattern_used
        if total_matches is not UNSET:
            field_dict["total_matches"] = total_matches
        if repositories_searched is not UNSET:
            field_dict["repositories_searched"] = repositories_searched
        if results is not UNSET:
            field_dict["results"] = results
        if truncated is not UNSET:
            field_dict["truncated"] = truncated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.regex_search_response_results_item import RegexSearchResponseResultsItem

        d = dict(src_dict)
        query = d.pop("query", UNSET)

        pattern_used = d.pop("pattern_used", UNSET)

        total_matches = d.pop("total_matches", UNSET)

        repositories_searched = cast(list[str], d.pop("repositories_searched", UNSET))

        _results = d.pop("results", UNSET)
        results: list[RegexSearchResponseResultsItem] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = RegexSearchResponseResultsItem.from_dict(results_item_data)

                results.append(results_item)

        truncated = d.pop("truncated", UNSET)

        regex_search_response = cls(
            query=query,
            pattern_used=pattern_used,
            total_matches=total_matches,
            repositories_searched=repositories_searched,
            results=results,
            truncated=truncated,
        )

        regex_search_response.additional_properties = d
        return regex_search_response

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
