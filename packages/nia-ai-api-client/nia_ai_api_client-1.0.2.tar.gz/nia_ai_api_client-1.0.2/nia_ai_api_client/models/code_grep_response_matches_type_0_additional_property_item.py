from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CodeGrepResponseMatchesType0AdditionalPropertyItem")


@_attrs_define
class CodeGrepResponseMatchesType0AdditionalPropertyItem:
    """
    Attributes:
        line_number (int | Unset):
        line (str | Unset):
        context (str | Unset):
    """

    line_number: int | Unset = UNSET
    line: str | Unset = UNSET
    context: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        line_number = self.line_number

        line = self.line

        context = self.context

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if line_number is not UNSET:
            field_dict["line_number"] = line_number
        if line is not UNSET:
            field_dict["line"] = line
        if context is not UNSET:
            field_dict["context"] = context

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        line_number = d.pop("line_number", UNSET)

        line = d.pop("line", UNSET)

        context = d.pop("context", UNSET)

        code_grep_response_matches_type_0_additional_property_item = cls(
            line_number=line_number,
            line=line,
            context=context,
        )

        code_grep_response_matches_type_0_additional_property_item.additional_properties = d
        return code_grep_response_matches_type_0_additional_property_item

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
