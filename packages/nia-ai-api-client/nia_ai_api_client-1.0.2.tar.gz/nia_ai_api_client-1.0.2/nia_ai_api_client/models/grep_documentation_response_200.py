from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.grep_documentation_response_200_counts import GrepDocumentationResponse200Counts
    from ..models.grep_documentation_response_200_matches_item import GrepDocumentationResponse200MatchesItem
    from ..models.grep_documentation_response_200_options import GrepDocumentationResponse200Options


T = TypeVar("T", bound="GrepDocumentationResponse200")


@_attrs_define
class GrepDocumentationResponse200:
    """
    Attributes:
        success (bool | Unset):
        matches (list[GrepDocumentationResponse200MatchesItem] | Unset): Matches grouped by file (when output_mode is
            'content')
        files (list[str] | Unset): List of file paths (when output_mode is 'files_with_matches')
        counts (GrepDocumentationResponse200Counts | Unset): Match counts per file (when output_mode is 'count')
        pattern (str | Unset): The pattern that was searched
        path_filter (str | Unset): Path filter that was applied
        total_matches (int | Unset):
        files_searched (int | Unset):
        files_with_matches (int | Unset): Number of files that contained matches
        truncated (bool | Unset): Whether results were truncated due to limits
        options (GrepDocumentationResponse200Options | Unset): Applied search options
    """

    success: bool | Unset = UNSET
    matches: list[GrepDocumentationResponse200MatchesItem] | Unset = UNSET
    files: list[str] | Unset = UNSET
    counts: GrepDocumentationResponse200Counts | Unset = UNSET
    pattern: str | Unset = UNSET
    path_filter: str | Unset = UNSET
    total_matches: int | Unset = UNSET
    files_searched: int | Unset = UNSET
    files_with_matches: int | Unset = UNSET
    truncated: bool | Unset = UNSET
    options: GrepDocumentationResponse200Options | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        matches: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.matches, Unset):
            matches = []
            for matches_item_data in self.matches:
                matches_item = matches_item_data.to_dict()
                matches.append(matches_item)

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
        from ..models.grep_documentation_response_200_counts import GrepDocumentationResponse200Counts
        from ..models.grep_documentation_response_200_matches_item import GrepDocumentationResponse200MatchesItem
        from ..models.grep_documentation_response_200_options import GrepDocumentationResponse200Options

        d = dict(src_dict)
        success = d.pop("success", UNSET)

        _matches = d.pop("matches", UNSET)
        matches: list[GrepDocumentationResponse200MatchesItem] | Unset = UNSET
        if _matches is not UNSET:
            matches = []
            for matches_item_data in _matches:
                matches_item = GrepDocumentationResponse200MatchesItem.from_dict(matches_item_data)

                matches.append(matches_item)

        files = cast(list[str], d.pop("files", UNSET))

        _counts = d.pop("counts", UNSET)
        counts: GrepDocumentationResponse200Counts | Unset
        if isinstance(_counts, Unset):
            counts = UNSET
        else:
            counts = GrepDocumentationResponse200Counts.from_dict(_counts)

        pattern = d.pop("pattern", UNSET)

        path_filter = d.pop("path_filter", UNSET)

        total_matches = d.pop("total_matches", UNSET)

        files_searched = d.pop("files_searched", UNSET)

        files_with_matches = d.pop("files_with_matches", UNSET)

        truncated = d.pop("truncated", UNSET)

        _options = d.pop("options", UNSET)
        options: GrepDocumentationResponse200Options | Unset
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = GrepDocumentationResponse200Options.from_dict(_options)

        grep_documentation_response_200 = cls(
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

        grep_documentation_response_200.additional_properties = d
        return grep_documentation_response_200

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
