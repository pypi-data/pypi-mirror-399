from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_search_response_contexts_item import ContextSearchResponseContextsItem


T = TypeVar("T", bound="ContextSearchResponse")


@_attrs_define
class ContextSearchResponse:
    """Response for text search in contexts.

    Attributes:
        search_query (str): The search query used
        contexts (list[ContextSearchResponseContextsItem] | Unset): Matching contexts
        total_results (int | Unset): Total number of results Default: 0.
    """

    search_query: str
    contexts: list[ContextSearchResponseContextsItem] | Unset = UNSET
    total_results: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        search_query = self.search_query

        contexts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.contexts, Unset):
            contexts = []
            for contexts_item_data in self.contexts:
                contexts_item = contexts_item_data.to_dict()
                contexts.append(contexts_item)

        total_results = self.total_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "search_query": search_query,
            }
        )
        if contexts is not UNSET:
            field_dict["contexts"] = contexts
        if total_results is not UNSET:
            field_dict["total_results"] = total_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_search_response_contexts_item import ContextSearchResponseContextsItem

        d = dict(src_dict)
        search_query = d.pop("search_query")

        _contexts = d.pop("contexts", UNSET)
        contexts: list[ContextSearchResponseContextsItem] | Unset = UNSET
        if _contexts is not UNSET:
            contexts = []
            for contexts_item_data in _contexts:
                contexts_item = ContextSearchResponseContextsItem.from_dict(contexts_item_data)

                contexts.append(contexts_item)

        total_results = d.pop("total_results", UNSET)

        context_search_response = cls(
            search_query=search_query,
            contexts=contexts,
            total_results=total_results,
        )

        context_search_response.additional_properties = d
        return context_search_response

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
