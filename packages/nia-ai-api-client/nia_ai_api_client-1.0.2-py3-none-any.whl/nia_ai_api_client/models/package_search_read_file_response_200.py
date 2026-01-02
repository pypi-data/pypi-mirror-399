from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchReadFileResponse200")


@_attrs_define
class PackageSearchReadFileResponse200:
    """
    Attributes:
        version_used (str | Unset): Version of the package
        file_path (str | Unset): Path of the file within the package
        start_line (int | Unset): Starting line number
        end_line (int | Unset): Ending line number
        content (str | Unset): File content for the specified line range
        total_lines (int | Unset): Total number of lines in the file
    """

    version_used: str | Unset = UNSET
    file_path: str | Unset = UNSET
    start_line: int | Unset = UNSET
    end_line: int | Unset = UNSET
    content: str | Unset = UNSET
    total_lines: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version_used = self.version_used

        file_path = self.file_path

        start_line = self.start_line

        end_line = self.end_line

        content = self.content

        total_lines = self.total_lines

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version_used is not UNSET:
            field_dict["version_used"] = version_used
        if file_path is not UNSET:
            field_dict["file_path"] = file_path
        if start_line is not UNSET:
            field_dict["start_line"] = start_line
        if end_line is not UNSET:
            field_dict["end_line"] = end_line
        if content is not UNSET:
            field_dict["content"] = content
        if total_lines is not UNSET:
            field_dict["total_lines"] = total_lines

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        version_used = d.pop("version_used", UNSET)

        file_path = d.pop("file_path", UNSET)

        start_line = d.pop("start_line", UNSET)

        end_line = d.pop("end_line", UNSET)

        content = d.pop("content", UNSET)

        total_lines = d.pop("total_lines", UNSET)

        package_search_read_file_response_200 = cls(
            version_used=version_used,
            file_path=file_path,
            start_line=start_line,
            end_line=end_line,
            content=content,
            total_lines=total_lines,
        )

        package_search_read_file_response_200.additional_properties = d
        return package_search_read_file_response_200

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
