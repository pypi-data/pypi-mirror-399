from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.oracle_research_request_model import OracleResearchRequestModel
from ..types import UNSET, Unset

T = TypeVar("T", bound="OracleResearchRequest")


@_attrs_define
class OracleResearchRequest:
    """
    Attributes:
        query (str): Research question to investigate Example: How does authentication work in the FastAPI codebase?.
        repositories (list[str] | Unset): Optional list of repository identifiers to search Example: ['fastapi/fastapi',
            'tiangolo/sqlmodel'].
        data_sources (list[str] | Unset): Optional list of documentation source identifiers to search Example: ['FastAPI
            Documentation', 'SQLModel Docs'].
        output_format (str | Unset): Optional output format specification Example: markdown report with code examples.
        model (OracleResearchRequestModel | Unset): Optional model selection for Oracle (defaults to claude-
            opus-4-5-20251101)
    """

    query: str
    repositories: list[str] | Unset = UNSET
    data_sources: list[str] | Unset = UNSET
    output_format: str | Unset = UNSET
    model: OracleResearchRequestModel | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        repositories: list[str] | Unset = UNSET
        if not isinstance(self.repositories, Unset):
            repositories = self.repositories

        data_sources: list[str] | Unset = UNSET
        if not isinstance(self.data_sources, Unset):
            data_sources = self.data_sources

        output_format = self.output_format

        model: str | Unset = UNSET
        if not isinstance(self.model, Unset):
            model = self.model.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if repositories is not UNSET:
            field_dict["repositories"] = repositories
        if data_sources is not UNSET:
            field_dict["data_sources"] = data_sources
        if output_format is not UNSET:
            field_dict["output_format"] = output_format
        if model is not UNSET:
            field_dict["model"] = model

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        repositories = cast(list[str], d.pop("repositories", UNSET))

        data_sources = cast(list[str], d.pop("data_sources", UNSET))

        output_format = d.pop("output_format", UNSET)

        _model = d.pop("model", UNSET)
        model: OracleResearchRequestModel | Unset
        if isinstance(_model, Unset):
            model = UNSET
        else:
            model = OracleResearchRequestModel(_model)

        oracle_research_request = cls(
            query=query,
            repositories=repositories,
            data_sources=data_sources,
            output_format=output_format,
            model=model,
        )

        oracle_research_request.additional_properties = d
        return oracle_research_request

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
