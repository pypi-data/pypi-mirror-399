from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.web_search_documentation import WebSearchDocumentation
    from ..models.web_search_git_hub_repo import WebSearchGitHubRepo
    from ..models.web_search_other_content import WebSearchOtherContent


T = TypeVar("T", bound="WebSearchResponse")


@_attrs_define
class WebSearchResponse:
    """Response for web search.

    Attributes:
        github_repos (list[WebSearchGitHubRepo] | Unset): GitHub repositories found
        documentation (list[WebSearchDocumentation] | Unset): Documentation pages found
        other_content (list[WebSearchOtherContent] | Unset): Other content found
        total_results (int | Unset): Total number of results Default: 0.
    """

    github_repos: list[WebSearchGitHubRepo] | Unset = UNSET
    documentation: list[WebSearchDocumentation] | Unset = UNSET
    other_content: list[WebSearchOtherContent] | Unset = UNSET
    total_results: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        github_repos: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.github_repos, Unset):
            github_repos = []
            for github_repos_item_data in self.github_repos:
                github_repos_item = github_repos_item_data.to_dict()
                github_repos.append(github_repos_item)

        documentation: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.documentation, Unset):
            documentation = []
            for documentation_item_data in self.documentation:
                documentation_item = documentation_item_data.to_dict()
                documentation.append(documentation_item)

        other_content: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.other_content, Unset):
            other_content = []
            for other_content_item_data in self.other_content:
                other_content_item = other_content_item_data.to_dict()
                other_content.append(other_content_item)

        total_results = self.total_results

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if github_repos is not UNSET:
            field_dict["github_repos"] = github_repos
        if documentation is not UNSET:
            field_dict["documentation"] = documentation
        if other_content is not UNSET:
            field_dict["other_content"] = other_content
        if total_results is not UNSET:
            field_dict["total_results"] = total_results

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.web_search_documentation import WebSearchDocumentation
        from ..models.web_search_git_hub_repo import WebSearchGitHubRepo
        from ..models.web_search_other_content import WebSearchOtherContent

        d = dict(src_dict)
        _github_repos = d.pop("github_repos", UNSET)
        github_repos: list[WebSearchGitHubRepo] | Unset = UNSET
        if _github_repos is not UNSET:
            github_repos = []
            for github_repos_item_data in _github_repos:
                github_repos_item = WebSearchGitHubRepo.from_dict(github_repos_item_data)

                github_repos.append(github_repos_item)

        _documentation = d.pop("documentation", UNSET)
        documentation: list[WebSearchDocumentation] | Unset = UNSET
        if _documentation is not UNSET:
            documentation = []
            for documentation_item_data in _documentation:
                documentation_item = WebSearchDocumentation.from_dict(documentation_item_data)

                documentation.append(documentation_item)

        _other_content = d.pop("other_content", UNSET)
        other_content: list[WebSearchOtherContent] | Unset = UNSET
        if _other_content is not UNSET:
            other_content = []
            for other_content_item_data in _other_content:
                other_content_item = WebSearchOtherContent.from_dict(other_content_item_data)

                other_content.append(other_content_item)

        total_results = d.pop("total_results", UNSET)

        web_search_response = cls(
            github_repos=github_repos,
            documentation=documentation,
            other_content=other_content,
            total_results=total_results,
        )

        web_search_response.additional_properties = d
        return web_search_response

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
