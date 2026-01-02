from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.deep_research_response_status import DeepResearchResponseStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deep_research_response_citations_item import DeepResearchResponseCitationsItem
    from ..models.deep_research_response_data import DeepResearchResponseData


T = TypeVar("T", bound="DeepResearchResponse")


@_attrs_define
class DeepResearchResponse:
    """
    Attributes:
        data (DeepResearchResponseData | Unset): Structured research data based on the query
        citations (list[DeepResearchResponseCitationsItem] | Unset): Sources cited in the research
        status (DeepResearchResponseStatus | Unset):
    """

    data: DeepResearchResponseData | Unset = UNSET
    citations: list[DeepResearchResponseCitationsItem] | Unset = UNSET
    status: DeepResearchResponseStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.data, Unset):
            data = self.data.to_dict()

        citations: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.citations, Unset):
            citations = []
            for citations_item_data in self.citations:
                citations_item = citations_item_data.to_dict()
                citations.append(citations_item)

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data is not UNSET:
            field_dict["data"] = data
        if citations is not UNSET:
            field_dict["citations"] = citations
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deep_research_response_citations_item import DeepResearchResponseCitationsItem
        from ..models.deep_research_response_data import DeepResearchResponseData

        d = dict(src_dict)
        _data = d.pop("data", UNSET)
        data: DeepResearchResponseData | Unset
        if isinstance(_data, Unset):
            data = UNSET
        else:
            data = DeepResearchResponseData.from_dict(_data)

        _citations = d.pop("citations", UNSET)
        citations: list[DeepResearchResponseCitationsItem] | Unset = UNSET
        if _citations is not UNSET:
            citations = []
            for citations_item_data in _citations:
                citations_item = DeepResearchResponseCitationsItem.from_dict(citations_item_data)

                citations.append(citations_item)

        _status = d.pop("status", UNSET)
        status: DeepResearchResponseStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = DeepResearchResponseStatus(_status)

        deep_research_response = cls(
            data=data,
            citations=citations,
            status=status,
        )

        deep_research_response.additional_properties = d
        return deep_research_response

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
