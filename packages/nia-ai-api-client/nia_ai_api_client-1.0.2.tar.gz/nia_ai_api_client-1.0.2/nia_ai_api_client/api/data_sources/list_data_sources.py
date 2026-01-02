from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_source_response import DataSourceResponse
from ...models.error import Error
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: str | Unset = UNSET,
    status: str | Unset = UNSET,
    source_type: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["q"] = q

    params["status"] = status

    params["source_type"] = source_type

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/data-sources",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | list[DataSourceResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DataSourceResponse.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | list[DataSourceResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    status: str | Unset = UNSET,
    source_type: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[Error | list[DataSourceResponse]]:
    """List all data sources

     List all indexed documentation and web sources for the authenticated user

    Args:
        q (str | Unset):
        status (str | Unset):
        source_type (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[DataSourceResponse]]
    """

    kwargs = _get_kwargs(
        q=q,
        status=status,
        source_type=source_type,
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
    q: str | Unset = UNSET,
    status: str | Unset = UNSET,
    source_type: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Error | list[DataSourceResponse] | None:
    """List all data sources

     List all indexed documentation and web sources for the authenticated user

    Args:
        q (str | Unset):
        status (str | Unset):
        source_type (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[DataSourceResponse]
    """

    return sync_detailed(
        client=client,
        q=q,
        status=status,
        source_type=source_type,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    status: str | Unset = UNSET,
    source_type: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[Error | list[DataSourceResponse]]:
    """List all data sources

     List all indexed documentation and web sources for the authenticated user

    Args:
        q (str | Unset):
        status (str | Unset):
        source_type (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | list[DataSourceResponse]]
    """

    kwargs = _get_kwargs(
        q=q,
        status=status,
        source_type=source_type,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    q: str | Unset = UNSET,
    status: str | Unset = UNSET,
    source_type: str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Error | list[DataSourceResponse] | None:
    """List all data sources

     List all indexed documentation and web sources for the authenticated user

    Args:
        q (str | Unset):
        status (str | Unset):
        source_type (str | Unset):
        limit (int | Unset):  Default: 100.
        offset (int | Unset):  Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | list[DataSourceResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            status=status,
            source_type=source_type,
            limit=limit,
            offset=offset,
        )
    ).parsed
