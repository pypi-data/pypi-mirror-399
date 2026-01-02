from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_data_source_content_body import GetDataSourceContentBody
from ...models.get_data_source_content_response_200 import GetDataSourceContentResponse200
from ...types import Response


def _get_kwargs(
    source_id: str,
    *,
    body: GetDataSourceContentBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/data-sources/{source_id}/content".format(
            source_id=quote(str(source_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetDataSourceContentResponse200 | None:
    if response.status_code == 200:
        response_200 = GetDataSourceContentResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if response.status_code == 429:
        response_429 = Error.from_dict(response.json())

        return response_429

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | GetDataSourceContentResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GetDataSourceContentBody,
) -> Response[Error | GetDataSourceContentResponse200]:
    """Get data source page content

     Retrieve the full content of a page from an indexed documentation source.
    Provide the virtual path within the documentation to get its contents.

    Args:
        source_id (str):
        body (GetDataSourceContentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetDataSourceContentResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GetDataSourceContentBody,
) -> Error | GetDataSourceContentResponse200 | None:
    """Get data source page content

     Retrieve the full content of a page from an indexed documentation source.
    Provide the virtual path within the documentation to get its contents.

    Args:
        source_id (str):
        body (GetDataSourceContentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetDataSourceContentResponse200
    """

    return sync_detailed(
        source_id=source_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GetDataSourceContentBody,
) -> Response[Error | GetDataSourceContentResponse200]:
    """Get data source page content

     Retrieve the full content of a page from an indexed documentation source.
    Provide the virtual path within the documentation to get its contents.

    Args:
        source_id (str):
        body (GetDataSourceContentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetDataSourceContentResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: GetDataSourceContentBody,
) -> Error | GetDataSourceContentResponse200 | None:
    """Get data source page content

     Retrieve the full content of a page from an indexed documentation source.
    Provide the virtual path within the documentation to get its contents.

    Args:
        source_id (str):
        body (GetDataSourceContentBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetDataSourceContentResponse200
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            body=body,
        )
    ).parsed
