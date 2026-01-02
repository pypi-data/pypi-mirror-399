from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.repository_status_status import RepositoryStatusStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repository_status_progress import RepositoryStatusProgress


T = TypeVar("T", bound="RepositoryStatus")


@_attrs_define
class RepositoryStatus:
    """
    Attributes:
        repository (str): Repository identifier
        branch (str): Branch being indexed
        status (RepositoryStatusStatus): Current indexing status
        progress (RepositoryStatusProgress | Unset): Detailed progress information
        error (str | Unset): Error message if status is 'error'
    """

    repository: str
    branch: str
    status: RepositoryStatusStatus
    progress: RepositoryStatusProgress | Unset = UNSET
    error: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        branch = self.branch

        status = self.status.value

        progress: dict[str, Any] | Unset = UNSET
        if not isinstance(self.progress, Unset):
            progress = self.progress.to_dict()

        error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository": repository,
                "branch": branch,
                "status": status,
            }
        )
        if progress is not UNSET:
            field_dict["progress"] = progress
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repository_status_progress import RepositoryStatusProgress

        d = dict(src_dict)
        repository = d.pop("repository")

        branch = d.pop("branch")

        status = RepositoryStatusStatus(d.pop("status"))

        _progress = d.pop("progress", UNSET)
        progress: RepositoryStatusProgress | Unset
        if isinstance(_progress, Unset):
            progress = UNSET
        else:
            progress = RepositoryStatusProgress.from_dict(_progress)

        error = d.pop("error", UNSET)

        repository_status = cls(
            repository=repository,
            branch=branch,
            status=status,
            progress=progress,
            error=error,
        )

        repository_status.additional_properties = d
        return repository_status

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
