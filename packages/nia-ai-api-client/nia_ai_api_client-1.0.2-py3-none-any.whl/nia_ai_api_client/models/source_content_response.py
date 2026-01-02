from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.source_content_response_metadata import SourceContentResponseMetadata


T = TypeVar("T", bound="SourceContentResponse")


@_attrs_define
class SourceContentResponse:
    """
    Attributes:
        success (bool | Unset):
        content (str | Unset): Full content of the source file or document
        metadata (SourceContentResponseMetadata | Unset):
        error (str | Unset): Error message if retrieval failed
    """

    success: bool | Unset = UNSET
    content: str | Unset = UNSET
    metadata: SourceContentResponseMetadata | Unset = UNSET
    error: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        content = self.content

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if content is not UNSET:
            field_dict["content"] = content
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_content_response_metadata import SourceContentResponseMetadata

        d = dict(src_dict)
        success = d.pop("success", UNSET)

        content = d.pop("content", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: SourceContentResponseMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = SourceContentResponseMetadata.from_dict(_metadata)

        error = d.pop("error", UNSET)

        source_content_response = cls(
            success=success,
            content=content,
            metadata=metadata,
            error=error,
        )

        source_content_response.additional_properties = d
        return source_content_response

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
