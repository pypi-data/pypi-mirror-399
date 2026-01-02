from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_share_response import ContextShareResponse


T = TypeVar("T", bound="SearchContextsResponse200")


@_attrs_define
class SearchContextsResponse200:
    """
    Attributes:
        contexts (list[ContextShareResponse] | Unset):
        search_query (str | Unset):
        total_results (int | Unset):
    """

    contexts: list[ContextShareResponse] | Unset = UNSET
    search_query: str | Unset = UNSET
    total_results: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contexts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.contexts, Unset):
            contexts = []
            for contexts_item_data in self.contexts:
                contexts_item = contexts_item_data.to_dict()
                contexts.append(contexts_item)

        search_query = self.search_query

        total_results = self.total_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contexts is not UNSET:
            field_dict["contexts"] = contexts
        if search_query is not UNSET:
            field_dict["search_query"] = search_query
        if total_results is not UNSET:
            field_dict["total_results"] = total_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_share_response import ContextShareResponse

        d = dict(src_dict)
        _contexts = d.pop("contexts", UNSET)
        contexts: list[ContextShareResponse] | Unset = UNSET
        if _contexts is not UNSET:
            contexts = []
            for contexts_item_data in _contexts:
                contexts_item = ContextShareResponse.from_dict(contexts_item_data)

                contexts.append(contexts_item)

        search_query = d.pop("search_query", UNSET)

        total_results = d.pop("total_results", UNSET)

        search_contexts_response_200 = cls(
            contexts=contexts,
            search_query=search_query,
            total_results=total_results,
        )

        search_contexts_response_200.additional_properties = d
        return search_contexts_response_200

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
