from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_share_response import ContextShareResponse
    from ..models.list_contexts_response_200_pagination import ListContextsResponse200Pagination


T = TypeVar("T", bound="ListContextsResponse200")


@_attrs_define
class ListContextsResponse200:
    """
    Attributes:
        contexts (list[ContextShareResponse] | Unset):
        pagination (ListContextsResponse200Pagination | Unset):
    """

    contexts: list[ContextShareResponse] | Unset = UNSET
    pagination: ListContextsResponse200Pagination | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        contexts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.contexts, Unset):
            contexts = []
            for contexts_item_data in self.contexts:
                contexts_item = contexts_item_data.to_dict()
                contexts.append(contexts_item)

        pagination: dict[str, Any] | Unset = UNSET
        if not isinstance(self.pagination, Unset):
            pagination = self.pagination.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if contexts is not UNSET:
            field_dict["contexts"] = contexts
        if pagination is not UNSET:
            field_dict["pagination"] = pagination

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_share_response import ContextShareResponse
        from ..models.list_contexts_response_200_pagination import ListContextsResponse200Pagination

        d = dict(src_dict)
        _contexts = d.pop("contexts", UNSET)
        contexts: list[ContextShareResponse] | Unset = UNSET
        if _contexts is not UNSET:
            contexts = []
            for contexts_item_data in _contexts:
                contexts_item = ContextShareResponse.from_dict(contexts_item_data)

                contexts.append(contexts_item)

        _pagination = d.pop("pagination", UNSET)
        pagination: ListContextsResponse200Pagination | Unset
        if isinstance(_pagination, Unset):
            pagination = UNSET
        else:
            pagination = ListContextsResponse200Pagination.from_dict(_pagination)

        list_contexts_response_200 = cls(
            contexts=contexts,
            pagination=pagination,
        )

        list_contexts_response_200.additional_properties = d
        return list_contexts_response_200

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
