from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.deep_research_response_citations_type_0_item import DeepResearchResponseCitationsType0Item
    from ..models.deep_research_response_data_type_0 import DeepResearchResponseDataType0


T = TypeVar("T", bound="DeepResearchResponse")


@_attrs_define
class DeepResearchResponse:
    """Response for deep research.

    Attributes:
        status (str): Research task status
        data (DeepResearchResponseDataType0 | None | Unset): Structured research data
        citations (list[DeepResearchResponseCitationsType0Item] | None | Unset): Citations with URLs
    """

    status: str
    data: DeepResearchResponseDataType0 | None | Unset = UNSET
    citations: list[DeepResearchResponseCitationsType0Item] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.deep_research_response_data_type_0 import DeepResearchResponseDataType0

        status = self.status

        data: dict[str, Any] | None | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, DeepResearchResponseDataType0):
            data = self.data.to_dict()
        else:
            data = self.data

        citations: list[dict[str, Any]] | None | Unset
        if isinstance(self.citations, Unset):
            citations = UNSET
        elif isinstance(self.citations, list):
            citations = []
            for citations_type_0_item_data in self.citations:
                citations_type_0_item = citations_type_0_item_data.to_dict()
                citations.append(citations_type_0_item)

        else:
            citations = self.citations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if data is not UNSET:
            field_dict["data"] = data
        if citations is not UNSET:
            field_dict["citations"] = citations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.deep_research_response_citations_type_0_item import DeepResearchResponseCitationsType0Item
        from ..models.deep_research_response_data_type_0 import DeepResearchResponseDataType0

        d = dict(src_dict)
        status = d.pop("status")

        def _parse_data(data: object) -> DeepResearchResponseDataType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_type_0 = DeepResearchResponseDataType0.from_dict(data)

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DeepResearchResponseDataType0 | None | Unset, data)

        data = _parse_data(d.pop("data", UNSET))

        def _parse_citations(data: object) -> list[DeepResearchResponseCitationsType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                citations_type_0 = []
                _citations_type_0 = data
                for citations_type_0_item_data in _citations_type_0:
                    citations_type_0_item = DeepResearchResponseCitationsType0Item.from_dict(citations_type_0_item_data)

                    citations_type_0.append(citations_type_0_item)

                return citations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[DeepResearchResponseCitationsType0Item] | None | Unset, data)

        citations = _parse_citations(d.pop("citations", UNSET))

        deep_research_response = cls(
            status=status,
            data=data,
            citations=citations,
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
