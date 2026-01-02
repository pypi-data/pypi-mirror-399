from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UniversalSearchRequest")


@_attrs_define
class UniversalSearchRequest:
    """
    Attributes:
        query (str): Natural language search query Example: How does authentication work in FastAPI?.
        top_k (int | Unset): Total number of results to return Default: 20.
        include_repos (bool | Unset): Include repository sources in search Default: True.
        include_docs (bool | Unset): Include documentation sources in search Default: True.
        alpha (float | Unset): Weight for vector search (1-alpha for BM25). Higher values favor semantic similarity.
            Default: 0.7.
        compress_output (bool | Unset): Use AI to compress results into a concise answer with citations Default: False.
    """

    query: str
    top_k: int | Unset = 20
    include_repos: bool | Unset = True
    include_docs: bool | Unset = True
    alpha: float | Unset = 0.7
    compress_output: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        top_k = self.top_k

        include_repos = self.include_repos

        include_docs = self.include_docs

        alpha = self.alpha

        compress_output = self.compress_output

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if include_repos is not UNSET:
            field_dict["include_repos"] = include_repos
        if include_docs is not UNSET:
            field_dict["include_docs"] = include_docs
        if alpha is not UNSET:
            field_dict["alpha"] = alpha
        if compress_output is not UNSET:
            field_dict["compress_output"] = compress_output

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        top_k = d.pop("top_k", UNSET)

        include_repos = d.pop("include_repos", UNSET)

        include_docs = d.pop("include_docs", UNSET)

        alpha = d.pop("alpha", UNSET)

        compress_output = d.pop("compress_output", UNSET)

        universal_search_request = cls(
            query=query,
            top_k=top_k,
            include_repos=include_repos,
            include_docs=include_docs,
            alpha=alpha,
            compress_output=compress_output,
        )

        universal_search_request.additional_properties = d
        return universal_search_request

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
