from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.get_documentation_tree_response_200 import GetDocumentationTreeResponse200
from ...types import Response


def _get_kwargs(
    source_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/data-sources/{source_id}/tree".format(
            source_id=quote(str(source_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GetDocumentationTreeResponse200 | None:
    if response.status_code == 200:
        response_200 = GetDocumentationTreeResponse200.from_dict(response.json())

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
) -> Response[Error | GetDocumentationTreeResponse200]:
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
) -> Response[Error | GetDocumentationTreeResponse200]:
    """Get documentation tree structure

     Get the filesystem-like tree structure of indexed documentation.
    Shows all indexed pages organized as a virtual file tree, making it easy
    to browse documentation structure without remembering URLs.

    Args:
        source_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetDocumentationTreeResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetDocumentationTreeResponse200 | None:
    """Get documentation tree structure

     Get the filesystem-like tree structure of indexed documentation.
    Shows all indexed pages organized as a virtual file tree, making it easy
    to browse documentation structure without remembering URLs.

    Args:
        source_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetDocumentationTreeResponse200
    """

    return sync_detailed(
        source_id=source_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | GetDocumentationTreeResponse200]:
    """Get documentation tree structure

     Get the filesystem-like tree structure of indexed documentation.
    Shows all indexed pages organized as a virtual file tree, making it easy
    to browse documentation structure without remembering URLs.

    Args:
        source_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GetDocumentationTreeResponse200]
    """

    kwargs = _get_kwargs(
        source_id=source_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | GetDocumentationTreeResponse200 | None:
    """Get documentation tree structure

     Get the filesystem-like tree structure of indexed documentation.
    Shows all indexed pages organized as a virtual file tree, making it easy
    to browse documentation structure without remembering URLs.

    Args:
        source_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GetDocumentationTreeResponse200
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
        )
    ).parsed
