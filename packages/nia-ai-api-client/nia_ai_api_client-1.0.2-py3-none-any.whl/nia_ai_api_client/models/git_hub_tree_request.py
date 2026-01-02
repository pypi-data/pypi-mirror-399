from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GitHubTreeRequest")


@_attrs_define
class GitHubTreeRequest:
    """
    Attributes:
        repository_id (str): Repository identifier (owner/repo format)
        branch (str | Unset): Branch name (optional, defaults to repository's default branch)
        include_paths (list[str] | Unset): Only show files in these paths (e.g., ["src/", "lib/"])
        exclude_paths (list[str] | Unset): Hide files in these paths (e.g., ["node_modules/", "dist/"])
        file_extensions (list[str] | Unset): Only show these file types (e.g., [".py", ".js", ".ts"])
        exclude_extensions (list[str] | Unset): Hide these file types (e.g., [".md", ".lock", ".json"])
        show_full_paths (bool | Unset): Show full paths instead of tree structure Default: False.
    """

    repository_id: str
    branch: str | Unset = UNSET
    include_paths: list[str] | Unset = UNSET
    exclude_paths: list[str] | Unset = UNSET
    file_extensions: list[str] | Unset = UNSET
    exclude_extensions: list[str] | Unset = UNSET
    show_full_paths: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository_id = self.repository_id

        branch = self.branch

        include_paths: list[str] | Unset = UNSET
        if not isinstance(self.include_paths, Unset):
            include_paths = self.include_paths

        exclude_paths: list[str] | Unset = UNSET
        if not isinstance(self.exclude_paths, Unset):
            exclude_paths = self.exclude_paths

        file_extensions: list[str] | Unset = UNSET
        if not isinstance(self.file_extensions, Unset):
            file_extensions = self.file_extensions

        exclude_extensions: list[str] | Unset = UNSET
        if not isinstance(self.exclude_extensions, Unset):
            exclude_extensions = self.exclude_extensions

        show_full_paths = self.show_full_paths

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository_id": repository_id,
            }
        )
        if branch is not UNSET:
            field_dict["branch"] = branch
        if include_paths is not UNSET:
            field_dict["include_paths"] = include_paths
        if exclude_paths is not UNSET:
            field_dict["exclude_paths"] = exclude_paths
        if file_extensions is not UNSET:
            field_dict["file_extensions"] = file_extensions
        if exclude_extensions is not UNSET:
            field_dict["exclude_extensions"] = exclude_extensions
        if show_full_paths is not UNSET:
            field_dict["show_full_paths"] = show_full_paths

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repository_id = d.pop("repository_id")

        branch = d.pop("branch", UNSET)

        include_paths = cast(list[str], d.pop("include_paths", UNSET))

        exclude_paths = cast(list[str], d.pop("exclude_paths", UNSET))

        file_extensions = cast(list[str], d.pop("file_extensions", UNSET))

        exclude_extensions = cast(list[str], d.pop("exclude_extensions", UNSET))

        show_full_paths = d.pop("show_full_paths", UNSET)

        git_hub_tree_request = cls(
            repository_id=repository_id,
            branch=branch,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            file_extensions=file_extensions,
            exclude_extensions=exclude_extensions,
            show_full_paths=show_full_paths,
        )

        git_hub_tree_request.additional_properties = d
        return git_hub_tree_request

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
