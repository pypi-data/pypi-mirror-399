from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_repository_content_response_200_metadata import GetRepositoryContentResponse200Metadata


T = TypeVar("T", bound="GetRepositoryContentResponse200")


@_attrs_define
class GetRepositoryContentResponse200:
    """
    Attributes:
        success (bool | Unset):
        content (str | Unset): Full file content
        metadata (GetRepositoryContentResponse200Metadata | Unset):
    """

    success: bool | Unset = UNSET
    content: str | Unset = UNSET
    metadata: GetRepositoryContentResponse200Metadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        content = self.content

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if content is not UNSET:
            field_dict["content"] = content
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_repository_content_response_200_metadata import GetRepositoryContentResponse200Metadata

        d = dict(src_dict)
        success = d.pop("success", UNSET)

        content = d.pop("content", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: GetRepositoryContentResponse200Metadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = GetRepositoryContentResponse200Metadata.from_dict(_metadata)

        get_repository_content_response_200 = cls(
            success=success,
            content=content,
            metadata=metadata,
        )

        get_repository_content_response_200.additional_properties = d
        return get_repository_content_response_200

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
