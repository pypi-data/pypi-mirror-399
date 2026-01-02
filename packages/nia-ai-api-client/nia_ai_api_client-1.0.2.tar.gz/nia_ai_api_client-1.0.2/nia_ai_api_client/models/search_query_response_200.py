from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.search_query_response_200_sources_item_type_1 import SearchQueryResponse200SourcesItemType1


T = TypeVar("T", bound="SearchQueryResponse200")


@_attrs_define
class SearchQueryResponse200:
    """
    Attributes:
        content (str | Unset):
        sources (list[SearchQueryResponse200SourcesItemType1 | str] | Unset): Code snippets used to generate the
            response (included when include_sources=true)
        source_paths (list[str] | Unset): File paths of the code snippets (included when include_sources=false)
    """

    content: str | Unset = UNSET
    sources: list[SearchQueryResponse200SourcesItemType1 | str] | Unset = UNSET
    source_paths: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.search_query_response_200_sources_item_type_1 import SearchQueryResponse200SourcesItemType1

        content = self.content

        sources: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.sources, Unset):
            sources = []
            for sources_item_data in self.sources:
                sources_item: dict[str, Any] | str
                if isinstance(sources_item_data, SearchQueryResponse200SourcesItemType1):
                    sources_item = sources_item_data.to_dict()
                else:
                    sources_item = sources_item_data
                sources.append(sources_item)

        source_paths: list[str] | Unset = UNSET
        if not isinstance(self.source_paths, Unset):
            source_paths = self.source_paths

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if content is not UNSET:
            field_dict["content"] = content
        if sources is not UNSET:
            field_dict["sources"] = sources
        if source_paths is not UNSET:
            field_dict["source_paths"] = source_paths

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.search_query_response_200_sources_item_type_1 import SearchQueryResponse200SourcesItemType1

        d = dict(src_dict)
        content = d.pop("content", UNSET)

        _sources = d.pop("sources", UNSET)
        sources: list[SearchQueryResponse200SourcesItemType1 | str] | Unset = UNSET
        if _sources is not UNSET:
            sources = []
            for sources_item_data in _sources:

                def _parse_sources_item(data: object) -> SearchQueryResponse200SourcesItemType1 | str:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        sources_item_type_1 = SearchQueryResponse200SourcesItemType1.from_dict(data)

                        return sources_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(SearchQueryResponse200SourcesItemType1 | str, data)

                sources_item = _parse_sources_item(sources_item_data)

                sources.append(sources_item)

        source_paths = cast(list[str], d.pop("source_paths", UNSET))

        search_query_response_200 = cls(
            content=content,
            sources=sources,
            source_paths=source_paths,
        )

        search_query_response_200.additional_properties = d
        return search_query_response_200

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
