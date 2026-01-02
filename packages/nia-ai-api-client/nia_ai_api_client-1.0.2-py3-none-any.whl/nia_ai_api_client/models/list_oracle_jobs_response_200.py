from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.list_oracle_jobs_response_200_jobs_item import ListOracleJobsResponse200JobsItem


T = TypeVar("T", bound="ListOracleJobsResponse200")


@_attrs_define
class ListOracleJobsResponse200:
    """
    Attributes:
        jobs (list[ListOracleJobsResponse200JobsItem] | Unset):
        total (int | Unset):
        limit (int | Unset):
        skip (int | Unset):
    """

    jobs: list[ListOracleJobsResponse200JobsItem] | Unset = UNSET
    total: int | Unset = UNSET
    limit: int | Unset = UNSET
    skip: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        jobs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.jobs, Unset):
            jobs = []
            for jobs_item_data in self.jobs:
                jobs_item = jobs_item_data.to_dict()
                jobs.append(jobs_item)

        total = self.total

        limit = self.limit

        skip = self.skip

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if jobs is not UNSET:
            field_dict["jobs"] = jobs
        if total is not UNSET:
            field_dict["total"] = total
        if limit is not UNSET:
            field_dict["limit"] = limit
        if skip is not UNSET:
            field_dict["skip"] = skip

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.list_oracle_jobs_response_200_jobs_item import ListOracleJobsResponse200JobsItem

        d = dict(src_dict)
        _jobs = d.pop("jobs", UNSET)
        jobs: list[ListOracleJobsResponse200JobsItem] | Unset = UNSET
        if _jobs is not UNSET:
            jobs = []
            for jobs_item_data in _jobs:
                jobs_item = ListOracleJobsResponse200JobsItem.from_dict(jobs_item_data)

                jobs.append(jobs_item)

        total = d.pop("total", UNSET)

        limit = d.pop("limit", UNSET)

        skip = d.pop("skip", UNSET)

        list_oracle_jobs_response_200 = cls(
            jobs=jobs,
            total=total,
            limit=limit,
            skip=skip,
        )

        list_oracle_jobs_response_200.additional_properties = d
        return list_oracle_jobs_response_200

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
