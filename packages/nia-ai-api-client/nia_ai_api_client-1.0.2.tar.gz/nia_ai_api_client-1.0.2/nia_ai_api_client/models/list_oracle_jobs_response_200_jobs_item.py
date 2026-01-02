from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.list_oracle_jobs_response_200_jobs_item_status import ListOracleJobsResponse200JobsItemStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ListOracleJobsResponse200JobsItem")


@_attrs_define
class ListOracleJobsResponse200JobsItem:
    """
    Attributes:
        job_id (str | Unset):
        session_id (str | Unset):
        query (str | Unset):
        status (ListOracleJobsResponse200JobsItemStatus | Unset):
        created_at (datetime.datetime | Unset):
        updated_at (datetime.datetime | Unset):
        iterations (int | Unset):
        duration_ms (int | Unset):
        error (str | Unset):
    """

    job_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    query: str | Unset = UNSET
    status: ListOracleJobsResponse200JobsItemStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
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
        if iterations is not UNSET:
            field_dict["iterations"] = iterations
        if duration_ms is not UNSET:
            field_dict["duration_ms"] = duration_ms
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        query = d.pop("query", UNSET)

        _status = d.pop("status", UNSET)
        status: ListOracleJobsResponse200JobsItemStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ListOracleJobsResponse200JobsItemStatus(_status)

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

        iterations = d.pop("iterations", UNSET)

        duration_ms = d.pop("duration_ms", UNSET)

        error = d.pop("error", UNSET)

        list_oracle_jobs_response_200_jobs_item = cls(
            job_id=job_id,
            session_id=session_id,
            query=query,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            iterations=iterations,
            duration_ms=duration_ms,
            error=error,
        )

        list_oracle_jobs_response_200_jobs_item.additional_properties = d
        return list_oracle_jobs_response_200_jobs_item

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
