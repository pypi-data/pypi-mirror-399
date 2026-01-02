from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.semantic_search_contexts_response_200_results_item import SemanticSearchContextsResponse200ResultsItem
    from ..models.semantic_search_contexts_response_200_search_metadata import (
        SemanticSearchContextsResponse200SearchMetadata,
    )
    from ..models.semantic_search_contexts_response_200_suggestions import SemanticSearchContextsResponse200Suggestions


T = TypeVar("T", bound="SemanticSearchContextsResponse200")


@_attrs_define
class SemanticSearchContextsResponse200:
    """
    Attributes:
        results (list[SemanticSearchContextsResponse200ResultsItem] | Unset):
        search_query (str | Unset):
        search_metadata (SemanticSearchContextsResponse200SearchMetadata | Unset):
        suggestions (SemanticSearchContextsResponse200Suggestions | Unset):
    """

    results: list[SemanticSearchContextsResponse200ResultsItem] | Unset = UNSET
    search_query: str | Unset = UNSET
    search_metadata: SemanticSearchContextsResponse200SearchMetadata | Unset = UNSET
    suggestions: SemanticSearchContextsResponse200Suggestions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        search_query = self.search_query

        search_metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.search_metadata, Unset):
            search_metadata = self.search_metadata.to_dict()

        suggestions: dict[str, Any] | Unset = UNSET
        if not isinstance(self.suggestions, Unset):
            suggestions = self.suggestions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if results is not UNSET:
            field_dict["results"] = results
        if search_query is not UNSET:
            field_dict["search_query"] = search_query
        if search_metadata is not UNSET:
            field_dict["search_metadata"] = search_metadata
        if suggestions is not UNSET:
            field_dict["suggestions"] = suggestions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.semantic_search_contexts_response_200_results_item import (
            SemanticSearchContextsResponse200ResultsItem,
        )
        from ..models.semantic_search_contexts_response_200_search_metadata import (
            SemanticSearchContextsResponse200SearchMetadata,
        )
        from ..models.semantic_search_contexts_response_200_suggestions import (
            SemanticSearchContextsResponse200Suggestions,
        )

        d = dict(src_dict)
        _results = d.pop("results", UNSET)
        results: list[SemanticSearchContextsResponse200ResultsItem] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = SemanticSearchContextsResponse200ResultsItem.from_dict(results_item_data)

                results.append(results_item)

        search_query = d.pop("search_query", UNSET)

        _search_metadata = d.pop("search_metadata", UNSET)
        search_metadata: SemanticSearchContextsResponse200SearchMetadata | Unset
        if isinstance(_search_metadata, Unset):
            search_metadata = UNSET
        else:
            search_metadata = SemanticSearchContextsResponse200SearchMetadata.from_dict(_search_metadata)

        _suggestions = d.pop("suggestions", UNSET)
        suggestions: SemanticSearchContextsResponse200Suggestions | Unset
        if isinstance(_suggestions, Unset):
            suggestions = UNSET
        else:
            suggestions = SemanticSearchContextsResponse200Suggestions.from_dict(_suggestions)

        semantic_search_contexts_response_200 = cls(
            results=results,
            search_query=search_query,
            search_metadata=search_metadata,
            suggestions=suggestions,
        )

        semantic_search_contexts_response_200.additional_properties = d
        return semantic_search_contexts_response_200

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
