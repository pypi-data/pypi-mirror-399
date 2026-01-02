from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.package_search_read_file_request_registry import PackageSearchReadFileRequestRegistry
from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchReadFileRequest")


@_attrs_define
class PackageSearchReadFileRequest:
    """
    Attributes:
        registry (PackageSearchReadFileRequestRegistry): Package registry containing the file Example: npm.
        package_name (str): Name of the package containing the file Example: react.
        filename_sha256 (str): SHA256 hash of the file to read (obtained from grep/hybrid search) Example:
            a1b2c3d4e5f6....
        start_line (int): Starting line number (1-based, inclusive) Example: 1.
        end_line (int): Ending line number (1-based, inclusive) Example: 100.
        version (str | Unset): Specific version of the package (optional, defaults to latest) Example: 18.2.0.
    """

    registry: PackageSearchReadFileRequestRegistry
    package_name: str
    filename_sha256: str
    start_line: int
    end_line: int
    version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registry = self.registry.value

        package_name = self.package_name

        filename_sha256 = self.filename_sha256

        start_line = self.start_line

        end_line = self.end_line

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
        registry = PackageSearchReadFileRequestRegistry(d.pop("registry"))

        package_name = d.pop("package_name")

        filename_sha256 = d.pop("filename_sha256")

        start_line = d.pop("start_line")

        end_line = d.pop("end_line")

        version = d.pop("version", UNSET)

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
