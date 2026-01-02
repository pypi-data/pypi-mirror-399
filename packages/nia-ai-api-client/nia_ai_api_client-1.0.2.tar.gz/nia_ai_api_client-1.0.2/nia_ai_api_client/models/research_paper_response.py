from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.research_paper_response_status import ResearchPaperResponseStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ResearchPaperResponse")


@_attrs_define
class ResearchPaperResponse:
    """
    Attributes:
        id (str | Unset): Unique identifier for the data source
        arxiv_id (str | Unset): The arXiv identifier (e.g., "2312.00752")
        title (str | Unset): Paper title extracted from arXiv
        authors (list[str] | Unset): List of paper authors
        abstract (str | Unset): Paper abstract
        categories (list[str] | Unset): arXiv categories (e.g., ["cs.CL", "cs.AI"])
        primary_category (str | Unset): Primary arXiv category
        status (ResearchPaperResponseStatus | Unset): Current indexing status (aligned with DataSourceResponse)
        created_at (datetime.datetime | Unset):
        updated_at (datetime.datetime | Unset):
        chunk_count (int | Unset): Number of text chunks created from the paper Default: 0.
        doi (None | str | Unset): DOI if available
        published_date (None | str | Unset): Publication date from arXiv
        pdf_url (str | Unset): Direct URL to the PDF
        abs_url (str | Unset): URL to the arXiv abstract page
        error (None | str | Unset): Error message if status is 'failed'
    """

    id: str | Unset = UNSET
    arxiv_id: str | Unset = UNSET
    title: str | Unset = UNSET
    authors: list[str] | Unset = UNSET
    abstract: str | Unset = UNSET
    categories: list[str] | Unset = UNSET
    primary_category: str | Unset = UNSET
    status: ResearchPaperResponseStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    chunk_count: int | Unset = 0
    doi: None | str | Unset = UNSET
    published_date: None | str | Unset = UNSET
    pdf_url: str | Unset = UNSET
    abs_url: str | Unset = UNSET
    error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        arxiv_id = self.arxiv_id

        title = self.title

        authors: list[str] | Unset = UNSET
        if not isinstance(self.authors, Unset):
            authors = self.authors

        abstract = self.abstract

        categories: list[str] | Unset = UNSET
        if not isinstance(self.categories, Unset):
            categories = self.categories

        primary_category = self.primary_category

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        chunk_count = self.chunk_count

        doi: None | str | Unset
        if isinstance(self.doi, Unset):
            doi = UNSET
        else:
            doi = self.doi

        published_date: None | str | Unset
        if isinstance(self.published_date, Unset):
            published_date = UNSET
        else:
            published_date = self.published_date

        pdf_url = self.pdf_url

        abs_url = self.abs_url

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if arxiv_id is not UNSET:
            field_dict["arxiv_id"] = arxiv_id
        if title is not UNSET:
            field_dict["title"] = title
        if authors is not UNSET:
            field_dict["authors"] = authors
        if abstract is not UNSET:
            field_dict["abstract"] = abstract
        if categories is not UNSET:
            field_dict["categories"] = categories
        if primary_category is not UNSET:
            field_dict["primary_category"] = primary_category
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if chunk_count is not UNSET:
            field_dict["chunk_count"] = chunk_count
        if doi is not UNSET:
            field_dict["doi"] = doi
        if published_date is not UNSET:
            field_dict["published_date"] = published_date
        if pdf_url is not UNSET:
            field_dict["pdf_url"] = pdf_url
        if abs_url is not UNSET:
            field_dict["abs_url"] = abs_url
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        arxiv_id = d.pop("arxiv_id", UNSET)

        title = d.pop("title", UNSET)

        authors = cast(list[str], d.pop("authors", UNSET))

        abstract = d.pop("abstract", UNSET)

        categories = cast(list[str], d.pop("categories", UNSET))

        primary_category = d.pop("primary_category", UNSET)

        _status = d.pop("status", UNSET)
        status: ResearchPaperResponseStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = ResearchPaperResponseStatus(_status)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        chunk_count = d.pop("chunk_count", UNSET)

        def _parse_doi(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        doi = _parse_doi(d.pop("doi", UNSET))

        def _parse_published_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        published_date = _parse_published_date(d.pop("published_date", UNSET))

        pdf_url = d.pop("pdf_url", UNSET)

        abs_url = d.pop("abs_url", UNSET)

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        research_paper_response = cls(
            id=id,
            arxiv_id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract,
            categories=categories,
            primary_category=primary_category,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            chunk_count=chunk_count,
            doi=doi,
            published_date=published_date,
            pdf_url=pdf_url,
            abs_url=abs_url,
            error=error,
        )

        research_paper_response.additional_properties = d
        return research_paper_response

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
