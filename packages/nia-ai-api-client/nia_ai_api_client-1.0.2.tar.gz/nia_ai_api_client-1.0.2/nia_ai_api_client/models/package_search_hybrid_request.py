from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.package_search_hybrid_request_registry import PackageSearchHybridRequestRegistry
from ..types import UNSET, Unset

T = TypeVar("T", bound="PackageSearchHybridRequest")


@_attrs_define
class PackageSearchHybridRequest:
    """
    Attributes:
        registry (PackageSearchHybridRequestRegistry): Package registry to search Example: npm.
        package_name (str): Name of the package to search Example: react.
        semantic_queries (list[str]): 1-5 semantic queries about the codebase Example: ['How does React handle state
            updates?', 'What are the main hooks available?'].
        version (str | Unset): Specific version to search (optional, defaults to latest) Example: 18.2.0.
        filename_sha256 (str | Unset): SHA256 hash of specific file to search in
        pattern (str | Unset): Optional regex pattern for pre-filtering results
        language (str | Unset): Language filter for search results Example: TypeScript.
    """

    registry: PackageSearchHybridRequestRegistry
    package_name: str
    semantic_queries: list[str]
    version: str | Unset = UNSET
    filename_sha256: str | Unset = UNSET
    pattern: str | Unset = UNSET
    language: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        registry = self.registry.value

        package_name = self.package_name

        semantic_queries = self.semantic_queries

        version = self.version

        filename_sha256 = self.filename_sha256

        pattern = self.pattern

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
        registry = PackageSearchHybridRequestRegistry(d.pop("registry"))

        package_name = d.pop("package_name")

        semantic_queries = cast(list[str], d.pop("semantic_queries"))

        version = d.pop("version", UNSET)

        filename_sha256 = d.pop("filename_sha256", UNSET)

        pattern = d.pop("pattern", UNSET)

        language = d.pop("language", UNSET)

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
