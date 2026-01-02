from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.grep_documentation_response_200_matches_item_matches_item import (
        GrepDocumentationResponse200MatchesItemMatchesItem,
    )


T = TypeVar("T", bound="GrepDocumentationResponse200MatchesItem")


@_attrs_define
class GrepDocumentationResponse200MatchesItem:
    """
    Attributes:
        path (str | Unset): Virtual path of the matched file
        url (str | Unset): Actual URL of the page
        matches (list[GrepDocumentationResponse200MatchesItemMatchesItem] | Unset):
    """

    path: str | Unset = UNSET
    url: str | Unset = UNSET
    matches: list[GrepDocumentationResponse200MatchesItemMatchesItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        url = self.url

        matches: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.matches, Unset):
            matches = []
            for matches_item_data in self.matches:
                matches_item = matches_item_data.to_dict()
                matches.append(matches_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if path is not UNSET:
            field_dict["path"] = path
        if url is not UNSET:
            field_dict["url"] = url
        if matches is not UNSET:
            field_dict["matches"] = matches

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.grep_documentation_response_200_matches_item_matches_item import (
            GrepDocumentationResponse200MatchesItemMatchesItem,
        )

        d = dict(src_dict)
        path = d.pop("path", UNSET)

        url = d.pop("url", UNSET)

        _matches = d.pop("matches", UNSET)
        matches: list[GrepDocumentationResponse200MatchesItemMatchesItem] | Unset = UNSET
        if _matches is not UNSET:
            matches = []
            for matches_item_data in _matches:
                matches_item = GrepDocumentationResponse200MatchesItemMatchesItem.from_dict(matches_item_data)

                matches.append(matches_item)

        grep_documentation_response_200_matches_item = cls(
            path=path,
            url=url,
            matches=matches,
        )

        grep_documentation_response_200_matches_item.additional_properties = d
        return grep_documentation_response_200_matches_item

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
