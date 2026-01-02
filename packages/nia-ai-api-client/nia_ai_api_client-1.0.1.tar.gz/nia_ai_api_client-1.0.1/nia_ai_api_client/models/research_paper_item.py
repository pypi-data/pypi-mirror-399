from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResearchPaperItem")


@_attrs_define
class ResearchPaperItem:
    """A single research paper.

    Attributes:
        id (str): Paper ID
        title (str): Paper title
        url (str): Paper URL
        status (str): Indexing status
        arxiv_id (None | str | Unset): arXiv ID
        created_at (datetime.datetime | None | Unset): When indexed
    """

    id: str
    title: str
    url: str
    status: str
    arxiv_id: None | str | Unset = UNSET
    created_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        url = self.url

        status = self.status

        arxiv_id: None | str | Unset
        if isinstance(self.arxiv_id, Unset):
            arxiv_id = UNSET
        else:
            arxiv_id = self.arxiv_id

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "title": title,
                "url": url,
                "status": status,
            }
        )
        if arxiv_id is not UNSET:
            field_dict["arxiv_id"] = arxiv_id
        if created_at is not UNSET:
            field_dict["created_at"] = created_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        title = d.pop("title")

        url = d.pop("url")

        status = d.pop("status")

        def _parse_arxiv_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        arxiv_id = _parse_arxiv_id(d.pop("arxiv_id", UNSET))

        def _parse_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = isoparse(data)

                return created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        research_paper_item = cls(
            id=id,
            title=title,
            url=url,
            status=status,
            arxiv_id=arxiv_id,
            created_at=created_at,
        )

        research_paper_item.additional_properties = d
        return research_paper_item

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
