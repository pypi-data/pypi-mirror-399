from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WebSearchResponseDocumentationItem")


@_attrs_define
class WebSearchResponseDocumentationItem:
    """
    Attributes:
        url (str | Unset):
        title (str | Unset):
        summary (str | Unset):
        highlights (list[str] | Unset):
    """

    url: str | Unset = UNSET
    title: str | Unset = UNSET
    summary: str | Unset = UNSET
    highlights: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        title = self.title

        summary = self.summary

        highlights: list[str] | Unset = UNSET
        if not isinstance(self.highlights, Unset):
            highlights = self.highlights

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if url is not UNSET:
            field_dict["url"] = url
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary
        if highlights is not UNSET:
            field_dict["highlights"] = highlights

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url", UNSET)

        title = d.pop("title", UNSET)

        summary = d.pop("summary", UNSET)

        highlights = cast(list[str], d.pop("highlights", UNSET))

        web_search_response_documentation_item = cls(
            url=url,
            title=title,
            summary=summary,
            highlights=highlights,
        )

        web_search_response_documentation_item.additional_properties = d
        return web_search_response_documentation_item

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
