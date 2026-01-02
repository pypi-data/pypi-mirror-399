from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.read_documentation_page_response_200_metadata import ReadDocumentationPageResponse200Metadata


T = TypeVar("T", bound="ReadDocumentationPageResponse200")


@_attrs_define
class ReadDocumentationPageResponse200:
    """
    Attributes:
        success (bool | Unset):
        path (str | Unset): The virtual path requested
        url (str | Unset): The actual URL of the page
        content (str | Unset): Full or partial content of the documentation page
        total_lines (int | Unset): Total number of lines in the document
        returned_lines (list[int] | Unset): [start_line, end_line] range of returned content
        truncated (bool | Unset): Whether content was truncated due to max_length limit
        metadata (ReadDocumentationPageResponse200Metadata | Unset):
    """

    success: bool | Unset = UNSET
    path: str | Unset = UNSET
    url: str | Unset = UNSET
    content: str | Unset = UNSET
    total_lines: int | Unset = UNSET
    returned_lines: list[int] | Unset = UNSET
    truncated: bool | Unset = UNSET
    metadata: ReadDocumentationPageResponse200Metadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        path = self.path

        url = self.url

        content = self.content

        total_lines = self.total_lines

        returned_lines: list[int] | Unset = UNSET
        if not isinstance(self.returned_lines, Unset):
            returned_lines = self.returned_lines

        truncated = self.truncated

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if path is not UNSET:
            field_dict["path"] = path
        if url is not UNSET:
            field_dict["url"] = url
        if content is not UNSET:
            field_dict["content"] = content
        if total_lines is not UNSET:
            field_dict["total_lines"] = total_lines
        if returned_lines is not UNSET:
            field_dict["returned_lines"] = returned_lines
        if truncated is not UNSET:
            field_dict["truncated"] = truncated
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.read_documentation_page_response_200_metadata import ReadDocumentationPageResponse200Metadata

        d = dict(src_dict)
        success = d.pop("success", UNSET)

        path = d.pop("path", UNSET)

        url = d.pop("url", UNSET)

        content = d.pop("content", UNSET)

        total_lines = d.pop("total_lines", UNSET)

        returned_lines = cast(list[int], d.pop("returned_lines", UNSET))

        truncated = d.pop("truncated", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: ReadDocumentationPageResponse200Metadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ReadDocumentationPageResponse200Metadata.from_dict(_metadata)

        read_documentation_page_response_200 = cls(
            success=success,
            path=path,
            url=url,
            content=content,
            total_lines=total_lines,
            returned_lines=returned_lines,
            truncated=truncated,
            metadata=metadata,
        )

        read_documentation_page_response_200.additional_properties = d
        return read_documentation_page_response_200

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
