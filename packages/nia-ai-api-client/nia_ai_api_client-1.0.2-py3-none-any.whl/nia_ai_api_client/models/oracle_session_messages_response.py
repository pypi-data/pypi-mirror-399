from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.oracle_chat_message import OracleChatMessage


T = TypeVar("T", bound="OracleSessionMessagesResponse")


@_attrs_define
class OracleSessionMessagesResponse:
    """
    Attributes:
        session_id (str | Unset):
        messages (list[OracleChatMessage] | Unset):
        total (int | Unset):
    """

    session_id: str | Unset = UNSET
    messages: list[OracleChatMessage] | Unset = UNSET
    total: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        session_id = self.session_id

        messages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.messages, Unset):
            messages = []
            for messages_item_data in self.messages:
                messages_item = messages_item_data.to_dict()
                messages.append(messages_item)

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if messages is not UNSET:
            field_dict["messages"] = messages
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.oracle_chat_message import OracleChatMessage

        d = dict(src_dict)
        session_id = d.pop("session_id", UNSET)

        _messages = d.pop("messages", UNSET)
        messages: list[OracleChatMessage] | Unset = UNSET
        if _messages is not UNSET:
            messages = []
            for messages_item_data in _messages:
                messages_item = OracleChatMessage.from_dict(messages_item_data)

                messages.append(messages_item)

        total = d.pop("total", UNSET)

        oracle_session_messages_response = cls(
            session_id=session_id,
            messages=messages,
            total=total,
        )

        oracle_session_messages_response.additional_properties = d
        return oracle_session_messages_response

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
