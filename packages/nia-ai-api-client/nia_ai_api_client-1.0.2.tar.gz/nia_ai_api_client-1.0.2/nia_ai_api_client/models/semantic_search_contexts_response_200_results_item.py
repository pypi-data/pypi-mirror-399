from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.context_share_response_metadata import ContextShareResponseMetadata
    from ..models.edited_file import EditedFile
    from ..models.nia_references import NiaReferences
    from ..models.semantic_search_contexts_response_200_results_item_match_metadata import (
        SemanticSearchContextsResponse200ResultsItemMatchMetadata,
    )


T = TypeVar("T", bound="SemanticSearchContextsResponse200ResultsItem")


@_attrs_define
class SemanticSearchContextsResponse200ResultsItem:
    """
    Attributes:
        id (str | Unset): Unique identifier for the context
        user_id (str | Unset): User who created the context
        organization_id (str | Unset): Organization ID if context belongs to an organization
        title (str | Unset): Context title
        summary (str | Unset): Context summary
        content (str | Unset): Full context content
        tags (list[str] | Unset):
        agent_source (str | Unset): Source agent (e.g., "cursor", "claude-code")
        created_at (datetime.datetime | Unset): When the context was created
        updated_at (datetime.datetime | Unset): When the context was last updated
        metadata (ContextShareResponseMetadata | Unset):
        nia_references (NiaReferences | Unset): References to NIA resources used during the conversation
        edited_files (list[EditedFile] | Unset):
        relevance_score (float | Unset): Relevance score from vector search (0-1)
        match_metadata (SemanticSearchContextsResponse200ResultsItemMatchMetadata | Unset):
        match_highlights (list[str] | Unset): Highlighted matches from content
        files_edited (list[str] | Unset): Paths of edited files (up to 5)
        workspace_name (str | Unset): Workspace/project name
    """

    id: str | Unset = UNSET
    user_id: str | Unset = UNSET
    organization_id: str | Unset = UNSET
    title: str | Unset = UNSET
    summary: str | Unset = UNSET
    content: str | Unset = UNSET
    tags: list[str] | Unset = UNSET
    agent_source: str | Unset = UNSET
    created_at: datetime.datetime | Unset = UNSET
    updated_at: datetime.datetime | Unset = UNSET
    metadata: ContextShareResponseMetadata | Unset = UNSET
    nia_references: NiaReferences | Unset = UNSET
    edited_files: list[EditedFile] | Unset = UNSET
    relevance_score: float | Unset = UNSET
    match_metadata: SemanticSearchContextsResponse200ResultsItemMatchMetadata | Unset = UNSET
    match_highlights: list[str] | Unset = UNSET
    files_edited: list[str] | Unset = UNSET
    workspace_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        user_id = self.user_id

        organization_id = self.organization_id

        title = self.title

        summary = self.summary

        content = self.content

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        agent_source = self.agent_source

        created_at: str | Unset = UNSET
        if not isinstance(self.created_at, Unset):
            created_at = self.created_at.isoformat()

        updated_at: str | Unset = UNSET
        if not isinstance(self.updated_at, Unset):
            updated_at = self.updated_at.isoformat()

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        nia_references: dict[str, Any] | Unset = UNSET
        if not isinstance(self.nia_references, Unset):
            nia_references = self.nia_references.to_dict()

        edited_files: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.edited_files, Unset):
            edited_files = []
            for edited_files_item_data in self.edited_files:
                edited_files_item = edited_files_item_data.to_dict()
                edited_files.append(edited_files_item)

        relevance_score = self.relevance_score

        match_metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.match_metadata, Unset):
            match_metadata = self.match_metadata.to_dict()

        match_highlights: list[str] | Unset = UNSET
        if not isinstance(self.match_highlights, Unset):
            match_highlights = self.match_highlights

        files_edited: list[str] | Unset = UNSET
        if not isinstance(self.files_edited, Unset):
            files_edited = self.files_edited

        workspace_name = self.workspace_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if user_id is not UNSET:
            field_dict["user_id"] = user_id
        if organization_id is not UNSET:
            field_dict["organization_id"] = organization_id
        if title is not UNSET:
            field_dict["title"] = title
        if summary is not UNSET:
            field_dict["summary"] = summary
        if content is not UNSET:
            field_dict["content"] = content
        if tags is not UNSET:
            field_dict["tags"] = tags
        if agent_source is not UNSET:
            field_dict["agent_source"] = agent_source
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if metadata is not UNSET:
            field_dict["metadata"] = metadata
        if nia_references is not UNSET:
            field_dict["nia_references"] = nia_references
        if edited_files is not UNSET:
            field_dict["edited_files"] = edited_files
        if relevance_score is not UNSET:
            field_dict["relevance_score"] = relevance_score
        if match_metadata is not UNSET:
            field_dict["match_metadata"] = match_metadata
        if match_highlights is not UNSET:
            field_dict["match_highlights"] = match_highlights
        if files_edited is not UNSET:
            field_dict["files_edited"] = files_edited
        if workspace_name is not UNSET:
            field_dict["workspace_name"] = workspace_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.context_share_response_metadata import ContextShareResponseMetadata
        from ..models.edited_file import EditedFile
        from ..models.nia_references import NiaReferences
        from ..models.semantic_search_contexts_response_200_results_item_match_metadata import (
            SemanticSearchContextsResponse200ResultsItemMatchMetadata,
        )

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        user_id = d.pop("user_id", UNSET)

        organization_id = d.pop("organization_id", UNSET)

        title = d.pop("title", UNSET)

        summary = d.pop("summary", UNSET)

        content = d.pop("content", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        agent_source = d.pop("agent_source", UNSET)

        _created_at = d.pop("created_at", UNSET)
        created_at: datetime.datetime | Unset
        if isinstance(_created_at, Unset):
            created_at = UNSET
        else:
            created_at = isoparse(_created_at)

        _updated_at = d.pop("updated_at", UNSET)
        updated_at: datetime.datetime | Unset
        if isinstance(_updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = isoparse(_updated_at)

        _metadata = d.pop("metadata", UNSET)
        metadata: ContextShareResponseMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ContextShareResponseMetadata.from_dict(_metadata)

        _nia_references = d.pop("nia_references", UNSET)
        nia_references: NiaReferences | Unset
        if isinstance(_nia_references, Unset):
            nia_references = UNSET
        else:
            nia_references = NiaReferences.from_dict(_nia_references)

        _edited_files = d.pop("edited_files", UNSET)
        edited_files: list[EditedFile] | Unset = UNSET
        if _edited_files is not UNSET:
            edited_files = []
            for edited_files_item_data in _edited_files:
                edited_files_item = EditedFile.from_dict(edited_files_item_data)

                edited_files.append(edited_files_item)

        relevance_score = d.pop("relevance_score", UNSET)

        _match_metadata = d.pop("match_metadata", UNSET)
        match_metadata: SemanticSearchContextsResponse200ResultsItemMatchMetadata | Unset
        if isinstance(_match_metadata, Unset):
            match_metadata = UNSET
        else:
            match_metadata = SemanticSearchContextsResponse200ResultsItemMatchMetadata.from_dict(_match_metadata)

        match_highlights = cast(list[str], d.pop("match_highlights", UNSET))

        files_edited = cast(list[str], d.pop("files_edited", UNSET))

        workspace_name = d.pop("workspace_name", UNSET)

        semantic_search_contexts_response_200_results_item = cls(
            id=id,
            user_id=user_id,
            organization_id=organization_id,
            title=title,
            summary=summary,
            content=content,
            tags=tags,
            agent_source=agent_source,
            created_at=created_at,
            updated_at=updated_at,
            metadata=metadata,
            nia_references=nia_references,
            edited_files=edited_files,
            relevance_score=relevance_score,
            match_metadata=match_metadata,
            match_highlights=match_highlights,
            files_edited=files_edited,
            workspace_name=workspace_name,
        )

        semantic_search_contexts_response_200_results_item.additional_properties = d
        return semantic_search_contexts_response_200_results_item

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
