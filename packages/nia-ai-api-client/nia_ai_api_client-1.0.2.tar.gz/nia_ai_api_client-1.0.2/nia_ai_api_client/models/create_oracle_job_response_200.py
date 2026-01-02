from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.create_oracle_job_response_200_status import CreateOracleJobResponse200Status
from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateOracleJobResponse200")


@_attrs_define
class CreateOracleJobResponse200:
    """
    Attributes:
        job_id (str | Unset): Unique job identifier
        session_id (str | Unset): Research session identifier
        status (CreateOracleJobResponse200Status | Unset): Initial job status
        message (str | Unset): Status message
        created_at (datetime.datetime | Unset): When the job was created
    """

    job_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    status: CreateOracleJobResponse200Status | Unset = UNSET
    message: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        session_id = self.session_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        message = self.message

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if status is not UNSET:
            field_dict["status"] = status
        if message is not UNSET:
            field_dict["message"] = message
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        _status = d.pop("status", UNSET)
        status: CreateOracleJobResponse200Status | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = CreateOracleJobResponse200Status(_status)

        message = d.pop("message", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        create_oracle_job_response_200 = cls(
            job_id=job_id,
            session_id=session_id,
            status=status,
            message=message,
            created_at=created_at,
        )

        create_oracle_job_response_200.additional_properties = d
        return create_oracle_job_response_200

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
