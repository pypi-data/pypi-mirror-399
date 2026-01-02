from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.code_grep_request import CodeGrepRequest
from ...models.code_grep_response import CodeGrepResponse
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    repository_id: str,
    *,
    body: CodeGrepRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/repositories/{repository_id}/grep".format(
            repository_id=quote(str(repository_id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CodeGrepResponse | Error | None:
    if response.status_code == 200:
        response_200 = CodeGrepResponse.from_dict(response.json())

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

    if response.status_code == 500:
        response_500 = Error.from_dict(response.json())

        return response_500

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[CodeGrepResponse | Error]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> Response[CodeGrepResponse | Error]:
    """Search repository code with regex

     Search repository code with a regex pattern.
    Like the Unix 'grep' command, but for indexed repository code.
    Searches through all code chunks and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before), case sensitivity,
    whole word matching, and multiple output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CodeGrepResponse | Error]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> CodeGrepResponse | Error | None:
    """Search repository code with regex

     Search repository code with a regex pattern.
    Like the Unix 'grep' command, but for indexed repository code.
    Searches through all code chunks and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before), case sensitivity,
    whole word matching, and multiple output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CodeGrepResponse | Error
    """

    return sync_detailed(
        repository_id=repository_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> Response[CodeGrepResponse | Error]:
    """Search repository code with regex

     Search repository code with a regex pattern.
    Like the Unix 'grep' command, but for indexed repository code.
    Searches through all code chunks and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before), case sensitivity,
    whole word matching, and multiple output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CodeGrepResponse | Error]
    """

    kwargs = _get_kwargs(
        repository_id=repository_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repository_id: str,
    *,
    client: AuthenticatedClient | Client,
    body: CodeGrepRequest,
) -> CodeGrepResponse | Error | None:
    """Search repository code with regex

     Search repository code with a regex pattern.
    Like the Unix 'grep' command, but for indexed repository code.
    Searches through all code chunks and returns matches with context.

    By default (exhaustive=true), iterates through ALL indexed chunks to find every match,
    providing true grep-like behavior. For faster but potentially incomplete results,
    set exhaustive=false to use BM25 keyword search first.

    Supports asymmetric context lines (A for after, B for before), case sensitivity,
    whole word matching, and multiple output modes.

    Args:
        repository_id (str):
        body (CodeGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CodeGrepResponse | Error
    """

    return (
        await asyncio_detailed(
            repository_id=repository_id,
            client=client,
            body=body,
        )
    ).parsed
