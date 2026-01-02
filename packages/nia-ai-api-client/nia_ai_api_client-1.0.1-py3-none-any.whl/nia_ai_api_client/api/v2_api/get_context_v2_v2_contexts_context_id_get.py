from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.context_share_response import ContextShareResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    context_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v2/contexts/{context_id}".format(
            context_id=quote(str(context_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ContextShareResponse | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = ContextShareResponse.from_dict(response.json())

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
) -> Response[ContextShareResponse | HTTPValidationError]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContextShareResponse | HTTPValidationError]:
    """Get context

     Retrieve a specific context by ID.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextShareResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        context_id=context_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ContextShareResponse | HTTPValidationError | None:
    """Get context

     Retrieve a specific context by ID.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextShareResponse | HTTPValidationError
    """

    return sync_detailed(
        context_id=context_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ContextShareResponse | HTTPValidationError]:
    """Get context

     Retrieve a specific context by ID.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ContextShareResponse | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        context_id=context_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    context_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> ContextShareResponse | HTTPValidationError | None:
    """Get context

     Retrieve a specific context by ID.

    Args:
        context_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ContextShareResponse | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            context_id=context_id,
            client=client,
        )
    ).parsed
