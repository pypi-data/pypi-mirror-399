from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.data_source_response import DataSourceResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
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

    json_source_type: None | str | Unset
    if isinstance(source_type, Unset):
        json_source_type = UNSET
    else:
        json_source_type = source_type
    params["source_type"] = json_source_type

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/data-sources",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | list[DataSourceResponse] | None:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = DataSourceResponse.from_dict(response_200_item_data)

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
) -> Response[HTTPValidationError | list[DataSourceResponse]]:
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
    source_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[DataSourceResponse]]:
    """List data sources

     List all indexed documentation and web sources.

    Args:
        q (None | str | Unset): Optional substring filter (matches display_name/url/file_name)
        status (None | str | Unset): Optional status filter (e.g. completed|indexing|failed)
        source_type (None | str | Unset): Optional source type filter (e.g.
            web|documentation|research_paper)
        limit (int | Unset): Max data sources to return (db-level pagination) Default: 100.
        offset (int | Unset): Number of data sources to skip (db-level pagination) Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[DataSourceResponse]]
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
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[DataSourceResponse] | None:
    """List data sources

     List all indexed documentation and web sources.

    Args:
        q (None | str | Unset): Optional substring filter (matches display_name/url/file_name)
        status (None | str | Unset): Optional status filter (e.g. completed|indexing|failed)
        source_type (None | str | Unset): Optional source type filter (e.g.
            web|documentation|research_paper)
        limit (int | Unset): Max data sources to return (db-level pagination) Default: 100.
        offset (int | Unset): Number of data sources to skip (db-level pagination) Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[DataSourceResponse]
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
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[HTTPValidationError | list[DataSourceResponse]]:
    """List data sources

     List all indexed documentation and web sources.

    Args:
        q (None | str | Unset): Optional substring filter (matches display_name/url/file_name)
        status (None | str | Unset): Optional status filter (e.g. completed|indexing|failed)
        source_type (None | str | Unset): Optional source type filter (e.g.
            web|documentation|research_paper)
        limit (int | Unset): Max data sources to return (db-level pagination) Default: 100.
        offset (int | Unset): Number of data sources to skip (db-level pagination) Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | list[DataSourceResponse]]
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
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    source_type: None | str | Unset = UNSET,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> HTTPValidationError | list[DataSourceResponse] | None:
    """List data sources

     List all indexed documentation and web sources.

    Args:
        q (None | str | Unset): Optional substring filter (matches display_name/url/file_name)
        status (None | str | Unset): Optional status filter (e.g. completed|indexing|failed)
        source_type (None | str | Unset): Optional source type filter (e.g.
            web|documentation|research_paper)
        limit (int | Unset): Max data sources to return (db-level pagination) Default: 100.
        offset (int | Unset): Number of data sources to skip (db-level pagination) Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | list[DataSourceResponse]
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
