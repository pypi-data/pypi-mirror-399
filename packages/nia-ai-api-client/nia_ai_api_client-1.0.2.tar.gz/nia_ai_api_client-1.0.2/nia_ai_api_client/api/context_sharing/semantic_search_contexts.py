from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.semantic_search_contexts_response_200 import SemanticSearchContextsResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: str,
    limit: int | Unset = 20,
    include_highlights: bool | Unset = True,
    workspace_filter: str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["limit"] = limit

    params["include_highlights"] = include_highlights

    params["workspace_filter"] = workspace_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contexts/semantic-search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | SemanticSearchContextsResponse200 | None:
    if response.status_code == 200:
        response_200 = SemanticSearchContextsResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if response.status_code == 503:
        response_503 = Error.from_dict(response.json())

        return response_503

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | SemanticSearchContextsResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    include_highlights: bool | Unset = True,
    workspace_filter: str | Unset = UNSET,
) -> Response[Error | SemanticSearchContextsResponse200]:
    """Semantic search contexts

     Semantic search conversation contexts using vector embeddings and hybrid (vector + BM25) search.
    Uses vector store for fast similarity search across context content.
    Returns results ranked by relevance with optional match highlights and workspace filtering.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        include_highlights (bool | Unset):  Default: True.
        workspace_filter (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | SemanticSearchContextsResponse200]
    """

    kwargs = _get_kwargs(
        q=q,
        limit=limit,
        include_highlights=include_highlights,
        workspace_filter=workspace_filter,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    include_highlights: bool | Unset = True,
    workspace_filter: str | Unset = UNSET,
) -> Error | SemanticSearchContextsResponse200 | None:
    """Semantic search contexts

     Semantic search conversation contexts using vector embeddings and hybrid (vector + BM25) search.
    Uses vector store for fast similarity search across context content.
    Returns results ranked by relevance with optional match highlights and workspace filtering.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        include_highlights (bool | Unset):  Default: True.
        workspace_filter (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | SemanticSearchContextsResponse200
    """

    return sync_detailed(
        client=client,
        q=q,
        limit=limit,
        include_highlights=include_highlights,
        workspace_filter=workspace_filter,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    include_highlights: bool | Unset = True,
    workspace_filter: str | Unset = UNSET,
) -> Response[Error | SemanticSearchContextsResponse200]:
    """Semantic search contexts

     Semantic search conversation contexts using vector embeddings and hybrid (vector + BM25) search.
    Uses vector store for fast similarity search across context content.
    Returns results ranked by relevance with optional match highlights and workspace filtering.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        include_highlights (bool | Unset):  Default: True.
        workspace_filter (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | SemanticSearchContextsResponse200]
    """

    kwargs = _get_kwargs(
        q=q,
        limit=limit,
        include_highlights=include_highlights,
        workspace_filter=workspace_filter,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    q: str,
    limit: int | Unset = 20,
    include_highlights: bool | Unset = True,
    workspace_filter: str | Unset = UNSET,
) -> Error | SemanticSearchContextsResponse200 | None:
    """Semantic search contexts

     Semantic search conversation contexts using vector embeddings and hybrid (vector + BM25) search.
    Uses vector store for fast similarity search across context content.
    Returns results ranked by relevance with optional match highlights and workspace filtering.

    Args:
        q (str):
        limit (int | Unset):  Default: 20.
        include_highlights (bool | Unset):  Default: True.
        workspace_filter (str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | SemanticSearchContextsResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            limit=limit,
            include_highlights=include_highlights,
            workspace_filter=workspace_filter,
        )
    ).parsed
