from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.get_oracle_job_response_200_status import GetOracleJobResponse200Status
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_oracle_job_response_200_citations_item import GetOracleJobResponse200CitationsItem
    from ..models.get_oracle_job_response_200_tool_calls_item import GetOracleJobResponse200ToolCallsItem


T = TypeVar("T", bound="GetOracleJobResponse200")


@_attrs_define
class GetOracleJobResponse200:
    """
    Attributes:
        job_id (str | Unset):
        session_id (str | Unset):
        query (str | Unset):
        status (GetOracleJobResponse200Status | Unset):
        created_at (datetime.datetime | Unset):
        updated_at (datetime.datetime | Unset):
        completed_at (datetime.datetime | Unset):
        final_report (str | Unset): Research report (only for completed jobs)
        citations (list[GetOracleJobResponse200CitationsItem] | Unset): Source citations (only for completed jobs)
        tool_calls (list[GetOracleJobResponse200ToolCallsItem] | Unset): Tool execution log (only for completed jobs)
        iterations (int | Unset):
        duration_ms (int | Unset):
        error (str | Unset): Error message (only for failed jobs)
    """

    job_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    query: str | Unset = UNSET
    status: GetOracleJobResponse200Status | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    completed_at: datetime.datetime | Unset = UNSET
    final_report: str | Unset = UNSET
    citations: list[GetOracleJobResponse200CitationsItem] | Unset = UNSET
    tool_calls: list[GetOracleJobResponse200ToolCallsItem] | Unset = UNSET
    iterations: int | Unset = UNSET
    duration_ms: int | Unset = UNSET
    error: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        session_id = self.session_id

        query = self.query

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        completed_at: str | Unset = UNSET
        if not isinstance(self.completed_at, Unset):
            completed_at = self.completed_at.isoformat()

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

        iterations = self.iterations

        duration_ms = self.duration_ms

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if query is not UNSET:
            field_dict["query"] = query
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if completed_at is not UNSET:
            field_dict["completed_at"] = completed_at
        if final_report is not UNSET:
            field_dict["final_report"] = final_report
        if citations is not UNSET:
            field_dict["citations"] = citations
        if tool_calls is not UNSET:
            field_dict["tool_calls"] = tool_calls
        if iterations is not UNSET:
            field_dict["iterations"] = iterations
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_oracle_job_response_200_citations_item import GetOracleJobResponse200CitationsItem
        from ..models.get_oracle_job_response_200_tool_calls_item import GetOracleJobResponse200ToolCallsItem

        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        query = d.pop("query", UNSET)

        _status = d.pop("status", UNSET)
        status: GetOracleJobResponse200Status | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = GetOracleJobResponse200Status(_status)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _completed_at = d.pop("completed_at", UNSET)
        completed_at: datetime.datetime | Unset
        if isinstance(_completed_at, Unset):
            completed_at = UNSET
        else:
            completed_at = isoparse(_completed_at)

        final_report = d.pop("final_report", UNSET)

        _citations = d.pop("citations", UNSET)
        citations: list[GetOracleJobResponse200CitationsItem] | Unset = UNSET
        if _citations is not UNSET:
            citations = []
            for citations_item_data in _citations:
                citations_item = GetOracleJobResponse200CitationsItem.from_dict(citations_item_data)

                citations.append(citations_item)

        _tool_calls = d.pop("tool_calls", UNSET)
        tool_calls: list[GetOracleJobResponse200ToolCallsItem] | Unset = UNSET
        if _tool_calls is not UNSET:
            tool_calls = []
            for tool_calls_item_data in _tool_calls:
                tool_calls_item = GetOracleJobResponse200ToolCallsItem.from_dict(tool_calls_item_data)

                tool_calls.append(tool_calls_item)

        iterations = d.pop("iterations", UNSET)

        duration_ms = d.pop("duration_ms", UNSET)

        error = d.pop("error", UNSET)

        get_oracle_job_response_200 = cls(
            job_id=job_id,
            session_id=session_id,
            query=query,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at,
            final_report=final_report,
            citations=citations,
            tool_calls=tool_calls,
            iterations=iterations,
            duration_ms=duration_ms,
            error=error,
        )

        get_oracle_job_response_200.additional_properties = d
        return get_oracle_job_response_200

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
