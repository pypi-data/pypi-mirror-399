from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.list_documentation_directory_response_200 import ListDocumentationDirectoryResponse200
from ...types import UNSET, Response, Unset


def _get_kwargs(
    source_id: str,
    *,
    path: str | Unset = "/",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["path"] = path

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/data-sources/{source_id}/ls".format(
            source_id=quote(str(source_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | ListDocumentationDirectoryResponse200 | None:
    if response.status_code == 200:
        response_200 = ListDocumentationDirectoryResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 403:
        response_403 = Error.from_dict(response.json())

        return response_403

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
) -> Response[Error | ListDocumentationDirectoryResponse200]:
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
    path: str | Unset = "/",
) -> Response[Error | ListDocumentationDirectoryResponse200]:
    """List documentation directory contents

     List contents of a virtual directory in the documentation.
    Shows files (pages) and subdirectories at the specified path,
    similar to the Unix 'ls' command.

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ListDocumentationDirectoryResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str | Unset = "/",
) -> Error | ListDocumentationDirectoryResponse200 | None:
    """List documentation directory contents

     List contents of a virtual directory in the documentation.
    Shows files (pages) and subdirectories at the specified path,
    similar to the Unix 'ls' command.

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ListDocumentationDirectoryResponse200
    """

    return sync_detailed(
        source_id=source_id,
        client=client,
        path=path,
    ).parsed


async def asyncio_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str | Unset = "/",
) -> Response[Error | ListDocumentationDirectoryResponse200]:
    """List documentation directory contents

     List contents of a virtual directory in the documentation.
    Shows files (pages) and subdirectories at the specified path,
    similar to the Unix 'ls' command.

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | ListDocumentationDirectoryResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
        path=path,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
    path: str | Unset = "/",
) -> Error | ListDocumentationDirectoryResponse200 | None:
    """List documentation directory contents

     List contents of a virtual directory in the documentation.
    Shows files (pages) and subdirectories at the specified path,
    similar to the Unix 'ls' command.

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | ListDocumentationDirectoryResponse200
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            path=path,
        )
    ).parsed
