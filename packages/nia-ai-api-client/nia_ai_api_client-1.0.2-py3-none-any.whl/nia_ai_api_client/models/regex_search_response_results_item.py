from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegexSearchResponseResultsItem")


@_attrs_define
class RegexSearchResponseResultsItem:
    """
    Attributes:
        repository (str | Unset):
        file_path (str | Unset):
        line_number (int | Unset):
        matched_line (str | Unset):
        context_before (list[str] | Unset):
        context_after (list[str] | Unset):
        language (str | Unset):
    """

    repository: str | Unset = UNSET
    file_path: str | Unset = UNSET
    line_number: int | Unset = UNSET
    matched_line: str | Unset = UNSET
    context_before: list[str] | Unset = UNSET
    context_after: list[str] | Unset = UNSET
    language: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        file_path = self.file_path

        line_number = self.line_number

        matched_line = self.matched_line

        context_before: list[str] | Unset = UNSET
        if not isinstance(self.context_before, Unset):
            context_before = self.context_before

        context_after: list[str] | Unset = UNSET
        if not isinstance(self.context_after, Unset):
            context_after = self.context_after

        language = self.language

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if file_path is not UNSET:
            field_dict["file_path"] = file_path
        if line_number is not UNSET:
            field_dict["line_number"] = line_number
        if matched_line is not UNSET:
            field_dict["matched_line"] = matched_line
        if context_before is not UNSET:
            field_dict["context_before"] = context_before
        if context_after is not UNSET:
            field_dict["context_after"] = context_after
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository = d.pop("repository", UNSET)

        file_path = d.pop("file_path", UNSET)

        line_number = d.pop("line_number", UNSET)

        matched_line = d.pop("matched_line", UNSET)

        context_before = cast(list[str], d.pop("context_before", UNSET))

        context_after = cast(list[str], d.pop("context_after", UNSET))

        language = d.pop("language", UNSET)

        regex_search_response_results_item = cls(
            repository=repository,
            file_path=file_path,
            line_number=line_number,
            matched_line=matched_line,
            context_before=context_before,
            context_after=context_after,
            language=language,
        )

        regex_search_response_results_item.additional_properties = d
        return regex_search_response_results_item

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
