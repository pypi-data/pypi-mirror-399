from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.get_documentation_tree_response_200_tree import GetDocumentationTreeResponse200Tree


T = TypeVar("T", bound="GetDocumentationTreeResponse200")


@_attrs_define
class GetDocumentationTreeResponse200:
    """
    Attributes:
        success (bool | Unset):
        tree (GetDocumentationTreeResponse200Tree | Unset): Nested tree structure of documentation pages
        tree_string (str | Unset): Formatted text representation of the tree
        base_url (str | Unset): Base URL of the documentation
        page_count (int | Unset): Total number of indexed pages
    """

    success: bool | Unset = UNSET
    tree: GetDocumentationTreeResponse200Tree | Unset = UNSET
    tree_string: str | Unset = UNSET
    base_url: str | Unset = UNSET
    page_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        tree: dict[str, Any] | Unset = UNSET
        if not isinstance(self.tree, Unset):
            tree = self.tree.to_dict()

        tree_string = self.tree_string

        base_url = self.base_url

        page_count = self.page_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if success is not UNSET:
            field_dict["success"] = success
        if tree is not UNSET:
            field_dict["tree"] = tree
        if tree_string is not UNSET:
            field_dict["tree_string"] = tree_string
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if page_count is not UNSET:
            field_dict["page_count"] = page_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.get_documentation_tree_response_200_tree import GetDocumentationTreeResponse200Tree

        d = dict(src_dict)
        success = d.pop("success", UNSET)

        _tree = d.pop("tree", UNSET)
        tree: GetDocumentationTreeResponse200Tree | Unset
        if isinstance(_tree, Unset):
            tree = UNSET
        else:
            tree = GetDocumentationTreeResponse200Tree.from_dict(_tree)

        tree_string = d.pop("tree_string", UNSET)

        base_url = d.pop("base_url", UNSET)

        page_count = d.pop("page_count", UNSET)

        get_documentation_tree_response_200 = cls(
            success=success,
            tree=tree,
            tree_string=tree_string,
            base_url=base_url,
            page_count=page_count,
        )

        get_documentation_tree_response_200.additional_properties = d
        return get_documentation_tree_response_200

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
