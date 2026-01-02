from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.package_search_response_results_item import PackageSearchResponseResultsItem


T = TypeVar("T", bound="PackageSearchResponse")


@_attrs_define
class PackageSearchResponse:
    """Raw response from Chroma Package Search API

    Attributes:
        version_used (str | Unset): Version of the package that was searched Example: 18.2.0.
        results (list[PackageSearchResponseResultsItem] | Unset): Search results from the package
        truncation_message (str | Unset): Message indicating if results were truncated
    """

    version_used: str | Unset = UNSET
    results: list[PackageSearchResponseResultsItem] | Unset = UNSET
    truncation_message: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version_used = self.version_used

        results: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.results, Unset):
            results = []
            for results_item_data in self.results:
                results_item = results_item_data.to_dict()
                results.append(results_item)

        truncation_message = self.truncation_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version_used is not UNSET:
            field_dict["version_used"] = version_used
        if results is not UNSET:
            field_dict["results"] = results
        if truncation_message is not UNSET:
            field_dict["truncation_message"] = truncation_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.package_search_response_results_item import PackageSearchResponseResultsItem

        d = dict(src_dict)
        version_used = d.pop("version_used", UNSET)

        _results = d.pop("results", UNSET)
        results: list[PackageSearchResponseResultsItem] | Unset = UNSET
        if _results is not UNSET:
            results = []
            for results_item_data in _results:
                results_item = PackageSearchResponseResultsItem.from_dict(results_item_data)

                results.append(results_item)

        truncation_message = d.pop("truncation_message", UNSET)

        package_search_response = cls(
            version_used=version_used,
            results=results,
            truncation_message=truncation_message,
        )

        package_search_response.additional_properties = d
        return package_search_response

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
