from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_share_update_request_metadata import ContextShareUpdateRequestMetadata
    from ..models.edited_file import EditedFile
    from ..models.nia_references import NiaReferences


T = TypeVar("T", bound="ContextShareUpdateRequest")


@_attrs_define
class ContextShareUpdateRequest:
    """Request to update an existing context (all fields optional)

    Attributes:
        title (str | Unset):
        summary (str | Unset):
        content (str | Unset):
        tags (list[str] | Unset):
        metadata (ContextShareUpdateRequestMetadata | Unset):
        nia_references (NiaReferences | Unset): References to NIA resources used during the conversation
        edited_files (list[EditedFile] | Unset):
    """

    title: str | Unset = UNSET
    summary: str | Unset = UNSET
    content: str | Unset = UNSET
    tags: list[str] | Unset = UNSET
    metadata: ContextShareUpdateRequestMetadata | Unset = UNSET
    nia_references: NiaReferences | Unset = UNSET
    edited_files: list[EditedFile] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        summary = self.summary

        content = self.content

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        nia_references: dict[str, Any] | Unset = UNSET
        if not isinstance(self.nia_references, Unset):
            nia_references = self.nia_references.to_dict()

        edited_files: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.edited_files, Unset):
            edited_files = []
            for edited_files_item_data in self.edited_files:
                edited_files_item = edited_files_item_data.to_dict()
                edited_files.append(edited_files_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary
        if content is not UNSET:
            field_dict["content"] = content
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if nia_references is not UNSET:
            field_dict["nia_references"] = nia_references
        if edited_files is not UNSET:
            field_dict["edited_files"] = edited_files

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_share_update_request_metadata import ContextShareUpdateRequestMetadata
        from ..models.edited_file import EditedFile
        from ..models.nia_references import NiaReferences

        d = dict(src_dict)
        title = d.pop("title", UNSET)

        summary = d.pop("summary", UNSET)

        content = d.pop("content", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: ContextShareUpdateRequestMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ContextShareUpdateRequestMetadata.from_dict(_metadata)

        _nia_references = d.pop("nia_references", UNSET)
        nia_references: NiaReferences | Unset
        if isinstance(_nia_references, Unset):
            nia_references = UNSET
        else:
            nia_references = NiaReferences.from_dict(_nia_references)

        _edited_files = d.pop("edited_files", UNSET)
        edited_files: list[EditedFile] | Unset = UNSET
        if _edited_files is not UNSET:
            edited_files = []
            for edited_files_item_data in _edited_files:
                edited_files_item = EditedFile.from_dict(edited_files_item_data)

                edited_files.append(edited_files_item)

        context_share_update_request = cls(
            title=title,
            summary=summary,
            content=content,
            tags=tags,
            metadata=metadata,
            nia_references=nia_references,
            edited_files=edited_files,
        )

        context_share_update_request.additional_properties = d
        return context_share_update_request

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
