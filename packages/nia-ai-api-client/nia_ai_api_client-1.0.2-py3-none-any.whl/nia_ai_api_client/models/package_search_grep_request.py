from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.package_search_grep_request_output_mode import PackageSearchGrepRequestOutputMode
from ..models.package_search_grep_request_registry import PackageSearchGrepRequestRegistry
from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchGrepRequest")


@_attrs_define
class PackageSearchGrepRequest:
    """
    Attributes:
        registry (PackageSearchGrepRequestRegistry): Package registry to search Example: npm.
        package_name (str): Name of the package to search Example: react.
        pattern (str): Regex pattern to search for in the package source code Example: useState|useEffect.
        version (str | Unset): Specific version to search (optional, defaults to latest) Example: 18.2.0.
        language (str | Unset): Language filter for search results Example: TypeScript.
        filename_sha256 (str | Unset): SHA256 hash of specific file to search in
        a (int | Unset): Number of lines after each match to include
        b (int | Unset): Number of lines before each match to include
        c (int | Unset): Number of lines before and after each match to include
        head_limit (int | Unset): Maximum number of results to return Example: 10.
        output_mode (PackageSearchGrepRequestOutputMode | Unset): Format of the output results Default:
            PackageSearchGrepRequestOutputMode.CONTENT.
    """

    registry: PackageSearchGrepRequestRegistry
    package_name: str
    pattern: str
    version: str | Unset = UNSET
    language: str | Unset = UNSET
    filename_sha256: str | Unset = UNSET
    a: int | Unset = UNSET
    b: int | Unset = UNSET
    c: int | Unset = UNSET
    head_limit: int | Unset = UNSET
    output_mode: PackageSearchGrepRequestOutputMode | Unset = PackageSearchGrepRequestOutputMode.CONTENT
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registry = self.registry.value

        package_name = self.package_name

        pattern = self.pattern

        version = self.version

        language = self.language

        filename_sha256 = self.filename_sha256

        a = self.a

        b = self.b

        c = self.c

        head_limit = self.head_limit

        output_mode: str | Unset = UNSET
        if not isinstance(self.output_mode, Unset):
            output_mode = self.output_mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registry": registry,
                "package_name": package_name,
                "pattern": pattern,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if language is not UNSET:
            field_dict["language"] = language
        if filename_sha256 is not UNSET:
            field_dict["filename_sha256"] = filename_sha256
        if a is not UNSET:
            field_dict["a"] = a
        if b is not UNSET:
            field_dict["b"] = b
        if c is not UNSET:
            field_dict["c"] = c
        if head_limit is not UNSET:
            field_dict["head_limit"] = head_limit
        if output_mode is not UNSET:
            field_dict["output_mode"] = output_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        registry = PackageSearchGrepRequestRegistry(d.pop("registry"))

        package_name = d.pop("package_name")

        pattern = d.pop("pattern")

        version = d.pop("version", UNSET)

        language = d.pop("language", UNSET)

        filename_sha256 = d.pop("filename_sha256", UNSET)

        a = d.pop("a", UNSET)

        b = d.pop("b", UNSET)

        c = d.pop("c", UNSET)

        head_limit = d.pop("head_limit", UNSET)

        _output_mode = d.pop("output_mode", UNSET)
        output_mode: PackageSearchGrepRequestOutputMode | Unset
        if isinstance(_output_mode, Unset):
            output_mode = UNSET
        else:
            output_mode = PackageSearchGrepRequestOutputMode(_output_mode)

        package_search_grep_request = cls(
            registry=registry,
            package_name=package_name,
            pattern=pattern,
            version=version,
            language=language,
            filename_sha256=filename_sha256,
            a=a,
            b=b,
            c=c,
            head_limit=head_limit,
            output_mode=output_mode,
        )

        package_search_grep_request.additional_properties = d
        return package_search_grep_request

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
