from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReadDocumentationPageResponse200Metadata")


@_attrs_define
class ReadDocumentationPageResponse200Metadata:
    """
    Attributes:
        url (str | Unset):
        source_id (str | Unset):
        chunks_found (int | Unset):
        title (str | Unset):
    """

    url: str | Unset = UNSET
    source_id: str | Unset = UNSET
    chunks_found: int | Unset = UNSET
    title: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        source_id = self.source_id

        chunks_found = self.chunks_found

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if chunks_found is not UNSET:
            field_dict["chunks_found"] = chunks_found
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        source_id = d.pop("source_id", UNSET)

        chunks_found = d.pop("chunks_found", UNSET)

        title = d.pop("title", UNSET)

        read_documentation_page_response_200_metadata = cls(
            url=url,
            source_id=source_id,
            chunks_found=chunks_found,
            title=title,
        )

        read_documentation_page_response_200_metadata.additional_properties = d
        return read_documentation_page_response_200_metadata

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
