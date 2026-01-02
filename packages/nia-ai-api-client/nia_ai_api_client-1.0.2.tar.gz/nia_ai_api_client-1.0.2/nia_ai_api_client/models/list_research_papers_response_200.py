from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.research_paper_response import ResearchPaperResponse


T = TypeVar("T", bound="ListResearchPapersResponse200")


@_attrs_define
class ListResearchPapersResponse200:
    """
    Attributes:
        papers (list[ResearchPaperResponse] | Unset):
        total (int | Unset): Total number of matching papers
    """

    papers: list[ResearchPaperResponse] | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        papers: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.papers, Unset):
            papers = []
            for papers_item_data in self.papers:
                papers_item = papers_item_data.to_dict()
                papers.append(papers_item)

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if papers is not UNSET:
            field_dict["papers"] = papers
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.research_paper_response import ResearchPaperResponse

        d = dict(src_dict)
        _papers = d.pop("papers", UNSET)
        papers: list[ResearchPaperResponse] | Unset = UNSET
        if _papers is not UNSET:
            papers = []
            for papers_item_data in _papers:
                papers_item = ResearchPaperResponse.from_dict(papers_item_data)

                papers.append(papers_item)

        total = d.pop("total", UNSET)

        list_research_papers_response_200 = cls(
            papers=papers,
            total=total,
        )

        list_research_papers_response_200.additional_properties = d
        return list_research_papers_response_200

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
