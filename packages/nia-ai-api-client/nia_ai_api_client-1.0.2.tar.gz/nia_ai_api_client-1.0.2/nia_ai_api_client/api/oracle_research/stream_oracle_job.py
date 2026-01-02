from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.error import Error
from ...types import Response


def _get_kwargs(
    job_id: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/oracle/jobs/{job_id}/stream".format(
            job_id=quote(str(job_id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Error | str | None:
    if response.status_code == 200:
        response_200 = response.text
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


def _build_response(*, client: AuthenticatedClient | Client, response: httpx.Response) -> Response[Error | str]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | str]:
    """Stream Oracle job events (SSE)

     Subscribe to real-time progress updates for an Oracle research job via Server-Sent Events.

    This endpoint supports reconnection - you can subscribe to a running job at any time
    to receive remaining events. For completed jobs, returns the final result immediately.

    **Event types:**
    - `connected`: Connection established with session info
    - `started`: Research job has started
    - `iteration_start`: New research iteration beginning
    - `tool_start`: Tool execution starting (includes action, args, reason)
    - `tool_complete`: Tool finished (includes success status)
    - `generating_report`: Final report synthesis starting
    - `complete`: Research finished with full result
    - `error`: Error occurred
    - `workflow_event`: Workflow state change

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | str]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | str | None:
    """Stream Oracle job events (SSE)

     Subscribe to real-time progress updates for an Oracle research job via Server-Sent Events.

    This endpoint supports reconnection - you can subscribe to a running job at any time
    to receive remaining events. For completed jobs, returns the final result immediately.

    **Event types:**
    - `connected`: Connection established with session info
    - `started`: Research job has started
    - `iteration_start`: New research iteration beginning
    - `tool_start`: Tool execution starting (includes action, args, reason)
    - `tool_complete`: Tool finished (includes success status)
    - `generating_report`: Final report synthesis starting
    - `complete`: Research finished with full result
    - `error`: Error occurred
    - `workflow_event`: Workflow state change

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | str
    """

    return sync_detailed(
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Response[Error | str]:
    """Stream Oracle job events (SSE)

     Subscribe to real-time progress updates for an Oracle research job via Server-Sent Events.

    This endpoint supports reconnection - you can subscribe to a running job at any time
    to receive remaining events. For completed jobs, returns the final result immediately.

    **Event types:**
    - `connected`: Connection established with session info
    - `started`: Research job has started
    - `iteration_start`: New research iteration beginning
    - `tool_start`: Tool execution starting (includes action, args, reason)
    - `tool_complete`: Tool finished (includes success status)
    - `generating_report`: Final report synthesis starting
    - `complete`: Research finished with full result
    - `error`: Error occurred
    - `workflow_event`: Workflow state change

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Error | str]
    """

    kwargs = _get_kwargs(
        job_id=job_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    job_id: str,
    *,
    client: AuthenticatedClient | Client,
) -> Error | str | None:
    """Stream Oracle job events (SSE)

     Subscribe to real-time progress updates for an Oracle research job via Server-Sent Events.

    This endpoint supports reconnection - you can subscribe to a running job at any time
    to receive remaining events. For completed jobs, returns the final result immediately.

    **Event types:**
    - `connected`: Connection established with session info
    - `started`: Research job has started
    - `iteration_start`: New research iteration beginning
    - `tool_start`: Tool execution starting (includes action, args, reason)
    - `tool_complete`: Tool finished (includes success status)
    - `generating_report`: Final report synthesis starting
    - `complete`: Research finished with full result
    - `error`: Error occurred
    - `workflow_event`: Workflow state change

    Args:
        job_id (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Error | str
    """

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
        )
    ).parsed
