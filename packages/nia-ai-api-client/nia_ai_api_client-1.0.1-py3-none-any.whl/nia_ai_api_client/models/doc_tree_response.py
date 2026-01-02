from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.doc_tree_node import DocTreeNode


T = TypeVar("T", bound="DocTreeResponse")


@_attrs_define
class DocTreeResponse:
    """Response for documentation tree.

    Attributes:
        tree (list[DocTreeNode] | Unset): Tree structure
        total_pages (int | Unset): Total number of pages Default: 0.
    """

    tree: list[DocTreeNode] | Unset = UNSET
    total_pages: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tree: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tree, Unset):
            tree = []
            for tree_item_data in self.tree:
                tree_item = tree_item_data.to_dict()
                tree.append(tree_item)

        total_pages = self.total_pages

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tree is not UNSET:
            field_dict["tree"] = tree
        if total_pages is not UNSET:
            field_dict["total_pages"] = total_pages

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.doc_tree_node import DocTreeNode

        d = dict(src_dict)
        _tree = d.pop("tree", UNSET)
        tree: list[DocTreeNode] | Unset = UNSET
        if _tree is not UNSET:
            tree = []
            for tree_item_data in _tree:
                tree_item = DocTreeNode.from_dict(tree_item_data)

                tree.append(tree_item)

        total_pages = d.pop("total_pages", UNSET)

        doc_tree_response = cls(
            tree=tree,
            total_pages=total_pages,
        )

        doc_tree_response.additional_properties = d
        return doc_tree_response

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
