from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TreeItem")


@_attrs_define
class TreeItem:
    """A single item in a repository tree.

    Attributes:
        path (str): File/folder path
        type_ (str): Type: 'blob' (file) or 'tree' (directory)
        mode (None | str | Unset): Git file mode
        sha (None | str | Unset): Git SHA
        size (int | None | Unset): File size in bytes
        url (None | str | Unset): API URL for this item
    """

    path: str
    type_: str
    mode: None | str | Unset = UNSET
    sha: None | str | Unset = UNSET
    size: int | None | Unset = UNSET
    url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        type_ = self.type_

        mode: None | str | Unset
        if isinstance(self.mode, Unset):
            mode = UNSET
        else:
            mode = self.mode

        sha: None | str | Unset
        if isinstance(self.sha, Unset):
            sha = UNSET
        else:
            sha = self.sha

        size: int | None | Unset
        if isinstance(self.size, Unset):
            size = UNSET
        else:
            size = self.size

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
                "type": type_,
            }
        )
        if mode is not UNSET:
            field_dict["mode"] = mode
        if sha is not UNSET:
            field_dict["sha"] = sha
        if size is not UNSET:
            field_dict["size"] = size
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        path = d.pop("path")

        type_ = d.pop("type")

        def _parse_mode(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mode = _parse_mode(d.pop("mode", UNSET))

        def _parse_sha(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sha = _parse_sha(d.pop("sha", UNSET))

        def _parse_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        size = _parse_size(d.pop("size", UNSET))

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        tree_item = cls(
            path=path,
            type_=type_,
            mode=mode,
            sha=sha,
            size=size,
            url=url,
        )

        tree_item.additional_properties = d
        return tree_item

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
