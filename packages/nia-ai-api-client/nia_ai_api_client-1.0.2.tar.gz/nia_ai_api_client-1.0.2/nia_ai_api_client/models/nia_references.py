from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NiaReferences")


@_attrs_define
class NiaReferences:
    """References to NIA resources used during the conversation

    Attributes:
        indexed_repositories (list[str] | Unset): List of repository identifiers that were indexed
        indexed_documentation (list[str] | Unset): List of documentation source identifiers
        queried_repositories (list[str] | Unset): Repositories that were queried
        queried_documentation (list[str] | Unset): Documentation sources that were queried
        web_searches (list[str] | Unset): Web search queries performed
        deep_research_queries (list[str] | Unset): Deep research queries performed
    """

    indexed_repositories: list[str] | Unset = UNSET
    indexed_documentation: list[str] | Unset = UNSET
    queried_repositories: list[str] | Unset = UNSET
    queried_documentation: list[str] | Unset = UNSET
    web_searches: list[str] | Unset = UNSET
    deep_research_queries: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        indexed_repositories: list[str] | Unset = UNSET
        if not isinstance(self.indexed_repositories, Unset):
            indexed_repositories = self.indexed_repositories

        indexed_documentation: list[str] | Unset = UNSET
        if not isinstance(self.indexed_documentation, Unset):
            indexed_documentation = self.indexed_documentation

        queried_repositories: list[str] | Unset = UNSET
        if not isinstance(self.queried_repositories, Unset):
            queried_repositories = self.queried_repositories

        queried_documentation: list[str] | Unset = UNSET
        if not isinstance(self.queried_documentation, Unset):
            queried_documentation = self.queried_documentation

        web_searches: list[str] | Unset = UNSET
        if not isinstance(self.web_searches, Unset):
            web_searches = self.web_searches

        deep_research_queries: list[str] | Unset = UNSET
        if not isinstance(self.deep_research_queries, Unset):
            deep_research_queries = self.deep_research_queries

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if indexed_repositories is not UNSET:
            field_dict["indexed_repositories"] = indexed_repositories
        if indexed_documentation is not UNSET:
            field_dict["indexed_documentation"] = indexed_documentation
        if queried_repositories is not UNSET:
            field_dict["queried_repositories"] = queried_repositories
        if queried_documentation is not UNSET:
            field_dict["queried_documentation"] = queried_documentation
        if web_searches is not UNSET:
            field_dict["web_searches"] = web_searches
        if deep_research_queries is not UNSET:
            field_dict["deep_research_queries"] = deep_research_queries

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        indexed_repositories = cast(list[str], d.pop("indexed_repositories", UNSET))

        indexed_documentation = cast(list[str], d.pop("indexed_documentation", UNSET))

        queried_repositories = cast(list[str], d.pop("queried_repositories", UNSET))

        queried_documentation = cast(list[str], d.pop("queried_documentation", UNSET))

        web_searches = cast(list[str], d.pop("web_searches", UNSET))

        deep_research_queries = cast(list[str], d.pop("deep_research_queries", UNSET))

        nia_references = cls(
            indexed_repositories=indexed_repositories,
            indexed_documentation=indexed_documentation,
            queried_repositories=queried_repositories,
            queried_documentation=queried_documentation,
            web_searches=web_searches,
            deep_research_queries=deep_research_queries,
        )

        nia_references.additional_properties = d
        return nia_references

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
