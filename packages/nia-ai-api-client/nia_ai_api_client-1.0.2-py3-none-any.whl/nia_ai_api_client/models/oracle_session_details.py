from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.oracle_citation import OracleCitation
    from ..models.oracle_session_details_metadata import OracleSessionDetailsMetadata
    from ..models.oracle_tool_call import OracleToolCall


T = TypeVar("T", bound="OracleSessionDetails")


@_attrs_define
class OracleSessionDetails:
    """
    Attributes:
        session_id (str | Unset):
        title (None | str | Unset):
        query (str | Unset):
        created_at (datetime.datetime | Unset):
        iterations (int | None | Unset):
        duration_ms (int | None | Unset):
        status (str | Unset):
        model (None | str | Unset):
        final_report (str | Unset):
        citations (list[OracleCitation] | Unset):
        tool_calls (list[OracleToolCall] | Unset):
        research_notes (list[str] | Unset):
        prioritized_repositories (list[str] | Unset):
        prioritized_data_sources (list[str] | Unset):
        discovered_repositories (list[str] | Unset):
        discovered_data_sources (list[str] | Unset):
        output_format (None | str | Unset):
        metadata (OracleSessionDetailsMetadata | Unset):
    """

    session_id: str | Unset = UNSET
    title: None | str | Unset = UNSET
    query: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    iterations: int | None | Unset = UNSET
    duration_ms: int | None | Unset = UNSET
    status: str | Unset = UNSET
    model: None | str | Unset = UNSET
    final_report: str | Unset = UNSET
    citations: list[OracleCitation] | Unset = UNSET
    tool_calls: list[OracleToolCall] | Unset = UNSET
    research_notes: list[str] | Unset = UNSET
    prioritized_repositories: list[str] | Unset = UNSET
    prioritized_data_sources: list[str] | Unset = UNSET
    discovered_repositories: list[str] | Unset = UNSET
    discovered_data_sources: list[str] | Unset = UNSET
    output_format: None | str | Unset = UNSET
    metadata: OracleSessionDetailsMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        query = self.query

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        iterations: int | None | Unset
        if isinstance(self.iterations, Unset):
            iterations = UNSET
        else:
            iterations = self.iterations

        duration_ms: int | None | Unset
        if isinstance(self.duration_ms, Unset):
            duration_ms = UNSET
        else:
            duration_ms = self.duration_ms

        status = self.status

        model: None | str | Unset
        if isinstance(self.model, Unset):
            model = UNSET
        else:
            model = self.model

        final_report = self.final_report

        citations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.citations, Unset):
            citations = []
            for citations_item_data in self.citations:
                citations_item = citations_item_data.to_dict()
                citations.append(citations_item)

        tool_calls: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tool_calls, Unset):
            tool_calls = []
            for tool_calls_item_data in self.tool_calls:
                tool_calls_item = tool_calls_item_data.to_dict()
                tool_calls.append(tool_calls_item)

        research_notes: list[str] | Unset = UNSET
        if not isinstance(self.research_notes, Unset):
            research_notes = self.research_notes

        prioritized_repositories: list[str] | Unset = UNSET
        if not isinstance(self.prioritized_repositories, Unset):
            prioritized_repositories = self.prioritized_repositories

        prioritized_data_sources: list[str] | Unset = UNSET
        if not isinstance(self.prioritized_data_sources, Unset):
            prioritized_data_sources = self.prioritized_data_sources

        discovered_repositories: list[str] | Unset = UNSET
        if not isinstance(self.discovered_repositories, Unset):
            discovered_repositories = self.discovered_repositories

        discovered_data_sources: list[str] | Unset = UNSET
        if not isinstance(self.discovered_data_sources, Unset):
            discovered_data_sources = self.discovered_data_sources

        output_format: None | str | Unset
        if isinstance(self.output_format, Unset):
            output_format = UNSET
        else:
            output_format = self.output_format

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if title is not UNSET:
            field_dict["title"] = title
        if query is not UNSET:
            field_dict["query"] = query
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if iterations is not UNSET:
            field_dict["iterations"] = iterations
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if status is not UNSET:
            field_dict["status"] = status
        if model is not UNSET:
            field_dict["model"] = model
        if final_report is not UNSET:
            field_dict["final_report"] = final_report
        if citations is not UNSET:
            field_dict["citations"] = citations
        if tool_calls is not UNSET:
            field_dict["tool_calls"] = tool_calls
        if research_notes is not UNSET:
            field_dict["research_notes"] = research_notes
        if prioritized_repositories is not UNSET:
            field_dict["prioritized_repositories"] = prioritized_repositories
        if prioritized_data_sources is not UNSET:
            field_dict["prioritized_data_sources"] = prioritized_data_sources
        if discovered_repositories is not UNSET:
            field_dict["discovered_repositories"] = discovered_repositories
        if discovered_data_sources is not UNSET:
            field_dict["discovered_data_sources"] = discovered_data_sources
        if output_format is not UNSET:
            field_dict["output_format"] = output_format
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.oracle_citation import OracleCitation
        from ..models.oracle_session_details_metadata import OracleSessionDetailsMetadata
        from ..models.oracle_tool_call import OracleToolCall

        d = dict(src_dict)
        session_id = d.pop("session_id", UNSET)

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        query = d.pop("query", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        def _parse_iterations(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        iterations = _parse_iterations(d.pop("iterations", UNSET))

        def _parse_duration_ms(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        duration_ms = _parse_duration_ms(d.pop("duration_ms", UNSET))

        status = d.pop("status", UNSET)

        def _parse_model(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        model = _parse_model(d.pop("model", UNSET))

        final_report = d.pop("final_report", UNSET)

        _citations = d.pop("citations", UNSET)
        citations: list[OracleCitation] | Unset = UNSET
        if _citations is not UNSET:
            citations = []
            for citations_item_data in _citations:
                citations_item = OracleCitation.from_dict(citations_item_data)

                citations.append(citations_item)

        _tool_calls = d.pop("tool_calls", UNSET)
        tool_calls: list[OracleToolCall] | Unset = UNSET
        if _tool_calls is not UNSET:
            tool_calls = []
            for tool_calls_item_data in _tool_calls:
                tool_calls_item = OracleToolCall.from_dict(tool_calls_item_data)

                tool_calls.append(tool_calls_item)

        research_notes = cast(list[str], d.pop("research_notes", UNSET))

        prioritized_repositories = cast(list[str], d.pop("prioritized_repositories", UNSET))

        prioritized_data_sources = cast(list[str], d.pop("prioritized_data_sources", UNSET))

        discovered_repositories = cast(list[str], d.pop("discovered_repositories", UNSET))

        discovered_data_sources = cast(list[str], d.pop("discovered_data_sources", UNSET))

        def _parse_output_format(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_format = _parse_output_format(d.pop("output_format", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: OracleSessionDetailsMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = OracleSessionDetailsMetadata.from_dict(_metadata)

        oracle_session_details = cls(
            session_id=session_id,
            title=title,
            query=query,
            created_at=created_at,
            iterations=iterations,
            duration_ms=duration_ms,
            status=status,
            model=model,
            final_report=final_report,
            citations=citations,
            tool_calls=tool_calls,
            research_notes=research_notes,
            prioritized_repositories=prioritized_repositories,
            prioritized_data_sources=prioritized_data_sources,
            discovered_repositories=discovered_repositories,
            discovered_data_sources=discovered_data_sources,
            output_format=output_format,
            metadata=metadata,
        )

        oracle_session_details.additional_properties = d
        return oracle_session_details

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
