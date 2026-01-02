from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.oracle_tool_call_args import OracleToolCallArgs


T = TypeVar("T", bound="OracleToolCall")


@_attrs_define
class OracleToolCall:
    """A single tool call logged by Oracle during the run.

    Attributes:
        action (str | Unset): Tool/action name
        args (OracleToolCallArgs | Unset): Tool arguments used
        timestamp (datetime.datetime | Unset): ISO timestamp when the tool was executed
    """

    action: str | Unset = UNSET
    args: OracleToolCallArgs | Unset = UNSET
    timestamp: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        timestamp: str | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action is not UNSET:
            field_dict["action"] = action
        if args is not UNSET:
            field_dict["args"] = args
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.oracle_tool_call_args import OracleToolCallArgs

        d = dict(src_dict)
        action = d.pop("action", UNSET)

        _args = d.pop("args", UNSET)
        args: OracleToolCallArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = OracleToolCallArgs.from_dict(_args)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: datetime.datetime | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = isoparse(_timestamp)

        oracle_tool_call = cls(
            action=action,
            args=args,
            timestamp=timestamp,
        )

        oracle_tool_call.additional_properties = d
        return oracle_tool_call

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
