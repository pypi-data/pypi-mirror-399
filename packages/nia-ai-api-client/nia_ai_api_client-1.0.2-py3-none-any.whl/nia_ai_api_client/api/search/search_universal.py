from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.universal_search_request import UniversalSearchRequest
from ...models.universal_search_response import UniversalSearchResponse
from ...types import Response


def _get_kwargs(
    *,
    body: UniversalSearchRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/search/universal",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | UniversalSearchResponse | None:
    if response.status_code == 200:
        response_200 = UniversalSearchResponse.from_dict(response.json())

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

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | UniversalSearchResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UniversalSearchRequest,
) -> Response[Error | UniversalSearchResponse]:
    """Universal search across all public sources

     Search across ALL indexed public sources (repositories and documentation) in a single query.

    This endpoint performs a two-phase hybrid search:
    1. **Discovery Phase**: Fast O(1) search across a universal index to identify relevant sources
    2. **Deep Search Phase**: Targeted searches into the top matching source namespaces for
    comprehensive results

    Results are combined using Reciprocal Rank Fusion (RRF) for optimal ranking.

    Use this when you want to discover relevant content without knowing which specific sources to
    search.

    **Performance**: Typically returns results in 1-3 seconds for thousands of indexed sources.

    Args:
        body (UniversalSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | UniversalSearchResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: UniversalSearchRequest,
) -> Error | UniversalSearchResponse | None:
    """Universal search across all public sources

     Search across ALL indexed public sources (repositories and documentation) in a single query.

    This endpoint performs a two-phase hybrid search:
    1. **Discovery Phase**: Fast O(1) search across a universal index to identify relevant sources
    2. **Deep Search Phase**: Targeted searches into the top matching source namespaces for
    comprehensive results

    Results are combined using Reciprocal Rank Fusion (RRF) for optimal ranking.

    Use this when you want to discover relevant content without knowing which specific sources to
    search.

    **Performance**: Typically returns results in 1-3 seconds for thousands of indexed sources.

    Args:
        body (UniversalSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | UniversalSearchResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UniversalSearchRequest,
) -> Response[Error | UniversalSearchResponse]:
    """Universal search across all public sources

     Search across ALL indexed public sources (repositories and documentation) in a single query.

    This endpoint performs a two-phase hybrid search:
    1. **Discovery Phase**: Fast O(1) search across a universal index to identify relevant sources
    2. **Deep Search Phase**: Targeted searches into the top matching source namespaces for
    comprehensive results

    Results are combined using Reciprocal Rank Fusion (RRF) for optimal ranking.

    Use this when you want to discover relevant content without knowing which specific sources to
    search.

    **Performance**: Typically returns results in 1-3 seconds for thousands of indexed sources.

    Args:
        body (UniversalSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | UniversalSearchResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UniversalSearchRequest,
) -> Error | UniversalSearchResponse | None:
    """Universal search across all public sources

     Search across ALL indexed public sources (repositories and documentation) in a single query.

    This endpoint performs a two-phase hybrid search:
    1. **Discovery Phase**: Fast O(1) search across a universal index to identify relevant sources
    2. **Deep Search Phase**: Targeted searches into the top matching source namespaces for
    comprehensive results

    Results are combined using Reciprocal Rank Fusion (RRF) for optimal ranking.

    Use this when you want to discover relevant content without knowing which specific sources to
    search.

    **Performance**: Typically returns results in 1-3 seconds for thousands of indexed sources.

    Args:
        body (UniversalSearchRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | UniversalSearchResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
