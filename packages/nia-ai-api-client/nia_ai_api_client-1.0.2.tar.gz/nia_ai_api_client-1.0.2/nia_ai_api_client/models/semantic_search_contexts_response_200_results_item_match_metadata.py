from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.semantic_search_contexts_response_200_results_item_match_metadata_search_type import (
    SemanticSearchContextsResponse200ResultsItemMatchMetadataSearchType,
)
from ..types import UNSET, Unset

T = TypeVar("T", bound="SemanticSearchContextsResponse200ResultsItemMatchMetadata")


@_attrs_define
class SemanticSearchContextsResponse200ResultsItemMatchMetadata:
    """
    Attributes:
        search_type (SemanticSearchContextsResponse200ResultsItemMatchMetadataSearchType | Unset):
        vector_score (float | Unset):
        rank (int | Unset):
    """

    search_type: SemanticSearchContextsResponse200ResultsItemMatchMetadataSearchType | Unset = UNSET
    vector_score: float | Unset = UNSET
    rank: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        search_type: str | Unset = UNSET
        if not isinstance(self.search_type, Unset):
            search_type = self.search_type.value

        vector_score = self.vector_score

        rank = self.rank

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if search_type is not UNSET:
            field_dict["search_type"] = search_type
        if vector_score is not UNSET:
            field_dict["vector_score"] = vector_score
        if rank is not UNSET:
            field_dict["rank"] = rank

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _search_type = d.pop("search_type", UNSET)
        search_type: SemanticSearchContextsResponse200ResultsItemMatchMetadataSearchType | Unset
        if isinstance(_search_type, Unset):
            search_type = UNSET
        else:
            search_type = SemanticSearchContextsResponse200ResultsItemMatchMetadataSearchType(_search_type)

        vector_score = d.pop("vector_score", UNSET)

        rank = d.pop("rank", UNSET)

        semantic_search_contexts_response_200_results_item_match_metadata = cls(
            search_type=search_type,
            vector_score=vector_score,
            rank=rank,
        )

        semantic_search_contexts_response_200_results_item_match_metadata.additional_properties = d
        return semantic_search_contexts_response_200_results_item_match_metadata

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
