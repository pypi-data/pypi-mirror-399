from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.git_hub_tree_response_stats import GitHubTreeResponseStats
    from ..models.git_hub_tree_response_tree_item import GitHubTreeResponseTreeItem


T = TypeVar("T", bound="GitHubTreeResponse")


@_attrs_define
class GitHubTreeResponse:
    """
    Attributes:
        repository (str | Unset): Repository identifier
        branch (str | Unset): Branch name
        tree (list[GitHubTreeResponseTreeItem] | Unset):
        stats (GitHubTreeResponseStats | Unset):
        formatted_tree (str | Unset): Text representation of the tree structure
    """

    repository: str | Unset = UNSET
    branch: str | Unset = UNSET
    tree: list[GitHubTreeResponseTreeItem] | Unset = UNSET
    stats: GitHubTreeResponseStats | Unset = UNSET
    formatted_tree: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        branch = self.branch

        tree: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.tree, Unset):
            tree = []
            for tree_item_data in self.tree:
                tree_item = tree_item_data.to_dict()
                tree.append(tree_item)

        stats: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stats, Unset):
            stats = self.stats.to_dict()

        formatted_tree = self.formatted_tree

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if branch is not UNSET:
            field_dict["branch"] = branch
        if tree is not UNSET:
            field_dict["tree"] = tree
        if stats is not UNSET:
            field_dict["stats"] = stats
        if formatted_tree is not UNSET:
            field_dict["formatted_tree"] = formatted_tree

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.git_hub_tree_response_stats import GitHubTreeResponseStats
        from ..models.git_hub_tree_response_tree_item import GitHubTreeResponseTreeItem

        d = dict(src_dict)
        repository = d.pop("repository", UNSET)

        branch = d.pop("branch", UNSET)

        _tree = d.pop("tree", UNSET)
        tree: list[GitHubTreeResponseTreeItem] | Unset = UNSET
        if _tree is not UNSET:
            tree = []
            for tree_item_data in _tree:
                tree_item = GitHubTreeResponseTreeItem.from_dict(tree_item_data)

                tree.append(tree_item)

        _stats = d.pop("stats", UNSET)
        stats: GitHubTreeResponseStats | Unset
        if isinstance(_stats, Unset):
            stats = UNSET
        else:
            stats = GitHubTreeResponseStats.from_dict(_stats)

        formatted_tree = d.pop("formatted_tree", UNSET)

        git_hub_tree_response = cls(
            repository=repository,
            branch=branch,
            tree=tree,
            stats=stats,
            formatted_tree=formatted_tree,
        )

        git_hub_tree_response.additional_properties = d
        return git_hub_tree_response

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
