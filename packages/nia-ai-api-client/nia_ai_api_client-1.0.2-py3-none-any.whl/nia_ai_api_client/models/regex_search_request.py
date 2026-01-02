from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegexSearchRequest")


@_attrs_define
class RegexSearchRequest:
    r"""
    Attributes:
        repositories (list[str]): List of repositories to search (owner/repo format) Example: ['facebook/react',
            'vercel/next.js'].
        query (str): Natural language query or regex pattern Example: function handleSubmit.
        pattern (str | Unset): Optional explicit regex pattern (overrides automatic extraction from query) Example:
            async\s+function\s+\w+.
        file_extensions (list[str] | Unset): File extensions to filter (e.g., [".js", ".tsx", ".py"])
        languages (list[str] | Unset): Programming languages to filter (e.g., ["python", "javascript", "typescript"])
        max_results (int | Unset): Maximum number of results to return Default: 50.
        include_context (bool | Unset): Include surrounding context lines Default: True.
        context_lines (int | Unset): Number of context lines before/after match Default: 3.
    """

    repositories: list[str]
    query: str
    pattern: str | Unset = UNSET
    file_extensions: list[str] | Unset = UNSET
    languages: list[str] | Unset = UNSET
    max_results: int | Unset = 50
    include_context: bool | Unset = True
    context_lines: int | Unset = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repositories = self.repositories

        query = self.query

        pattern = self.pattern

        file_extensions: list[str] | Unset = UNSET
        if not isinstance(self.file_extensions, Unset):
            file_extensions = self.file_extensions

        languages: list[str] | Unset = UNSET
        if not isinstance(self.languages, Unset):
            languages = self.languages

        max_results = self.max_results

        include_context = self.include_context

        context_lines = self.context_lines

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repositories": repositories,
                "query": query,
            }
        )
        if pattern is not UNSET:
            field_dict["pattern"] = pattern
        if file_extensions is not UNSET:
            field_dict["file_extensions"] = file_extensions
        if languages is not UNSET:
            field_dict["languages"] = languages
        if max_results is not UNSET:
            field_dict["max_results"] = max_results
        if include_context is not UNSET:
            field_dict["include_context"] = include_context
        if context_lines is not UNSET:
            field_dict["context_lines"] = context_lines

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        repositories = cast(list[str], d.pop("repositories"))

        query = d.pop("query")

        pattern = d.pop("pattern", UNSET)

        file_extensions = cast(list[str], d.pop("file_extensions", UNSET))

        languages = cast(list[str], d.pop("languages", UNSET))

        max_results = d.pop("max_results", UNSET)

        include_context = d.pop("include_context", UNSET)

        context_lines = d.pop("context_lines", UNSET)

        regex_search_request = cls(
            repositories=repositories,
            query=query,
            pattern=pattern,
            file_extensions=file_extensions,
            languages=languages,
            max_results=max_results,
            include_context=include_context,
            context_lines=context_lines,
        )

        regex_search_request.additional_properties = d
        return regex_search_request

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
