from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.context_semantic_search_response import ContextSemanticSearchResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: str,
    limit: int | Unset = 20,
    include_highlights: bool | Unset = True,
    workspace_filter: None | str | Unset = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["limit"] = limit

    params["include_highlights"] = include_highlights

    json_workspace_filter: None | str | Unset
    if isinstance(workspace_filter, Unset):
        json_workspace_filter = UNSET
    else:
        json_workspace_filter = workspace_filter
    params["workspace_filter"] = json_workspace_filter

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/contexts/semantic-search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContextSemanticSearchResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ContextSemanticSearchResponse.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[ContextSemanticSearchResponse | HTTPValidationError]:
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
    workspace_filter: None | str | Unset = UNSET,
) -> Response[ContextSemanticSearchResponse | HTTPValidationError]:
    """Semantic search contexts

     Vector + BM25 hybrid search over contexts. Returns relevance scores and highlights.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextSemanticSearchResponse | HTTPValidationError]
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
    workspace_filter: None | str | Unset = UNSET,
) -> ContextSemanticSearchResponse | HTTPValidationError | None:
    """Semantic search contexts

     Vector + BM25 hybrid search over contexts. Returns relevance scores and highlights.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextSemanticSearchResponse | HTTPValidationError
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
    workspace_filter: None | str | Unset = UNSET,
) -> Response[ContextSemanticSearchResponse | HTTPValidationError]:
    """Semantic search contexts

     Vector + BM25 hybrid search over contexts. Returns relevance scores and highlights.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextSemanticSearchResponse | HTTPValidationError]
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
    workspace_filter: None | str | Unset = UNSET,
) -> ContextSemanticSearchResponse | HTTPValidationError | None:
    """Semantic search contexts

     Vector + BM25 hybrid search over contexts. Returns relevance scores and highlights.

    Args:
        q (str): Search query
        limit (int | Unset): Number of contexts to return Default: 20.
        include_highlights (bool | Unset): Include match highlights Default: True.
        workspace_filter (None | str | Unset): Filter by specific workspace name

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextSemanticSearchResponse | HTTPValidationError
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
