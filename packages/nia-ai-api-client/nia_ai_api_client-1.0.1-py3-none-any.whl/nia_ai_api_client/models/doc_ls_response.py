from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.doc_ls_item import DocLsItem


T = TypeVar("T", bound="DocLsResponse")


@_attrs_define
class DocLsResponse:
    """Response for documentation listing.

    Attributes:
        path (str): Current path
        items (list[DocLsItem] | Unset): Listed items
        total (int | Unset): Total items in this path Default: 0.
    """

    path: str
    items: list[DocLsItem] | Unset = UNSET
    total: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        path = self.path

        items: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.items, Unset):
            items = []
            for items_item_data in self.items:
                items_item = items_item_data.to_dict()
                items.append(items_item)

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "path": path,
            }
        )
        if items is not UNSET:
            field_dict["items"] = items
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.doc_ls_item import DocLsItem

        d = dict(src_dict)
        path = d.pop("path")

        _items = d.pop("items", UNSET)
        items: list[DocLsItem] | Unset = UNSET
        if _items is not UNSET:
            items = []
            for items_item_data in _items:
                items_item = DocLsItem.from_dict(items_item_data)

                items.append(items_item)

        total = d.pop("total", UNSET)

        doc_ls_response = cls(
            path=path,
            items=items,
            total=total,
        )

        doc_ls_response.additional_properties = d
        return doc_ls_response

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
