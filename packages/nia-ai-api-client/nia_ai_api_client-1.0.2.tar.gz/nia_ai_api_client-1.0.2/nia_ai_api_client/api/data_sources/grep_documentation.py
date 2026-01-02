from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.grep_documentation_body import GrepDocumentationBody
from ...models.grep_documentation_response_200 import GrepDocumentationResponse200
from ...types import Response


def _get_kwargs(
    source_id: str,
    *,
    body: GrepDocumentationBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/data-sources/{source_id}/grep".format(
            source_id=quote(str(source_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | GrepDocumentationResponse200 | None:
    if response.status_code == 200:
        response_200 = GrepDocumentationResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

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
) -> Response[Error | GrepDocumentationResponse200]:
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
    body: GrepDocumentationBody,
) -> Response[Error | GrepDocumentationResponse200]:
    """Search documentation with regex

     Search documentation content with a regex pattern.
    Like the Unix 'grep' command, but for indexed documentation.
    Searches through all pages and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before),
    case sensitivity, whole word matching, and multiple output modes.

    Args:
        source_id (str):
        body (GrepDocumentationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GrepDocumentationResponse200]
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
    body: GrepDocumentationBody,
) -> Error | GrepDocumentationResponse200 | None:
    """Search documentation with regex

     Search documentation content with a regex pattern.
    Like the Unix 'grep' command, but for indexed documentation.
    Searches through all pages and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before),
    case sensitivity, whole word matching, and multiple output modes.

    Args:
        source_id (str):
        body (GrepDocumentationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GrepDocumentationResponse200
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
    body: GrepDocumentationBody,
) -> Response[Error | GrepDocumentationResponse200]:
    """Search documentation with regex

     Search documentation content with a regex pattern.
    Like the Unix 'grep' command, but for indexed documentation.
    Searches through all pages and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before),
    case sensitivity, whole word matching, and multiple output modes.

    Args:
        source_id (str):
        body (GrepDocumentationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | GrepDocumentationResponse200]
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
    body: GrepDocumentationBody,
) -> Error | GrepDocumentationResponse200 | None:
    """Search documentation with regex

     Search documentation content with a regex pattern.
    Like the Unix 'grep' command, but for indexed documentation.
    Searches through all pages and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before),
    case sensitivity, whole word matching, and multiple output modes.

    Args:
        source_id (str):
        body (GrepDocumentationBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | GrepDocumentationResponse200
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            body=body,
        )
    ).parsed
