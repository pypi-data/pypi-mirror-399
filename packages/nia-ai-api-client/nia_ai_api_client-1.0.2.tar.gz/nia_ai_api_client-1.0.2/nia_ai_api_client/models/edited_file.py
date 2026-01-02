from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.edited_file_operation import EditedFileOperation
from ..types import UNSET, Unset

T = TypeVar("T", bound="EditedFile")


@_attrs_define
class EditedFile:
    """
    Attributes:
        file_path (str): Path to the edited file
        operation (EditedFileOperation | Unset): Type of operation performed on the file
        lines_added (int | Unset): Number of lines added (for created/modified operations)
        lines_removed (int | Unset): Number of lines removed (for modified/deleted operations)
        language (str | Unset): Programming language of the file
    """

    file_path: str
    operation: EditedFileOperation | Unset = UNSET
    lines_added: int | Unset = UNSET
    lines_removed: int | Unset = UNSET
    language: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_path = self.file_path

        operation: str | Unset = UNSET
        if not isinstance(self.operation, Unset):
            operation = self.operation.value

        lines_added = self.lines_added

        lines_removed = self.lines_removed

        language = self.language

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_path": file_path,
            }
        )
        if operation is not UNSET:
            field_dict["operation"] = operation
        if lines_added is not UNSET:
            field_dict["lines_added"] = lines_added
        if lines_removed is not UNSET:
            field_dict["lines_removed"] = lines_removed
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_path = d.pop("file_path")

        _operation = d.pop("operation", UNSET)
        operation: EditedFileOperation | Unset
        if isinstance(_operation, Unset):
            operation = UNSET
        else:
            operation = EditedFileOperation(_operation)

        lines_added = d.pop("lines_added", UNSET)

        lines_removed = d.pop("lines_removed", UNSET)

        language = d.pop("language", UNSET)

        edited_file = cls(
            file_path=file_path,
            operation=operation,
            lines_added=lines_added,
            lines_removed=lines_removed,
            language=language,
        )

        edited_file.additional_properties = d
        return edited_file

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
