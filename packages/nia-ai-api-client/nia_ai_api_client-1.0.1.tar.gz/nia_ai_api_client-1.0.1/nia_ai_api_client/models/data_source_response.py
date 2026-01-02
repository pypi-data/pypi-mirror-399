from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_source_response_metadata_type_0 import DataSourceResponseMetadataType0


T = TypeVar("T", bound="DataSourceResponse")


@_attrs_define
class DataSourceResponse:
    """
    Attributes:
        id (str):
        status (str):
        created_at (str):
        updated_at (str):
        url (None | str | Unset):
        file_name (None | str | Unset):
        page_count (int | Unset):  Default: 0.
        chunk_count (int | Unset):  Default: 0.
        project_id (None | str | Unset):
        source_type (str | Unset):  Default: 'web'.
        is_active (bool | Unset):  Default: True.
        display_name (None | str | Unset):
        arxiv_id (None | str | Unset):
        paper_source (None | str | Unset):
        metadata (DataSourceResponseMetadataType0 | None | Unset):
        error (None | str | Unset):
        error_code (None | str | Unset):
    """

    id: str
    status: str
    created_at: str
    updated_at: str
    url: None | str | Unset = UNSET
    file_name: None | str | Unset = UNSET
    page_count: int | Unset = 0
    chunk_count: int | Unset = 0
    project_id: None | str | Unset = UNSET
    source_type: str | Unset = "web"
    is_active: bool | Unset = True
    display_name: None | str | Unset = UNSET
    arxiv_id: None | str | Unset = UNSET
    paper_source: None | str | Unset = UNSET
    metadata: DataSourceResponseMetadataType0 | None | Unset = UNSET
    error: None | str | Unset = UNSET
    error_code: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_source_response_metadata_type_0 import DataSourceResponseMetadataType0

        id = self.id

        status = self.status

        created_at = self.created_at

        updated_at = self.updated_at

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        file_name: None | str | Unset
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        page_count = self.page_count

        chunk_count = self.chunk_count

        project_id: None | str | Unset
        if isinstance(self.project_id, Unset):
            project_id = UNSET
        else:
            project_id = self.project_id

        source_type = self.source_type

        is_active = self.is_active

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
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

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        error_code: None | str | Unset
        if isinstance(self.error_code, Unset):
            error_code = UNSET
        else:
            error_code = self.error_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if url is not UNSET:
            field_dict["url"] = url
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
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
        id = d.pop("id")

        status = d.pop("status")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        def _parse_file_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_name = _parse_file_name(d.pop("file_name", UNSET))

        page_count = d.pop("page_count", UNSET)

        chunk_count = d.pop("chunk_count", UNSET)

        def _parse_project_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_id = _parse_project_id(d.pop("project_id", UNSET))

        source_type = d.pop("source_type", UNSET)

        is_active = d.pop("is_active", UNSET)

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

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

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_error_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_code = _parse_error_code(d.pop("error_code", UNSET))

        data_source_response = cls(
            id=id,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
            url=url,
            file_name=file_name,
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
