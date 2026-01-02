from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.doc_content_response_metadata import DocContentResponseMetadata


T = TypeVar("T", bound="DocContentResponse")


@_attrs_define
class DocContentResponse:
    """Response for documentation content.

    Attributes:
        success (bool): Whether content was retrieved
        content (str | Unset): Page content (markdown) Default: ''.
        metadata (DocContentResponseMetadata | Unset): Page metadata
        error (None | str | Unset): Error message if failed
    """

    success: bool
    content: str | Unset = ""
    metadata: DocContentResponseMetadata | Unset = UNSET
    error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        content = self.content

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
            }
        )
        if content is not UNSET:
            field_dict["content"] = content
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.doc_content_response_metadata import DocContentResponseMetadata

        d = dict(src_dict)
        success = d.pop("success")

        content = d.pop("content", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: DocContentResponseMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = DocContentResponseMetadata.from_dict(_metadata)

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        doc_content_response = cls(
            success=success,
            content=content,
            metadata=metadata,
            error=error,
        )

        doc_content_response.additional_properties = d
        return doc_content_response

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
