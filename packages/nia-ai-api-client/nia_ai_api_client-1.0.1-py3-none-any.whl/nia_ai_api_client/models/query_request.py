from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query_request_data_sources_item_type_1 import QueryRequestDataSourcesItemType1
    from ..models.query_request_messages_item import QueryRequestMessagesItem
    from ..models.query_request_repositories_item_type_1 import QueryRequestRepositoriesItemType1


T = TypeVar("T", bound="QueryRequest")


@_attrs_define
class QueryRequest:
    """
    Attributes:
        messages (list[QueryRequestMessagesItem]): List of chat messages
        repositories (list[QueryRequestRepositoriesItemType1 | str] | Unset): List of repositories to query. Can be
            strings (slug, display name) or dicts with a 'repository' field.
        data_sources (list[QueryRequestDataSourcesItemType1 | str] | Unset): List of data sources to query. Can be
            strings (display_name, URL, or source_id) or dicts with 'source_id' or 'identifier' fields
        search_mode (str | Unset): Search mode: 'repositories', 'sources', or 'unified' Default: 'unified'.
        stream (bool | Unset): Whether to stream the response Default: False.
        include_sources (bool | Unset): Whether to include source texts in the response Default: True.
        fast_mode (bool | Unset): Skip LLM processing for faster results (100-500ms vs 2-8s). Set to false for deeper
            analysis. Default: True.
    """

    messages: list[QueryRequestMessagesItem]
    repositories: list[QueryRequestRepositoriesItemType1 | str] | Unset = UNSET
    data_sources: list[QueryRequestDataSourcesItemType1 | str] | Unset = UNSET
    search_mode: str | Unset = "unified"
    stream: bool | Unset = False
    include_sources: bool | Unset = True
    fast_mode: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.query_request_data_sources_item_type_1 import QueryRequestDataSourcesItemType1
        from ..models.query_request_repositories_item_type_1 import QueryRequestRepositoriesItemType1

        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        repositories: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.repositories, Unset):
            repositories = []
            for repositories_item_data in self.repositories:
                repositories_item: dict[str, Any] | str
                if isinstance(repositories_item_data, QueryRequestRepositoriesItemType1):
                    repositories_item = repositories_item_data.to_dict()
                else:
                    repositories_item = repositories_item_data
                repositories.append(repositories_item)

        data_sources: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.data_sources, Unset):
            data_sources = []
            for data_sources_item_data in self.data_sources:
                data_sources_item: dict[str, Any] | str
                if isinstance(data_sources_item_data, QueryRequestDataSourcesItemType1):
                    data_sources_item = data_sources_item_data.to_dict()
                else:
                    data_sources_item = data_sources_item_data
                data_sources.append(data_sources_item)

        search_mode = self.search_mode

        stream = self.stream

        include_sources = self.include_sources

        fast_mode = self.fast_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "messages": messages,
            }
        )
        if repositories is not UNSET:
            field_dict["repositories"] = repositories
        if data_sources is not UNSET:
            field_dict["data_sources"] = data_sources
        if search_mode is not UNSET:
            field_dict["search_mode"] = search_mode
        if stream is not UNSET:
            field_dict["stream"] = stream
        if include_sources is not UNSET:
            field_dict["include_sources"] = include_sources
        if fast_mode is not UNSET:
            field_dict["fast_mode"] = fast_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_request_data_sources_item_type_1 import QueryRequestDataSourcesItemType1
        from ..models.query_request_messages_item import QueryRequestMessagesItem
        from ..models.query_request_repositories_item_type_1 import QueryRequestRepositoriesItemType1

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = QueryRequestMessagesItem.from_dict(messages_item_data)

            messages.append(messages_item)

        _repositories = d.pop("repositories", UNSET)
        repositories: list[QueryRequestRepositoriesItemType1 | str] | Unset = UNSET
        if _repositories is not UNSET:
            repositories = []
            for repositories_item_data in _repositories:

                def _parse_repositories_item(data: object) -> QueryRequestRepositoriesItemType1 | str:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        repositories_item_type_1 = QueryRequestRepositoriesItemType1.from_dict(data)

                        return repositories_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(QueryRequestRepositoriesItemType1 | str, data)

                repositories_item = _parse_repositories_item(repositories_item_data)

                repositories.append(repositories_item)

        _data_sources = d.pop("data_sources", UNSET)
        data_sources: list[QueryRequestDataSourcesItemType1 | str] | Unset = UNSET
        if _data_sources is not UNSET:
            data_sources = []
            for data_sources_item_data in _data_sources:

                def _parse_data_sources_item(data: object) -> QueryRequestDataSourcesItemType1 | str:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        data_sources_item_type_1 = QueryRequestDataSourcesItemType1.from_dict(data)

                        return data_sources_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(QueryRequestDataSourcesItemType1 | str, data)

                data_sources_item = _parse_data_sources_item(data_sources_item_data)

                data_sources.append(data_sources_item)

        search_mode = d.pop("search_mode", UNSET)

        stream = d.pop("stream", UNSET)

        include_sources = d.pop("include_sources", UNSET)

        fast_mode = d.pop("fast_mode", UNSET)

        query_request = cls(
            messages=messages,
            repositories=repositories,
            data_sources=data_sources,
            search_mode=search_mode,
            stream=stream,
            include_sources=include_sources,
            fast_mode=fast_mode,
        )

        query_request.additional_properties = d
        return query_request

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
