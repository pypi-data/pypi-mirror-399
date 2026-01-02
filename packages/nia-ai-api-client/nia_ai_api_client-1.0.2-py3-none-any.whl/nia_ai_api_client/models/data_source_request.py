from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.data_source_request_llms_txt_strategy import DataSourceRequestLlmsTxtStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataSourceRequest")


@_attrs_define
class DataSourceRequest:
    """
    Attributes:
        url (str): URL to index (documentation or website) Example: https://docs.example.com.
        url_patterns (list[str] | Unset): URL patterns to include in crawling (supports wildcards) Example:
            ['https://docs.example.com/api/*', 'https://docs.example.com/guides/*'].
        exclude_patterns (list[str] | Unset): URL patterns to exclude from crawling Example: ['/blog/*',
            '/changelog/*'].
        project_id (str | Unset): Optional project ID to associate with
        max_age (int | Unset): Maximum age of cached content in seconds (for fast scraping)
        formats (list[str] | Unset): Content formats to return Example: ['markdown', 'html'].
        only_main_content (bool | Unset): Extract only main content (removes nav, ads, etc.) Default: True.
        limit (int | Unset): Maximum number of pages to crawl Default: 10000.
        max_depth (int | Unset): Maximum crawl depth Default: 20.
        crawl_entire_domain (bool | Unset): Whether to crawl the entire domain Default: True.
        wait_for (int | Unset): Time to wait for page to load in milliseconds Default: 2000.
        include_screenshot (bool | Unset): Include full page screenshot Default: True.
        check_llms_txt (bool | Unset): Check for llms.txt file for curated documentation URLs Default: True.
        llms_txt_strategy (DataSourceRequestLlmsTxtStrategy | Unset): How to use llms.txt if found:
            - prefer: Start with llms.txt URLs, then crawl additional pages if under limit
            - only: Only index URLs listed in llms.txt
            - ignore: Skip llms.txt check (traditional behavior)
             Default: DataSourceRequestLlmsTxtStrategy.PREFER.
    """

    url: str
    url_patterns: list[str] | Unset = UNSET
    exclude_patterns: list[str] | Unset = UNSET
    project_id: str | Unset = UNSET
    max_age: int | Unset = UNSET
    formats: list[str] | Unset = UNSET
    only_main_content: bool | Unset = True
    limit: int | Unset = 10000
    max_depth: int | Unset = 20
    crawl_entire_domain: bool | Unset = True
    wait_for: int | Unset = 2000
    include_screenshot: bool | Unset = True
    check_llms_txt: bool | Unset = True
    llms_txt_strategy: DataSourceRequestLlmsTxtStrategy | Unset = DataSourceRequestLlmsTxtStrategy.PREFER
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        url_patterns: list[str] | Unset = UNSET
        if not isinstance(self.url_patterns, Unset):
            url_patterns = self.url_patterns

        exclude_patterns: list[str] | Unset = UNSET
        if not isinstance(self.exclude_patterns, Unset):
            exclude_patterns = self.exclude_patterns

        project_id = self.project_id

        max_age = self.max_age

        formats: list[str] | Unset = UNSET
        if not isinstance(self.formats, Unset):
            formats = self.formats

        only_main_content = self.only_main_content

        limit = self.limit

        max_depth = self.max_depth

        crawl_entire_domain = self.crawl_entire_domain

        wait_for = self.wait_for

        include_screenshot = self.include_screenshot

        check_llms_txt = self.check_llms_txt

        llms_txt_strategy: str | Unset = UNSET
        if not isinstance(self.llms_txt_strategy, Unset):
            llms_txt_strategy = self.llms_txt_strategy.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
            }
        )
        if url_patterns is not UNSET:
            field_dict["url_patterns"] = url_patterns
        if exclude_patterns is not UNSET:
            field_dict["exclude_patterns"] = exclude_patterns
        if project_id is not UNSET:
            field_dict["project_id"] = project_id
        if max_age is not UNSET:
            field_dict["max_age"] = max_age
        if formats is not UNSET:
            field_dict["formats"] = formats
        if only_main_content is not UNSET:
            field_dict["only_main_content"] = only_main_content
        if limit is not UNSET:
            field_dict["limit"] = limit
        if max_depth is not UNSET:
            field_dict["max_depth"] = max_depth
        if crawl_entire_domain is not UNSET:
            field_dict["crawl_entire_domain"] = crawl_entire_domain
        if wait_for is not UNSET:
            field_dict["wait_for"] = wait_for
        if include_screenshot is not UNSET:
            field_dict["include_screenshot"] = include_screenshot
        if check_llms_txt is not UNSET:
            field_dict["check_llms_txt"] = check_llms_txt
        if llms_txt_strategy is not UNSET:
            field_dict["llms_txt_strategy"] = llms_txt_strategy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        url_patterns = cast(list[str], d.pop("url_patterns", UNSET))

        exclude_patterns = cast(list[str], d.pop("exclude_patterns", UNSET))

        project_id = d.pop("project_id", UNSET)

        max_age = d.pop("max_age", UNSET)

        formats = cast(list[str], d.pop("formats", UNSET))

        only_main_content = d.pop("only_main_content", UNSET)

        limit = d.pop("limit", UNSET)

        max_depth = d.pop("max_depth", UNSET)

        crawl_entire_domain = d.pop("crawl_entire_domain", UNSET)

        wait_for = d.pop("wait_for", UNSET)

        include_screenshot = d.pop("include_screenshot", UNSET)

        check_llms_txt = d.pop("check_llms_txt", UNSET)

        _llms_txt_strategy = d.pop("llms_txt_strategy", UNSET)
        llms_txt_strategy: DataSourceRequestLlmsTxtStrategy | Unset
        if isinstance(_llms_txt_strategy, Unset):
            llms_txt_strategy = UNSET
        else:
            llms_txt_strategy = DataSourceRequestLlmsTxtStrategy(_llms_txt_strategy)

        data_source_request = cls(
            url=url,
            url_patterns=url_patterns,
            exclude_patterns=exclude_patterns,
            project_id=project_id,
            max_age=max_age,
            formats=formats,
            only_main_content=only_main_content,
            limit=limit,
            max_depth=max_depth,
            crawl_entire_domain=crawl_entire_domain,
            wait_for=wait_for,
            include_screenshot=include_screenshot,
            check_llms_txt=check_llms_txt,
            llms_txt_strategy=llms_txt_strategy,
        )

        data_source_request.additional_properties = d
        return data_source_request

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
