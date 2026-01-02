from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.universal_search_response_results_item_source_type import UniversalSearchResponseResultsItemSourceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="UniversalSearchResponseResultsItemSource")


@_attrs_define
class UniversalSearchResponseResultsItemSource:
    """
    Attributes:
        type_ (UniversalSearchResponseResultsItemSourceType | Unset): Type of source
        url (str | Unset): URL of the source
        namespace (str | Unset): Namespace identifier
        file_path (str | Unset): File path within the source (if applicable)
        display_name (str | Unset): Human-readable name of the source
    """

    type_: UniversalSearchResponseResultsItemSourceType | Unset = UNSET
    url: str | Unset = UNSET
    namespace: str | Unset = UNSET
    file_path: str | Unset = UNSET
    display_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        url = self.url

        namespace = self.namespace

        file_path = self.file_path

        display_name = self.display_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if url is not UNSET:
            field_dict["url"] = url
        if namespace is not UNSET:
            field_dict["namespace"] = namespace
        if file_path is not UNSET:
            field_dict["file_path"] = file_path
        if display_name is not UNSET:
            field_dict["display_name"] = display_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: UniversalSearchResponseResultsItemSourceType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = UniversalSearchResponseResultsItemSourceType(_type_)

        url = d.pop("url", UNSET)

        namespace = d.pop("namespace", UNSET)

        file_path = d.pop("file_path", UNSET)

        display_name = d.pop("display_name", UNSET)

        universal_search_response_results_item_source = cls(
            type_=type_,
            url=url,
            namespace=namespace,
            file_path=file_path,
            display_name=display_name,
        )

        universal_search_response_results_item_source.additional_properties = d
        return universal_search_response_results_item_source

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
