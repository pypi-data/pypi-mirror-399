from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.query_request_search_mode import QueryRequestSearchMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query_request_data_sources_item_type_1 import QueryRequestDataSourcesItemType1
    from ..models.query_request_data_sources_item_type_2 import QueryRequestDataSourcesItemType2
    from ..models.query_request_messages_item import QueryRequestMessagesItem
    from ..models.query_request_repositories_item import QueryRequestRepositoriesItem


T = TypeVar("T", bound="QueryRequest")


@_attrs_define
class QueryRequest:
    """
    Attributes:
        messages (list[QueryRequestMessagesItem]): Chat messages for context and query Example: [{'role': 'user',
            'content': 'How does the error handling work in this codebase?'}].
        repositories (list[QueryRequestRepositoriesItem] | Unset): List of repositories to query
        data_sources (list[QueryRequestDataSourcesItemType1 | QueryRequestDataSourcesItemType2 | str] | Unset): List of
            documentation/web sources to query. Supports flexible identifiers:
            - String format (recommended): ["Vercel AI SDK - Core", "https://docs.trynia.ai/"]
            - Legacy object format: [{"source_id": "uuid"}]
            - New object format: [{"identifier": "display-name-or-url"}]
        search_mode (QueryRequestSearchMode | Unset): Search mode: 'repositories' searches only code, 'sources' searches
            only documentation Default: QueryRequestSearchMode.REPOSITORIES.
        stream (bool | Unset): Whether to stream the response Default: False.
        include_sources (bool | Unset): Whether to include full source texts in the response (when false, only file
            paths are returned) Default: True.
    """

    messages: list[QueryRequestMessagesItem]
    repositories: list[QueryRequestRepositoriesItem] | Unset = UNSET
    data_sources: list[QueryRequestDataSourcesItemType1 | QueryRequestDataSourcesItemType2 | str] | Unset = UNSET
    search_mode: QueryRequestSearchMode | Unset = QueryRequestSearchMode.REPOSITORIES
    stream: bool | Unset = False
    include_sources: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.query_request_data_sources_item_type_1 import QueryRequestDataSourcesItemType1
        from ..models.query_request_data_sources_item_type_2 import QueryRequestDataSourcesItemType2

        messages = []
        for messages_item_data in self.messages:
            messages_item = messages_item_data.to_dict()
            messages.append(messages_item)

        repositories: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.repositories, Unset):
            repositories = []
            for repositories_item_data in self.repositories:
                repositories_item = repositories_item_data.to_dict()
                repositories.append(repositories_item)

        data_sources: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.data_sources, Unset):
            data_sources = []
            for data_sources_item_data in self.data_sources:
                data_sources_item: dict[str, Any] | str
                if isinstance(data_sources_item_data, QueryRequestDataSourcesItemType1):
                    data_sources_item = data_sources_item_data.to_dict()
                elif isinstance(data_sources_item_data, QueryRequestDataSourcesItemType2):
                    data_sources_item = data_sources_item_data.to_dict()
                else:
                    data_sources_item = data_sources_item_data
                data_sources.append(data_sources_item)

        search_mode: str | Unset = UNSET
        if not isinstance(self.search_mode, Unset):
            search_mode = self.search_mode.value

        stream = self.stream

        include_sources = self.include_sources

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_request_data_sources_item_type_1 import QueryRequestDataSourcesItemType1
        from ..models.query_request_data_sources_item_type_2 import QueryRequestDataSourcesItemType2
        from ..models.query_request_messages_item import QueryRequestMessagesItem
        from ..models.query_request_repositories_item import QueryRequestRepositoriesItem

        d = dict(src_dict)
        messages = []
        _messages = d.pop("messages")
        for messages_item_data in _messages:
            messages_item = QueryRequestMessagesItem.from_dict(messages_item_data)

            messages.append(messages_item)

        _repositories = d.pop("repositories", UNSET)
        repositories: list[QueryRequestRepositoriesItem] | Unset = UNSET
        if _repositories is not UNSET:
            repositories = []
            for repositories_item_data in _repositories:
                repositories_item = QueryRequestRepositoriesItem.from_dict(repositories_item_data)

                repositories.append(repositories_item)

        _data_sources = d.pop("data_sources", UNSET)
        data_sources: list[QueryRequestDataSourcesItemType1 | QueryRequestDataSourcesItemType2 | str] | Unset = UNSET
        if _data_sources is not UNSET:
            data_sources = []
            for data_sources_item_data in _data_sources:

                def _parse_data_sources_item(
                    data: object,
                ) -> QueryRequestDataSourcesItemType1 | QueryRequestDataSourcesItemType2 | str:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        data_sources_item_type_1 = QueryRequestDataSourcesItemType1.from_dict(data)

                        return data_sources_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        data_sources_item_type_2 = QueryRequestDataSourcesItemType2.from_dict(data)

                        return data_sources_item_type_2
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(QueryRequestDataSourcesItemType1 | QueryRequestDataSourcesItemType2 | str, data)

                data_sources_item = _parse_data_sources_item(data_sources_item_data)

                data_sources.append(data_sources_item)

        _search_mode = d.pop("search_mode", UNSET)
        search_mode: QueryRequestSearchMode | Unset
        if isinstance(_search_mode, Unset):
            search_mode = UNSET
        else:
            search_mode = QueryRequestSearchMode(_search_mode)

        stream = d.pop("stream", UNSET)

        include_sources = d.pop("include_sources", UNSET)

        query_request = cls(
            messages=messages,
            repositories=repositories,
            data_sources=data_sources,
            search_mode=search_mode,
            stream=stream,
            include_sources=include_sources,
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
