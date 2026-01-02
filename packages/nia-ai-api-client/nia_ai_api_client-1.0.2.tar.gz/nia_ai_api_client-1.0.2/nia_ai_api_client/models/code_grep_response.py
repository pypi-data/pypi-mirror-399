from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.code_grep_response_counts import CodeGrepResponseCounts
    from ..models.code_grep_response_matches_type_0 import CodeGrepResponseMatchesType0
    from ..models.code_grep_response_matches_type_1_item import CodeGrepResponseMatchesType1Item
    from ..models.code_grep_response_options import CodeGrepResponseOptions


T = TypeVar("T", bound="CodeGrepResponse")


@_attrs_define
class CodeGrepResponse:
    """
    Attributes:
        success (bool | Unset):
        matches (CodeGrepResponseMatchesType0 | list[CodeGrepResponseMatchesType1Item] | Unset):
        files (list[str] | Unset): List of file paths (when output_mode is 'files_with_matches')
        counts (CodeGrepResponseCounts | Unset): Match counts per file (when output_mode is 'count')
        pattern (str | Unset): The regex pattern that was searched
        path_filter (str | Unset): Path filter that was applied
        total_matches (int | Unset): Total number of matches found
        files_searched (int | Unset): Number of code chunks searched
        files_with_matches (int | Unset): Number of files that contained matches
        truncated (bool | Unset): Whether results were truncated due to limits
        options (CodeGrepResponseOptions | Unset): Applied search options
    """

    success: bool | Unset = UNSET
    matches: CodeGrepResponseMatchesType0 | list[CodeGrepResponseMatchesType1Item] | Unset = UNSET
    files: list[str] | Unset = UNSET
    counts: CodeGrepResponseCounts | Unset = UNSET
    pattern: str | Unset = UNSET
    path_filter: str | Unset = UNSET
    total_matches: int | Unset = UNSET
    files_searched: int | Unset = UNSET
    files_with_matches: int | Unset = UNSET
    truncated: bool | Unset = UNSET
    options: CodeGrepResponseOptions | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.code_grep_response_matches_type_0 import CodeGrepResponseMatchesType0

        success = self.success

        matches: dict[str, Any] | list[dict[str, Any]] | Unset
        if isinstance(self.matches, Unset):
            matches = UNSET
        elif isinstance(self.matches, CodeGrepResponseMatchesType0):
            matches = self.matches.to_dict()
        else:
            matches = []
            for matches_type_1_item_data in self.matches:
                matches_type_1_item = matches_type_1_item_data.to_dict()
                matches.append(matches_type_1_item)

        files: list[str] | Unset = UNSET
        if not isinstance(self.files, Unset):
            files = self.files

        counts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.counts, Unset):
            counts = self.counts.to_dict()

        pattern = self.pattern

        path_filter = self.path_filter

        total_matches = self.total_matches

        files_searched = self.files_searched

        files_with_matches = self.files_with_matches

        truncated = self.truncated

        options: dict[str, Any] | Unset = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if matches is not UNSET:
            field_dict["matches"] = matches
        if files is not UNSET:
            field_dict["files"] = files
        if counts is not UNSET:
            field_dict["counts"] = counts
        if pattern is not UNSET:
            field_dict["pattern"] = pattern
        if path_filter is not UNSET:
            field_dict["path_filter"] = path_filter
        if total_matches is not UNSET:
            field_dict["total_matches"] = total_matches
        if files_searched is not UNSET:
            field_dict["files_searched"] = files_searched
        if files_with_matches is not UNSET:
            field_dict["files_with_matches"] = files_with_matches
        if truncated is not UNSET:
            field_dict["truncated"] = truncated
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.code_grep_response_counts import CodeGrepResponseCounts
        from ..models.code_grep_response_matches_type_0 import CodeGrepResponseMatchesType0
        from ..models.code_grep_response_matches_type_1_item import CodeGrepResponseMatchesType1Item
        from ..models.code_grep_response_options import CodeGrepResponseOptions

        d = dict(src_dict)
        success = d.pop("success", UNSET)

        def _parse_matches(
            data: object,
        ) -> CodeGrepResponseMatchesType0 | list[CodeGrepResponseMatchesType1Item] | Unset:
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                matches_type_0 = CodeGrepResponseMatchesType0.from_dict(data)

                return matches_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            if not isinstance(data, list):
                raise TypeError()
            matches_type_1 = []
            _matches_type_1 = data
            for matches_type_1_item_data in _matches_type_1:
                matches_type_1_item = CodeGrepResponseMatchesType1Item.from_dict(matches_type_1_item_data)

                matches_type_1.append(matches_type_1_item)

            return matches_type_1

        matches = _parse_matches(d.pop("matches", UNSET))

        files = cast(list[str], d.pop("files", UNSET))

        _counts = d.pop("counts", UNSET)
        counts: CodeGrepResponseCounts | Unset
        if isinstance(_counts, Unset):
            counts = UNSET
        else:
            counts = CodeGrepResponseCounts.from_dict(_counts)

        pattern = d.pop("pattern", UNSET)

        path_filter = d.pop("path_filter", UNSET)

        total_matches = d.pop("total_matches", UNSET)

        files_searched = d.pop("files_searched", UNSET)

        files_with_matches = d.pop("files_with_matches", UNSET)

        truncated = d.pop("truncated", UNSET)

        _options = d.pop("options", UNSET)
        options: CodeGrepResponseOptions | Unset
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = CodeGrepResponseOptions.from_dict(_options)

        code_grep_response = cls(
            success=success,
            matches=matches,
            files=files,
            counts=counts,
            pattern=pattern,
            path_filter=path_filter,
            total_matches=total_matches,
            files_searched=files_searched,
            files_with_matches=files_with_matches,
            truncated=truncated,
            options=options,
        )

        code_grep_response.additional_properties = d
        return code_grep_response

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
