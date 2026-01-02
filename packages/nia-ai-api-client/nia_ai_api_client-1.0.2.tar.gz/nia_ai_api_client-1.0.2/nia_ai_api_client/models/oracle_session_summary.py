from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="OracleSessionSummary")


@_attrs_define
class OracleSessionSummary:
    """Summary of a persisted Oracle research session.

    Attributes:
        session_id (str | Unset):
        title (None | str | Unset):
        query (str | Unset):
        created_at (datetime.datetime | Unset):
        iterations (int | None | Unset):
        duration_ms (int | None | Unset):
        status (str | Unset):
        model (None | str | Unset):
    """

    session_id: str | Unset = UNSET
    title: None | str | Unset = UNSET
    query: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    iterations: int | None | Unset = UNSET
    duration_ms: int | None | Unset = UNSET
    status: str | Unset = UNSET
    model: None | str | Unset = UNSET
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        oracle_session_summary = cls(
            session_id=session_id,
            title=title,
            query=query,
            created_at=created_at,
            iterations=iterations,
            duration_ms=duration_ms,
            status=status,
            model=model,
        )

        oracle_session_summary.additional_properties = d
        return oracle_session_summary

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
