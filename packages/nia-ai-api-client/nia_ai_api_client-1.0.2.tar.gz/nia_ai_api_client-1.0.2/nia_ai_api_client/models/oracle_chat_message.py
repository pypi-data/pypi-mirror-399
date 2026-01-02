from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.oracle_chat_message_role import OracleChatMessageRole
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.oracle_citation import OracleCitation


T = TypeVar("T", bound="OracleChatMessage")


@_attrs_define
class OracleChatMessage:
    """
    Attributes:
        role (OracleChatMessageRole | Unset):
        content (str | Unset):
        created_at (datetime.datetime | None | Unset):
        is_original (bool | Unset):
        message_id (None | str | Unset):
        citations (list[OracleCitation] | None | Unset):
    """

    role: OracleChatMessageRole | Unset = UNSET
    content: str | Unset = UNSET
    created_at: datetime.datetime | None | Unset = UNSET
    is_original: bool | Unset = UNSET
    message_id: None | str | Unset = UNSET
    citations: list[OracleCitation] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role: str | Unset = UNSET
        if not isinstance(self.role, Unset):
            role = self.role.value

        content = self.content

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        is_original = self.is_original

        message_id: None | str | Unset
        if isinstance(self.message_id, Unset):
            message_id = UNSET
        else:
            message_id = self.message_id

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
        field_dict.update({})
        if role is not UNSET:
            field_dict["role"] = role
        if content is not UNSET:
            field_dict["content"] = content
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if is_original is not UNSET:
            field_dict["is_original"] = is_original
        if message_id is not UNSET:
            field_dict["message_id"] = message_id
        if citations is not UNSET:
            field_dict["citations"] = citations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.oracle_citation import OracleCitation

        d = dict(src_dict)
        _role = d.pop("role", UNSET)
        role: OracleChatMessageRole | Unset
        if isinstance(_role, Unset):
            role = UNSET
        else:
            role = OracleChatMessageRole(_role)

        content = d.pop("content", UNSET)

        def _parse_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = isoparse(data)

                return created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        is_original = d.pop("is_original", UNSET)

        def _parse_message_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message_id = _parse_message_id(d.pop("message_id", UNSET))

        def _parse_citations(data: object) -> list[OracleCitation] | None | Unset:
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
                    citations_type_0_item = OracleCitation.from_dict(citations_type_0_item_data)

                    citations_type_0.append(citations_type_0_item)

                return citations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[OracleCitation] | None | Unset, data)

        citations = _parse_citations(d.pop("citations", UNSET))

        oracle_chat_message = cls(
            role=role,
            content=content,
            created_at=created_at,
            is_original=is_original,
            message_id=message_id,
            citations=citations,
        )

        oracle_chat_message.additional_properties = d
        return oracle_chat_message

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
