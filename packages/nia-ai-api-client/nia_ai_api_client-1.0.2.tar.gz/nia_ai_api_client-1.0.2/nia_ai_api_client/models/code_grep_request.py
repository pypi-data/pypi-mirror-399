from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.code_grep_request_output_mode import CodeGrepRequestOutputMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="CodeGrepRequest")


@_attrs_define
class CodeGrepRequest:
    r"""
    Attributes:
        pattern (str): Regex pattern to search for in repository code Example: async function\s+\w+.
        path (str | Unset): Limit search to files with this path prefix Default: ''. Example: src/.
        context_lines (int | Unset): Lines before AND after each match (shorthand for A/B). Overridden by A or B if
            specified.
        a (int | Unset): Lines after each match (like grep -A). Overrides context_lines for after.
        b (int | Unset): Lines before each match (like grep -B). Overrides context_lines for before.
        case_sensitive (bool | Unset): Case-sensitive matching (default is case-insensitive) Default: False.
        whole_word (bool | Unset): Match whole words only Default: False.
        fixed_string (bool | Unset): Treat pattern as literal string, not regex Default: False.
        max_matches_per_file (int | Unset): Maximum matches to return per file Default: 10.
        max_total_matches (int | Unset): Maximum total matches to return Default: 100.
        output_mode (CodeGrepRequestOutputMode | Unset): Output format:
            - content: Return matched lines with context (grouped by file)
            - files_with_matches: Return only file paths that matched
            - count: Return match counts per file
             Default: CodeGrepRequestOutputMode.CONTENT.
        highlight (bool | Unset): Add >>markers<< around matched text in results Default: False.
        include_line_numbers (bool | Unset): Include line numbers in results Default: True.
        group_by_file (bool | Unset): Group matches by file in results Default: True.
        exhaustive (bool | Unset): Search ALL chunks for complete results (default: true).
            When true, iterates through all indexed chunks to find every match (like real grep).
            When false, uses BM25 keyword search to find top candidates first (faster but may miss matches).
            Automatically enabled when pattern has no extractable keywords.
             Default: True.
    """

    pattern: str
    path: str | Unset = ""
    context_lines: int | Unset = UNSET
    a: int | Unset = UNSET
    b: int | Unset = UNSET
    case_sensitive: bool | Unset = False
    whole_word: bool | Unset = False
    fixed_string: bool | Unset = False
    max_matches_per_file: int | Unset = 10
    max_total_matches: int | Unset = 100
    output_mode: CodeGrepRequestOutputMode | Unset = CodeGrepRequestOutputMode.CONTENT
    highlight: bool | Unset = False
    include_line_numbers: bool | Unset = True
    group_by_file: bool | Unset = True
    exhaustive: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pattern = self.pattern

        path = self.path

        context_lines = self.context_lines

        a = self.a

        b = self.b

        case_sensitive = self.case_sensitive

        whole_word = self.whole_word

        fixed_string = self.fixed_string

        max_matches_per_file = self.max_matches_per_file

        max_total_matches = self.max_total_matches

        output_mode: str | Unset = UNSET
        if not isinstance(self.output_mode, Unset):
            output_mode = self.output_mode.value

        highlight = self.highlight

        include_line_numbers = self.include_line_numbers

        group_by_file = self.group_by_file

        exhaustive = self.exhaustive

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pattern": pattern,
            }
        )
        if path is not UNSET:
            field_dict["path"] = path
        if context_lines is not UNSET:
            field_dict["context_lines"] = context_lines
        if a is not UNSET:
            field_dict["A"] = a
        if b is not UNSET:
            field_dict["B"] = b
        if case_sensitive is not UNSET:
            field_dict["case_sensitive"] = case_sensitive
        if whole_word is not UNSET:
            field_dict["whole_word"] = whole_word
        if fixed_string is not UNSET:
            field_dict["fixed_string"] = fixed_string
        if max_matches_per_file is not UNSET:
            field_dict["max_matches_per_file"] = max_matches_per_file
        if max_total_matches is not UNSET:
            field_dict["max_total_matches"] = max_total_matches
        if output_mode is not UNSET:
            field_dict["output_mode"] = output_mode
        if highlight is not UNSET:
            field_dict["highlight"] = highlight
        if include_line_numbers is not UNSET:
            field_dict["include_line_numbers"] = include_line_numbers
        if group_by_file is not UNSET:
            field_dict["group_by_file"] = group_by_file
        if exhaustive is not UNSET:
            field_dict["exhaustive"] = exhaustive

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pattern = d.pop("pattern")

        path = d.pop("path", UNSET)

        context_lines = d.pop("context_lines", UNSET)

        a = d.pop("A", UNSET)

        b = d.pop("B", UNSET)

        case_sensitive = d.pop("case_sensitive", UNSET)

        whole_word = d.pop("whole_word", UNSET)

        fixed_string = d.pop("fixed_string", UNSET)

        max_matches_per_file = d.pop("max_matches_per_file", UNSET)

        max_total_matches = d.pop("max_total_matches", UNSET)

        _output_mode = d.pop("output_mode", UNSET)
        output_mode: CodeGrepRequestOutputMode | Unset
        if isinstance(_output_mode, Unset):
            output_mode = UNSET
        else:
            output_mode = CodeGrepRequestOutputMode(_output_mode)

        highlight = d.pop("highlight", UNSET)

        include_line_numbers = d.pop("include_line_numbers", UNSET)

        group_by_file = d.pop("group_by_file", UNSET)

        exhaustive = d.pop("exhaustive", UNSET)

        code_grep_request = cls(
            pattern=pattern,
            path=path,
            context_lines=context_lines,
            a=a,
            b=b,
            case_sensitive=case_sensitive,
            whole_word=whole_word,
            fixed_string=fixed_string,
            max_matches_per_file=max_matches_per_file,
            max_total_matches=max_total_matches,
            output_mode=output_mode,
            highlight=highlight,
            include_line_numbers=include_line_numbers,
            group_by_file=group_by_file,
            exhaustive=exhaustive,
        )

        code_grep_request.additional_properties = d
        return code_grep_request

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
