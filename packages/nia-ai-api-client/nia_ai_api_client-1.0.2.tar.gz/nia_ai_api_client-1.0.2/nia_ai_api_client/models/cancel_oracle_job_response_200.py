from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.cancel_oracle_job_response_200_status import CancelOracleJobResponse200Status
from ..types import UNSET, Unset

T = TypeVar("T", bound="CancelOracleJobResponse200")


@_attrs_define
class CancelOracleJobResponse200:
    """
    Attributes:
        job_id (str | Unset):
        session_id (str | Unset):
        status (CancelOracleJobResponse200Status | Unset):
        message (str | Unset):
    """

    job_id: str | Unset = UNSET
    session_id: str | Unset = UNSET
    status: CancelOracleJobResponse200Status | Unset = UNSET
    message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        session_id = self.session_id

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        message = self.message

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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id", UNSET)

        session_id = d.pop("session_id", UNSET)

        _status = d.pop("status", UNSET)
        status: CancelOracleJobResponse200Status | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = CancelOracleJobResponse200Status(_status)

        message = d.pop("message", UNSET)

        cancel_oracle_job_response_200 = cls(
            job_id=job_id,
            session_id=session_id,
            status=status,
            message=message,
        )

        cancel_oracle_job_response_200.additional_properties = d
        return cancel_oracle_job_response_200

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
