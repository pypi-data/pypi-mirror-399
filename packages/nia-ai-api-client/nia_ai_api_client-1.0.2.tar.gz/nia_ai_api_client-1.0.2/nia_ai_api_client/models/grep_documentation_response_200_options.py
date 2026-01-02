from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GrepDocumentationResponse200Options")


@_attrs_define
class GrepDocumentationResponse200Options:
    """Applied search options

    Attributes:
        case_sensitive (bool | Unset):
        whole_word (bool | Unset):
        lines_before (int | Unset):
        lines_after (int | Unset):
        output_mode (str | Unset):
    """

    case_sensitive: bool | Unset = UNSET
    whole_word: bool | Unset = UNSET
    lines_before: int | Unset = UNSET
    lines_after: int | Unset = UNSET
    output_mode: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        case_sensitive = self.case_sensitive

        whole_word = self.whole_word

        lines_before = self.lines_before

        lines_after = self.lines_after

        output_mode = self.output_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if case_sensitive is not UNSET:
            field_dict["case_sensitive"] = case_sensitive
        if whole_word is not UNSET:
            field_dict["whole_word"] = whole_word
        if lines_before is not UNSET:
            field_dict["lines_before"] = lines_before
        if lines_after is not UNSET:
            field_dict["lines_after"] = lines_after
        if output_mode is not UNSET:
            field_dict["output_mode"] = output_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        case_sensitive = d.pop("case_sensitive", UNSET)

        whole_word = d.pop("whole_word", UNSET)

        lines_before = d.pop("lines_before", UNSET)

        lines_after = d.pop("lines_after", UNSET)

        output_mode = d.pop("output_mode", UNSET)

        grep_documentation_response_200_options = cls(
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            lines_before=lines_before,
            lines_after=lines_after,
            output_mode=output_mode,
        )

        grep_documentation_response_200_options.additional_properties = d
        return grep_documentation_response_200_options

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
