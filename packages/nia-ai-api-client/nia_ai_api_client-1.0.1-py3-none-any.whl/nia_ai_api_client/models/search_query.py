from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SearchQuery")


@_attrs_define
class SearchQuery:
    """Represents a search query performed during the conversation.

    Attributes:
        query (str): The search query that was performed
        query_type (str): Type: 'codebase', 'documentation', etc.
        key_findings (str): Brief summary of what was found
        resources_searched (list[str] | Unset):
        useful_results_count (int | Unset):  Default: 0.
    """

    query: str
    query_type: str
    key_findings: str
    resources_searched: list[str] | Unset = UNSET
    useful_results_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        query_type = self.query_type

        key_findings = self.key_findings

        resources_searched: list[str] | Unset = UNSET
        if not isinstance(self.resources_searched, Unset):
            resources_searched = self.resources_searched

        useful_results_count = self.useful_results_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
                "query_type": query_type,
                "key_findings": key_findings,
            }
        )
        if resources_searched is not UNSET:
            field_dict["resources_searched"] = resources_searched
        if useful_results_count is not UNSET:
            field_dict["useful_results_count"] = useful_results_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        query_type = d.pop("query_type")

        key_findings = d.pop("key_findings")

        resources_searched = cast(list[str], d.pop("resources_searched", UNSET))

        useful_results_count = d.pop("useful_results_count", UNSET)

        search_query = cls(
            query=query,
            query_type=query_type,
            key_findings=key_findings,
            resources_searched=resources_searched,
            useful_results_count=useful_results_count,
        )

        search_query.additional_properties = d
        return search_query

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
