from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GrepMatch")


@_attrs_define
class GrepMatch:
    """A single grep match.

    Attributes:
        file_path (str): Path to the file
        line_number (int): Line number of the match
        line_content (str): Content of the matching line
        context_before (list[str] | None | Unset): Lines before the match
        context_after (list[str] | None | Unset): Lines after the match
    """

    file_path: str
    line_number: int
    line_content: str
    context_before: list[str] | None | Unset = UNSET
    context_after: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_path = self.file_path

        line_number = self.line_number

        line_content = self.line_content

        context_before: list[str] | None | Unset
        if isinstance(self.context_before, Unset):
            context_before = UNSET
        elif isinstance(self.context_before, list):
            context_before = self.context_before

        else:
            context_before = self.context_before

        context_after: list[str] | None | Unset
        if isinstance(self.context_after, Unset):
            context_after = UNSET
        elif isinstance(self.context_after, list):
            context_after = self.context_after

        else:
            context_after = self.context_after

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_path": file_path,
                "line_number": line_number,
                "line_content": line_content,
            }
        )
        if context_before is not UNSET:
            field_dict["context_before"] = context_before
        if context_after is not UNSET:
            field_dict["context_after"] = context_after

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file_path = d.pop("file_path")

        line_number = d.pop("line_number")

        line_content = d.pop("line_content")

        def _parse_context_before(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                context_before_type_0 = cast(list[str], data)

                return context_before_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        context_before = _parse_context_before(d.pop("context_before", UNSET))

        def _parse_context_after(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                context_after_type_0 = cast(list[str], data)

                return context_after_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        context_after = _parse_context_after(d.pop("context_after", UNSET))

        grep_match = cls(
            file_path=file_path,
            line_number=line_number,
            line_content=line_content,
            context_before=context_before,
            context_after=context_after,
        )

        grep_match.additional_properties = d
        return grep_match

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
