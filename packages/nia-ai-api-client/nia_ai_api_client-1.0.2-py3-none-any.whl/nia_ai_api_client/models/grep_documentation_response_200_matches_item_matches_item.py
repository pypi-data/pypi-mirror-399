from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GrepDocumentationResponse200MatchesItemMatchesItem")


@_attrs_define
class GrepDocumentationResponse200MatchesItemMatchesItem:
    """
    Attributes:
        line_number (int | Unset):
        line (str | Unset): The matched line
        context (list[str] | Unset): Context lines around the match
        context_start_line (int | Unset):
    """

    line_number: int | Unset = UNSET
    line: str | Unset = UNSET
    context: list[str] | Unset = UNSET
    context_start_line: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        line_number = self.line_number

        line = self.line

        context: list[str] | Unset = UNSET
        if not isinstance(self.context, Unset):
            context = self.context

        context_start_line = self.context_start_line

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if line_number is not UNSET:
            field_dict["line_number"] = line_number
        if line is not UNSET:
            field_dict["line"] = line
        if context is not UNSET:
            field_dict["context"] = context
        if context_start_line is not UNSET:
            field_dict["context_start_line"] = context_start_line

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        line_number = d.pop("line_number", UNSET)

        line = d.pop("line", UNSET)

        context = cast(list[str], d.pop("context", UNSET))

        context_start_line = d.pop("context_start_line", UNSET)

        grep_documentation_response_200_matches_item_matches_item = cls(
            line_number=line_number,
            line=line,
            context=context,
            context_start_line=context_start_line,
        )

        grep_documentation_response_200_matches_item_matches_item.additional_properties = d
        return grep_documentation_response_200_matches_item_matches_item

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
