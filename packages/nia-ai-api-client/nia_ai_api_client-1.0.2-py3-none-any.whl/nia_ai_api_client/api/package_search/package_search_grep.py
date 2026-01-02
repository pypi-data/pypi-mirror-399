from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.package_search_grep_request import PackageSearchGrepRequest
from ...models.package_search_response import PackageSearchResponse
from ...types import Response


def _get_kwargs(
    *,
    body: PackageSearchGrepRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/package-search/grep",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | PackageSearchResponse | None:
    if response.status_code == 200:
        response_200 = PackageSearchResponse.from_dict(response.json())

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
) -> Response[Error | PackageSearchResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PackageSearchGrepRequest,
) -> Response[Error | PackageSearchResponse]:
    """Search package source code with regex

     Execute a grep-style regex search over the source code of a public package.
    This endpoint is useful for deterministically finding specific code patterns in packages
    before implementing solutions that use external dependencies. Supports multiple package
    registries including npm, PyPI, crates.io, and Go modules.

    Args:
        body (PackageSearchGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PackageSearchResponse]
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
    body: PackageSearchGrepRequest,
) -> Error | PackageSearchResponse | None:
    """Search package source code with regex

     Execute a grep-style regex search over the source code of a public package.
    This endpoint is useful for deterministically finding specific code patterns in packages
    before implementing solutions that use external dependencies. Supports multiple package
    registries including npm, PyPI, crates.io, and Go modules.

    Args:
        body (PackageSearchGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PackageSearchResponse
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: PackageSearchGrepRequest,
) -> Response[Error | PackageSearchResponse]:
    """Search package source code with regex

     Execute a grep-style regex search over the source code of a public package.
    This endpoint is useful for deterministically finding specific code patterns in packages
    before implementing solutions that use external dependencies. Supports multiple package
    registries including npm, PyPI, crates.io, and Go modules.

    Args:
        body (PackageSearchGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | PackageSearchResponse]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: PackageSearchGrepRequest,
) -> Error | PackageSearchResponse | None:
    """Search package source code with regex

     Execute a grep-style regex search over the source code of a public package.
    This endpoint is useful for deterministically finding specific code patterns in packages
    before implementing solutions that use external dependencies. Supports multiple package
    registries including npm, PyPI, crates.io, and Go modules.

    Args:
        body (PackageSearchGrepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | PackageSearchResponse
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
