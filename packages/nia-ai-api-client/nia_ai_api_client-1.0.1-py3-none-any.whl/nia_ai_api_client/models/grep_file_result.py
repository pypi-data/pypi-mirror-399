from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.grep_match import GrepMatch


T = TypeVar("T", bound="GrepFileResult")


@_attrs_define
class GrepFileResult:
    """Grep results grouped by file.

    Attributes:
        file_path (str): Path to the file
        matches (list[GrepMatch] | Unset): Matches in this file
        match_count (int | Unset): Number of matches in this file Default: 0.
    """

    file_path: str
    matches: list[GrepMatch] | Unset = UNSET
    match_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file_path = self.file_path

        matches: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.matches, Unset):
            matches = []
            for matches_item_data in self.matches:
                matches_item = matches_item_data.to_dict()
                matches.append(matches_item)

        match_count = self.match_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file_path": file_path,
            }
        )
        if matches is not UNSET:
            field_dict["matches"] = matches
        if match_count is not UNSET:
            field_dict["match_count"] = match_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.grep_match import GrepMatch

        d = dict(src_dict)
        file_path = d.pop("file_path")

        _matches = d.pop("matches", UNSET)
        matches: list[GrepMatch] | Unset = UNSET
        if _matches is not UNSET:
            matches = []
            for matches_item_data in _matches:
                matches_item = GrepMatch.from_dict(matches_item_data)

                matches.append(matches_item)

        match_count = d.pop("match_count", UNSET)

        grep_file_result = cls(
            file_path=file_path,
            matches=matches,
            match_count=match_count,
        )

        grep_file_result.additional_properties = d
        return grep_file_result

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
