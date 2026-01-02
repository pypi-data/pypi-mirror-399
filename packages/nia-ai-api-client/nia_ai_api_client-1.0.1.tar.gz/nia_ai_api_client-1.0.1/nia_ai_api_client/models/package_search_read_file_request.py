from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchReadFileRequest")


@_attrs_define
class PackageSearchReadFileRequest:
    """Request model for reading package file

    Attributes:
        registry (str): Registry: crates_io, golang_proxy, npm, py_pi, or ruby_gems
        package_name (str): Package name
        filename_sha256 (str): File SHA256
        start_line (int): Start line (1-based)
        end_line (int): End line (1-based)
        version (None | str | Unset): Package version
    """

    registry: str
    package_name: str
    filename_sha256: str
    start_line: int
    end_line: int
    version: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registry = self.registry

        package_name = self.package_name

        filename_sha256 = self.filename_sha256

        start_line = self.start_line

        end_line = self.end_line

        version: None | str | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registry": registry,
                "package_name": package_name,
                "filename_sha256": filename_sha256,
                "start_line": start_line,
                "end_line": end_line,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        registry = d.pop("registry")

        package_name = d.pop("package_name")

        filename_sha256 = d.pop("filename_sha256")

        start_line = d.pop("start_line")

        end_line = d.pop("end_line")

        def _parse_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        package_search_read_file_request = cls(
            registry=registry,
            package_name=package_name,
            filename_sha256=filename_sha256,
            start_line=start_line,
            end_line=end_line,
            version=version,
        )

        package_search_read_file_request.additional_properties = d
        return package_search_read_file_request

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
