from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.context_share_response import ContextShareResponse
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    context_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/contexts/{context_id}".format(
            context_id=quote(str(context_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContextShareResponse | Error | None:
    if response.status_code == 200:
        response_200 = ContextShareResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

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
) -> Response[ContextShareResponse | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContextShareResponse | Error]:
    """Get conversation context

     Retrieve a specific conversation context by ID.
    Returns full context details including content, metadata, NIA references, and edited files.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextShareResponse | Error]
    """

    kwargs = _get_kwargs(
        context_id=context_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ContextShareResponse | Error | None:
    """Get conversation context

     Retrieve a specific conversation context by ID.
    Returns full context details including content, metadata, NIA references, and edited files.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextShareResponse | Error
    """

    return sync_detailed(
        context_id=context_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContextShareResponse | Error]:
    """Get conversation context

     Retrieve a specific conversation context by ID.
    Returns full context details including content, metadata, NIA references, and edited files.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextShareResponse | Error]
    """

    kwargs = _get_kwargs(
        context_id=context_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ContextShareResponse | Error | None:
    """Get conversation context

     Retrieve a specific conversation context by ID.
    Returns full context details including content, metadata, NIA references, and edited files.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextShareResponse | Error
    """

    return (
        await asyncio_detailed(
            context_id=context_id,
            client=client,
        )
    ).parsed
