from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.package_search_read_file_request import PackageSearchReadFileRequest
from ...models.package_search_read_file_response_200 import PackageSearchReadFileResponse200
from ...types import Response


def _get_kwargs(
    *,
    body: PackageSearchReadFileRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/package-search/read-file",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | PackageSearchReadFileResponse200 | None:
    if response.status_code == 200:
        response_200 = PackageSearchReadFileResponse200.from_dict(response.json())

        return response_200

    if response.status_code == 400:
        response_400 = Error.from_dict(response.json())

        return response_400

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
) -> Response[Error | PackageSearchReadFileResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PackageSearchReadFileRequest,
) -> Response[Error | PackageSearchReadFileResponse200]:
    """Read specific lines from a package file

     Read exact lines from a source file within a public package. This is useful for
    fetching complete file content when you already have the file SHA256 hash
    (typically obtained from grep or hybrid search results). Maximum 200 lines per request.

    Args:
        body (PackageSearchReadFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PackageSearchReadFileResponse200]
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
    body: PackageSearchReadFileRequest,
) -> Error | PackageSearchReadFileResponse200 | None:
    """Read specific lines from a package file

     Read exact lines from a source file within a public package. This is useful for
    fetching complete file content when you already have the file SHA256 hash
    (typically obtained from grep or hybrid search results). Maximum 200 lines per request.

    Args:
        body (PackageSearchReadFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PackageSearchReadFileResponse200
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PackageSearchReadFileRequest,
) -> Response[Error | PackageSearchReadFileResponse200]:
    """Read specific lines from a package file

     Read exact lines from a source file within a public package. This is useful for
    fetching complete file content when you already have the file SHA256 hash
    (typically obtained from grep or hybrid search results). Maximum 200 lines per request.

    Args:
        body (PackageSearchReadFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PackageSearchReadFileResponse200]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PackageSearchReadFileRequest,
) -> Error | PackageSearchReadFileResponse200 | None:
    """Read specific lines from a package file

     Read exact lines from a source file within a public package. This is useful for
    fetching complete file content when you already have the file SHA256 hash
    (typically obtained from grep or hybrid search results). Maximum 200 lines per request.

    Args:
        body (PackageSearchReadFileRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PackageSearchReadFileResponse200
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
