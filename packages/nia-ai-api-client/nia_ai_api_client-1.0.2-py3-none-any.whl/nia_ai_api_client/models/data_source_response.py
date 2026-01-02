from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.data_source_response_source_type import DataSourceResponseSourceType
from ..models.data_source_response_status import DataSourceResponseStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_source_response_metadata_type_0 import DataSourceResponseMetadataType0


T = TypeVar("T", bound="DataSourceResponse")


@_attrs_define
class DataSourceResponse:
    """
    Attributes:
        id (str | Unset): Unique identifier for the data source
        url (str | Unset): The indexed URL
        file_name (str | Unset): File name for text sources
        status (DataSourceResponseStatus | Unset): Current indexing status
        created_at (datetime.datetime | Unset):
        updated_at (datetime.datetime | Unset):
        page_count (int | Unset): Number of pages indexed Default: 0.
        chunk_count (int | Unset): Number of chunks/embeddings created Default: 0.
        project_id (str | Unset): Associated project ID if any
        source_type (DataSourceResponseSourceType | Unset):  Default: DataSourceResponseSourceType.WEB.
        is_active (bool | Unset):  Default: True.
        display_name (str | Unset): Custom display name for the data source
        arxiv_id (None | str | Unset): arXiv identifier when source_type is research_paper
        paper_source (None | str | Unset): Research paper source provider (e.g. arxiv)
        metadata (DataSourceResponseMetadataType0 | None | Unset): Optional lightweight metadata. For research_paper
            sources this may include title/authors/etc.
            For other source types this may be omitted.
        error (str | Unset): Error message if status is 'error' or 'failed'
        error_code (str | Unset): Error code for programmatic error handling
    """

    id: str | Unset = UNSET
    url: str | Unset = UNSET
    file_name: str | Unset = UNSET
    status: DataSourceResponseStatus | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    page_count: int | Unset = 0
    chunk_count: int | Unset = 0
    project_id: str | Unset = UNSET
    source_type: DataSourceResponseSourceType | Unset = DataSourceResponseSourceType.WEB
    is_active: bool | Unset = True
    display_name: str | Unset = UNSET
    arxiv_id: None | str | Unset = UNSET
    paper_source: None | str | Unset = UNSET
    metadata: DataSourceResponseMetadataType0 | None | Unset = UNSET
    error: str | Unset = UNSET
    error_code: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_source_response_metadata_type_0 import DataSourceResponseMetadataType0

        id = self.id

        url = self.url

        file_name = self.file_name

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        page_count = self.page_count

        chunk_count = self.chunk_count

        project_id = self.project_id

        source_type: str | Unset = UNSET
        if not isinstance(self.source_type, Unset):
            source_type = self.source_type.value

        is_active = self.is_active

        display_name = self.display_name

        arxiv_id: None | str | Unset
        if isinstance(self.arxiv_id, Unset):
            arxiv_id = UNSET
        else:
            arxiv_id = self.arxiv_id

        paper_source: None | str | Unset
        if isinstance(self.paper_source, Unset):
            paper_source = UNSET
        else:
            paper_source = self.paper_source

        metadata: dict[str, Any] | None | Unset
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, DataSourceResponseMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        error = self.error

        error_code = self.error_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if url is not UNSET:
            field_dict["url"] = url
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if status is not UNSET:
            field_dict["status"] = status
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if page_count is not UNSET:
            field_dict["page_count"] = page_count
        if chunk_count is not UNSET:
            field_dict["chunk_count"] = chunk_count
        if project_id is not UNSET:
            field_dict["project_id"] = project_id
        if source_type is not UNSET:
            field_dict["source_type"] = source_type
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if arxiv_id is not UNSET:
            field_dict["arxiv_id"] = arxiv_id
        if paper_source is not UNSET:
            field_dict["paper_source"] = paper_source
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if error is not UNSET:
            field_dict["error"] = error
        if error_code is not UNSET:
            field_dict["error_code"] = error_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_source_response_metadata_type_0 import DataSourceResponseMetadataType0

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        url = d.pop("url", UNSET)

        file_name = d.pop("file_name", UNSET)

        _status = d.pop("status", UNSET)
        status: DataSourceResponseStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = DataSourceResponseStatus(_status)

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

        page_count = d.pop("page_count", UNSET)

        chunk_count = d.pop("chunk_count", UNSET)

        project_id = d.pop("project_id", UNSET)

        _source_type = d.pop("source_type", UNSET)
        source_type: DataSourceResponseSourceType | Unset
        if isinstance(_source_type, Unset):
            source_type = UNSET
        else:
            source_type = DataSourceResponseSourceType(_source_type)

        is_active = d.pop("is_active", UNSET)

        display_name = d.pop("display_name", UNSET)

        def _parse_arxiv_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        arxiv_id = _parse_arxiv_id(d.pop("arxiv_id", UNSET))

        def _parse_paper_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        paper_source = _parse_paper_source(d.pop("paper_source", UNSET))

        def _parse_metadata(data: object) -> DataSourceResponseMetadataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = DataSourceResponseMetadataType0.from_dict(data)

                return metadata_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataSourceResponseMetadataType0 | None | Unset, data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        error = d.pop("error", UNSET)

        error_code = d.pop("error_code", UNSET)

        data_source_response = cls(
            id=id,
            url=url,
            file_name=file_name,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            page_count=page_count,
            chunk_count=chunk_count,
            project_id=project_id,
            source_type=source_type,
            is_active=is_active,
            display_name=display_name,
            arxiv_id=arxiv_id,
            paper_source=paper_source,
            metadata=metadata,
            error=error,
            error_code=error_code,
        )

        data_source_response.additional_properties = d
        return data_source_response

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
