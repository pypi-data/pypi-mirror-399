from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...models.oracle_session_messages_response import OracleSessionMessagesResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    session_id: str,
    *,
    limit: int | Unset = 100,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oracle/sessions/{session_id}/messages".format(
            session_id=quote(str(session_id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Error | OracleSessionMessagesResponse | None:
    if response.status_code == 200:
        response_200 = OracleSessionMessagesResponse.from_dict(response.json())

        return response_200

    if response.status_code == 401:
        response_401 = Error.from_dict(response.json())

        return response_401

    if response.status_code == 404:
        response_404 = Error.from_dict(response.json())

        return response_404

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Error | OracleSessionMessagesResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 100,
) -> Response[Error | OracleSessionMessagesResponse]:
    """Get Oracle session chat messages

     Get chat messages for an Oracle research session, including the original query/report and follow-up
    messages.

    Args:
        session_id (str):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OracleSessionMessagesResponse]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 100,
) -> Error | OracleSessionMessagesResponse | None:
    """Get Oracle session chat messages

     Get chat messages for an Oracle research session, including the original query/report and follow-up
    messages.

    Args:
        session_id (str):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OracleSessionMessagesResponse
    """

    return sync_detailed(
        session_id=session_id,
        client=client,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 100,
) -> Response[Error | OracleSessionMessagesResponse]:
    """Get Oracle session chat messages

     Get chat messages for an Oracle research session, including the original query/report and follow-up
    messages.

    Args:
        session_id (str):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | OracleSessionMessagesResponse]
    """

    kwargs = _get_kwargs(
        session_id=session_id,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    session_id: str,
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 100,
) -> Error | OracleSessionMessagesResponse | None:
    """Get Oracle session chat messages

     Get chat messages for an Oracle research session, including the original query/report and follow-up
    messages.

    Args:
        session_id (str):
        limit (int | Unset):  Default: 100.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | OracleSessionMessagesResponse
    """

    return (
        await asyncio_detailed(
            session_id=session_id,
            client=client,
            limit=limit,
        )
    ).parsed
