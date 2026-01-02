from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.repository_item import RepositoryItem
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_q: None | str | Unset
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_limit: int | None | Unset
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/repositories",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[RepositoryItem] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = RepositoryItem.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[HTTPValidationError | list[RepositoryItem]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[RepositoryItem]]:
    """List all repositories

     List all indexed repositories for the authenticated user.

    Args:
        q (None | str | Unset): Optional substring filter
        status (None | str | Unset): Optional status filter
        limit (int | None | Unset): Max repositories to return
        offset (int | Unset): Number of repositories to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[RepositoryItem]]
    """

    kwargs = _get_kwargs(
        q=q,
        status=status,
        limit=limit,
        offset=offset,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[RepositoryItem] | None:
    """List all repositories

     List all indexed repositories for the authenticated user.

    Args:
        q (None | str | Unset): Optional substring filter
        status (None | str | Unset): Optional status filter
        limit (int | None | Unset): Max repositories to return
        offset (int | Unset): Number of repositories to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[RepositoryItem]
    """

    return sync_detailed(
        client=client,
        q=q,
        status=status,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[RepositoryItem]]:
    """List all repositories

     List all indexed repositories for the authenticated user.

    Args:
        q (None | str | Unset): Optional substring filter
        status (None | str | Unset): Optional status filter
        limit (int | None | Unset): Max repositories to return
        offset (int | Unset): Number of repositories to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[RepositoryItem]]
    """

    kwargs = _get_kwargs(
        q=q,
        status=status,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | None | Unset = UNSET,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[RepositoryItem] | None:
    """List all repositories

     List all indexed repositories for the authenticated user.

    Args:
        q (None | str | Unset): Optional substring filter
        status (None | str | Unset): Optional status filter
        limit (int | None | Unset): Max repositories to return
        offset (int | Unset): Number of repositories to skip Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[RepositoryItem]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            status=status,
            limit=limit,
            offset=offset,
        )
    ).parsed
