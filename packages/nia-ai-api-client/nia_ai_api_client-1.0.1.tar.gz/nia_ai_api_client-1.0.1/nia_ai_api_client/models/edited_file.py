from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EditedFile")


@_attrs_define
class EditedFile:
    """Represents a file that was modified during the conversation.

    Attributes:
        file_path (str): Path to the file
        operation (str): Type: 'created', 'modified', 'deleted'
        changes_description (str): Brief description of changes
        key_changes (list[str] | Unset):
        language (None | str | Unset): Programming language of the file
    """

    file_path: str
    operation: str
    changes_description: str
    key_changes: list[str] | Unset = UNSET
    language: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_path = self.file_path

        operation = self.operation

        changes_description = self.changes_description

        key_changes: list[str] | Unset = UNSET
        if not isinstance(self.key_changes, Unset):
            key_changes = self.key_changes

        language: None | str | Unset
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_path": file_path,
                "operation": operation,
                "changes_description": changes_description,
            }
        )
        if key_changes is not UNSET:
            field_dict["key_changes"] = key_changes
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_path = d.pop("file_path")

        operation = d.pop("operation")

        changes_description = d.pop("changes_description")

        key_changes = cast(list[str], d.pop("key_changes", UNSET))

        def _parse_language(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        language = _parse_language(d.pop("language", UNSET))

        edited_file = cls(
            file_path=file_path,
            operation=operation,
            changes_description=changes_description,
            key_changes=key_changes,
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
