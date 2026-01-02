from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchHybridRequest")


@_attrs_define
class PackageSearchHybridRequest:
    """Request model for package hybrid search

    Attributes:
        registry (str): Registry: crates_io, golang_proxy, npm, py_pi, or ruby_gems
        package_name (str): Package name
        semantic_queries (list[str]): 1-5 semantic queries
        version (None | str | Unset): Package version
        filename_sha256 (None | str | Unset): File SHA256 filter
        pattern (None | str | Unset): Regex pattern filter
        language (None | str | Unset): Language filter
    """

    registry: str
    package_name: str
    semantic_queries: list[str]
    version: None | str | Unset = UNSET
    filename_sha256: None | str | Unset = UNSET
    pattern: None | str | Unset = UNSET
    language: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registry = self.registry

        package_name = self.package_name

        semantic_queries = self.semantic_queries

        version: None | str | Unset
        if isinstance(self.version, Unset):
            version = UNSET
        else:
            version = self.version

        filename_sha256: None | str | Unset
        if isinstance(self.filename_sha256, Unset):
            filename_sha256 = UNSET
        else:
            filename_sha256 = self.filename_sha256

        pattern: None | str | Unset
        if isinstance(self.pattern, Unset):
            pattern = UNSET
        else:
            pattern = self.pattern

        language: None | str | Unset
        if isinstance(self.language, Unset):
            language = UNSET
        else:
            language = self.language

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "registry": registry,
                "package_name": package_name,
                "semantic_queries": semantic_queries,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version
        if filename_sha256 is not UNSET:
            field_dict["filename_sha256"] = filename_sha256
        if pattern is not UNSET:
            field_dict["pattern"] = pattern
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        registry = d.pop("registry")

        package_name = d.pop("package_name")

        semantic_queries = cast(list[str], d.pop("semantic_queries"))

        def _parse_version(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        version = _parse_version(d.pop("version", UNSET))

        def _parse_filename_sha256(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename_sha256 = _parse_filename_sha256(d.pop("filename_sha256", UNSET))

        def _parse_pattern(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        pattern = _parse_pattern(d.pop("pattern", UNSET))

        def _parse_language(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        language = _parse_language(d.pop("language", UNSET))

        package_search_hybrid_request = cls(
            registry=registry,
            package_name=package_name,
            semantic_queries=semantic_queries,
            version=version,
            filename_sha256=filename_sha256,
            pattern=pattern,
            language=language,
        )

        package_search_hybrid_request.additional_properties = d
        return package_search_hybrid_request

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
