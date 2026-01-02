from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.doc_ls_response import DocLsResponse
from ...models.http_validation_error import HTTPValidationError
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
        "url": "/v2/data-sources/{source_id}/ls".format(
            source_id=quote(str(source_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DocLsResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = DocLsResponse.from_dict(response.json())

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
) -> Response[DocLsResponse | HTTPValidationError]:
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
) -> Response[DocLsResponse | HTTPValidationError]:
    """List directory

     List files and subdirectories at a virtual path (like unix ls).

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocLsResponse | HTTPValidationError]
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
) -> DocLsResponse | HTTPValidationError | None:
    """List directory

     List files and subdirectories at a virtual path (like unix ls).

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocLsResponse | HTTPValidationError
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
) -> Response[DocLsResponse | HTTPValidationError]:
    """List directory

     List files and subdirectories at a virtual path (like unix ls).

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DocLsResponse | HTTPValidationError]
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
) -> DocLsResponse | HTTPValidationError | None:
    """List directory

     List files and subdirectories at a virtual path (like unix ls).

    Args:
        source_id (str):
        path (str | Unset):  Default: '/'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DocLsResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            source_id=source_id,
            client=client,
            path=path,
        )
    ).parsed
