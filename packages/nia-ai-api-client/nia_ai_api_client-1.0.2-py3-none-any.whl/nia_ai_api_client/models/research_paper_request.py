from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ResearchPaperRequest")


@_attrs_define
class ResearchPaperRequest:
    """
    Attributes:
        url (str): arXiv URL or raw ID. Supports multiple formats:
            - Full URL: https://arxiv.org/abs/2312.00752
            - PDF URL: https://arxiv.org/pdf/2312.00752.pdf
            - Raw new-format ID: 2312.00752
            - Raw old-format ID: hep-th/9901001
            - With version: 2312.00752v1
             Example: 2312.00752.
    """

    url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        research_paper_request = cls(
            url=url,
        )

        research_paper_request.additional_properties = d
        return research_paper_request

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
