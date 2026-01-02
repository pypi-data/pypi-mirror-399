from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="IndexRepositoryResponse200Data")


@_attrs_define
class IndexRepositoryResponse200Data:
    """
    Attributes:
        repository_id (str | Unset):
        status (str | Unset):
        status_url (str | Unset):
    """

    repository_id: str | Unset = UNSET
    status: str | Unset = UNSET
    status_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository_id = self.repository_id

        status = self.status

        status_url = self.status_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if status is not UNSET:
            field_dict["status"] = status
        if status_url is not UNSET:
            field_dict["status_url"] = status_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository_id = d.pop("repository_id", UNSET)

        status = d.pop("status", UNSET)

        status_url = d.pop("status_url", UNSET)

        index_repository_response_200_data = cls(
            repository_id=repository_id,
            status=status,
            status_url=status_url,
        )

        index_repository_response_200_data.additional_properties = d
        return index_repository_response_200_data

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
