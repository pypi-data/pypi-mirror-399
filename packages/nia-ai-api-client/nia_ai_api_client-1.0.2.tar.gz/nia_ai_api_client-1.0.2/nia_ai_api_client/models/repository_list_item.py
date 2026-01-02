from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.repository_list_item_status import RepositoryListItemStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repository_list_item_progress import RepositoryListItemProgress


T = TypeVar("T", bound="RepositoryListItem")


@_attrs_define
class RepositoryListItem:
    """
    Attributes:
        repository_id (str | Unset): Unique identifier for the repository
        id (str | Unset): Internal project ID for graph visualization
        repository (str | Unset): Repository identifier in owner/repo format
        branch (str | Unset): Indexed branch
        status (RepositoryListItemStatus | Unset):
        display_name (str | Unset): Custom display name for the repository
        progress (RepositoryListItemProgress | Unset):
        error (str | Unset): Error message if status is 'error'
    """

    repository_id: str | Unset = UNSET
    id: str | Unset = UNSET
    repository: str | Unset = UNSET
    branch: str | Unset = UNSET
    status: RepositoryListItemStatus | Unset = UNSET
    display_name: str | Unset = UNSET
    progress: RepositoryListItemProgress | Unset = UNSET
    error: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository_id = self.repository_id

        id = self.id

        repository = self.repository

        branch = self.branch

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        display_name = self.display_name

        progress: dict[str, Any] | Unset = UNSET
        if not isinstance(self.progress, Unset):
            progress = self.progress.to_dict()

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository_id is not UNSET:
            field_dict["repository_id"] = repository_id
        if id is not UNSET:
            field_dict["id"] = id
        if repository is not UNSET:
            field_dict["repository"] = repository
        if branch is not UNSET:
            field_dict["branch"] = branch
        if status is not UNSET:
            field_dict["status"] = status
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if progress is not UNSET:
            field_dict["progress"] = progress
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repository_list_item_progress import RepositoryListItemProgress

        d = dict(src_dict)
        repository_id = d.pop("repository_id", UNSET)

        id = d.pop("id", UNSET)

        repository = d.pop("repository", UNSET)

        branch = d.pop("branch", UNSET)

        _status = d.pop("status", UNSET)
        status: RepositoryListItemStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = RepositoryListItemStatus(_status)

        display_name = d.pop("display_name", UNSET)

        _progress = d.pop("progress", UNSET)
        progress: RepositoryListItemProgress | Unset
        if isinstance(_progress, Unset):
            progress = UNSET
        else:
            progress = RepositoryListItemProgress.from_dict(_progress)

        error = d.pop("error", UNSET)

        repository_list_item = cls(
            repository_id=repository_id,
            id=id,
            repository=repository,
            branch=branch,
            status=status,
            display_name=display_name,
            progress=progress,
            error=error,
        )

        repository_list_item.additional_properties = d
        return repository_list_item

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
