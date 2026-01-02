from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.grep_file_result import GrepFileResult


T = TypeVar("T", bound="CodeGrepResponse")


@_attrs_define
class CodeGrepResponse:
    """Response for code grep search.

    Attributes:
        pattern (str): The search pattern used
        results (list[GrepFileResult] | Unset): Grep results by file
        total_matches (int | Unset): Total number of matches found Default: 0.
        files_searched (int | Unset): Number of files searched Default: 0.
        truncated (bool | Unset): Whether results were truncated Default: False.
    """

    pattern: str
    results: list[GrepFileResult] | Unset = UNSET
    total_matches: int | Unset = 0
    files_searched: int | Unset = 0
    truncated: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pattern = self.pattern

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        total_matches = self.total_matches

        files_searched = self.files_searched

        truncated = self.truncated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pattern": pattern,
            }
        )
        if results is not UNSET:
            field_dict["results"] = results
        if total_matches is not UNSET:
            field_dict["total_matches"] = total_matches
        if files_searched is not UNSET:
            field_dict["files_searched"] = files_searched
        if truncated is not UNSET:
            field_dict["truncated"] = truncated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.grep_file_result import GrepFileResult

        d = dict(src_dict)
        pattern = d.pop("pattern")

        _results = d.pop("results", UNSET)
        results: list[GrepFileResult] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = GrepFileResult.from_dict(results_item_data)

                results.append(results_item)

        total_matches = d.pop("total_matches", UNSET)

        files_searched = d.pop("files_searched", UNSET)

        truncated = d.pop("truncated", UNSET)

        code_grep_response = cls(
            pattern=pattern,
            results=results,
            total_matches=total_matches,
            files_searched=files_searched,
            truncated=truncated,
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
