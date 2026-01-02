from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.source_content_request_source_type import SourceContentRequestSourceType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.source_content_request_metadata import SourceContentRequestMetadata


T = TypeVar("T", bound="SourceContentRequest")


@_attrs_define
class SourceContentRequest:
    """
    Attributes:
        source_type (SourceContentRequestSourceType): Type of source to retrieve
        source_identifier (str): Identifier for the source:
            - For repositories: 'owner/repo:path/to/file' (e.g., 'facebook/react:src/React.js')
            - For documentation: The source URL
        metadata (SourceContentRequestMetadata | Unset): Optional metadata from search results to help locate the source
    """

    source_type: SourceContentRequestSourceType
    source_identifier: str
    metadata: SourceContentRequestMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_type = self.source_type.value

        source_identifier = self.source_identifier

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_type": source_type,
                "source_identifier": source_identifier,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_content_request_metadata import SourceContentRequestMetadata

        d = dict(src_dict)
        source_type = SourceContentRequestSourceType(d.pop("source_type"))

        source_identifier = d.pop("source_identifier")

        _metadata = d.pop("metadata", UNSET)
        metadata: SourceContentRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SourceContentRequestMetadata.from_dict(_metadata)

        source_content_request = cls(
            source_type=source_type,
            source_identifier=source_identifier,
            metadata=metadata,
        )

        source_content_request.additional_properties = d
        return source_content_request

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
