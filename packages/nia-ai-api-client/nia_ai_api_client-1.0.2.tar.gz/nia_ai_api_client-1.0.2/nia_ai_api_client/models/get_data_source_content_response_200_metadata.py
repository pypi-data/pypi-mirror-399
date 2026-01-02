from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetDataSourceContentResponse200Metadata")


@_attrs_define
class GetDataSourceContentResponse200Metadata:
    """
    Attributes:
        title (str | Unset):
        total_lines (int | Unset):
    """

    title: str | Unset = UNSET
    total_lines: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        total_lines = self.total_lines

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if total_lines is not UNSET:
            field_dict["total_lines"] = total_lines

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title", UNSET)

        total_lines = d.pop("total_lines", UNSET)

        get_data_source_content_response_200_metadata = cls(
            title=title,
            total_lines=total_lines,
        )

        get_data_source_content_response_200_metadata.additional_properties = d
        return get_data_source_content_response_200_metadata

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
