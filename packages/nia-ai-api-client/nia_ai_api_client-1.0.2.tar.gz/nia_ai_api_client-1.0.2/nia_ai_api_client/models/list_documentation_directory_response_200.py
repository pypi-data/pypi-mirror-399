from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ListDocumentationDirectoryResponse200")


@_attrs_define
class ListDocumentationDirectoryResponse200:
    """
    Attributes:
        success (bool | Unset):
        path (str | Unset): The path that was listed
        directories (list[str] | Unset): Subdirectories at this path
        files (list[str] | Unset): Files (pages) at this path
        total (int | Unset): Total number of items
    """

    success: bool | Unset = UNSET
    path: str | Unset = UNSET
    directories: list[str] | Unset = UNSET
    files: list[str] | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        path = self.path

        directories: list[str] | Unset = UNSET
        if not isinstance(self.directories, Unset):
            directories = self.directories

        files: list[str] | Unset = UNSET
        if not isinstance(self.files, Unset):
            files = self.files

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if path is not UNSET:
            field_dict["path"] = path
        if directories is not UNSET:
            field_dict["directories"] = directories
        if files is not UNSET:
            field_dict["files"] = files
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success", UNSET)

        path = d.pop("path", UNSET)

        directories = cast(list[str], d.pop("directories", UNSET))

        files = cast(list[str], d.pop("files", UNSET))

        total = d.pop("total", UNSET)

        list_documentation_directory_response_200 = cls(
            success=success,
            path=path,
            directories=directories,
            files=files,
            total=total,
        )

        list_documentation_directory_response_200.additional_properties = d
        return list_documentation_directory_response_200

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
