from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SourceContentResponseMetadata")


@_attrs_define
class SourceContentResponseMetadata:
    """
    Attributes:
        repository (str | Unset):
        file_path (str | Unset):
        branch (str | Unset):
        language (str | Unset):
        url (str | Unset):
        title (str | Unset):
        source_type (str | Unset):
    """

    repository: str | Unset = UNSET
    file_path: str | Unset = UNSET
    branch: str | Unset = UNSET
    language: str | Unset = UNSET
    url: str | Unset = UNSET
    title: str | Unset = UNSET
    source_type: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        file_path = self.file_path

        branch = self.branch

        language = self.language

        url = self.url

        title = self.title

        source_type = self.source_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if file_path is not UNSET:
            field_dict["file_path"] = file_path
        if branch is not UNSET:
            field_dict["branch"] = branch
        if language is not UNSET:
            field_dict["language"] = language
        if url is not UNSET:
            field_dict["url"] = url
        if title is not UNSET:
            field_dict["title"] = title
        if source_type is not UNSET:
            field_dict["source_type"] = source_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository = d.pop("repository", UNSET)

        file_path = d.pop("file_path", UNSET)

        branch = d.pop("branch", UNSET)

        language = d.pop("language", UNSET)

        url = d.pop("url", UNSET)

        title = d.pop("title", UNSET)

        source_type = d.pop("source_type", UNSET)

        source_content_response_metadata = cls(
            repository=repository,
            file_path=file_path,
            branch=branch,
            language=language,
            url=url,
            title=title,
            source_type=source_type,
        )

        source_content_response_metadata.additional_properties = d
        return source_content_response_metadata

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
