from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.universal_search_response_results_item_source import UniversalSearchResponseResultsItemSource


T = TypeVar("T", bound="UniversalSearchResponseResultsItem")


@_attrs_define
class UniversalSearchResponseResultsItem:
    """
    Attributes:
        content (str | Unset): Text content of the search result
        score (float | Unset): Relevance score (higher is better)
        source (UniversalSearchResponseResultsItemSource | Unset):
    """

    content: str | Unset = UNSET
    score: float | Unset = UNSET
    source: UniversalSearchResponseResultsItemSource | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        score = self.score

        source: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source, Unset):
            source = self.source.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content
        if score is not UNSET:
            field_dict["score"] = score
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.universal_search_response_results_item_source import UniversalSearchResponseResultsItemSource

        d = dict(src_dict)
        content = d.pop("content", UNSET)

        score = d.pop("score", UNSET)

        _source = d.pop("source", UNSET)
        source: UniversalSearchResponseResultsItemSource | Unset
        if isinstance(_source, Unset):
            source = UNSET
        else:
            source = UniversalSearchResponseResultsItemSource.from_dict(_source)

        universal_search_response_results_item = cls(
            content=content,
            score=score,
            source=source,
        )

        universal_search_response_results_item.additional_properties = d
        return universal_search_response_results_item

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
