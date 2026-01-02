from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.oracle_citation_args import OracleCitationArgs


T = TypeVar("T", bound="OracleCitation")


@_attrs_define
class OracleCitation:
    """A single grounded "citation" entry recorded by Oracle during tool use.

    Attributes:
        source_id (int | Unset): Monotonic integer id (1-based) assigned during the run
        tool (str | Unset): Tool/action name that produced this citation
        args (OracleCitationArgs | Unset): Tool arguments used
        summary (str | Unset): Short summary of the tool result (truncated)
    """

    source_id: int | Unset = UNSET
    tool: str | Unset = UNSET
    args: OracleCitationArgs | Unset = UNSET
    summary: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_id = self.source_id

        tool = self.tool

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        summary = self.summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if tool is not UNSET:
            field_dict["tool"] = tool
        if args is not UNSET:
            field_dict["args"] = args
        if summary is not UNSET:
            field_dict["summary"] = summary

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.oracle_citation_args import OracleCitationArgs

        d = dict(src_dict)
        source_id = d.pop("source_id", UNSET)

        tool = d.pop("tool", UNSET)

        _args = d.pop("args", UNSET)
        args: OracleCitationArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = OracleCitationArgs.from_dict(_args)

        summary = d.pop("summary", UNSET)

        oracle_citation = cls(
            source_id=source_id,
            tool=tool,
            args=args,
            summary=summary,
        )

        oracle_citation.additional_properties = d
        return oracle_citation

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
