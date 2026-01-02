from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repository_progress import RepositoryProgress


T = TypeVar("T", bound="RepositoryItem")


@_attrs_define
class RepositoryItem:
    """A single repository in the list.

    Attributes:
        repository_id (str): Internal repository ID
        repository (str): Repository identifier (owner/repo)
        branch (str): Branch name
        status (str): Indexing status
        id (None | str | Unset): Project ID
        display_name (None | str | Unset): Custom display name
        is_global (bool | None | Unset): Whether this is a global source
        global_source_id (None | str | Unset): Global source ID if applicable
        global_namespace (None | str | Unset): Global namespace if applicable
        progress (None | RepositoryProgress | Unset): Indexing progress
        error (None | str | Unset): Error message if status is error
    """

    repository_id: str
    repository: str
    branch: str
    status: str
    id: None | str | Unset = UNSET
    display_name: None | str | Unset = UNSET
    is_global: bool | None | Unset = UNSET
    global_source_id: None | str | Unset = UNSET
    global_namespace: None | str | Unset = UNSET
    progress: None | RepositoryProgress | Unset = UNSET
    error: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.repository_progress import RepositoryProgress

        repository_id = self.repository_id

        repository = self.repository

        branch = self.branch

        status = self.status

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        is_global: bool | None | Unset
        if isinstance(self.is_global, Unset):
            is_global = UNSET
        else:
            is_global = self.is_global

        global_source_id: None | str | Unset
        if isinstance(self.global_source_id, Unset):
            global_source_id = UNSET
        else:
            global_source_id = self.global_source_id

        global_namespace: None | str | Unset
        if isinstance(self.global_namespace, Unset):
            global_namespace = UNSET
        else:
            global_namespace = self.global_namespace

        progress: dict[str, Any] | None | Unset
        if isinstance(self.progress, Unset):
            progress = UNSET
        elif isinstance(self.progress, RepositoryProgress):
            progress = self.progress.to_dict()
        else:
            progress = self.progress

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repository_id": repository_id,
                "repository": repository,
                "branch": branch,
                "status": status,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if is_global is not UNSET:
            field_dict["is_global"] = is_global
        if global_source_id is not UNSET:
            field_dict["global_source_id"] = global_source_id
        if global_namespace is not UNSET:
            field_dict["global_namespace"] = global_namespace
        if progress is not UNSET:
            field_dict["progress"] = progress
        if error is not UNSET:
            field_dict["error"] = error

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.repository_progress import RepositoryProgress

        d = dict(src_dict)
        repository_id = d.pop("repository_id")

        repository = d.pop("repository")

        branch = d.pop("branch")

        status = d.pop("status")

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_is_global(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_global = _parse_is_global(d.pop("is_global", UNSET))

        def _parse_global_source_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        global_source_id = _parse_global_source_id(d.pop("global_source_id", UNSET))

        def _parse_global_namespace(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        global_namespace = _parse_global_namespace(d.pop("global_namespace", UNSET))

        def _parse_progress(data: object) -> None | RepositoryProgress | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                progress_type_0 = RepositoryProgress.from_dict(data)

                return progress_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RepositoryProgress | Unset, data)

        progress = _parse_progress(d.pop("progress", UNSET))

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        repository_item = cls(
            repository_id=repository_id,
            repository=repository,
            branch=branch,
            status=status,
            id=id,
            display_name=display_name,
            is_global=is_global,
            global_source_id=global_source_id,
            global_namespace=global_namespace,
            progress=progress,
            error=error,
        )

        repository_item.additional_properties = d
        return repository_item

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
